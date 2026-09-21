"""Full signed-Q8.8 domain model for the normalizer's byte reduction.

The sign paths use one's-complement magnitudes. For vectors whose magnitudes
are both below 256, negative magnitudes are incremented, saturating at 255.
Both magnitudes are then shifted together until the major byte is 128..255.
Enumerating the endpoints of each reduction cell covers every signed 16-bit
input, including -32768, without sampling all 2**32 vectors.
"""
from __future__ import annotations

import math


def ceildiv(a, b):
    return -((-a) // b)


def cell_range(shift, mantissa):
    scale = 1 << shift
    return max(0, ceildiv(mantissa * 256, scale)), min(32767, ((mantissa + 1) * 256 - 1) // scale)


def major_range(shift, mantissa):
    lo, hi = cell_range(shift, mantissa)
    return max(lo, ceildiv(32768, 1 << shift)), min(hi, 65535 // (1 << shift))


def ratio_bounds(a0, a1, b0, b1, da, db):
    if b0 > a1:
        return None
    low = (b0 + db) / (a1 + da)
    maxima = []
    if b1 < a0:
        maxima.append((b1 + db) / (a0 + da))
    else:
        first, last = max(a0, b0), min(a1, b1)
        if first <= last:
            maxima.extend(((first + db) / (first + da), (last + db) / (last + da)))
        if b1 <= a1:
            maxima.append((b1 + db) / (max(a0, b1) + da))
    if not maxima:
        return None
    high = max(maxima)
    return min(low, high), max(low, high)


def reduced_cells():
    """Yield (major byte, minor byte, minimum angle, maximum angle)."""
    for major in range(128, 256):
        for minor in range(major + 1):
            ranges = []
            for shift in range(1, 8):
                a0, a1 = major_range(shift, major)
                b0, b1 = cell_range(shift, minor)
                if a0 > a1 or b0 > b1 or b0 > a1:
                    continue
                for da in (0, 1):
                    for db in (0, 1):
                        ranges.append((a0, a1, b0, b1, da, db))
            for shift in range(8, 16):
                a0, a1 = major_range(shift, major)
                b0, b1 = cell_range(shift, minor)
                a0, a1, b0, b1 = max(a0, 1), min(a1, 255), max(b0, 0), min(b1, 255)
                if a0 > a1 or b0 > b1 or b0 > a1:
                    continue
                ranges.append((a0, a1, b0, b1, 0, 0))
                if a0 <= 255 <= a1:
                    ranges.append((255, 255, b0, min(b1, 255), 1, 0))
                if b0 <= 255 <= b1 and a1 >= 255:
                    ranges.append((max(a0, 255), a1, 255, 255, 0, 1))
                if a0 <= 255 <= a1 and b0 <= 255 <= b1:
                    ranges.append((255, 255, 255, 255, 1, 1))
            for args in ranges:
                bounds = ratio_bounds(*args)
                if bounds is not None:
                    yield major, minor, math.degrees(math.atan(bounds[0])), math.degrees(math.atan(bounds[1]))


def reduce_vector(x, y):
    ax, ay = (x if x >= 0 else ~x), (y if y >= 0 else ~y)
    if ax < 256 and ay < 256:
        if x < 0:
            ax = min(255, ax + 1)
        if y < 0:
            ay = min(255, ay + 1)
    if not (ax or ay):
        return None
    x_major = ax >= ay
    major, minor = (ax, ay) if x_major else (ay, ax)
    shift = 16 - major.bit_length()
    return x_major, (major << shift) >> 8, (minor << shift) >> 8


def normalized_reference(x, y, design, backend="log"):
    reduced = reduce_vector(x, y)
    if reduced is None:
        return 0, 0
    x_major, major, minor = reduced
    if backend == "log":
        index = design["zero_index"] if not minor else design["indices"][design["logs"][major] - design["logs"][minor]]
    else:
        index = (1 + minor + ((minor * design["recip"][major - 128]) >> 8)) & 255
    a, b = design["comps"][index]
    ox, oy = (a, b) if x_major else (b, a)
    return (-ox if x < 0 else ox), (-oy if y < 0 else oy)
