#!/usr/bin/env python3
"""Benchmark strict positive-fraction prepared ratio against general PREP/APPLY.

This harness uses the shipped V2 image through tools/mini6502.py. It compares:

  general_fast      signed/general unrolled PREP + same_x APPLY
  general_safe      signed/general unrolled PREP + generic-rebind APPLY
  fraction_fast     trusted 0<n<d PREP + specialized signed-component APPLY
  fraction_safe     trusted 0<n<d PREP + safe generic-rebind APPLY
  quake64_current   scale_nd + lerp16 twice with ratio save/restore

The corpus uses strictly-front second endpoints (z1>ZCLIP), so 0<n<d is true
for every case. This is research evidence, not release certification.
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
from generate_prepared_ratio import generate_unrolled as generate_general  # noqa: E402
from generate_prepared_fraction import generate_unrolled as generate_fraction  # noqa: E402
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
    prepared_reference,
    put16,
    quake_cpu,
    summarize,
    trunc_div,
)


def candidate_cpu(kind: str, state: str):
    cpu = CPU(load_prg(V2_PRG))
    cpu.d = 0
    cpu.call(MATH_INIT)
    if kind == 'general':
        source = generate_general(state=state)
        prep_label = 'ratio_prep_unrolled'
        apply_label = 'ratio_apply'
    elif kind == 'fraction':
        source = generate_fraction(state=state)
        prep_label = 'ratio_fraction_prep'
        apply_label = 'ratio_fraction_apply_s16'
    else:
        raise ValueError(kind)
    labels = patch(cpu.mem, source)
    return cpu, labels[prep_label], labels[apply_label]


def run_candidate(cpu, prep: int, apply: int, n: int, d: int, ya: int, yb: int):
    put16(cpu.mem, N0, n)
    put16(cpu.mem, D0, d)
    cp = cpu.call(prep)
    put16(cpu.mem, Y0, ya)
    ca = cpu.call(apply)
    ga = gets16(cpu.mem, Z0)
    put16(cpu.mem, Y0, yb)
    cb = cpu.call(apply)
    gb = gets16(cpu.mem, Z0)
    return cp, ca, cb, ga, gb


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    variants = {}
    for kind in ('general', 'fraction'):
        for state in ('fast', 'safe'):
            name = f'{kind}_{state}'
            cpu, prep, apply = candidate_cpu(kind, state)
            variants[name] = {
                'cpu': cpu,
                'prep_entry': prep,
                'apply_entry': apply,
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
        # Strictly in front, not exactly on the plane: guarantees 0<n<d.
        z1 = rng.randint(ZCLIP + 1, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        assert 0 < n < d <= 0xFFFF
        ya = rng.randint(-8192, 8191)
        yb = rng.randint(-8192, 8191)
        exact_a = trunc_div(ya * n, d)
        exact_b = trunc_div(yb * n, d)
        prep_a = prepared_reference(ya, n, d)
        prep_b = prepared_reference(yb, n, d)

        for row in variants.values():
            cp, ca, cb, ga, gb = run_candidate(
                row['cpu'], row['prep_entry'], row['apply_entry'], n, d, ya, yb
            )
            row['prep_cycles'].append(cp)
            row['apply_cycles'].extend((ca, cb))
            row['pair_cycles'].append(cp + ca + cb)
            row['contract_errors'] += int(ga != prep_a) + int(gb != prep_b)
            row['exact_errors'].extend((ga - exact_a, gb - exact_b))

        # Literal Quake comparison, including ratio save/restore overhead.
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, ya)
        qa = qc.call(qrun); qga = gets16(qc.mem, QROT)
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, yb)
        qb = qc.call(qrun); qgb = gets16(qc.mem, QROT)
        quake_pair.append(qa + qb + 28)
        quake_exact_errors.extend((qga - exact_a, qgb - exact_b))

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
            'invariant': '0 < n=ZCLIP-z0 < d=z1-z0',
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

    gf = result['variants']['general_fast']['pair_cycles']['mean']
    ff = result['variants']['fraction_fast']['pair_cycles']['mean']
    gs = result['variants']['general_safe']['pair_cycles']['mean']
    fs = result['variants']['fraction_safe']['pair_cycles']['mean']
    result['fraction_gain_vs_general_percent'] = {
        'fast': 100.0 * (gf - ff) / gf,
        'safe': 100.0 * (gs - fs) / gs,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for name, row in result['variants'].items():
            print(
                f"{name:14s} prep={row['prep_cycles']['mean']:.3f} "
                f"apply={row['apply_cycles']['mean']:.3f} "
                f"pair={row['pair_cycles']['mean']:.3f} "
                f"vs_quake={row['speedup_vs_quake64_percent']:.2f}% "
                f"errors={row['prepared_contract_errors']}"
            )
        print(
            f"quake64_current pair={result['quake64_current']['pair_cycles']['mean']:.3f}"
        )
        print(
            f"fraction gain vs general: fast={result['fraction_gain_vs_general_percent']['fast']:.2f}% "
            f"safe={result['fraction_gain_vs_general_percent']['safe']:.2f}%"
        )

    if any(row['contract_errors'] for row in variants.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
