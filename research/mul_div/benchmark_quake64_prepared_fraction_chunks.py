#!/usr/bin/env python3
"""Benchmark compact, chunked and full-unrolled Quake-native PREP variants.

All candidates share the same nearest-Q0.16 arithmetic contract and the same
Quake-native SMC APPLY. The only changing dimension is PREP organization.
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
from generate_quake64_prepared_fraction_smc_chunked import generate as generate_chunked  # noqa: E402
from benchmark_quake64_prepared_fraction_smc import fill_quake_sq_tables, run_quake_smc  # noqa: E402
from benchmark_prepared_fraction_pareto import prepared_reference  # noqa: E402
from benchmark_prepared_ratio import (  # noqa: E402
    QD, QN, QROT, QY, ZCLIP, err_summary, gets16, put16, quake_cpu, summarize, trunc_div,
)


def make_cpu(source: str):
    mem = bytearray(65536)
    fill_quake_sq_tables(mem)
    cpu = CPU(mem)
    cpu.d = 0
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

    sources = {
        'compact': generate_compact(rounding='nearest'),
        'chunk1': generate_chunked(rounding='nearest', chunk=1),
        'chunk2': generate_chunked(rounding='nearest', chunk=2),
        'chunk4': generate_chunked(rounding='nearest', chunk=4),
        'chunk8': generate_chunked(rounding='nearest', chunk=8),
        'unrolled': generate_unrolled(rounding='nearest'),
    }
    rows = {}
    for name, source in sources.items():
        cpu, prep, apply, size = make_cpu(source)
        rows[name] = {
            'cpu': cpu, 'prep_entry': prep, 'apply_entry': apply,
            'code_bytes': size, 'prep': [], 'apply': [], 'pair': [],
            'errors': 0, 'exact': [],
        }

    qc, qrun = quake_cpu()
    quake_pair = []
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
        ref_x = prepared_reference(xa, n, d, 'nearest')
        ref_y = prepared_reference(ya, n, d, 'nearest')

        for row in rows.values():
            cp, cx, cy, gx, gy = run_quake_smc(
                row['cpu'], row['prep_entry'], row['apply_entry'], n, d, xa, ya
            )
            row['prep'].append(cp)
            row['apply'].extend((cx, cy))
            row['pair'].append(cp + cx + cy)
            row['errors'] += int(gx != ref_x) + int(gy != ref_y)
            row['exact'].extend((gx - exact_x, gy - exact_y))

        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, xa)
        qx_c = qc.call(qrun)
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, ya)
        qy_c = qc.call(qrun)
        quake_pair.append(qx_c + qy_c + 28)

    qmean = statistics.fmean(quake_pair)
    result = {
        'status': 'research_evidence_not_game_build_certification',
        'cases': args.cases,
        'seed': args.seed,
        'rounding': 'nearest',
        'corpus': {
            'zclip': ZCLIP,
            'z0_range': [-8192, ZCLIP - 1],
            'z1_range': [ZCLIP + 1, 8191],
            'component_range': [-8192, 8191],
            'invariant': '0<n<d',
        },
        'quake_current_pair_mean': qmean,
        'variants': {},
    }

    for name, row in rows.items():
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

    # Pareto mark: no other candidate may be both <= bytes and <= cycles with
    # at least one strict improvement.
    for name, row in result['variants'].items():
        dominated_by = []
        for other, o in result['variants'].items():
            if other == name:
                continue
            if (o['assembled_code_bytes'] <= row['assembled_code_bytes'] and
                    o['pair_cycles']['mean'] <= row['pair_cycles']['mean'] and
                    (o['assembled_code_bytes'] < row['assembled_code_bytes'] or
                     o['pair_cycles']['mean'] < row['pair_cycles']['mean'])):
                dominated_by.append(other)
        row['pareto'] = not dominated_by
        row['dominated_by'] = dominated_by

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for name, row in result['variants'].items():
            print(
                f"{name:8s} code={row['assembled_code_bytes']:4d} "
                f"prep={row['prep_cycles']['mean']:.3f} "
                f"pair={row['pair_cycles']['mean']:.3f} "
                f"pareto={row['pareto']} errors={row['prepared_contract_errors']}"
            )

    if any(row['errors'] for row in rows.values()):
        raise SystemExit(1)
    if any(max(abs(e) for e in row['exact']) > 1 for row in rows.values()):
        raise SystemExit('candidate exceeded <=1 error bound')


if __name__ == '__main__':
    main()
