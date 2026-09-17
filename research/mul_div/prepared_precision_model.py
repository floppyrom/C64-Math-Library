#!/usr/bin/env python3
"""Model the minimum fixed-point precision needed for prepared ratio.

For a rounded Qp ratio:

    m = round((n/d) * 2^p)

nearest rounding guarantees ratio error <= 1/(2*2^p). If the applied signed
component satisfies |y| <= M, the real-valued product error is therefore:

    <= M / 2^(p+1)

So p=14 is sufficient for the full signed16 domain (M=32768) to guarantee that
integer truncation differs from exact trunc(y*n/d) by at most one. The previous
Q16 prepared-ratio prototype was therefore two fractional bits more precise
than its <=1 integer error contract required.

This script also models lower precisions for bounded component domains and
calibrates the strict-fraction PREP cycle geometry against the existing Q16
model result.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics

ZCLIP = 0x0100
KNOWN_Q16_STRICT_PREP_MEAN = 695.3604
KNOWN_STRICT_APPLY_MEAN = 182.1937
QUAKE_REFERENCE_MEAN = 3510.2862


def trunc_div(num: int, den: int) -> int:
    sign = -1 if num < 0 else 1
    return sign * (abs(num) // den)


def frac_steps(n: int, d: int, bits: int) -> tuple[int, int, int]:
    """Return floor(n*2^bits/d), remainder, and modeled unrolled step cycles."""
    rem = n
    q = 0
    cycles = 0
    for _ in range(bits):
        # Generated binary stage: ROL q0,q1,r0,A.
        base = 5 + 5 + 5 + 2
        raw = rem << 1
        carry17 = raw > 0xFFFF
        low = raw & 0xFFFF

        if carry17:
            # BCS force + TAX/LDA/SBC/STA/TXA/SBC/SEC.
            cycles += base + 3 + (2 + 3 + 3 + 3 + 2 + 3 + 2)
            rem = raw - d
            bit = 1
        else:
            cycles += base + 2  # BCS not taken
            rh, rl = low >> 8, low & 0xFF
            dh, dl = d >> 8, d & 0xFF
            cycles += 3  # CMP dhi
            if rh < dh:
                cycles += 3
                rem = low
                bit = 0
            elif rh > dh:
                cycles += 2 + 3
                cycles += 2 + 3 + 3 + 3 + 2 + 3 + 3
                rem = low - d
                bit = 1
            elif rl < dl:
                cycles += 2 + 2 + 3 + 3 + 3
                rem = low
                bit = 0
            else:
                cycles += 2 + 2 + 3 + 3 + 2
                cycles += 2 + 3 + 3 + 3 + 2 + 3 + 3
                rem = low - d
                bit = 1

        q = (q << 1) | bit

    return q, rem, cycles


def prep_raw_cycles(n: int, d: int, bits: int) -> tuple[int, int]:
    q, rem, cycles = frac_steps(n, d, bits)

    # Positive strict-fraction input copies/clear/initial carry and LDA high.
    cycles += 41

    # Carry pipeline needs one final quotient insertion; preserve remainder high.
    cycles += 5 + 5 + 3

    # Round to nearest: compare 2*remainder with divisor.
    doubled = rem << 1
    carry17 = doubled > 0xFFFF
    rr = doubled & 0xFFFF
    cycles += 5 + 5
    if carry17:
        cycles += 3
        do_round = True
    else:
        cycles += 2 + 3 + 3
        rh, rl = rr >> 8, rr & 0xFF
        dh, dl = d >> 8, d & 0xFF
        if rh < dh:
            cycles += 3
            do_round = False
        elif rh > dh:
            cycles += 2 + 3
            do_round = True
        else:
            cycles += 2 + 2 + 3 + 3
            if rl < dl:
                cycles += 3
                do_round = False
            else:
                cycles += 2
                do_round = True

    if do_round:
        q += 1
        cycles += 5  # INC rq0
        if q & 0xFF:
            cycles += 3
        else:
            cycles += 2 + 5

    # Convert Qp to the native multiplier's Q16 representation.
    cycles += 10 * (16 - bits)

    # Fast-state native X binding + CLC/RTS.
    cycles += 42
    return q, cycles


def precision_bound(component_max: int) -> int:
    # Need M / 2^(p+1) <= 1 for <=1 integer truncation error.
    if component_max <= 1:
        return 0
    return max(0, math.ceil(math.log2(component_max)) - 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    rng = random.Random(args.seed)
    corpus = []
    for _ in range(args.cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP + 1, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        x = rng.randint(-8192, 8191)
        y = rng.randint(-8192, 8191)
        corpus.append((n, d, x, y))

    raw_q16 = statistics.fmean(prep_raw_cycles(n, d, 16)[1] for n, d, _, _ in corpus)
    calibration = KNOWN_Q16_STRICT_PREP_MEAN - raw_q16

    rows = {}
    for bits in (16, 15, 14, 13, 12, 11):
        prep = []
        errors = []
        identity_rounds = 0
        for n, d, x, y in corpus:
            q, cyc = prep_raw_cycles(n, d, bits)
            prep.append(cyc + calibration)
            identity_rounds += int(q == (1 << bits))
            for v in (x, y):
                got = trunc_div(v * q, 1 << bits)
                exact = trunc_div(v * n, d)
                errors.append(got - exact)

        rows[f'q{bits}'] = {
            'bits': bits,
            'full_signed16_guarantee': bits >= 14,
            'guaranteed_component_abs_max_for_error_le_1': min(32768, 1 << (bits + 1)),
            'modeled_prep_mean_cycles': statistics.fmean(prep),
            'modeled_prep_min_cycles': min(prep),
            'modeled_prep_max_cycles': max(prep),
            'identity_rounds': identity_rounds,
            'nonzero_error_percent_on_stress': 100.0 * sum(e != 0 for e in errors) / len(errors),
            'mean_absolute_error_on_stress': statistics.fmean(abs(e) for e in errors),
            'max_absolute_error_on_stress': max(abs(e) for e in errors),
        }

    q14_prep = rows['q14']['modeled_prep_mean_cycles']
    separate_q14 = q14_prep + 2 * KNOWN_STRICT_APPLY_MEAN
    first_positive = sum(x >= 0 for _, _, x, _ in corpus)
    first_negative = args.cases - first_positive
    first_return_saving = (8 * first_positive + 5 * first_negative) / args.cases
    fused_q14 = separate_q14 - 8 - first_return_saving

    result = {
        'status': 'calibrated_cycle_model_not_resident_image_certification',
        'cases': args.cases,
        'seed': args.seed,
        'precision_law': {
            'ratio_error_bound': '1 / 2^(p+1)',
            'product_error_bound': 'M / 2^(p+1)',
            'minimum_p_for_full_signed16_error_le_1': 14,
            'minimum_p_examples': {
                'abs_component_le_32768': precision_bound(32768),
                'abs_component_le_16384': precision_bound(16384),
                'abs_component_le_8192': precision_bound(8192),
                'abs_component_le_4096': precision_bound(4096),
            },
        },
        'q16_cycle_calibration': {
            'raw_model_mean_cycles': raw_q16,
            'known_calibrated_mean_cycles': KNOWN_Q16_STRICT_PREP_MEAN,
            'applied_offset_cycles': calibration,
        },
        'variants': rows,
        'q14_fused_scale2_prediction': {
            'prep_mean_cycles': q14_prep,
            'apply_mean_cycles': KNOWN_STRICT_APPLY_MEAN,
            'separate_prep_plus_two_apply_mean_cycles': separate_q14,
            'fused_internal_mean_cycles': fused_q14,
            'fused_plus_one_caller_jsr_mean_cycles': fused_q14 + 6,
            'saving_vs_quake_reference_percent': 100.0 * (QUAKE_REFERENCE_MEAN - fused_q14) / QUAKE_REFERENCE_MEAN,
            'note': 'Q14 identity-round case must copy/negate inputs rather than bind 65536 as a 16-bit multiplier.'
        }
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print('minimum full signed16 precision: Q14')
        for name, row in rows.items():
            print(
                f"{name:4s} prep={row['modeled_prep_mean_cycles']:.3f} "
                f"maxerr={row['max_absolute_error_on_stress']} "
                f"guaranteed |y|<={row['guaranteed_component_abs_max_for_error_le_1']}"
            )
        print(
            f"Q14 fused SCALE2 ~= {fused_q14:.3f} cycles internal, "
            f"{fused_q14+6:.3f} including one caller JSR"
        )


if __name__ == '__main__':
    main()
