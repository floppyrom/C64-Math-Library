#!/usr/bin/env python3
"""Resident-image benchmark for prepared strict fractions on shipped V2.

Unlike the earlier record-core experiment, every prepared candidate here is
built around the implementation actually installed in V2 Pareto-Fast:

    I_UMUL8 = $5300
    I_UMUL16 = $5400 integrated 3xUMUL8 public-I/O kernel

Variants:

  pareto_current_nearest
      generate_prepared_fraction_pareto.py

  pareto_inline_nearest
      fixed-X balanced inline products, rounded Q0.16 PREP

  pareto_inline_floor
      fixed-X balanced inline products, floor Q0.16 PREP

The comparison side is the literal Quake64 scale_nd + lerp16 pair already used
by benchmark_prepared_ratio.py. This is research evidence, not release
certification and not a claim about real gameplay event frequencies.
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
from generate_prepared_fraction_pareto import generate as generate_pareto  # noqa: E402
from generate_prepared_fraction_pareto_inline import generate as generate_inline  # noqa: E402
from benchmark_prepared_ratio import (  # noqa: E402
    D0,
    MATH_INIT,
    N0,
    QD,
    QN,
    QROT,
    QY,
    QUAKE_COMMIT,
    V2_PRG,
    Y0,
    Z0,
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


def candidate_cpu(kind: str):
    cpu = CPU(load_prg(V2_PRG))
    cpu.d = 0
    cpu.call(MATH_INIT)
    if kind == 'pareto_current_nearest':
        source = generate_pareto()
        prep_label = 'ratio_fraction_prep_pareto'
        apply_label = 'ratio_fraction_apply_pareto_s16'
    elif kind == 'pareto_inline_nearest':
        source = generate_inline(rounding='nearest')
        prep_label = 'ratio_fraction_prep_pareto_inline'
        apply_label = 'ratio_fraction_apply_pareto_inline_s16'
    elif kind == 'pareto_inline_floor':
        source = generate_inline(rounding='floor')
        prep_label = 'ratio_fraction_prep_pareto_inline'
        apply_label = 'ratio_fraction_apply_pareto_inline_s16'
    else:
        raise ValueError(kind)
    labels = patch(cpu.mem, source)
    return cpu, labels[prep_label], labels[apply_label]


def prepared_reference(y: int, n: int, d: int, rounding: str) -> int:
    if rounding == 'nearest':
        m = ((n << 16) + d // 2) // d
    elif rounding == 'floor':
        m = (n << 16) // d
    else:
        raise ValueError(rounding)
    q = (abs(y) * m) >> 16
    return -q if y < 0 else q


def run_candidate(cpu, prep: int, apply: int, n: int, d: int, xa: int, ya: int):
    put16(cpu.mem, N0, n)
    put16(cpu.mem, D0, d)
    cp = cpu.call(prep)
    put16(cpu.mem, Y0, xa)
    cx = cpu.call(apply)
    gx = gets16(cpu.mem, Z0)
    put16(cpu.mem, Y0, ya)
    cy = cpu.call(apply)
    gy = gets16(cpu.mem, Z0)
    return cp, cx, cy, gx, gy


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    names = (
        'pareto_current_nearest',
        'pareto_inline_nearest',
        'pareto_inline_floor',
    )
    variants = {}
    for name in names:
        cpu, prep, apply = candidate_cpu(name)
        variants[name] = {
            'cpu': cpu,
            'prep': prep,
            'apply': apply,
            'prep_cycles': [],
            'apply_cycles': [],
            'pair_cycles': [],
            'contract_errors': 0,
            'exact_errors': [],
        }

    qc, qrun = quake_cpu()
    quake_pair = []
    quake_exact_errors = []
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
            rounding = 'floor' if name.endswith('_floor') else 'nearest'
            cp, cx, cy, gx, gy = run_candidate(
                row['cpu'], row['prep'], row['apply'], n, d, xa, ya
            )
            row['prep_cycles'].append(cp)
            row['apply_cycles'].extend((cx, cy))
            row['pair_cycles'].append(cp + cx + cy)
            rx = prepared_reference(xa, n, d, rounding)
            ry = prepared_reference(ya, n, d, rounding)
            row['contract_errors'] += int(gx != rx) + int(gy != ry)
            row['exact_errors'].extend((gx - exact_x, gy - exact_y))

        # Current Quake arithmetic pair; original n/d is restored between X/Y.
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, xa)
        qxc = qc.call(qrun); qx = gets16(qc.mem, QROT)
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, ya)
        qyc = qc.call(qrun); qy = gets16(qc.mem, QROT)
        quake_pair.append(qxc + qyc + 28)
        quake_exact_errors.extend((qx - exact_x, qy - exact_y))

    qmean = statistics.fmean(quake_pair)
    result = {
        'status': 'research_evidence_not_release_certification',
        'v2_prg_sha256': hashlib.sha256(V2_PRG.read_bytes()).hexdigest(),
        'quake64_source_commit': QUAKE_COMMIT,
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
        'quake64_current': {
            'pair_cycles': summarize(quake_pair),
            'accuracy_vs_exact': err_summary(quake_exact_errors),
        },
    }

    for name, row in variants.items():
        pair = summarize(row['pair_cycles'])
        result['variants'][name] = {
            'prep_cycles': summarize(row['prep_cycles']),
            'apply_cycles': summarize(row['apply_cycles']),
            'pair_cycles': pair,
            'speedup_vs_quake64_percent': 100.0 * (qmean - pair['mean']) / qmean,
            'prepared_contract_errors': row['contract_errors'],
            'accuracy_vs_exact': err_summary(row['exact_errors']),
        }

    base = result['variants']['pareto_current_nearest']['pair_cycles']['mean']
    for name in ('pareto_inline_nearest', 'pareto_inline_floor'):
        mean = result['variants'][name]['pair_cycles']['mean']
        result['variants'][name]['speedup_vs_pareto_current_percent'] = (
            100.0 * (base - mean) / base
        )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for name in names:
            row = result['variants'][name]
            print(
                f"{name:24s} prep={row['prep_cycles']['mean']:.3f} "
                f"apply={row['apply_cycles']['mean']:.3f} "
                f"pair={row['pair_cycles']['mean']:.3f} "
                f"vs_quake={row['speedup_vs_quake64_percent']:.2f}% "
                f"errors={row['prepared_contract_errors']}"
            )
        print(f"quake64_current pair={qmean:.3f}")

    if any(row['contract_errors'] for row in variants.values()):
        raise SystemExit('prepared contract mismatch')
    if result['variants']['pareto_inline_nearest']['accuracy_vs_exact']['max_absolute_error'] > 1:
        raise SystemExit('nearest <=1 error contract failed')
    if result['variants']['pareto_inline_floor']['accuracy_vs_exact']['max_absolute_error'] > 1:
        raise SystemExit('floor <=1 error contract failed')


if __name__ == '__main__':
    main()
