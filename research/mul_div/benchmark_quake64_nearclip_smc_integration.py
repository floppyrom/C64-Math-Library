#!/usr/bin/env python3
"""Benchmark Quake64-native prepared fraction in the near0 clipping shape.

This is the integration follow-up to benchmark_quake64_prepared_fraction_smc.py.
It includes the caller work that actually differs at the Quake64 near-plane
clip site:

  * form n = ZCLIP-z0 and d = z1-z0
  * form signed X/Y endpoint deltas
  * prepare the dynamic ratio once
  * apply it to X and Y
  * accumulate both clipped coordinates
  * write ZCLIP

The candidate reuses Quake64's own quarter-square tables at $F000-$F7FF and its
existing math scratch. It is compared with a literal standalone transcription
of the current scale_nd + lerp16 near0 path.

This is still not a full Quake64 build/runtime certification: CAM loading,
edge-loop dispatch, later projection and VIC/IRQ/SID activity are outside the
measured region.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(HERE))

from mini6502 import CPU  # noqa: E402
from benchmark_quake64_prepared_fraction_smc import (  # noqa: E402
    QNATIVE_D,
    QNATIVE_N,
    QNATIVE_Y,
    QNATIVE_Z,
    quake_smc_cpu,
)
from benchmark_quake64_nearclip_integration import (  # noqa: E402
    E0X,
    E0Y,
    E0Z,
    E1X,
    E1Y,
    E1Z,
    current_quake_cpu,
    output,
    set_endpoints,
)
from benchmark_prepared_ratio import (  # noqa: E402
    QUAKE_COMMIT,
    ZCLIP,
    err_summary,
    gets16,
    patch,
    put16,
    summarize,
    trunc_div,
)

WRAPPER = 0xD000


def wrapper_source(prep: int, apply: int) -> str:
    return f"""E0X=${E0X:04X}
E0Y=${E0Y:04X}
E0Z=${E0Z:04X}
E1X=${E1X:04X}
E1Y=${E1Y:04X}
E1Z=${E1Z:04X}
nlo=${QNATIVE_N:02X}
nhi=${QNATIVE_N+1:02X}
dlo=${QNATIVE_D:02X}
dhi=${QNATIVE_D+1:02X}
ylo=${QNATIVE_Y:02X}
yhi=${QNATIVE_Y+1:02X}
rot0=${QNATIVE_Z:02X}
rot1=${QNATIVE_Z+1:02X}
PREP=${prep:04X}
APPLY=${apply:04X}
.org ${WRAPPER:04X}
quake_smc_near0:
    ; Shared dynamic fraction d=z1-z0, n=ZCLIP-z0.
    sec
    lda E1Z
    sbc E0Z
    sta dlo
    lda E1Z+1
    sbc E0Z+1
    sta dhi

    sec
    lda #$00
    sbc E0Z
    sta nlo
    lda #$01
    sbc E0Z+1
    sta nhi

    jsr PREP

    ; X component.
    sec
    lda E1X
    sbc E0X
    sta ylo
    lda E1X+1
    sbc E0X+1
    sta yhi
    jsr APPLY
    clc
    lda rot0
    adc E0X
    sta E0X
    lda rot1
    adc E0X+1
    sta E0X+1

    ; Y component, same prepared ratio.
    sec
    lda E1Y
    sbc E0Y
    sta ylo
    lda E1Y+1
    sbc E0Y+1
    sta yhi
    jsr APPLY
    clc
    lda rot0
    adc E0Y
    sta E0Y
    lda rot1
    adc E0Y+1
    sta E0Y+1

    lda #$00
    sta E0Z
    lda #$01
    sta E0Z+1
    rts
"""


def candidate_cpu(rounding: str):
    cpu, prep, apply, code_bytes = quake_smc_cpu(rounding)
    labels = patch(cpu.mem, wrapper_source(prep, apply))
    return cpu, labels['quake_smc_near0'], code_bytes


def prepared_delta(v: int, n: int, d: int, rounding: str) -> int:
    if rounding == 'nearest':
        m = ((n << 16) + d // 2) // d
    elif rounding == 'floor':
        m = (n << 16) // d
    else:
        raise ValueError(rounding)
    sign = -1 if v < 0 else 1
    return sign * ((abs(v) * m) >> 16)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    near_cpu, near_entry, near_bytes = candidate_cpu('nearest')
    floor_cpu, floor_entry, floor_bytes = candidate_cpu('floor')
    quake, quake_entry = current_quake_cpu()

    rows = {
        'quake_smc_nearest': {'cycles': [], 'contract_errors': 0, 'exact_errors': [], 'code_bytes': near_bytes},
        'quake_smc_floor': {'cycles': [], 'contract_errors': 0, 'exact_errors': [], 'code_bytes': floor_bytes},
        'quake64_current': {'cycles': [], 'exact_errors': []},
    }

    rng = random.Random(args.seed)
    for _ in range(args.cases):
        e0z = rng.randint(-8192, ZCLIP - 1)
        e1z = rng.randint(ZCLIP + 1, 8191)
        n = ZCLIP - e0z
        d = e1z - e0z
        assert 0 < n < d <= 0xFFFF

        e0x = rng.randint(-4096, 4095)
        e0y = rng.randint(-4096, 4095)
        dx = rng.randint(-8192, 8191)
        dy = rng.randint(-8192, 8191)
        e1x = e0x + dx
        e1y = e0y + dy

        exact_x = e0x + trunc_div(dx * n, d)
        exact_y = e0y + trunc_div(dy * n, d)

        for name, cpu, entry, rounding in (
            ('quake_smc_nearest', near_cpu, near_entry, 'nearest'),
            ('quake_smc_floor', floor_cpu, floor_entry, 'floor'),
        ):
            set_endpoints(cpu, e0x, e0y, e0z, e1x, e1y, e1z)
            cyc = cpu.call(entry)
            gx, gy, gz = output(cpu)
            refx = e0x + prepared_delta(dx, n, d, rounding)
            refy = e0y + prepared_delta(dy, n, d, rounding)
            row = rows[name]
            row['cycles'].append(cyc)
            row['contract_errors'] += int((gx, gy, gz) != (refx, refy, ZCLIP))
            row['exact_errors'].extend((gx - exact_x, gy - exact_y))

        set_endpoints(quake, e0x, e0y, e0z, e1x, e1y, e1z)
        qcyc = quake.call(quake_entry)
        qx, qy, qz = output(quake)
        rows['quake64_current']['cycles'].append(qcyc)
        rows['quake64_current']['exact_errors'].extend((qx - exact_x, qy - exact_y))
        if qz != ZCLIP:
            raise AssertionError(('quake z', qz))

    qmean = statistics.fmean(rows['quake64_current']['cycles'])
    result = {
        'status': 'standalone_nearclip_game_native_integration_research_not_full_build_certification',
        'quake64_source_commit': QUAKE_COMMIT,
        'cases': args.cases,
        'seed': args.seed,
        'included_work': [
            'n/d formation',
            'X/Y delta formation',
            'Quake-native prepared fraction',
            'two Quake-native SMC applications',
            'endpoint accumulation',
            'near-Z writeback',
        ],
        'excluded_work': [
            'CAM endpoint loading',
            'edge-loop dispatch',
            'projection after clipping',
            'full Quake64 build/runtime integration',
            'VIC/IRQ/SID effects',
        ],
        'variants': {},
    }

    for name in ('quake_smc_nearest', 'quake_smc_floor'):
        row = rows[name]
        cycles = summarize(row['cycles'])
        result['variants'][name] = {
            'cycles': cycles,
            'prepared_contract_errors': row['contract_errors'],
            'accuracy_vs_exact_endpoint': err_summary(row['exact_errors']),
            'speedup_vs_quake64_percent': 100.0 * (qmean - cycles['mean']) / qmean,
            'prepared_kernel_code_bytes': row['code_bytes'],
        }

    result['variants']['quake64_current'] = {
        'cycles': summarize(rows['quake64_current']['cycles']),
        'accuracy_vs_exact_endpoint': err_summary(rows['quake64_current']['exact_errors']),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for name, row in result['variants'].items():
            print(
                f"{name:20s} mean={row['cycles']['mean']:.3f} "
                f"range={row['cycles']['min']}-{row['cycles']['max']}"
                + (f" speedup={row['speedup_vs_quake64_percent']:.2f}% errors={row['prepared_contract_errors']}"
                   if name != 'quake64_current' else '')
            )

    bad = sum(rows[name].get('contract_errors', 0) for name in rows)
    if bad:
        raise SystemExit(1)
    for name in ('quake_smc_nearest', 'quake_smc_floor'):
        if max(abs(e) for e in rows[name]['exact_errors']) > 1:
            raise SystemExit(f'{name} exceeded <=1 exact endpoint error')


if __name__ == '__main__':
    main()
