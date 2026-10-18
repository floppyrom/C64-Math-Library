#!/usr/bin/env python3
"""Lock the biased quarter-square and carry-neutral row identities.

Independent Python arithmetic invariants only: not a native timing,
source-assembled 6502 ABI or performance certification.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "mul_u16_u16_u32_shifted99.asm",
    "mul_u16_u16_u32_shifted106.asm",
    "mul_u16_u16_u32_shifted116.asm",
    "mul_u16_u16_u32_shifted134.asm",
)
BIAS = 0xCA


def biased_square(n: int) -> int:
    if not 0 <= n <= 510:
        raise ValueError("square-table index outside 8-bit input sum")
    return (n * n) // 4 + BIAS * (n & 1)


class BiasedQuarterSquareOffsets(unittest.TestCase):
    def test_all_byte_products_are_exact(self):
        for a in range(256):
            for b in range(256):
                result = biased_square(a + b) - biased_square(abs(a - b))
                self.assertEqual(result, a * b, (a, b))

    def test_low_byte_plus_one_has_no_carry(self):
        for n in range(511):
            q = biased_square(n)
            self.assertNotEqual(q & 255, 255, n)
            # Low+1 table uses the original high plane.
            self.assertEqual((q + 1) >> 8, q >> 8, n)
            # High+1 represents exactly a +256 partial offset.
            self.assertEqual((q + 256) >> 8, (q >> 8) + 1, n)

    def test_adjacent_partial_biases_cancel(self):
        # The identity holds algebraically over the full word domain.
        for x in (0, 1, 255, 256, 257, 0x7fff, 0xffff):
            for b in (0, 1, 2, 127, 128, 254, 255):
                x0, x1 = x & 255, x >> 8
                partial0 = x0 * b + 256
                partial1 = x1 * b - 1
                self.assertEqual(partial0 + 256 * partial1, x * b)

    def test_historical_sources_preserve_offset_contract(self):
        source_dir = ROOT / "routines" / "multiply"
        for name in FILES:
            with self.subTest(source=name):
                text = (source_dir / name).read_text(encoding="utf-8")
                match = re.search(r"(?m)^PARITY_BIAS\s*=\s*\$([0-9a-fA-F]+)\s*$", text)
                self.assertIsNotNone(match, name)
                self.assertEqual(int(match.group(1), 16), BIAS)
                for marker in (
                    "sqr_lo:", "sqr_hi:", "neg_sqr_lo:",
                    "neg_sqr_hi:", "sqr_hi_plus1:",
                    "neg_sqr_lo_plus1:",
                ):
                    self.assertIn(marker, text)
                self.assertIn("PARITY_BIAS*(i&1)", text)


if __name__ == "__main__":
    unittest.main()
