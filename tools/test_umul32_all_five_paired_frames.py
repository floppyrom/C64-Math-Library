#!/usr/bin/env python3
"""Five-source UMUL32 same-call busiest-frame comparison at two placements."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from umul32_all_five_paired_frames import (
    API, CALL_COUNT, FRAMES, VARIANTS, compare, evaluate, scenario,
)


class UMUL32FiveWayFrameTests(unittest.TestCase):
    def test_shared_identical_150_complete_public_calls_two_maps(self):
        for code, io in ((0x8000, 0xc000), (0x7123, 0xc040)):
            with self.subTest(code=code):
                result = compare(code, io, 0x70 if code == 0x7123 else 0x50)
                self.assertEqual(result["paired_calls"], CALL_COUNT)
                self.assertEqual(result["frames"], FRAMES)
                self.assertEqual(set(result["per_variant"]), set(VARIANTS))
                compact = result["per_variant"]["link:compact-zerozp"]
                self.assertEqual(compact["zero_page_bytes"], 0)
                for name, candidate in result["per_variant"].items():
                    self.assertGreater(candidate["mean_public_cycles"], 0)
                    self.assertGreater(candidate["peak_frame_math_cycles"], 0)
                    self.assertGreater(candidate["p95_frame_math_cycles"], 0)
                    self.assertGreater(candidate["source_sha256"], "")
                    self.assertEqual(len(candidate["linked_prg_sha256"]), 64)
                    self.assertGreaterEqual(candidate["main_ram_total_bytes"],
                                            candidate["code_span_bytes"])
                print("UMUL32_ALL_FIVE_SAME_INPUT_FRAME",
                      json.dumps(result, sort_keys=True), flush=True)

    def test_reject_unqualified_variants_and_identical_scenario(self):
        self.assertEqual(len(scenario()), 150)
        self.assertEqual(len(set(row[-1] for row in scenario())), 150)
        with self.assertRaises(ValueError):
            evaluate("link:imaginary-portable-kernel")
        for variant in VARIANTS:
            self.assertTrue(variant.startswith("link:"))


if __name__ == "__main__":
    unittest.main()
