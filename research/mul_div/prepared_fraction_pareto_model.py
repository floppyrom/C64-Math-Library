#!/usr/bin/env python3
"""Instruction-level model for strict-fraction ratio work on shipped V2.

This model deliberately targets the V2 Pareto-Fast implementation that is
actually present in the shipped resident image:

    I_UMUL8 = $5300, 45.494140625-cycle exhaustive native mean
    I_UMUL16 = $5400, integrated 3xUMUL8 public-I/O kernel

It does NOT model the separate record_umul16_17zp research source as though it
were the installed V2 UMUL16 implementation.

The script compares three research points on the deterministic Quake-derived
strict-fraction stress corpus:

  pareto_current_nearest
      generate_prepared_fraction_pareto.py shape: rounded Q0.16 PREP followed
      by a 3x shipped-UMUL8 APPLY.

  pareto_inline_nearest
      same arithmetic, but PREP patches three fixed-X quarter-square multiply
      sites and APPLY inlines them, eliminating generic fixed-operand setup and
      JSR/RTS overhead.

  pareto_inline_floor
      same inline APPLY, but PREP uses floor(n*65536/d) instead of rounding.
      This removes the final rounding stage while retaining max integer error
      <= 1 for signed16 applied values.

The cycle results are instruction-level models, not resident-image
certification. The shipped UMUL8 submodel is independently calibrated exactly
against its published exhaustive mean/min/max.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics

ZCLIP = 0x0100


def umul8_cycles(x: int, y: int) -> int:
    """Exact cycle model of V2 pareto_umul8.a native core, RTS included."""
    if not (0 <= x <= 255 and 0 <= y <= 255):
        raise ValueError((x, y))
    cross = int(x + y > 255)
    negative_difference = y < x
    # SEC, STX, STX, TYA, SBC zp, TAX, LDA (zp),Y, BCC,
    # SBC abs,X, STA zp, LDA (zp),Y, SBC abs,X, RTS.
    return (
        2 + 3 + 3 + 2 + 3 + 2 + (5 + cross)
        + (3 if negative_difference else 2)
        + 4 + 3 + (5 + cross) + 4 + 6
    )


def fixed_inline_mul_cycles(x: int, y: int) -> int:
    """Cycle model of one PREP-patched fixed-X inline quarter-square product.

    The fixed X value is patched into SBC #imm and the low bytes of two abs,Y
    sum-square loads. Difference tables remain ordinary abs,X accesses.
    Output low/high stores are included; there is no JSR/RTS.
    """
    cross = int(x + y > 255)
    neg = y < x
    common = 2 + 2 + 2 + 2 + (4 + cross)  # SEC/TYA/SBC#/TAX/LDA abs,Y
    if neg:
        # BCC taken; negative low/high table path; falls through to high store.
        return common + 3 + 4 + 3 + (4 + cross) + 4 + 3
    # Positive path uses a JMP over the negative duplicate before the high store.
    return common + 2 + 4 + 3 + (4 + cross) + 4 + 3 + 3 + 3


def _pareto_state_cycles(m: int) -> int:
    """Store m0/m1 + |m1-m0| + sign as in current Pareto generator."""
    m0, m1 = m & 255, (m >> 8) & 255
    cycles = 3 + 4 + 3 + 4 + 2 + 3
    if m1 >= m0:
        cycles += 3 + 4 + 2 + 4 + 2 + 6
    else:
        cycles += 2 + 2 + 2 + 2 + 4 + 2 + 4 + 2 + 6
    return cycles


def _inline_patch_cycles(m: int) -> int:
    """Patch three fixed-X product sites and retain only difference sign state."""
    m0, m1 = m & 255, (m >> 8) & 255
    # For m0 and m1: LDA zp + three absolute STA patch writes each.
    cycles = (3 + 4 + 4 + 4) + (3 + 4 + 4 + 4) + 2 + 3
    if m1 >= m0:
        cycles += 3 + 4 + 4 + 4 + 2 + 4 + 2 + 6
    else:
        cycles += 2 + 2 + 2 + 2 + 4 + 4 + 4 + 2 + 4 + 2 + 6
    return cycles


def prep_cycles(n: int, d: int, *, rounding: str, state: str) -> tuple[int, int]:
    """Instruction-level model of the unrolled strict-fraction PREP."""
    if not (0 < n < d <= 0xFFFF):
        raise ValueError((n, d))

    # Copy N/D (28), clear q0/q1 (8), CLC (2), LDA rn1 (3).
    cycles = 41
    rem = n
    q = 0
    carry = 0

    for _ in range(16):
        # ROL q0; ROL q1; ROL rn0; ROL A.
        cycles += 17
        q = ((q << 1) | carry) & 0xFFFF
        shifted = rem * 2

        if shifted > 0xFFFF:
            cycles += 3  # BCS force taken
            # TAX/LDA/SBC/STA/TXA/SBC/SEC
            cycles += 18
            rem = (shifted - d) & 0xFFFF
            carry = 1
            continue

        r16 = shifted
        cycles += 2 + 3  # BCS not taken; CMP rd1
        rh, dh = r16 >> 8, d >> 8
        if rh < dh:
            cycles += 3  # BCC no taken
            rem, carry = r16, 0
            continue

        cycles += 2  # BCC not taken
        if rh != dh:
            cycles += 3  # BNE take
            cycles += 19  # subtraction body including final BCS
            rem, carry = r16 - d, 1
            continue

        cycles += 2 + 3 + 3  # BNE not; LDX rn0; CPX rd0
        if (r16 & 255) < (d & 255):
            cycles += 3
            rem, carry = r16, 0
        else:
            cycles += 2 + 19
            rem, carry = r16 - d, 1

    # Insert the final quotient decision.
    cycles += 10
    q = ((q << 1) | carry) & 0xFFFF

    if rounding == 'nearest':
        cycles += 3 + 10  # STA rn1; ASL rn0; ROL rn1
        doubled = rem * 2
        if doubled > 0xFFFF:
            cycles += 3
            do_round = True
        else:
            rr = doubled & 0xFFFF
            cycles += 2 + 3 + 3  # BCS not; LDA rn1; CMP rd1
            rrh, dh = rr >> 8, d >> 8
            if rrh < dh:
                cycles += 3
                do_round = False
            else:
                cycles += 2
                if rrh != dh:
                    cycles += 3
                    do_round = True
                else:
                    cycles += 2 + 3 + 3
                    if (rr & 255) < (d & 255):
                        cycles += 3
                        do_round = False
                    else:
                        cycles += 2
                        do_round = True
        if do_round:
            cycles += 5
            if (q & 255) != 255:
                cycles += 3
            else:
                cycles += 2 + 5
            q = (q + 1) & 0xFFFF
    elif rounding == 'floor':
        pass
    else:
        raise ValueError(rounding)

    if state == 'pareto':
        cycles += _pareto_state_cycles(q)
    elif state == 'inline':
        cycles += _inline_patch_cycles(q)
    else:
        raise ValueError(state)
    return cycles, q


def pareto_apply_cycles(m: int, y: int) -> int:
    """Current actual-V2 3xUMUL8 prepared APPLY model."""
    m0, m1 = m & 255, (m >> 8) & 255
    md = m1 - m0
    mdiff, msign = abs(md), md < 0
    ay = abs(y)
    y0, y1 = ay & 255, (ay >> 8) & 255
    neg = y < 0
    c = 0

    # Copy public Y, capture sign, optionally form magnitude.
    c += 4 + 3 + 4 + 2 + 3 + 4 + 3
    c += 3 if neg else 2
    if neg:
        c += 2 + 2 + 3 + 3 + 2 + 3 + 3

    # M=m0*y0 and L=m1*y1: load fixed X, load Y, JSR core, publish low/high.
    c += 4 + 3 + 6 + umul8_cycles(m0, y0) + 3 + 3 + 3
    c += 4 + 3 + 6 + umul8_cycles(m1, y1) + 3 + 3 + 3

    # v=|y1-y0| and parity.
    c += 3 + 2 + 3
    vd = y1 - y0
    if vd >= 0:
        c += 3
        v = vd
        c += 2 + 4 + 3
        parity = msign
    else:
        c += 2
        v = -vd
        c += 2 + 2 + 2 + 2 + 2 + 4 + 3 + 3
        parity = not msign

    # Q=|m1-m0|*v.
    c += 4 + 6 + umul8_cycles(mdiff, v) + 3

    # S=M+L.
    c += 2 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 2 + 3

    # Cross add/subtract.
    c += 3
    if parity:
        c += 3
        c += 2 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 3
    else:
        c += 2
        c += 2 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 3
        c += 3  # mathematically nonnegative cross => BCS combine

    # Publish high half.
    c += 3 + 2 + 3 + 3 + 3 + 4 + 3 + 3 + 4

    # Restore output sign.
    c += 3
    if neg:
        c += 2 + 2 + 2 + 4 + 4 + 2 + 4 + 4
    else:
        c += 3
    c += 2 + 6
    return c


def inline_apply_cycles(m: int, y: int) -> int:
    """Prepared fixed-X inline APPLY cycle model."""
    m0, m1 = m & 255, (m >> 8) & 255
    md = m1 - m0
    mdiff, msign = abs(md), md < 0
    ay = abs(y)
    y0, y1 = ay & 255, (ay >> 8) & 255
    neg = y < 0
    c = 0

    c += 4 + 3 + 4 + 2 + 3 + 4 + 3
    c += 3 if neg else 2
    if neg:
        c += 2 + 2 + 3 + 3 + 2 + 3 + 3

    # Y load + inline fixed-X product. No X load, JSR or RTS.
    c += 3 + fixed_inline_mul_cycles(m0, y0)
    c += 3 + fixed_inline_mul_cycles(m1, y1)

    c += 3 + 2 + 3
    vd = y1 - y0
    if vd >= 0:
        c += 3
        v = vd
        c += 2 + 4 + 3
        parity = msign
    else:
        c += 2
        v = -vd
        c += 2 + 2 + 2 + 2 + 2 + 4 + 3 + 3
        parity = not msign

    # Y already contains v from the difference path.
    c += fixed_inline_mul_cycles(mdiff, v)

    c += 2 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 2 + 3
    c += 3
    if parity:
        c += 3
        c += 2 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 3
    else:
        c += 2
        c += 2 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 3
        c += 3

    c += 3 + 2 + 3 + 3 + 3 + 4 + 3 + 3 + 4
    c += 3
    if neg:
        c += 2 + 2 + 2 + 4 + 4 + 2 + 4 + 4
    else:
        c += 3
    c += 2 + 6
    return c


def _trunc_ratio(y: int, n: int, d: int) -> int:
    q = abs(y) * n // d
    return -q if y < 0 else q


def _apply_value(y: int, m: int) -> int:
    q = (abs(y) * m) >> 16
    return -q if y < 0 else q


def summary(xs: list[int]) -> dict[str, float | int]:
    return {'mean': statistics.fmean(xs), 'min': min(xs), 'max': max(xs)}


def error_summary(xs: list[int]) -> dict[str, float | int]:
    return {
        'outputs': len(xs),
        'nonzero_error_percent': 100.0 * sum(v != 0 for v in xs) / len(xs),
        'mean_absolute_error': statistics.fmean(abs(v) for v in xs),
        'max_absolute_error': max(abs(v) for v in xs),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    # Exhaustive calibration of the installed V2 UMUL8 cycle model.
    all_umul8 = [umul8_cycles(x, y) for x in range(256) for y in range(256)]

    rng = random.Random(args.seed)
    cur_prep: list[int] = []
    cur_apply: list[int] = []
    inline_prep: list[int] = []
    inline_apply: list[int] = []
    floor_prep: list[int] = []
    floor_apply: list[int] = []
    nearest_errors: list[int] = []
    floor_errors: list[int] = []

    for _ in range(args.cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP + 1, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        assert 0 < n < d <= 0xFFFF
        x = rng.randint(-8192, 8191)
        y = rng.randint(-8192, 8191)

        cp, mn = prep_cycles(n, d, rounding='nearest', state='pareto')
        ip, mn2 = prep_cycles(n, d, rounding='nearest', state='inline')
        fp, mf = prep_cycles(n, d, rounding='floor', state='inline')
        assert mn == mn2
        cur_prep.append(cp)
        inline_prep.append(ip)
        floor_prep.append(fp)

        for value in (x, y):
            cur_apply.append(pareto_apply_cycles(mn, value))
            inline_apply.append(inline_apply_cycles(mn, value))
            floor_apply.append(inline_apply_cycles(mf, value))
            exact = _trunc_ratio(value, n, d)
            nearest_errors.append(_apply_value(value, mn) - exact)
            floor_errors.append(_apply_value(value, mf) - exact)

    cur_pair_mean = statistics.fmean(cur_prep) + 2 * statistics.fmean(cur_apply)
    inline_pair_mean = statistics.fmean(inline_prep) + 2 * statistics.fmean(inline_apply)
    floor_pair_mean = statistics.fmean(floor_prep) + 2 * statistics.fmean(floor_apply)

    result = {
        'status': 'instruction_level_model_not_resident_image_certification',
        'cases': args.cases,
        'seed': args.seed,
        'v2_umul8_calibration': {
            'modeled_mean': statistics.fmean(all_umul8),
            'modeled_min': min(all_umul8),
            'modeled_max': max(all_umul8),
            'published_mean': 45.494141,
            'published_min': 44,
            'published_max': 47,
        },
        'corpus': {
            'zclip': ZCLIP,
            'z0_range': [-8192, ZCLIP - 1],
            'z1_range': [ZCLIP + 1, 8191],
            'component_range': [-8192, 8191],
            'invariant': '0<n<d',
            'applications_per_preparation': 2,
        },
        'pareto_current_nearest': {
            'prep_cycles': summary(cur_prep),
            'apply_cycles': summary(cur_apply),
            'pair_mean_cycles': cur_pair_mean,
            'accuracy_vs_exact': error_summary(nearest_errors),
        },
        'pareto_inline_nearest': {
            'prep_cycles': summary(inline_prep),
            'apply_cycles': summary(inline_apply),
            'pair_mean_cycles': inline_pair_mean,
            'saving_vs_current_percent': 100.0 * (cur_pair_mean - inline_pair_mean) / cur_pair_mean,
            'accuracy_vs_exact': error_summary(nearest_errors),
        },
        'pareto_inline_floor': {
            'prep_cycles': summary(floor_prep),
            'apply_cycles': summary(floor_apply),
            'pair_mean_cycles': floor_pair_mean,
            'saving_vs_current_percent': 100.0 * (cur_pair_mean - floor_pair_mean) / cur_pair_mean,
            'accuracy_vs_exact': error_summary(floor_errors),
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        cal = result['v2_umul8_calibration']
        print(
            f"V2 UMUL8 calibration mean={cal['modeled_mean']:.6f} "
            f"range={cal['modeled_min']}-{cal['modeled_max']}"
        )
        for key in ('pareto_current_nearest', 'pareto_inline_nearest', 'pareto_inline_floor'):
            row = result[key]
            print(
                f"{key:24s} prep={row['prep_cycles']['mean']:.3f} "
                f"apply={row['apply_cycles']['mean']:.3f} pair={row['pair_mean_cycles']:.3f} "
                f"maxerr={row['accuracy_vs_exact']['max_absolute_error']}"
            )

    if result['v2_umul8_calibration']['modeled_min'] != 44:
        raise SystemExit('UMUL8 calibration failed')
    if abs(result['v2_umul8_calibration']['modeled_mean'] - 45.494140625) > 1e-12:
        raise SystemExit('UMUL8 mean calibration failed')
    if result['pareto_inline_nearest']['accuracy_vs_exact']['max_absolute_error'] > 1:
        raise SystemExit('nearest exceeded <=1 error contract')
    if result['pareto_inline_floor']['accuracy_vs_exact']['max_absolute_error'] > 1:
        raise SystemExit('floor exceeded <=1 error contract')


if __name__ == '__main__':
    main()
