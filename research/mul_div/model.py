#!/usr/bin/env python3
"""Independent arithmetic and cycle-geometry model for UMULDIV16 research.

This does not execute the resident 6502 image. It proves the bounded recurrence
against Python integer arithmetic and estimates the unrolled tail under several
scratch-placement choices. Use benchmark.py for cycle-accurate image results.
"""
from __future__ import annotations

import argparse
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Placement:
    name: str
    q_zp: bool
    r_zp: bool
    d_zp: bool

    @property
    def live_zp(self) -> int:
        return (2 if self.q_zp else 0) + (1 if self.r_zp else 0) + (2 if self.d_zp else 0)


PLACEMENTS = (
    Placement('absolute_0zp', False, False, False),
    Placement('remainder_1zp', False, True, False),
    Placement('divisor_2zp', False, False, True),
    Placement('quotient_2zp', True, False, False),
    Placement('remainder_divisor_3zp', False, True, True),
    Placement('quotient_remainder_3zp', True, True, False),
    Placement('quotient_divisor_4zp', True, False, True),
    Placement('all_5zp', True, True, True),
)


def reference(a: int, b: int, d: int):
    p = a * b
    if d == 0:
        return 'div0', 0, 0
    q, r = divmod(p, d)
    if q > 0xFFFF:
        return 'overflow', 0, 0
    return 'ok', q, r


def bounded_recurrence(a: int, b: int, d: int):
    p = a * b
    if d == 0:
        return 'div0', 0, 0
    hi = (p >> 16) & 0xFFFF
    lo = p & 0xFFFF
    if hi >= d:
        return 'overflow', 0, 0

    q = lo
    r = hi
    for _ in range(16):
        incoming = (q >> 15) & 1
        q = (q << 1) & 0xFFFF
        r = (r << 1) | incoming
        if r >= d:
            r -= d
            q |= 1
    return 'ok', q, r


def stage_cycles(a: int, b: int, d: int, p: Placement) -> int:
    """Model unrolled constrained divide stage, excluding UMUL16/range test.

    Includes scratch moves, the 16 bit stages, final quotient insertion,
    Z writeback, C normalization and RTS. Branch page-cross penalties are not
    included; benchmark.py measures those from the actual assembled layout.
    """
    product = a * b
    hi = (product >> 16) & 0xFFFF
    lo = product & 0xFFFF
    if d == 0 or hi >= d:
        raise ValueError('stage_cycles is defined only for successful bounded cases')

    # RMW zp/abs costs. A is the high remainder byte.
    cq = 5 if p.q_zp else 6
    cr = 5 if p.r_zp else 6
    cd = 3 if p.d_zp else 4
    lr = 3 if p.r_zp else 4
    sr = 3 if p.r_zp else 4

    q = lo
    r = hi
    cycles = 0

    for _ in range(16):
        incoming = (q >> 15) & 1
        q = (q << 1) & 0xFFFF
        raw = (r << 1) | incoming
        carry17 = raw >> 16
        low = raw & 0xFFFF
        base = 2 * cq + cr + 2  # ROL q0,q1,r0,A

        if carry17:
            # BCS force + TAX/LDA/SBC/STA/TXA/SBC/SEC.
            cycles += base + 3 + 2 + lr + cd + sr + 2 + cd + 2
        else:
            rh, rl = low >> 8, low & 0xFF
            dh, dl = d >> 8, d & 0xFF
            if rh < dh:
                # BCS not, CMP, BCC taken.
                cycles += base + 2 + cd + 3
            elif rh > dh:
                # BCS not, CMP, BCC not, BNE taken, subtract, BCS taken.
                cycles += base + 2 + cd + 2 + 3 + 2 + lr + cd + sr + 2 + cd + 3
            elif rl < dl:
                # Equal high byte; low-byte compare rejects subtraction.
                cycles += base + 2 + cd + 2 + 2 + lr + cd + 3
            else:
                # Equal high byte; low-byte compare accepts subtraction.
                cycles += base + 2 + cd + 2 + 2 + lr + cd + 2 + 2 + lr + cd + sr + 2 + cd + 3

        if carry17 or low >= d:
            r = raw - d
            q |= 1
        else:
            r = low

    # Final carry -> quotient bit, store A high remainder, CLC, RTS.
    cycles += 2 * cq + 4 + 2 + 6

    # Scratch setup/writeback. Each abs->zp or zp->abs byte is 4+3 cycles.
    setup = 4  # load product high into A
    if p.q_zp:
        setup += 14
    if p.r_zp:
        setup += 7
    if p.d_zp:
        setup += 14

    writeback = 0
    if p.q_zp:
        writeback += 14
    if p.r_zp:
        writeback += 7

    return cycles + setup + writeback


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=1_000_000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    stats = {p.name: [0, 0, 10**9, 0] for p in PLACEMENTS}
    ok = div0 = overflow = errors = 0

    # Structured sanity edges first.
    edges = [0, 1, 2, 0x7F, 0x80, 0xFF, 0x100, 0x7FFF, 0x8000, 0xFFFE, 0xFFFF]
    for a in edges:
        for b in edges:
            for d in edges:
                ref = reference(a, b, d)
                got = bounded_recurrence(a, b, d)
                if ref != got:
                    raise SystemExit(f'edge mismatch a={a} b={b} d={d}: {got} != {ref}')

    for _ in range(args.cases):
        a = rng.randrange(0x10000)
        b = rng.randrange(0x10000)
        d = rng.randrange(1, 0x10000)
        ref = reference(a, b, d)
        got = bounded_recurrence(a, b, d)
        if ref != got:
            errors += 1
            if errors < 5:
                print('mismatch', a, b, d, got, ref)
            continue

        if ref[0] == 'ok':
            ok += 1
            for p in PLACEMENTS:
                v = stage_cycles(a, b, d, p)
                s = stats[p.name]
                s[0] += 1
                s[1] += v
                s[2] = min(s[2], v)
                s[3] = max(s[3], v)
        elif ref[0] == 'overflow':
            overflow += 1
        else:
            div0 += 1

    print(f'cases={args.cases} seed=${args.seed:X} errors={errors}')
    print(f'bounded_ok={ok} overflow={overflow} div0={div0}')
    print()
    print('placement                     live_zp   mean_stage   min   max')
    print('----------------------------------------------------------------')
    for p in PLACEMENTS:
        count, total, mn, mx = stats[p.name]
        mean = total / count if count else float('nan')
        print(f'{p.name:29s} {p.live_zp:7d} {mean:12.3f} {mn:5d} {mx:5d}')

    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
