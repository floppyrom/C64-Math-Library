#!/usr/bin/env python3
"""Model a tighter positive-fraction prepared-ratio specialization.

This is a calibrated cycle model, not resident-image certification.

The real Quake64 near-plane interpolation ratio has the stronger contract:

    0 < n < d <= 65535

so the ratio itself is always positive and strictly fractional. That lets PREP
skip signed abs/sign/mode work and lets APPLY handle only the sign of the signed
component y.

The V2 record UMUL16 same_x core is modeled instruction-for-instruction,
including (zp),Y page-cross costs and carry branches. The model is checked
against the measured current prepared APPLY mean on the same deterministic
corpus before estimating the specialization.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics

BIAS = 202
ZCLIP = 0x0100


def _q(n: int) -> int:
    return (n * n) // 4 + BIAS * (n & 1)


SL = [_q(i) & 0xFF for i in range(511)]
SH = [(_q(i) >> 8) & 0xFF for i in range(511)]
NL = [(255 - (_q(255 - i) & 0xFF)) & 0xFF for i in range(511)]
NH = [(255 - ((_q(255 - i) >> 8) & 0xFF)) & 0xFF for i in range(511)]


def _adc(a: int, b: int, c: int) -> tuple[int, int]:
    s = a + b + c
    return s & 0xFF, int(s > 0xFF)


def same_x_cycles_and_product(x16: int, y16: int) -> tuple[int, int]:
    """Exact model of record_umul16_17zp.a same_x."""
    x0 = x16 & 0xFF
    x1 = (x16 >> 8) & 0xFF
    y0 = y16 & 0xFF
    y1 = (y16 >> 8) & 0xFF
    cycles = 0

    def lookup(table, base_low: int, index: int) -> int:
        nonlocal cycles
        cycles += 5 + int(base_low + index > 0xFF)
        return table[base_low + index]

    cycles += 2  # SEC
    c = 1
    a = lookup(SL, x0, y0)
    a, c = _adc(a, lookup(NL, 255 - x0, y0), c)
    z0 = a
    cycles += 3
    a = lookup(SH, x0, y0)
    a, c = _adc(a, lookup(NH, 255 - x0, y0), c)
    a, c = _adc(a, lookup(SL, x1, y0), c)

    if c:
        cycles += 3  # BCS taken
        cycles += 2  # CLC
        c = 0
        a, c = _adc(a, lookup(NL, 255 - x1, y0), c)
        xreg = a
        cycles += 2  # TAX
        a = 1
        cycles += 2  # LDA #1
        a, c = _adc(a, lookup(SH, x1, y0), c)
        if c:
            raise AssertionError("unexpected carry0 continuation")
        cycles += 3  # BCC taken
    else:
        cycles += 2  # BCS not taken
        a, c = _adc(a, lookup(NL, 255 - x1, y0), c)
        xreg = a
        cycles += 2
        a = lookup(SH, x1, y0)

    a, c = _adc(a, lookup(NH, 255 - x1, y0), c)
    high0 = a
    cycles += 4  # SMC STA abs

    yy = y1
    cycles += 2  # LDY #imm
    a = lookup(SL, x0, yy)
    a, c = _adc(a, lookup(NL, 255 - x0, yy), c)
    low1 = a
    cycles += 4
    a = lookup(SH, x0, yy)
    a, c = _adc(a, lookup(NH, 255 - x0, yy), c)
    a, c = _adc(a, lookup(SL, x1, yy), c)

    if c:
        cycles += 3
        cycles += 2
        c = 0
        a, c = _adc(a, lookup(NL, 255 - x1, yy), c)
        high1 = a
        cycles += 4
        a = 1
        cycles += 2
        a, c = _adc(a, lookup(SH, x1, yy), c)
        if c:
            raise AssertionError("unexpected carry1 continuation")
        cycles += 3
    else:
        cycles += 2
        a, c = _adc(a, lookup(NL, 255 - x1, yy), c)
        high1 = a
        cycles += 4
        a = lookup(SH, x1, yy)

    a, c = _adc(a, lookup(NH, 255 - x1, yy), c)
    yreg = a
    cycles += 2  # TAY
    cycles += 2  # CLC
    c = 0
    a = xreg
    cycles += 2  # TXA
    a, c = _adc(a, low1, c)
    cycles += 2
    xreg = a
    cycles += 2  # TAX
    a = high0
    cycles += 2  # LDA #imm
    a, c = _adc(a, high1, c)
    cycles += 2
    if c:
        cycles += 3
        yreg = (yreg + 1) & 0xFF
        cycles += 2
        cycles += 6
    else:
        cycles += 2
        cycles += 6

    product = z0 | (xreg << 8) | (a << 16) | (yreg << 24)
    if product != x16 * y16:
        raise AssertionError((x16, y16, product, x16 * y16))
    return cycles, product


# Current fast APPLY general-path wrapper overhead, excluding native same_x.
CURRENT_POS_OVERHEAD = 65
CURRENT_NEG_OVERHEAD = 100

# Positive-fraction specialization:
#   no RATIO_MODE check in hot APPLY
#   no ratio-sign EOR/store/check
#   duplicate positive/negative y tails
#   negative output is formed directly from A:Y without publishing then rereading
SPECIAL_POS_OVERHEAD = 37
SPECIAL_NEG_OVERHEAD = 60


def current_apply_cycles(m: int, y: int) -> int:
    core, _ = same_x_cycles_and_product(m, abs(y))
    return core + (CURRENT_POS_OVERHEAD if y >= 0 else CURRENT_NEG_OVERHEAD)


def special_apply_cycles(m: int, y: int) -> int:
    core, _ = same_x_cycles_and_product(m, abs(y))
    return core + (SPECIAL_POS_OVERHEAD if y >= 0 else SPECIAL_NEG_OVERHEAD)


def current_prefix_cycles(n: int, d: int) -> int:
    """Current signed PREP prefix through fraction initialization on n,d>0,n<d."""
    # sign (14), abs/copy n (17), abs/copy d (17), d!=0 (9), n!=0 (9)
    cycles = 66
    if (n >> 8) < (d >> 8):
        cycles += 9
    else:
        # n<d, so equal high bytes implies low-byte BCC path.
        cycles += 19
    # LDA #0; STA mode; STA rq0; STA rq1
    cycles += 12
    return cycles


def special_prefix_cycles() -> int:
    # Copy n,d to ZP (28), clear rq0/rq1 while keeping general-only contract (8),
    # and explicitly CLC for the first carry-pipelined fractional step (2).
    # No sign/mode/range/zero handling exists in this specialized entry.
    return 38


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    # Independent native-core sanity sample.
    core_rng = random.Random(args.seed ^ 0x6510)
    core_cycles = []
    for _ in range(10000):
        x = core_rng.randrange(0x10000)
        y = core_rng.randrange(0x10000)
        c, _ = same_x_cycles_and_product(x, y)
        core_cycles.append(c)

    rng = random.Random(args.seed)
    current_cycles = []
    special_cycles = []
    current_prefix = []
    positive_current = []
    positive_special = []
    negative_current = []
    negative_special = []
    arithmetic_errors = 0

    for _ in range(args.cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        # Benchmark seed currently produces no identity cases. Keep this model
        # explicitly on the strict-fraction subset because that is the proposed API.
        if not (0 < n < d):
            # Preserve RNG progression to mirror benchmark_prepared_ratio.py.
            rng.randint(-8192, 8191)
            rng.randint(-8192, 8191)
            continue
        m = ((n << 16) + d // 2) // d
        current_prefix.append(current_prefix_cycles(n, d))

        for y in (rng.randint(-8192, 8191), rng.randint(-8192, 8191)):
            cc = current_apply_cycles(m, y)
            sc = special_apply_cycles(m, y)
            current_cycles.append(cc)
            special_cycles.append(sc)
            if y >= 0:
                positive_current.append(cc)
                positive_special.append(sc)
            else:
                negative_current.append(cc)
                negative_special.append(sc)

            # Arithmetic is unchanged: magnitude multiply + sign restore.
            _, prod = same_x_cycles_and_product(m, abs(y))
            got = (prod >> 16) & 0xFFFF
            if y < 0:
                got = (-got) & 0xFFFF
            signed_got = got if got < 0x8000 else got - 0x10000
            exact_prepared = (abs(y) * m) >> 16
            if y < 0:
                exact_prepared = -exact_prepared
            arithmetic_errors += int(signed_got != exact_prepared)

    measured_current_apply = 216.1442
    model_current_apply = statistics.fmean(current_cycles)
    measured_unrolled_prep = 744.5384
    measured_unrolled_pair = 1176.8268
    quake_pair = 3510.2862

    prefix_saving = statistics.fmean(current_prefix) - special_prefix_cycles()
    predicted_prep = measured_unrolled_prep - prefix_saving
    predicted_apply = statistics.fmean(special_cycles)
    predicted_pair = predicted_prep + 2 * predicted_apply

    result = {
        'status': 'calibrated_cycle_model_not_resident_image_certification',
        'cases': args.cases,
        'seed': args.seed,
        'strict_fraction_cases': len(current_prefix),
        'native_same_x_sanity': {
            'cases': len(core_cycles),
            'mean_cycles': statistics.fmean(core_cycles),
            'min_cycles': min(core_cycles),
            'max_cycles': max(core_cycles),
            'note': 'uniform random direct same_x model; generic umult adds 28 binding cycles',
        },
        'calibration': {
            'measured_current_apply_mean': measured_current_apply,
            'modeled_current_apply_mean': model_current_apply,
            'difference_cycles': model_current_apply - measured_current_apply,
        },
        'specialized_apply': {
            'mean_cycles': predicted_apply,
            'min_cycles': min(special_cycles),
            'max_cycles': max(special_cycles),
            'saving_vs_current_apply_cycles': model_current_apply - predicted_apply,
            'positive_y_current_mean': statistics.fmean(positive_current),
            'positive_y_special_mean': statistics.fmean(positive_special),
            'negative_y_current_mean': statistics.fmean(negative_current),
            'negative_y_special_mean': statistics.fmean(negative_special),
            'arithmetic_errors': arithmetic_errors,
        },
        'specialized_unrolled_pair_prediction': {
            'current_prefix_mean_cycles': statistics.fmean(current_prefix),
            'special_prefix_cycles': special_prefix_cycles(),
            'prefix_saving_cycles': prefix_saving,
            'predicted_prep_mean_cycles': predicted_prep,
            'predicted_prep_plus_two_apply_mean_cycles': predicted_pair,
            'measured_general_prepared_pair_mean_cycles': measured_unrolled_pair,
            'saving_vs_general_prepared_pair_percent': 100.0 * (measured_unrolled_pair - predicted_pair) / measured_unrolled_pair,
            'quake64_current_pair_mean_cycles': quake_pair,
            'saving_vs_quake64_current_pair_percent': 100.0 * (quake_pair - predicted_pair) / quake_pair,
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"calibration measured={measured_current_apply:.4f} modeled={model_current_apply:.4f}")
        print(
            f"special APPLY mean={predicted_apply:.4f} saving={model_current_apply-predicted_apply:.4f} "
            f"errors={arithmetic_errors}"
        )
        print(
            f"predicted unrolled PREP={predicted_prep:.4f} pair={predicted_pair:.4f} "
            f"vs-general={result['specialized_unrolled_pair_prediction']['saving_vs_general_prepared_pair_percent']:.2f}% "
            f"vs-Quake={result['specialized_unrolled_pair_prediction']['saving_vs_quake64_current_pair_percent']:.2f}%"
        )


if __name__ == '__main__':
    main()
