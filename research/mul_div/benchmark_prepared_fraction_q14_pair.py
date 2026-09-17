#!/usr/bin/env python3
"""Benchmark Q14 fused strict-fraction SCALE2 on the shipped V2 image.

Compares:
  * Q16 fused strict-fraction SCALE2
  * Q14 fused strict-fraction SCALE2
  * Quake64 current scale_nd + lerp16 pair

The Q14 contract is rounded n/d in Q14 and therefore guarantees maximum integer
error <=1 for the complete signed16 component domain. The harness additionally
checks near-one ratios that round to the Q14 identity representation.

Research evidence only; no stable API is modified.
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
from generate_prepared_fraction_pair import generate as generate_q16  # noqa: E402
from generate_prepared_fraction_q14_pair import generate as generate_q14  # noqa: E402
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

X0 = 0xC000
Z2 = Z0 + 2


def make_cpu(kind: str):
    cpu = CPU(load_prg(V2_PRG))
    cpu.d = 0
    cpu.call(MATH_INIT)
    if kind == 'q16':
        labels = patch(cpu.mem, generate_q16())
        entry = labels['ratio_fraction_scale2']
    elif kind == 'q14':
        labels = patch(cpu.mem, generate_q14())
        entry = labels['ratio_fraction_q14_scale2']
    else:
        raise ValueError(kind)
    return cpu, entry


def q14_reference(y: int, n: int, d: int) -> int:
    q = ((n << 14) + d // 2) // d
    if q == 0x4000:
        return y
    return trunc_div(y * q, 1 << 14)


def run_pair(cpu: CPU, entry: int, n: int, d: int, x: int, y: int):
    put16(cpu.mem, N0, n)
    put16(cpu.mem, D0, d)
    put16(cpu.mem, X0, x)
    put16(cpu.mem, Y0, y)
    cycles = cpu.call(entry)
    return cycles, gets16(cpu.mem, Z0), gets16(cpu.mem, Z2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--full-domain-cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    q16cpu, q16entry = make_cpu('q16')
    q14cpu, q14entry = make_cpu('q14')
    qcpu, qrun = quake_cpu()

    q16_cycles = []
    q14_cycles = []
    quake_cycles = []
    q16_contract_errors = 0
    q14_contract_errors = 0
    q16_exact_errors = []
    q14_exact_errors = []
    quake_exact_errors = []
    q14_identity_cases = 0

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

        c16, x16, y16 = run_pair(q16cpu, q16entry, n, d, x, y)
        q16_cycles.append(c16)
        e16x = prepared_reference(x, n, d)
        e16y = prepared_reference(y, n, d)
        q16_contract_errors += int(x16 != e16x) + int(y16 != e16y)
        q16_exact_errors.extend((x16 - exact_x, y16 - exact_y))

        c14, x14, y14 = run_pair(q14cpu, q14entry, n, d, x, y)
        q14_cycles.append(c14)
        e14x = q14_reference(x, n, d)
        e14y = q14_reference(y, n, d)
        q14_contract_errors += int(x14 != e14x) + int(y14 != e14y)
        q14_exact_errors.extend((x14 - exact_x, y14 - exact_y))
        q14_identity_cases += int(((n << 14) + d // 2) // d == 0x4000)

        put16(qcpu.mem, QN, n); put16(qcpu.mem, QD, d); put16(qcpu.mem, QY, x)
        qx_c = qcpu.call(qrun); qx = gets16(qcpu.mem, QROT)
        put16(qcpu.mem, QN, n); put16(qcpu.mem, QD, d); put16(qcpu.mem, QY, y)
        qy_c = qcpu.call(qrun); qy = gets16(qcpu.mem, QROT)
        quake_cycles.append(qx_c + qy_c + 28)
        quake_exact_errors.extend((qx - exact_x, qy - exact_y))

    # Explicit near-one/identity tests. For d>32768, n=d-1 may round to Q14 1.0.
    identity_contract_errors = 0
    identity_exact_errors = []
    identity_test_cases = 0
    edge_components = (-32768, -32767, -8192, -1, 0, 1, 8191, 32767)
    for d in (32769, 40000, 49151, 65534, 65535):
        n = d - 1
        q = ((n << 14) + d // 2) // d
        if q != 0x4000:
            continue
        for x in edge_components:
            for y in edge_components:
                _, gx, gy = run_pair(q14cpu, q14entry, n, d, x, y)
                rx, ry = q14_reference(x, n, d), q14_reference(y, n, d)
                ex, ey = trunc_div(x * n, d), trunc_div(y * n, d)
                identity_contract_errors += int(gx != rx) + int(gy != ry)
                identity_exact_errors.extend((gx - ex, gy - ey))
                identity_test_cases += 1

    # Random full signed16 component validation for the <=1 Q14 guarantee.
    full_rng = random.Random(args.seed ^ 0x14C64)
    full_contract_errors = 0
    full_exact_errors = []
    for _ in range(args.full_domain_cases):
        d = full_rng.randint(2, 0xFFFF)
        n = full_rng.randint(1, d - 1)
        x = full_rng.randint(-32768, 32767)
        y = full_rng.randint(-32768, 32767)
        _, gx, gy = run_pair(q14cpu, q14entry, n, d, x, y)
        rx, ry = q14_reference(x, n, d), q14_reference(y, n, d)
        ex, ey = trunc_div(x * n, d), trunc_div(y * n, d)
        full_contract_errors += int(gx != rx) + int(gy != ry)
        full_exact_errors.extend((gx - ex, gy - ey))

    q16mean = statistics.fmean(q16_cycles)
    q14mean = statistics.fmean(q14_cycles)
    qmean = statistics.fmean(quake_cycles)
    result = {
        'status': 'research_evidence_not_release_certification',
        'v2_prg_sha256': hashlib.sha256(V2_PRG.read_bytes()).hexdigest(),
        'quake64_source_commit': QUAKE_COMMIT,
        'cases': args.cases,
        'full_domain_cases': args.full_domain_cases,
        'seed': args.seed,
        'stress_corpus': {
            'zclip': ZCLIP,
            'z0_range': [-8192, ZCLIP - 1],
            'z1_range': [ZCLIP + 1, 8191],
            'component_range': [-8192, 8191],
            'invariant': '0<n<d',
            'q14_identity_rounds': q14_identity_cases,
        },
        'q16_fused': {
            'cycles': summarize(q16_cycles),
            'prepared_contract_errors': q16_contract_errors,
            'accuracy_vs_exact': err_summary(q16_exact_errors),
        },
        'q14_fused': {
            'cycles': summarize(q14_cycles),
            'prepared_contract_errors': q14_contract_errors,
            'accuracy_vs_exact': err_summary(q14_exact_errors),
            'saving_vs_q16_percent': 100.0 * (q16mean - q14mean) / q16mean,
            'saving_vs_quake64_percent': 100.0 * (qmean - q14mean) / qmean,
        },
        'q14_identity_validation': {
            'cases': identity_test_cases,
            'contract_errors': identity_contract_errors,
            'accuracy_vs_exact': err_summary(identity_exact_errors),
        },
        'q14_full_signed16_random_validation': {
            'cases': args.full_domain_cases,
            'outputs': 2 * args.full_domain_cases,
            'contract_errors': full_contract_errors,
            'accuracy_vs_exact': err_summary(full_exact_errors),
        },
        'quake64_current': {
            'cycles': summarize(quake_cycles),
            'accuracy_vs_exact': err_summary(quake_exact_errors),
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Q16 fused mean={q16mean:.3f}")
        print(
            f"Q14 fused mean={q14mean:.3f} "
            f"gain-vs-Q16={result['q14_fused']['saving_vs_q16_percent']:.2f}% "
            f"gain-vs-Quake={result['q14_fused']['saving_vs_quake64_percent']:.2f}%"
        )
        print(f"Quake current mean={qmean:.3f}")
        print(
            f"errors stress/full/identity={q14_contract_errors}/"
            f"{full_contract_errors}/{identity_contract_errors}"
        )

    if q16_contract_errors or q14_contract_errors or identity_contract_errors or full_contract_errors:
        raise SystemExit(1)
    if max(abs(e) for e in q14_exact_errors) > 1:
        raise SystemExit('Q14 stress path exceeded <=1 exact-ratio error')
    if max(abs(e) for e in full_exact_errors) > 1:
        raise SystemExit('Q14 full signed16 random path exceeded <=1 exact-ratio error')
    if identity_exact_errors and max(abs(e) for e in identity_exact_errors) > 1:
        raise SystemExit('Q14 identity path exceeded <=1 exact-ratio error')


if __name__ == '__main__':
    main()
