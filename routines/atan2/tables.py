#!/usr/bin/env python3
"""Shared table generator and exact reference helpers for the ATAN2 kernels."""
from __future__ import annotations

import collections
import math

LOG_SCALE = 11.63
LOG_OFFSET = 82


def signed8(v: int) -> int:
    return v if v < 128 else v - 256


def exact_phase(x: int, y: int) -> int:
    if x == 0 and y == 0:
        return 0
    return round((math.atan2(y, x) % (2 * math.pi)) * 128 / math.pi) & 255


def phase_error(a: int, b: int) -> int:
    return min((a - b) & 255, (b - a) & 255)


def build_tables():
    """Return LOG, compact Q0, fast Q0/Q1/Q2/Q3, quantizer and max class span.

    The return shape intentionally matches the historical upgrade tool so the
    installed profile images remain byte-identical after the source cleanup.
    """
    q = [0] + [math.floor(LOG_SCALE * math.log2(m)) for m in range(1, 129)]
    if max(q[1:]) - min(q[1:]) != 81:
        raise RuntimeError('unexpected log quantizer span')

    log = [0] * 256
    for raw in range(256):
        m = abs(signed8(raw))
        log[raw] = 0 if m == 0 else LOG_OFFSET + q[m]

    groups = collections.defaultdict(list)
    for x in range(1, 129):
        for y in range(1, 129):
            idx = (q[x] - q[y]) & 255
            groups[idx].append(round(math.atan2(y, x) * 128 / math.pi))

    base = [0] * 256
    max_span = 0
    for idx, vals in groups.items():
        lo, hi = min(vals), max(vals)
        max_span = max(max_span, hi - lo)
        base[idx] = (lo + hi) // 2
    if max_span > 2:
        raise RuntimeError(f'quantizer angle class span {max_span} > 2')

    # y=0 is nonnegative and reaches Q0/Q1. Its log-difference indices occupy
    # $52-$A3, outside finite difference ranges $00-$51/$AF-$FF.
    for m in range(1, 129):
        base[LOG_OFFSET + q[m]] = 0

    q0 = list(base)
    q1 = [(128 - v) & 255 for v in base]
    q2 = [(128 + v) & 255 for v in base]
    q3 = [(-v) & 255 for v in base]
    for m in range(1, 129):
        idx = LOG_OFFSET + q[m]
        q0[idx] = 0
        q1[idx] = 128

    return (
        bytes(log), bytes(base), bytes(q0), bytes(q1), bytes(q2), bytes(q3),
        q, max_span,
    )
