#!/usr/bin/env python3
"""Prepared signed-ratio research for the MUL_DIV roadmap.

This models the Quake64 near-plane interpolation pattern:
    out = trunc_toward_zero(y * n / d)
where |n| <= |d| and the same dynamic ratio is applied to multiple signed
16-bit values.

Two paths are compared:
  * Quake64-style scale_nd: arithmetic-shift n and d until both fit s8,
    then perform the reduced exact ratio.
  * rounded Q16 prepared ratio: m = round(|n|*65536/|d|), then
    out = trunc(y*sign*m/65536).

The Q16 path is deliberately approximate. For signed16 y and |n|<=|d|,
nearest rounding guarantees an integer result error of at most one.
"""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass

B = 1 << 16
ZCLIP = 0x0100


def trunc_div(num: int, den: int) -> int:
    if den == 0:
        raise ZeroDivisionError
    sign = -1 if (num < 0) ^ (den < 0) else 1
    return sign * (abs(num) // abs(den))


def fits_s8(v: int) -> bool:
    return -128 <= v <= 127


def quake_scale_nd(n: int, d: int) -> tuple[int, int, int]:
    """Arithmetic-shift n and d together until both fit signed byte."""
    shifts = 0
    for _ in range(8):
        if fits_s8(n) and fits_s8(d):
            break
        n >>= 1
        d >>= 1
        shifts += 1
    return n, d, shifts


def quake_scaled_apply(y: int, n: int, d: int) -> int:
    ns, ds, _ = quake_scale_nd(n, d)
    if ds == 0:
        return 0
    return trunc_div(y * ns, ds)


def prep_ratio_q16_round(n: int, d: int) -> tuple[int, int]:
    """Return (sign, magnitude), where magnitude may be 65536 for identity."""
    if d == 0:
        raise ZeroDivisionError
    sign = -1 if (n < 0) ^ (d < 0) else 1
    an, ad = abs(n), abs(d)
    if an > ad:
        raise ValueError("prepared bounded-ratio model requires |n| <= |d|")
    if an == ad:
        return sign, B
    # Nearest integer Q0.16 ratio. Ties round upward in magnitude.
    m = ((an << 16) + (ad // 2)) // ad
    return sign, m


def prepared_apply(y: int, state: tuple[int, int]) -> int:
    sign, m = state
    return trunc_div(y * sign * m, B)


def exact_apply(y: int, n: int, d: int) -> int:
    return trunc_div(y * n, d)


@dataclass
class ErrorStats:
    cases: int = 0
    nonzero: int = 0
    sum_abs: int = 0
    max_abs: int = 0
    worst: tuple[int, int, int, int, int, int] | None = None

    def add(self, y: int, n: int, d: int, exact: int, got: int) -> None:
        err = got - exact
        ae = abs(err)
        self.cases += 1
        self.nonzero += int(err != 0)
        self.sum_abs += ae
        if ae > self.max_abs:
            self.max_abs = ae
            self.worst = (err, y, n, d, exact, got)

    def report(self) -> dict:
        return {
            "cases": self.cases,
            "nonzero_error_percent": 100.0 * self.nonzero / self.cases,
            "mean_absolute_error": self.sum_abs / self.cases,
            "max_absolute_error": self.max_abs,
            "worst": self.worst,
        }


def validate_edges() -> None:
    ys = (-32768, -32767, -8192, -257, -1, 0, 1, 257, 8191, 32767)
    ds = (1, 2, 3, 7, 127, 128, 255, 256, 257, 1024, 8192, 32767)
    for d in ds:
        ns = sorted({0, 1, d // 2, max(0, d - 1), d})
        for n in ns:
            for ratio_sign in (1, -1):
                sn = n * ratio_sign
                state = prep_ratio_q16_round(sn, d)
                for y in ys:
                    ex = exact_apply(y, sn, d)
                    got = prepared_apply(y, state)
                    if abs(got - ex) > 1:
                        raise AssertionError((y, sn, d, ex, got))


def synthetic_near_clip(cases: int, y_limit: int, seed: int) -> dict:
    """Generate valid positive near-plane crossings in 8.8 depth.

    z0 is behind ZCLIP and z1 is in front, so:
        n = ZCLIP-z0
        d = z1-z0
        0 < n <= d

    Ranges are deliberately broad stress ranges, not a claim about an actual
    Quake64 runtime distribution.
    """
    rng = random.Random(seed)
    current = ErrorStats()
    q16 = ErrorStats()
    shift_hist: dict[int, int] = {}

    for _ in range(cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        y = rng.randint(-y_limit, y_limit - 1)

        ex = exact_apply(y, n, d)
        cur = quake_scaled_apply(y, n, d)
        pre = prepared_apply(y, prep_ratio_q16_round(n, d))

        current.add(y, n, d, ex, cur)
        q16.add(y, n, d, ex, pre)
        _, _, shifts = quake_scale_nd(n, d)
        shift_hist[shifts] = shift_hist.get(shifts, 0) + 1

    return {
        "cases": cases,
        "seed": seed,
        "y_range": [-y_limit, y_limit - 1],
        "current_scale_nd": current.report(),
        "prepared_q16_round": q16.report(),
        "scale_nd_shift_histogram": dict(sorted(shift_hist.items())),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=int, default=1_000_000)
    ap.add_argument("--seed", type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    validate_edges()

    result = {
        "status": "research_model_not_cycle_certification",
        "contract": "signed16 y, signed16 n/d, |n|<=|d|, trunc_toward_zero target",
        "q16_error_bound": 1,
        "corpora": {
            "full_signed16_y": synthetic_near_clip(
                args.cases, 32768, args.seed
            ),
            "plusminus_32_world_units_8_8": synthetic_near_clip(
                args.cases, 8192, args.seed + 1
            ),
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("Prepared ratio Q16 research")
    print("edge validation: PASS (|error| <= 1)")
    for name, row in result["corpora"].items():
        print()
        print(name)
        for impl in ("current_scale_nd", "prepared_q16_round"):
            r = row[impl]
            print(
                f"  {impl:22s} nonzero={r['nonzero_error_percent']:.4f}% "
                f"mean_abs={r['mean_absolute_error']:.6f} "
                f"max_abs={r['max_absolute_error']}"
            )


if __name__ == "__main__":
    main()
