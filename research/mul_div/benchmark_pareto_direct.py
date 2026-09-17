#!/usr/bin/env python3
"""Benchmark actual-core V2 Pareto MUL_DIV16 candidates.

This harness deliberately excludes the historical record-core `direct` and
`direct_hybrid` variants from benchmark.py. It compares only implementations
that match the shipped V2 Pareto-Fast resident image:

  composed                 public UMUL16 + public UDIV32_16
  fused                    public UMUL16 + bounded 16-step tail
  hybrid                   public UMUL16 + native UDIV16 small-product path
  pareto_direct            inlined shipped 3xUMUL8 + live bounded tail
  pareto_direct_hybrid     same + q=0/q=1/native UDIV16 small-product knees
  pareto_width_hybrid      1/2/3-UMUL8 operand-width knees + same quotient knees

The generated research kernels are patched into RAM under KERNAL in the
mini6502 model. No shipped binary or stable API is modified.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(HERE))

from mini6502 import CPU  # noqa: E402
from benchmark import (  # noqa: E402
    MATH_INIT,
    ORIGIN_CANDIDATE,
    ORIGIN_COMPOSED,
    PROFILE_PRG,
    corpus,
    corpus_shape,
    edge_cases,
    expected,
    get_outputs,
    load_prg,
    patch_source,
    set_inputs,
)
from generate_umuldiv16 import (  # noqa: E402
    generate_bounded,
    generate_composed,
    generate_hybrid,
)
from generate_umuldiv16_pareto import (  # noqa: E402
    generate_direct as generate_pareto_direct,
    generate_direct_hybrid as generate_pareto_direct_hybrid,
)
from generate_umuldiv16_pareto_width import generate as generate_pareto_width_hybrid  # noqa: E402

VARIANTS = (
    'composed',
    'fused',
    'hybrid',
    'pareto_direct',
    'pareto_direct_hybrid',
    'pareto_width_hybrid',
)


def make_cpu(kind: str):
    path = PROFILE_PRG['v2']
    if not path.exists():
        raise FileNotFoundError(path)
    cpu = CPU(load_prg(path))
    cpu.d = 0
    cpu.call(MATH_INIT)  # initialization deliberately outside timed call

    if kind == 'composed':
        labels = patch_source(cpu.mem, generate_composed(ORIGIN_COMPOSED))
        entry = labels['umuldiv16_composed']
    elif kind == 'fused':
        labels = patch_source(cpu.mem, generate_bounded(ORIGIN_CANDIDATE))
        entry = labels['umuldiv16_bounded']
    elif kind == 'hybrid':
        labels = patch_source(cpu.mem, generate_hybrid('v2', ORIGIN_CANDIDATE))
        entry = labels['umuldiv16_hybrid']
    elif kind == 'pareto_direct':
        labels = patch_source(cpu.mem, generate_pareto_direct(ORIGIN_CANDIDATE))
        entry = labels['umuldiv16_pareto_direct']
    elif kind == 'pareto_direct_hybrid':
        labels = patch_source(cpu.mem, generate_pareto_direct_hybrid(ORIGIN_CANDIDATE))
        entry = labels['umuldiv16_pareto_direct_hybrid']
    elif kind == 'pareto_width_hybrid':
        labels = patch_source(cpu.mem, generate_pareto_width_hybrid(ORIGIN_CANDIDATE))
        entry = labels['umuldiv16_pareto_width_hybrid']
    else:
        raise ValueError(kind)
    return cpu, entry


def run_variant(kind: str, cases):
    cpu, entry = make_cpu(kind)
    cycles = []
    errors = 0
    first_errors = []
    for a, b, d in cases:
        exp = expected(a, b, d)
        set_inputs(cpu, a, b, d)
        cyc = cpu.call(entry)
        got = get_outputs(cpu)
        if got != exp:
            errors += 1
            if len(first_errors) < 8:
                first_errors.append({
                    'a': a,
                    'b': b,
                    'd': d,
                    'got': list(got),
                    'expected': list(exp),
                })
        cycles.append(cyc)
    return {
        'cases': len(cases),
        'errors': errors,
        'first_errors': first_errors,
        'mean_cycles': statistics.fmean(cycles),
        'min_cycles': min(cycles),
        'max_cycles': max(cycles),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument(
        '--corpus',
        choices=('bounded_uniform', 'mixed_uniform', 'game8', 'game12_bounded', 'all'),
        default='all',
    )
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    names = (
        ('bounded_uniform', 'mixed_uniform', 'game8', 'game12_bounded')
        if args.corpus == 'all' else (args.corpus,)
    )
    result = {
        'status': 'research_evidence_not_release_certification',
        'profile': 'v2_pareto_fast',
        'seed': args.seed,
        'variants': VARIANTS,
        'historical_record_core_variants_excluded': True,
        'edge_cases': {},
        'corpora': {},
    }

    edges = edge_cases()
    for kind in VARIANTS:
        result['edge_cases'][kind] = run_variant(kind, edges)

    for i, name in enumerate(names):
        cases = corpus(name, args.cases, args.seed + i)
        row = {'shape': corpus_shape(cases)}
        for kind in VARIANTS:
            row[kind] = run_variant(kind, cases)
        baseline = row['composed']['mean_cycles']
        row['speedup_vs_composed_percent'] = {
            kind: 100.0 * (baseline - row[kind]['mean_cycles']) / baseline
            for kind in VARIANTS if kind != 'composed'
        }
        result['corpora'][name] = row

    total_errors = sum(
        r['errors'] for r in result['edge_cases'].values()
    ) + sum(
        row[k]['errors']
        for row in result['corpora'].values()
        for k in VARIANTS
    )
    result['total_errors'] = total_errors

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"profile=v2_pareto_fast seed=${args.seed:X}")
        for kind, r in result['edge_cases'].items():
            print(
                f"edge {kind:22s} mean={r['mean_cycles']:.3f} "
                f"range={r['min_cycles']}-{r['max_cycles']} errors={r['errors']}"
            )
        for name, row in result['corpora'].items():
            print(f"\n{name}: {row['shape']}")
            for kind in VARIANTS:
                r = row[kind]
                print(
                    f"  {kind:22s} mean={r['mean_cycles']:.3f} "
                    f"range={r['min_cycles']}-{r['max_cycles']} errors={r['errors']}"
                )

    if total_errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
