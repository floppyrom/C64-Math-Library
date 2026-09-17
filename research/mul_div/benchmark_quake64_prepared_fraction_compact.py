#!/usr/bin/env python3
"""Compare compact and unrolled Quake-native prepared-fraction kernels.

Both candidates reuse Quake64's $F000-$F7FF quarter-square tables and exactly
the same APPLY implementation. Only PREP changes: unrolled 16-step fractional
division versus a compact loop.

The benchmark uses the same 5,000-edge strict near-clip stress corpus as the
existing Quake-native evidence and compares both against Quake64's current
scale_nd + lerp16 pair.
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

from mini6502 import Assembler, CPU  # noqa: E402
from generate_quake64_prepared_fraction_smc import generate as generate_unrolled  # noqa: E402
from generate_quake64_prepared_fraction_smc_compact import generate as generate_compact  # noqa: E402
from benchmark_quake64_prepared_fraction_smc import (  # noqa: E402
    QNATIVE_D,
    QNATIVE_N,
    QNATIVE_Y,
    QNATIVE_Z,
    fill_quake_sq_tables,
    run_quake_smc,
)
from benchmark_prepared_fraction_pareto import prepared_reference  # noqa: E402
from benchmark_prepared_ratio import (  # noqa: E402
    QD,
    QN,
    QROT,
    QY,
    ZCLIP,
    err_summary,
    gets16,
    put16,
    quake_cpu,
    summarize,
    trunc_div,
)


def candidate_cpu(kind: str, rounding: str):
    mem = bytearray(65536)
    fill_quake_sq_tables(mem)
    cpu = CPU(mem)
    cpu.d = 0
    source = (
        generate_compact(rounding=rounding)
        if kind == 'compact'
        else generate_unrolled(rounding=rounding)
    )
    code, labels, _ = Assembler().assemble(source)
    for addr, value in code.items():
        cpu.mem[addr] = value
    return cpu, labels['qfrac_prep'], labels['qfrac_apply_s16'], len(code)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    variants = {}
    for kind in ('compact', 'unrolled'):
        for rounding in ('nearest', 'floor'):
            name = f'{kind}_{rounding}'
            cpu, prep, apply, code_bytes = candidate_cpu(kind, rounding)
            variants[name] = {
                'cpu': cpu,
                'prep_entry': prep,
                'apply_entry': apply,
                'code_bytes': code_bytes,
                'prep': [],
                'apply': [],
                'pair': [],
                'errors': 0,
                'exact': [],
            }

    qc, qrun = quake_cpu()
    quake_pair = []
    quake_exact = []
    rng = random.Random(args.seed)

    for _ in range(args.cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP + 1, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        assert 0 < n < d <= 0xFFFF
        xa = rng.randint(-8192, 8191)
        ya = rng.randint(-8192, 8191)
        exact_x = trunc_div(xa * n, d)
        exact_y = trunc_div(ya * n, d)

        for name, row in variants.items():
            rounding = name.rsplit('_', 1)[1]
            cp, cx, cy, gx, gy = run_quake_smc(
                row['cpu'], row['prep_entry'], row['apply_entry'], n, d, xa, ya
            )
            ref_x = prepared_reference(xa, n, d, rounding)
            ref_y = prepared_reference(ya, n, d, rounding)
            row['prep'].append(cp)
            row['apply'].extend((cx, cy))
            row['pair'].append(cp + cx + cy)
            row['errors'] += int(gx != ref_x) + int(gy != ref_y)
            row['exact'].extend((gx - exact_x, gy - exact_y))

        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, xa)
        qx_c = qc.call(qrun); qx = gets16(qc.mem, QROT)
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, ya)
        qy_c = qc.call(qrun); qy = gets16(qc.mem, QROT)
        quake_pair.append(qx_c + qy_c + 28)
        quake_exact.extend((qx - exact_x, qy - exact_y))

    qmean = statistics.fmean(quake_pair)
    result = {
        'status': 'research_evidence_not_game_build_certification',
        'cases': args.cases,
        'seed': args.seed,
        'corpus': {
            'zclip': ZCLIP,
            'z0_range': [-8192, ZCLIP - 1],
            'z1_range': [ZCLIP + 1, 8191],
            'component_range': [-8192, 8191],
            'invariant': '0<n<d',
            'applications_per_preparation': 2,
        },
        'variants': {},
        'quake_current': {
            'pair_cycles': summarize(quake_pair),
            'accuracy_vs_exact': err_summary(quake_exact),
        },
    }

    for name, row in variants.items():
        pair = summarize(row['pair'])
        result['variants'][name] = {
            'assembled_code_bytes': row['code_bytes'],
            'prep_cycles': summarize(row['prep']),
            'apply_cycles': summarize(row['apply']),
            'pair_cycles': pair,
            'prepared_contract_errors': row['errors'],
            'accuracy_vs_exact': err_summary(row['exact']),
            'speedup_vs_quake_current_percent': 100.0 * (qmean - pair['mean']) / qmean,
        }

    for rounding in ('nearest', 'floor'):
        c = result['variants'][f'compact_{rounding}']['pair_cycles']['mean']
        u = result['variants'][f'unrolled_{rounding}']['pair_cycles']['mean']
        cb = result['variants'][f'compact_{rounding}']['assembled_code_bytes']
        ub = result['variants'][f'unrolled_{rounding}']['assembled_code_bytes']
        result[f'compact_vs_unrolled_{rounding}'] = {
            'cycle_penalty': c - u,
            'cycle_penalty_percent': 100.0 * (c - u) / u,
            'bytes_saved': ub - cb,
            'size_reduction_percent': 100.0 * (ub - cb) / ub,
        }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for name, row in result['variants'].items():
            print(
                f"{name:18s} code={row['assembled_code_bytes']:4d} "
                f"prep={row['prep_cycles']['mean']:.3f} "
                f"apply={row['apply_cycles']['mean']:.3f} "
                f"pair={row['pair_cycles']['mean']:.3f} "
                f"errors={row['prepared_contract_errors']}"
            )
        print(f"quake_current pair={qmean:.3f}")

    if any(row['errors'] for row in variants.values()):
        raise SystemExit(1)
    if any(max(abs(e) for e in row['exact']) > 1 for row in variants.values()):
        raise SystemExit('prepared candidate exceeded <=1 endpoint error bound')


if __name__ == '__main__':
    main()
