#!/usr/bin/env python3
"""Benchmark integrated Quake64 near0 clipping against V2 ratio candidates.

This includes the surrounding work that differs between the implementations:

Quake current:
    compute n/d
    save n/d on stack
    form X delta -> scale_nd + lerp16 -> add to endpoint
    restore n/d
    form Y delta -> scale_nd + lerp16 -> add to endpoint
    set clipped Z

Prepared separate candidate:
    compute n/d into library vectors
    PREP once
    form X delta -> APPLY -> add to endpoint
    form Y delta -> APPLY -> add to endpoint
    set clipped Z

Fused SCALE2 candidate:
    compute n/d into library vectors
    form X and Y deltas into library X/Y vectors
    one SCALE2 call -> two scaled deltas
    add both to endpoint
    set clipped Z

The V2 candidates use the corrected profile-native Pareto quarter-square geometry.
Both nearest and floor Q0.16 forms are measured.

This is a standalone integration harness derived from the Quake64 source shape;
it does not patch or build the Quake64 repository itself. It includes caller
marshalling around the arithmetic operation, but not unrelated edge-loop, CAM
loading, projection, IRQ/VIC/SID costs, or a complete game build.
"""
from __future__ import annotations

import argparse
import hashlib
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
from generate_prepared_fraction_pareto_inline import generate as generate_inline  # noqa: E402
from generate_scale2_fraction_pareto import generate as generate_scale2  # noqa: E402
from benchmark_prepared_ratio import (  # noqa: E402
    MATH_INIT,
    QUAKE_COMMIT,
    V2_PRG,
    ZCLIP,
    err_summary,
    gets16,
    load_prg,
    patch,
    put16,
    quake_cpu,
    summarize,
    trunc_div,
)

# Isolated integration endpoint state.
E0X, E0Y, E0Z = 0xB000, 0xB002, 0xB004
E1X, E1Y, E1Z = 0xB006, 0xB008, 0xB00A

# Stable public vectors.
PX0 = 0xC000
PY0 = 0xC004
PZ0 = 0xC008
PZ2 = 0xC00A
PN0 = 0xC010
PD0 = 0xC014

PREP = 0xE000
APPLY = 0xE800
SCALE2 = 0xE000
WRAPPER = 0xF000

# Quake standalone scratch addresses from benchmark_prepared_ratio.py.
QN = 0x48
QD = 0x4A
QY = 0x4C
QROT = 0x45


def candidate_wrapper_source() -> str:
    return f"""E0X=${E0X:04X}
E0Y=${E0Y:04X}
E0Z=${E0Z:04X}
E1X=${E1X:04X}
E1Y=${E1Y:04X}
E1Z=${E1Z:04X}
Y0=${PY0:04X}
Z0=${PZ0:04X}
N0=${PN0:04X}
D0=${PD0:04X}
PREP=${PREP:04X}
APPLY=${APPLY:04X}
.org ${WRAPPER:04X}
candidate_near0:
    ; d = e1z-e0z directly into the library D vector.
    sec
    lda E1Z
    sbc E0Z
    sta D0
    lda E1Z+1
    sbc E0Z+1
    sta D0+1

    ; n = ZCLIP-e0z directly into the library N vector.
    sec
    lda #$00
    sbc E0Z
    sta N0
    lda #$01
    sbc E0Z+1
    sta N0+1

    jsr PREP

    ; x delta = e1x-e0x -> public Y input.
    sec
    lda E1X
    sbc E0X
    sta Y0
    lda E1X+1
    sbc E0X+1
    sta Y0+1
    jsr APPLY
    clc
    lda Z0
    adc E0X
    sta E0X
    lda Z0+1
    adc E0X+1
    sta E0X+1

    ; y delta = e1y-e0y, same prepared ratio.
    sec
    lda E1Y
    sbc E0Y
    sta Y0
    lda E1Y+1
    sbc E0Y+1
    sta Y0+1
    jsr APPLY
    clc
    lda Z0
    adc E0Y
    sta E0Y
    lda Z0+1
    adc E0Y+1
    sta E0Y+1

    lda #$00
    sta E0Z
    lda #$01
    sta E0Z+1
    rts
"""


def scale2_wrapper_source() -> str:
    return f"""E0X=${E0X:04X}
E0Y=${E0Y:04X}
E0Z=${E0Z:04X}
E1X=${E1X:04X}
E1Y=${E1Y:04X}
E1Z=${E1Z:04X}
X0=${PX0:04X}
Y0=${PY0:04X}
Z0=${PZ0:04X}
Z2=${PZ2:04X}
N0=${PN0:04X}
D0=${PD0:04X}
SCALE2=${SCALE2:04X}
.org ${WRAPPER:04X}
scale2_near0:
    ; Shared dynamic fraction.
    sec
    lda E1Z
    sbc E0Z
    sta D0
    lda E1Z+1
    sbc E0Z+1
    sta D0+1
    sec
    lda #$00
    sbc E0Z
    sta N0
    lda #$01
    sbc E0Z+1
    sta N0+1

    ; Feed both component deltas before the one compound math call.
    sec
    lda E1X
    sbc E0X
    sta X0
    lda E1X+1
    sbc E0X+1
    sta X0+1
    sec
    lda E1Y
    sbc E0Y
    sta Y0
    lda E1Y+1
    sbc E0Y+1
    sta Y0+1

    jsr SCALE2

    clc
    lda Z0
    adc E0X
    sta E0X
    lda Z0+1
    adc E0X+1
    sta E0X+1

    clc
    lda Z2
    adc E0Y
    sta E0Y
    lda Z2+1
    adc E0Y+1
    sta E0Y+1

    lda #$00
    sta E0Z
    lda #$01
    sta E0Z+1
    rts
"""


def quake_wrapper_source(qrun: int) -> str:
    return f"""E0X=${E0X:04X}
E0Y=${E0Y:04X}
E0Z=${E0Z:04X}
E1X=${E1X:04X}
E1Y=${E1Y:04X}
E1Z=${E1Z:04X}
nlo=${QN:02X}
nhi=${QN+1:02X}
dlo=${QD:02X}
dhi=${QD+1:02X}
ylo=${QY:02X}
yhi=${QY+1:02X}
rot0=${QROT:02X}
rot1=${QROT+1:02X}
NLRUN=${qrun:04X}
.org ${WRAPPER:04X}
quake_near0:
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

    lda nlo
    pha
    lda nhi
    pha
    lda dlo
    pha
    lda dhi
    pha

    sec
    lda E1X
    sbc E0X
    sta ylo
    lda E1X+1
    sbc E0X+1
    sta yhi
    jsr NLRUN
    clc
    adc E0X
    sta E0X
    lda rot1
    adc E0X+1
    sta E0X+1

    pla
    sta dhi
    pla
    sta dlo
    pla
    sta nhi
    pla
    sta nlo

    sec
    lda E1Y
    sbc E0Y
    sta ylo
    lda E1Y+1
    sbc E0Y+1
    sta yhi
    jsr NLRUN
    clc
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
    cpu = CPU(load_prg(V2_PRG))
    cpu.d = 0
    cpu.call(MATH_INIT)
    patch(cpu.mem, generate_inline(PREP, APPLY, rounding))
    labels = patch(cpu.mem, candidate_wrapper_source())
    return cpu, labels['candidate_near0']


def scale2_cpu(rounding: str):
    cpu = CPU(load_prg(V2_PRG))
    cpu.d = 0
    cpu.call(MATH_INIT)
    patch(cpu.mem, generate_scale2(SCALE2, rounding))
    labels = patch(cpu.mem, scale2_wrapper_source())
    return cpu, labels['scale2_near0']


def current_quake_cpu():
    cpu, qrun = quake_cpu()
    labels = patch(cpu.mem, quake_wrapper_source(qrun))
    return cpu, labels['quake_near0']


def set_endpoints(cpu: CPU, e0x: int, e0y: int, e0z: int,
                  e1x: int, e1y: int, e1z: int) -> None:
    put16(cpu.mem, E0X, e0x)
    put16(cpu.mem, E0Y, e0y)
    put16(cpu.mem, E0Z, e0z)
    put16(cpu.mem, E1X, e1x)
    put16(cpu.mem, E1Y, e1y)
    put16(cpu.mem, E1Z, e1z)


def output(cpu: CPU):
    return gets16(cpu.mem, E0X), gets16(cpu.mem, E0Y), gets16(cpu.mem, E0Z)


def prepared_delta(v: int, n: int, d: int, rounding: str) -> int:
    if rounding == 'nearest':
        m = ((n << 16) + d // 2) // d
    else:
        m = (n << 16) // d
    sign = -1 if v < 0 else 1
    return sign * ((abs(v) * m) >> 16)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    nearest_cpu, nearest_entry = candidate_cpu('nearest')
    floor_cpu, floor_entry = candidate_cpu('floor')
    scale_nearest_cpu, scale_nearest_entry = scale2_cpu('nearest')
    scale_floor_cpu, scale_floor_entry = scale2_cpu('floor')
    quake, quake_entry = current_quake_cpu()

    rows = {
        'prepared_inline_nearest': {'cycles': [], 'contract_errors': 0, 'exact_errors': []},
        'prepared_inline_floor': {'cycles': [], 'contract_errors': 0, 'exact_errors': []},
        'scale2_nearest': {'cycles': [], 'contract_errors': 0, 'exact_errors': []},
        'scale2_floor': {'cycles': [], 'contract_errors': 0, 'exact_errors': []},
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
            ('prepared_inline_nearest', nearest_cpu, nearest_entry, 'nearest'),
            ('prepared_inline_floor', floor_cpu, floor_entry, 'floor'),
            ('scale2_nearest', scale_nearest_cpu, scale_nearest_entry, 'nearest'),
            ('scale2_floor', scale_floor_cpu, scale_floor_entry, 'floor'),
        ):
            set_endpoints(cpu, e0x, e0y, e0z, e1x, e1y, e1z)
            cyc = cpu.call(entry)
            gx, gy, gz = output(cpu)
            refx = e0x + prepared_delta(dx, n, d, rounding)
            refy = e0y + prepared_delta(dy, n, d, rounding)
            rows[name]['cycles'].append(cyc)
            rows[name]['contract_errors'] += int((gx, gy, gz) != (refx, refy, ZCLIP))
            rows[name]['exact_errors'].extend((gx - exact_x, gy - exact_y))

        set_endpoints(quake, e0x, e0y, e0z, e1x, e1y, e1z)
        qcyc = quake.call(quake_entry)
        qx, qy, qz = output(quake)
        rows['quake64_current']['cycles'].append(qcyc)
        rows['quake64_current']['exact_errors'].extend((qx - exact_x, qy - exact_y))
        if qz != ZCLIP:
            raise AssertionError(('quake z', qz))

    qmean = statistics.fmean(rows['quake64_current']['cycles'])
    result = {
        'status': 'standalone_nearclip_integration_research_not_game_build_certification',
        'v2_prg_sha256': hashlib.sha256(V2_PRG.read_bytes()).hexdigest(),
        'quake64_source_commit': QUAKE_COMMIT,
        'cases': args.cases,
        'seed': args.seed,
        'included_work': [
            'n/d formation',
            'ratio save/restore on Quake path',
            'X/Y delta formation',
            'ratio application(s)',
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

    for name, row in rows.items():
        entry = {
            'cycles': summarize(row['cycles']),
            'accuracy_vs_exact_endpoint': err_summary(row['exact_errors']),
        }
        if name != 'quake64_current':
            entry['prepared_contract_errors'] = row['contract_errors']
            entry['speedup_vs_quake64_percent'] = 100.0 * (
                qmean - statistics.fmean(row['cycles'])
            ) / qmean
        result['variants'][name] = entry

    floor_sep = result['variants']['prepared_inline_floor']['cycles']['mean']
    floor_s2 = result['variants']['scale2_floor']['cycles']['mean']
    near_sep = result['variants']['prepared_inline_nearest']['cycles']['mean']
    near_s2 = result['variants']['scale2_nearest']['cycles']['mean']
    result['scale2_gain_vs_separate_percent'] = {
        'nearest': 100.0 * (near_sep - near_s2) / near_sep,
        'floor': 100.0 * (floor_sep - floor_s2) / floor_sep,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for name, row in result['variants'].items():
            extra = ''
            if name != 'quake64_current':
                extra = f" speedup={row['speedup_vs_quake64_percent']:.2f}% errors={row['prepared_contract_errors']}"
            c = row['cycles']
            print(f"{name:24s} mean={c['mean']:.3f} range={c['min']}-{c['max']}{extra}")
        print(
            f"scale2 gain vs separate nearest={result['scale2_gain_vs_separate_percent']['nearest']:.2f}% "
            f"floor={result['scale2_gain_vs_separate_percent']['floor']:.2f}%"
        )

    for name in ('prepared_inline_nearest', 'prepared_inline_floor', 'scale2_nearest', 'scale2_floor'):
        if rows[name]['contract_errors']:
            raise SystemExit(f'{name} prepared contract errors')
        if max(abs(e) for e in rows[name]['exact_errors']) > 1:
            raise SystemExit(f'{name} exceeded <=1 endpoint error')


if __name__ == '__main__':
    main()
