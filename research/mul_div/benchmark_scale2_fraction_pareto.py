#!/usr/bin/env python3
"""Resident-image benchmark for profile-native V2 strict-fraction SCALE2.

Compares the one-call compound operation against:
  * the corrected fixed-X PREP + two APPLY calls, nearest and floor;
  * the literal Quake64 scale_nd + lerp16 arithmetic pair.

The corpus uses valid strict near-plane crossings (0<n<d) and two signed16
components. This is research evidence, not a full Quake64 build certification.
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
from generate_scale2_fraction_pareto import generate as generate_scale2  # noqa: E402
from benchmark_prepared_fraction_pareto import (  # noqa: E402
    candidate_cpu as separate_cpu,
    prepared_reference,
    run_candidate as run_separate,
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
ORIGIN = 0xE000


def scale2_cpu(rounding: str):
    cpu = CPU(load_prg(V2_PRG))
    cpu.d = 0
    cpu.call(MATH_INIT)
    source = generate_scale2(ORIGIN, rounding)
    code, labels, _ = __import__('mini6502').Assembler().assemble(source)
    for addr, value in code.items():
        cpu.mem[addr] = value
    return cpu, labels['scale2_fraction_pareto'], len(code)


def run_scale2(cpu, entry: int, n: int, d: int, x: int, y: int):
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

    variants = {}
    for rounding in ('nearest', 'floor'):
        scpu, sentry, size = scale2_cpu(rounding)
        sep_name = f'pareto_inline_{rounding}'
        pcpu, prep, apply = separate_cpu(sep_name)
        variants[rounding] = {
            'scale_cpu': scpu,
            'scale_entry': sentry,
            'scale_code_bytes': size,
            'separate_cpu': pcpu,
            'prep': prep,
            'apply': apply,
            'scale_cycles': [],
            'separate_cycles': [],
            'scale_contract_errors': 0,
            'separate_contract_errors': 0,
            'scale_exact_errors': [],
            'separate_exact_errors': [],
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

        for rounding, row in variants.items():
            rx = prepared_reference(x, n, d, rounding)
            ry = prepared_reference(y, n, d, rounding)

            sc, sx, sy = run_scale2(
                row['scale_cpu'], row['scale_entry'], n, d, x, y
            )
            row['scale_cycles'].append(sc)
            row['scale_contract_errors'] += int(sx != rx) + int(sy != ry)
            row['scale_exact_errors'].extend((sx - exact_x, sy - exact_y))

            cp, cx, cy, px, py = run_separate(
                row['separate_cpu'], row['prep'], row['apply'], n, d, x, y
            )
            row['separate_cycles'].append(cp + cx + cy)
            row['separate_contract_errors'] += int(px != rx) + int(py != ry)
            row['separate_exact_errors'].extend((px - exact_x, py - exact_y))

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
        },
        'variants': {},
        'quake64_current': {
            'cycles': summarize(quake_cycles),
            'accuracy_vs_exact': err_summary(quake_exact_errors),
        },
    }

    total_errors = 0
    for rounding, row in variants.items():
        sm = statistics.fmean(row['separate_cycles'])
        fm = statistics.fmean(row['scale_cycles'])
        total_errors += row['scale_contract_errors'] + row['separate_contract_errors']
        result['variants'][rounding] = {
            'scale2_code_bytes': row['scale_code_bytes'],
            'separate_cycles': summarize(row['separate_cycles']),
            'scale2_cycles': summarize(row['scale_cycles']),
            'scale2_saving_vs_separate_percent': 100.0 * (sm - fm) / sm,
            'scale2_saving_vs_quake_percent': 100.0 * (qmean - fm) / qmean,
            'scale2_contract_errors': row['scale_contract_errors'],
            'separate_contract_errors': row['separate_contract_errors'],
            'scale2_accuracy_vs_exact': err_summary(row['scale_exact_errors']),
            'separate_accuracy_vs_exact': err_summary(row['separate_exact_errors']),
        }
    result['total_contract_errors'] = total_errors

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for rounding, row in result['variants'].items():
            print(
                f"{rounding:7s} separate={row['separate_cycles']['mean']:.3f} "
                f"scale2={row['scale2_cycles']['mean']:.3f} "
                f"gain-separate={row['scale2_saving_vs_separate_percent']:.2f}% "
                f"gain-Quake={row['scale2_saving_vs_quake_percent']:.2f}% "
                f"errors={row['scale2_contract_errors']}"
            )
        print(f"quake64={qmean:.3f}")

    if total_errors:
        raise SystemExit(1)
    for row in result['variants'].values():
        if row['scale2_accuracy_vs_exact']['max_absolute_error'] > 1:
            raise SystemExit('SCALE2 exceeded <=1 error contract')


if __name__ == '__main__':
    main()
