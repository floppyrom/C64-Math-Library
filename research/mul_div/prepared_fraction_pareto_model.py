#!/usr/bin/env python3
"""Instruction-level strict-fraction model for the shipped V2 Pareto core.

Targets the implementation actually present in V2:

    I_UMUL8 = $5300  (Pareto practical quarter-square core)
    I_UMUL16 = $5400 (integrated 3xUMUL8 public-I/O kernel)

It deliberately does not treat the separate record_umul16_17zp research source
as the installed V2 UMUL16 implementation.

Three points are modeled on the deterministic Quake-derived 0<n<d corpus:

  pareto_current_nearest  current actual-core prepared candidate
  pareto_inline_nearest   PREP-patched balanced fixed-X inline products
  pareto_inline_floor     same, but floor Q0.16 PREP without final rounding

Cycle results are models, not resident-image certification. The UMUL8 submodel
is calibrated exhaustively against the published V2 native mean/min/max.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics

ZCLIP = 0x0100


def umul8_cycles(x: int, y: int) -> int:
    """Exact V2 pareto_umul8.a cycles; RTS included, caller JSR excluded."""
    cross = int(x + y > 255)
    neg = y < x
    return (
        2 + 3 + 3 + 2 + 3 + 2 + (5 + cross)
        + (3 if neg else 2)
        + 4 + 3 + (5 + cross) + 4 + 6
    )


def fixed_inline_mul_cycles(x: int, y: int) -> int:
    """Balanced fixed-X inline product emitted by the inline generator."""
    cross = int(x + y > 255)
    neg = y < x
    # SEC; TYA; SBC #X; normalize negative difference if needed; TAX;
    # two abs,Y sum loads and two abs,X difference loads; two result stores.
    c = 2 + 2 + 2
    if neg:
        c += 2 + 2 + 2  # BCS not; SBC #0; EOR #$ff
    else:
        c += 3          # BCS taken
    c += 2 + (4 + cross) + 4 + 3 + (4 + cross) + 4 + 3
    return c


def pareto_state_cycles(m: int) -> int:
    """State cost of generate_prepared_fraction_pareto.py."""
    m0, m1 = m & 255, (m >> 8) & 255
    c = 3 + 4 + 3 + 4 + 2 + 3
    if m1 >= m0:
        c += 3 + 4 + 2 + 4 + 2 + 6
    else:
        c += 2 + 2 + 2 + 2 + 4 + 2 + 4 + 2 + 6
    return c


def inline_patch_cycles(m: int) -> int:
    """Patch X into SBC #imm plus sum-low/sum-high operands for 3 products."""
    m0, m1 = m & 255, (m >> 8) & 255
    # m0 and m1: LDA zp + three STA abs patch writes each.
    c = (3 + 4 + 4 + 4) + (3 + 4 + 4 + 4) + 2 + 3
    # |m1-m0| gets the same three writes, plus retained sign state.
    if m1 >= m0:
        c += 3 + 4 + 4 + 4 + 2 + 4 + 2 + 6
    else:
        c += 2 + 2 + 2 + 2 + 4 + 4 + 4 + 2 + 4 + 2 + 6
    return c


def prep_cycles(n: int, d: int, *, rounding: str, state: str) -> tuple[int, int]:
    """Exact instruction-count model of the unrolled trusted 0<n<d PREP."""
    if not (0 < n < d <= 0xFFFF):
        raise ValueError((n, d))

    # Copy N/D 28; clear q0/q1 8; CLC 2; LDA rn1 3.
    c = 41
    rem = n
    q = 0
    carry = 0

    for _ in range(16):
        c += 17  # ROL q0,q1,rn0,A
        q = ((q << 1) | carry) & 0xFFFF
        shifted = rem * 2

        if shifted > 0xFFFF:
            c += 3 + 18
            rem = (shifted - d) & 0xFFFF
            carry = 1
            continue

        r = shifted
        c += 2 + 3  # BCS not; CMP high
        rh, dh = r >> 8, d >> 8
        if rh < dh:
            c += 3
            rem, carry = r, 0
            continue

        c += 2
        if rh != dh:
            c += 3 + 19
            rem, carry = r - d, 1
            continue

        c += 2 + 3 + 3
        if (r & 255) < (d & 255):
            c += 3
            rem, carry = r, 0
        else:
            c += 2 + 19
            rem, carry = r - d, 1

    c += 10
    q = ((q << 1) | carry) & 0xFFFF

    if rounding == 'nearest':
        c += 3 + 10  # STA rn1; double remainder
        doubled = rem * 2
        if doubled > 0xFFFF:
            c += 3
            do_round = True
        else:
            rr = doubled & 0xFFFF
            c += 2 + 3 + 3
            rrh, dh = rr >> 8, d >> 8
            if rrh < dh:
                c += 3
                do_round = False
            else:
                c += 2
                if rrh != dh:
                    c += 3
                    do_round = True
                else:
                    c += 2 + 3 + 3
                    if (rr & 255) < (d & 255):
                        c += 3
                        do_round = False
                    else:
                        c += 2
                        do_round = True
        if do_round:
            c += 5
            if (q & 255) != 255:
                c += 3
            else:
                c += 2 + 5
            q = (q + 1) & 0xFFFF
    elif rounding != 'floor':
        raise ValueError(rounding)

    c += pareto_state_cycles(q) if state == 'pareto' else inline_patch_cycles(q)
    return c, q


def pareto_apply_cycles(m: int, y: int) -> int:
    """Current prepared APPLY using three calls to shipped V2 UMUL8."""
    m0, m1 = m & 255, (m >> 8) & 255
    md = m1 - m0
    mdiff, msign = abs(md), md < 0
    ay = abs(y)
    y0, y1 = ay & 255, (ay >> 8) & 255
    neg = y < 0
    c = 4 + 3 + 4 + 2 + 3 + 4 + 3
    c += 3 if neg else 2
    if neg:
        c += 2 + 2 + 3 + 3 + 2 + 3 + 3

    c += 4 + 3 + 6 + umul8_cycles(m0, y0) + 3 + 3 + 3
    c += 4 + 3 + 6 + umul8_cycles(m1, y1) + 3 + 3 + 3

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

    c += 4 + 6 + umul8_cycles(mdiff, v) + 3
    c += 2 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 2 + 3
    c += 3
    if parity:
        c += 3 + (2 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 3)
    else:
        c += 2 + (2 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 3) + 3

    c += 3 + 2 + 3 + 3 + 3 + 4 + 3 + 3 + 4
    c += 3
    if neg:
        c += 2 + 2 + 2 + 4 + 4 + 2 + 4 + 4
    else:
        c += 3
    return c + 2 + 6


def inline_apply_cycles(m: int, y: int) -> int:
    """PREP-patched balanced fixed-X inline APPLY."""
    m0, m1 = m & 255, (m >> 8) & 255
    md = m1 - m0
    mdiff, msign = abs(md), md < 0
    ay = abs(y)
    y0, y1 = ay & 255, (ay >> 8) & 255
    neg = y < 0
    c = 4 + 3 + 4 + 2 + 3 + 4 + 3
    c += 3 if neg else 2
    if neg:
        c += 2 + 2 + 3 + 3 + 2 + 3 + 3

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

    c += fixed_inline_mul_cycles(mdiff, v)
    c += 2 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 2 + 3
    c += 3
    if parity:
        c += 3 + (2 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 3)
    else:
        c += 2 + (2 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 3 + 2 + 3) + 3

    c += 3 + 2 + 3 + 3 + 3 + 4 + 3 + 3 + 4
    c += 3
    if neg:
        c += 2 + 2 + 2 + 4 + 4 + 2 + 4 + 4
    else:
        c += 3
    return c + 2 + 6


def _exact(y: int, n: int, d: int) -> int:
    q = abs(y) * n // d
    return -q if y < 0 else q


def _prepared(y: int, m: int) -> int:
    q = (abs(y) * m) >> 16
    return -q if y < 0 else q


def _stats(xs: list[int]) -> dict[str, float | int]:
    return {'mean': statistics.fmean(xs), 'min': min(xs), 'max': max(xs)}


def _err(xs: list[int]) -> dict[str, float | int]:
    return {
        'outputs': len(xs),
        'nonzero_error_percent': 100.0 * sum(x != 0 for x in xs) / len(xs),
        'mean_absolute_error': statistics.fmean(abs(x) for x in xs),
        'max_absolute_error': max(abs(x) for x in xs),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    cal = [umul8_cycles(x, y) for x in range(256) for y in range(256)]
    rng = random.Random(args.seed)
    cp: list[int] = []
    ca: list[int] = []
    ip: list[int] = []
    ia: list[int] = []
    fp: list[int] = []
    fa: list[int] = []
    en: list[int] = []
    ef: list[int] = []

    for _ in range(args.cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP + 1, 8191)
        n, d = ZCLIP - z0, z1 - z0
        x, y = rng.randint(-8192, 8191), rng.randint(-8192, 8191)

        cpc, mn = prep_cycles(n, d, rounding='nearest', state='pareto')
        ipc, mn2 = prep_cycles(n, d, rounding='nearest', state='inline')
        fpc, mf = prep_cycles(n, d, rounding='floor', state='inline')
        assert mn == mn2
        cp.append(cpc); ip.append(ipc); fp.append(fpc)

        for v in (x, y):
            ca.append(pareto_apply_cycles(mn, v))
            ia.append(inline_apply_cycles(mn, v))
            fa.append(inline_apply_cycles(mf, v))
            ex = _exact(v, n, d)
            en.append(_prepared(v, mn) - ex)
            ef.append(_prepared(v, mf) - ex)

    cur = statistics.fmean(cp) + 2 * statistics.fmean(ca)
    near = statistics.fmean(ip) + 2 * statistics.fmean(ia)
    floor = statistics.fmean(fp) + 2 * statistics.fmean(fa)
    result = {
        'status': 'instruction_level_model_not_resident_image_certification',
        'cases': args.cases,
        'seed': args.seed,
        'v2_umul8_calibration': {
            'modeled_mean': statistics.fmean(cal),
            'modeled_min': min(cal),
            'modeled_max': max(cal),
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
            'prep_cycles': _stats(cp),
            'apply_cycles': _stats(ca),
            'pair_mean_cycles': cur,
            'accuracy_vs_exact': _err(en),
        },
        'pareto_inline_nearest': {
            'prep_cycles': _stats(ip),
            'apply_cycles': _stats(ia),
            'pair_mean_cycles': near,
            'saving_vs_current_percent': 100.0 * (cur - near) / cur,
            'accuracy_vs_exact': _err(en),
        },
        'pareto_inline_floor': {
            'prep_cycles': _stats(fp),
            'apply_cycles': _stats(fa),
            'pair_mean_cycles': floor,
            'saving_vs_current_percent': 100.0 * (cur - floor) / cur,
            'accuracy_vs_exact': _err(ef),
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"V2 UMUL8 calibration mean={statistics.fmean(cal):.6f} "
            f"range={min(cal)}-{max(cal)}"
        )
        for k in ('pareto_current_nearest', 'pareto_inline_nearest', 'pareto_inline_floor'):
            r = result[k]
            print(
                f"{k:24s} prep={r['prep_cycles']['mean']:.3f} "
                f"apply={r['apply_cycles']['mean']:.3f} "
                f"pair={r['pair_mean_cycles']:.3f} "
                f"maxerr={r['accuracy_vs_exact']['max_absolute_error']}"
            )

    if abs(statistics.fmean(cal) - 45.494140625) > 1e-12 or min(cal) != 44 or max(cal) != 47:
        raise SystemExit('V2 UMUL8 calibration failed')
    if result['pareto_inline_nearest']['accuracy_vs_exact']['max_absolute_error'] > 1:
        raise SystemExit('nearest error contract failed')
    if result['pareto_inline_floor']['accuracy_vs_exact']['max_absolute_error'] > 1:
        raise SystemExit('floor error contract failed')


if __name__ == '__main__':
    main()
