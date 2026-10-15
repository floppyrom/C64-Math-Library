#!/usr/bin/env python3
"""Issue #144 B: mathematically exact radix-256 32/16 quotient-digit trial.

Source-independent arithmetic experiment only. It DOES NOT measure real 6510
cycles or install an implementation. Target is a future generalized producer
with fewer than sixteen low-word restoring-bit iterations.

For each 8-bit quotient digit, normalize the divisor to $8000..$FFFF,
estimate using the leading byte, and correct the remainder exactly.
- Exact 16/8 trial: qhat=min(255, Rnorm//(Dnorm>>8)); <=2 corrections.
- Reciprocal seed: qhat=min(255,(Rnorm*ceil(65536/v))>>16);
  v=Dnorm>>8; <=3 corrections. This is a mathematical model, NOT a
  claimed fast 6502 reciprocal/multiply implementation.
"""
from __future__ import annotations
import collections
import hashlib
import json
import random
import sys


def trial_digit(remainder: int, next_byte: int, dnorm: int, method: str):
    assert 0 <= remainder < dnorm and 0 <= next_byte <= 255
    assert 32768 <= dnorm <= 65535
    v = dnorm >> 8
    if method == "exact_highbyte":
        q = min(255, remainder // v)
        cap = 2
    elif method == "reciprocal_seed":
        inv = (65536 + v - 1) // v
        q = min(255, (remainder * inv) >> 16)
        cap = 3
    else:
        raise ValueError(method)
    t = (remainder << 8) | next_byte
    rem = t - q * dnorm
    fixups = 0
    while rem < 0:
        q -= 1
        rem += dnorm
        fixups += 1
        if fixups > cap:
            raise AssertionError(("upper correction bound", method, remainder,
                                  next_byte, dnorm, fixups))
    assert 0 <= rem < dnorm
    assert (q, rem) == divmod(t, dnorm)
    return q, rem, fixups


def udiv32_16(n: int, d: int, method: str):
    assert 0 <= n <= 0xffffffff and 0 <= d <= 0xffff
    if not d:
        return 0, 0, 1, (0, 0), 0
    highword, lowword = n >> 16, n & 65535
    high_q, r = divmod(highword, d)
    s = 16 - d.bit_length()
    dnorm = d << s
    shifted_low = lowword << s
    rnorm = (r << s) + (shifted_low >> 16)
    assert 0 <= rnorm < dnorm
    feed = shifted_low & 65535
    qhi, rnorm, c1 = trial_digit(rnorm, feed >> 8, dnorm, method)
    qlo, rnorm, c0 = trial_digit(rnorm, feed & 255, dnorm, method)
    assert rnorm % (1 << s) == 0
    q = (high_q << 16) | (qhi << 8) | qlo
    return q, rnorm >> s, 0, (c1, c0), s


def samples():
    # Complete D16 coverage with boundary numerators, followed by an
    # independent uniform broad-width corpus.
    for d in range(65536):
        for n in (0, 1, max(0, d - 1), d, min(0xffffffff, d + 1),
                  0x0000ffff, 0x00010000, 0x7fffffff,
                  0x80000000, 0xffffffff):
            yield n, d
    r = random.Random(0x144D256)
    for _ in range(500000):
        yield r.getrandbits(32), r.getrandbits(16)


def main():
    counters = {method: collections.Counter() for method in
                ("exact_highbyte", "reciprocal_seed")}
    shift_classes = collections.Counter()
    digest = hashlib.sha256()
    count = 0
    zero = 0
    for n, d in samples():
        digest.update(n.to_bytes(4, "little") + d.to_bytes(2, "little"))
        expected = ((n // d, n % d, 0) if d else (0, 0, 1))
        for method in counters:
            q, r, c, corrections, shift = udiv32_16(n, d, method)
            assert (q, r, c) == expected, (hex(n), hex(d), method,
                                           (q, r, c), expected)
            if d:
                counters[method].update(corrections)
                assert max(corrections) <= (2 if method == "exact_highbyte" else 3)
        if d:
            shift_classes[16 - d.bit_length()] += 1
        else:
            zero += 1
        count += 1
    assert count == 65536*10+500000
    summary = {
        "status": "PASS_NUMERICAL_SOURCE_INDEPENDENT",
        "date": "2026-10-15",
        "scope": "full unsigned N32,D16 arithmetic; not assembled C64 code",
        "total_input_pairs": count,
        "divisor_zero_pairs": zero,
        "operand_sha256": digest.hexdigest(),
        "corrections_per_quotient_digit": {
            method: {str(k): v for k, v in sorted(counter.items())}
            for method, counter in counters.items()
        },
        "max_corrections": {method: max(counter) for method,counter in counters.items()},
        "divisor_normalization_shifts": {
            str(s): v for s, v in sorted(shift_classes.items())
        },
        "still_unproven": [
            "fast exact 6510 quotient-estimator producer",
            "normal public ABI, MATH_INIT/zero-divisor and mixed-call safety",
            "physical code/ZP/table footprint and placement",
            "identical-input public-call cycle advantage over current fast core",
            "native VICE equivalence and independent package release"
        ],
        "default_public_divider_changed": False,
        "private_optisearch_code_published": False
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
