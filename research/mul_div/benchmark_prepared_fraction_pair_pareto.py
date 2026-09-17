#!/usr/bin/env python3
"""Resident-image benchmark for the profile-native fused strict-fraction SCALE2.

This is the corrected shipped-V2 benchmark. It compares:

  pareto_inline_floor_separate
      floor PREP once + fixed-X APPLY twice

  pareto_inline_nearest_separate
      nearest PREP once + fixed-X APPLY twice

  pareto_scale2_floor
      one fused PREP + X/Y APPLY call using the same fixed-X body twice

  pareto_scale2_nearest
      nearest-Q0.16 fused form

  quake64_current
      literal scale_nd + lerp16 pair with ratio save/restore

Research evidence only. No stable API is modified.
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
from generate_prepared_fraction_pair_pareto_inline import generate as generate_pair  # noqa: E402
from benchmark_prepared_fraction_pareto import (  # noqa: E402
    candidate_cpu,
    prepared_reference,
    run_candidate,
)
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

X0 = 0xC000
Z2 = Z0 + 2


def fused_cpu(rounding: str):
    cpu = CPU(load_prg(V2_PRG))
    cpu.d = 0
    cpu.call(MATH_INIT)
    labels = patch(cpu.mem, generate_pair(rounding=rounding))
    return cpu, labels['ratio_fraction_scale2_pareto_inline']


def run_fused(cpu, entry: int, n: int, d: int, x: int, y: int):
    put16(cpu.mem, N0, n)
    put16(cpu.mem, D0, d)
    put16(cpu.mem, X0, x)
    put16(cpu.mem, Y0, y)
    cyc = cpu.call(entry)
    return cyc, gets16(cpu.mem, Z0), gets16(cpu.mem, Z2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    sep = {}
    for rounding in ('nearest', 'floor'):
        name = f'pareto_inline_{rounding}'
        cpu, prep, apply = candidate_cpu(name)
        sep[rounding] = {
            'cpu': cpu,
            'prep': prep,
            'apply': apply,
            'cycles': [],
            'contract_errors': 0,
            'exact_errors': [],
        }

    fused = {}
    for rounding in ('nearest', 'floor'):
        cpu, entry = fused_cpu(rounding)
        fused[rounding] = {
            'cpu': cpu,
            'entry': entry,
            'cycles': [],
            'contract_errors': 0,
            'exact_errors': [],
        }

    qc, qrun = quake_cpu()
    quake_cycles = []
    quake_exact_errors = []
    rng = random.Random(args.seed)

    for _ in range(args.cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP + 1, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        assert 0 < n < d <= 0xFFFF
        x = rng.randint(-8192, 8191)
        y = rng.randint(-8192, 8191)
        exact_x = trunc_div(x * n, d)
        exact_y = trunc_div(y * n, d)

        for rounding, row in sep.items():
            cp, cx, cy, gx, gy = run_candidate(
                row['cpu'], row['prep'], row['apply'], n, d, x, y
            )
            row['cycles'].append(cp + cx + cy)
            rx = prepared_reference(x, n, d, rounding)
            ry = prepared_reference(y, n, d, rounding)
            row['contract_errors'] += int(gx != rx) + int(gy != ry)
            row['exact_errors'].extend((gx - exact_x, gy - exact_y))

        for rounding, row in fused.items():
            cyc, gx, gy = run_fused(row['cpu'], row['entry'], n, d, x, y)
            row['cycles'].append(cyc)
            rx = prepared_reference(x, n, d, rounding)
            ry = prepared_reference(y, n, d, rounding)
            row['contract_errors'] += int(gx != rx) + int(gy != ry)
            row['exact_errors'].extend((gx - exact_x, gy - exact_y))

        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, x)
        qxc = qc.call(qrun); qx = gets16(qc.mem, QROT)
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, y)
        qyc = qc.call(qrun); qy = gets16(qc.mem, QROT)
        quake_cycles.append(qxc + qyc + 28)
        quake_exact_errors.extend((qx - exact_x, qy - exact_y))

    qmean = statistics.fmean(quake_cycles)
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
            'applications_per_ratio': 2,
        },
        'separate': {},
        'fused': {},
        'quake64_current': {
            'cycles': summarize(quake_cycles),
            'accuracy_vs_exact': err_summary(quake_exact_errors),
        },
    }

    for rounding, row in sep.items():
        result['separate'][rounding] = {
            'cycles': summarize(row['cycles']),
            'prepared_contract_errors': row['contract_errors'],
            'accuracy_vs_exact': err_summary(row['exact_errors']),
        }

    for rounding, row in fused.items():
        fsum = summarize(row['cycles'])
        smean = result['separate'][rounding]['cycles']['mean']
        result['fused'][rounding] = {
            'cycles': fsum,
            'prepared_contract_errors': row['contract_errors'],
            'accuracy_vs_exact': err_summary(row['exact_errors']),
            'speedup_vs_separate_percent': 100.0 * (smean - fsum['mean']) / smean,
            'speedup_vs_quake64_percent': 100.0 * (qmean - fsum['mean']) / qmean,
        }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for rounding in ('nearest', 'floor'):
            s = result['separate'][rounding]
            f = result['fused'][rounding]
            print(
                f"{rounding:7s} separate={s['cycles']['mean']:.3f} "
                f"fused={f['cycles']['mean']:.3f} "
                f"vs_sep={f['speedup_vs_separate_percent']:.2f}% "
                f"vs_quake={f['speedup_vs_quake64_percent']:.2f}% "
                f"errors={f['prepared_contract_errors']}"
            )
        print(f"quake64 current={qmean:.3f}")

    bad = any(row['contract_errors'] for row in sep.values())
    bad |= any(row['contract_errors'] for row in fused.values())
    if bad:
        raise SystemExit(1)
    for row in fused.values():
        if max(abs(e) for e in row['exact_errors']) > 1:
            raise SystemExit('fused SCALE2 exceeded <=1 error contract')


if __name__ == '__main__':
    main()
