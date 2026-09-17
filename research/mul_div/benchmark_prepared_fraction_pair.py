#!/usr/bin/env python3
"""Benchmark fused strict-fraction SCALE2 against separate prepared calls.

This harness is the resident-image certification gate for
`generate_prepared_fraction_pair.py`. It uses the shipped V2 image through
`tools/mini6502.py` and the same strict near-clip stress corpus as
`benchmark_prepared_fraction.py`.

Compared paths:

  fraction_fast_separate
      strict PREP once + APPLY_S16 twice

  fraction_scale2_fused
      strict PREP + both signed16 applications in one compound call

  quake64_current
      scale_nd + lerp16 twice, including the 4 PHA + 4 PLA ratio save/restore

Research only; no stable API is modified.
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
from generate_prepared_fraction_pair import generate as generate_pair  # noqa: E402
from benchmark_prepared_fraction import candidate_cpu, run_candidate  # noqa: E402
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
    X0,
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

Z2 = Z0 + 2


def pair_cpu():
    cpu = CPU(load_prg(V2_PRG))
    cpu.d = 0
    cpu.call(MATH_INIT)
    labels = patch(cpu.mem, generate_pair())
    return cpu, labels['ratio_fraction_scale2']


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    scpu, sprep, sapply = candidate_cpu('fraction', 'fast')
    fcpu, fentry = pair_cpu()
    qcpu, qrun = quake_cpu()

    separate_cycles = []
    fused_cycles = []
    quake_cycles = []
    separate_contract_errors = 0
    fused_contract_errors = 0
    separate_exact_errors = []
    fused_exact_errors = []
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
        prep_x = prepared_reference(xa, n, d)
        prep_y = prepared_reference(ya, n, d)

        # Separate strict-fraction fast state.
        cp, cx, cy, sx, sy = run_candidate(
            scpu, sprep, sapply, n, d, xa, ya
        )
        separate_cycles.append(cp + cx + cy)
        separate_contract_errors += int(sx != prep_x) + int(sy != prep_y)
        separate_exact_errors.extend((sx - exact_x, sy - exact_y))

        # Fused pair: X/Y are two signed components, Z0:1/Z2:3 are outputs.
        put16(fcpu.mem, N0, n)
        put16(fcpu.mem, D0, d)
        put16(fcpu.mem, X0, xa)
        put16(fcpu.mem, Y0, ya)
        fc = fcpu.call(fentry)
        fx = gets16(fcpu.mem, Z0)
        fy = gets16(fcpu.mem, Z2)
        fused_cycles.append(fc)
        fused_contract_errors += int(fx != prep_x) + int(fy != prep_y)
        fused_exact_errors.extend((fx - exact_x, fy - exact_y))

        # Literal Quake current arithmetic pair.
        put16(qcpu.mem, QN, n); put16(qcpu.mem, QD, d); put16(qcpu.mem, QY, xa)
        qx_c = qcpu.call(qrun); qx = gets16(qcpu.mem, QROT)
        put16(qcpu.mem, QN, n); put16(qcpu.mem, QD, d); put16(qcpu.mem, QY, ya)
        qy_c = qcpu.call(qrun); qy = gets16(qcpu.mem, QROT)
        quake_cycles.append(qx_c + qy_c + 28)
        quake_exact_errors.extend((qx - exact_x, qy - exact_y))

    sm = statistics.fmean(separate_cycles)
    fm = statistics.fmean(fused_cycles)
    qm = statistics.fmean(quake_cycles)
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
        'fraction_fast_separate': {
            'cycles': summarize(separate_cycles),
            'prepared_contract_errors': separate_contract_errors,
            'accuracy_vs_exact': err_summary(separate_exact_errors),
        },
        'fraction_scale2_fused': {
            'cycles': summarize(fused_cycles),
            'prepared_contract_errors': fused_contract_errors,
            'accuracy_vs_exact': err_summary(fused_exact_errors),
            'saving_vs_separate_percent': 100.0 * (sm - fm) / sm,
            'saving_vs_quake64_percent': 100.0 * (qm - fm) / qm,
        },
        'quake64_current': {
            'cycles': summarize(quake_cycles),
            'accuracy_vs_exact': err_summary(quake_exact_errors),
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        print(f"fraction separate={sm:.3f}")
        print(
            f"fraction SCALE2 fused={fm:.3f} "
            f"gain-vs-separate={result['fraction_scale2_fused']['saving_vs_separate_percent']:.2f}% "
            f"gain-vs-Quake={result['fraction_scale2_fused']['saving_vs_quake64_percent']:.2f}%"
        )
        print(f"quake64 current={qm:.3f}")
        print(
            f"errors separate/fused={separate_contract_errors}/{fused_contract_errors}"
        )

    if separate_contract_errors or fused_contract_errors:
        raise SystemExit(1)
    if max(abs(e) for e in fused_exact_errors) > 1:
        raise SystemExit('fused SCALE2 exceeded <=1 error contract')


if __name__ == '__main__':
    main()
