#!/usr/bin/env python3
"""Calibrated model for fused strict-fraction PREP+APPLY2.

This model composes the already calibrated strict-fraction APPLY model with the
same unrolled PREP body, then removes only instruction sequences that disappear
in the fused one-call assembly candidate.

It is deliberately labeled a model until benchmark_prepared_fraction_pair.py is
run against the shipped V2 image.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics

from prepared_fraction_model import special_apply_cycles

ZCLIP = 0x0100

# From PREPARED_FRACTION_RESULTS.md: calibrated strict-fraction fast PREP model.
STRICT_FAST_PREP_MEAN = 695.3604
QUAKE_PAIR_REFERENCE = 3510.2862


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    rng = random.Random(args.seed)
    separate = []
    fused = []
    apply = []
    first_positive = first_negative = 0

    for _ in range(args.cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP + 1, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        assert 0 < n < d <= 0xFFFF
        ya = rng.randint(-8192, 8191)
        yb = rng.randint(-8192, 8191)
        m = ((n << 16) + d // 2) // d

        ca = special_apply_cycles(m, ya)
        cb = special_apply_cycles(m, yb)
        apply.extend((ca, cb))

        sep = STRICT_FAST_PREP_MEAN + ca + cb
        separate.append(sep)

        # Fused assembly removes PREP's terminal CLC+RTS (8 cycles).
        # The first APPLY no longer returns. Positive X falls through and saves
        # all 8 terminal cycles. Negative X uses a 3-cycle JMP to skip the
        # positive duplicate, so its net saving is 5 cycles.
        first_return_saving = 8 if ya >= 0 else 5
        first_positive += int(ya >= 0)
        first_negative += int(ya < 0)
        fused.append(sep - 8 - first_return_saving)

    sep_mean = statistics.fmean(separate)
    fused_mean = statistics.fmean(fused)
    result = {
        'status': 'calibrated_cycle_model_not_resident_image_certification',
        'cases': args.cases,
        'seed': args.seed,
        'corpus': {
            'zclip': ZCLIP,
            'z0_range': [-8192, ZCLIP - 1],
            'z1_range': [ZCLIP + 1, 8191],
            'component_range': [-8192, 8191],
            'invariant': '0<n<d',
            'first_component_positive': first_positive,
            'first_component_negative': first_negative,
        },
        'strict_fraction_apply': {
            'mean_cycles': statistics.fmean(apply),
            'min_cycles': min(apply),
            'max_cycles': max(apply),
        },
        'separate_fast_prediction': {
            'prep_mean_cycles': STRICT_FAST_PREP_MEAN,
            'prep_plus_two_apply_mean_cycles': sep_mean,
        },
        'fused_scale2_prediction': {
            'mean_cycles_excluding_external_jsr': fused_mean,
            'min_cycles_excluding_external_jsr': min(fused),
            'max_cycles_excluding_external_jsr': max(fused),
            'mean_cycles_including_one_external_jsr': fused_mean + 6,
            'saving_vs_separate_internal_cycles': sep_mean - fused_mean,
            'saving_vs_separate_internal_percent': 100.0 * (sep_mean - fused_mean) / sep_mean,
            'saving_vs_reference_quake_pair_percent': 100.0 * (QUAKE_PAIR_REFERENCE - fused_mean) / QUAKE_PAIR_REFERENCE,
        },
        'notes': [
            'The Quake reference mean is the earlier measured 5000-case stress result; the strict z1 range differs by one endpoint value.',
            'The fused delta itself is instruction-exact relative to the calibrated separate strict-fraction model.',
            'Resident-image certification must come from benchmark_prepared_fraction_pair.py.'
        ]
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        print(f"strict APPLY mean={result['strict_fraction_apply']['mean_cycles']:.4f}")
        print(f"separate pair={sep_mean:.4f}")
        print(
            f"fused scale2={fused_mean:.4f} "
            f"including caller JSR={fused_mean+6:.4f} "
            f"vs separate={result['fused_scale2_prediction']['saving_vs_separate_internal_percent']:.2f}%"
        )


if __name__ == '__main__':
    main()
