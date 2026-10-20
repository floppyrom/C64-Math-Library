#!/usr/bin/env python3
"""Tests for exhaustive crossed choices within a 7-API candidate family."""
from __future__ import annotations

import unittest

import mixed_seven_frame_parity as seven
from mixed_frame_frontier import summarize
from mul32_frame_frontier import frontier, select
from mixed_seven_cross_pareto import BASELINE_MAP, LOCATIONS, OPS, options, complete_report


class SevenWayCrossFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.options = options()
        cls.report = complete_report()

    def test_unique_source_complete_candidate_enumeration(self):
        self.assertEqual(len(self.options), 16)
        self.assertEqual(len({tuple(x.items()) for x in self.options.values()}), 16)
        self.assertEqual(len(OPS), 7)
        for name, selected in self.options.items():
            with self.subTest(name=name):
                self.assertEqual(set(selected), set(OPS))
                self.assertEqual(selected["MATH_UDIV32_32"],
                                 selected["MATH_UMOD32_32"])
                self.assertEqual(selected["MATH_SDIV32_32"],
                                 selected["MATH_SMOD32_32"])

    def test_old_four_provenance_and_entire_source_pins_retained(self):
        for old, new in BASELINE_MAP.items():
            with self.subTest(option=old):
                self.assertEqual(self.options[new], seven.OPTIONS[old])
        self.assertEqual(len(self.report["placements"]), 2)
        for place in self.report["placements"]:
            self.assertEqual(place["frames"], 24)
            self.assertEqual(place["paired_calls"], 150)
            self.assertTrue(place["cpu_model_only"])
            self.assertFalse(place["native_pal_timing"])
            self.assertEqual(set(place["per_option"]), set(self.options))
            for name, row in place["per_option"].items():
                self.assertEqual(row["variant_map"], self.options[name])
                self.assertEqual(set(row["source_sha256"]), set(OPS))
                self.assertEqual(len(row["linked_prg_sha256"]), 64)
                self.assertGreater(row["main_ram_total_bytes"], 0)
                self.assertGreater(row["peak_frame_math_cycles"], 0)
                self.assertLessEqual(row["p95_frame_math_cycles"],
                                     row["peak_frame_math_cycles"])
                self.assertEqual(sum(item["calls"] for item in row["per_operation"]), 150)

    def test_all_sixteen_use_same_public_input_and_physical_geometry(self):
        a, b = self.report["placements"]
        self.assertEqual(a["input_corpus_sha256"], b["input_corpus_sha256"])
        self.assertEqual(self.report["candidate_count"], 16)
        self.assertFalse(self.report["physical_pal_frame_qualified"])
        self.assertEqual(a["code"], "$%04X" % LOCATIONS[0][0])
        self.assertEqual(b["code"], "$%04X" % LOCATIONS[1][0])
        for name in self.options:
            with self.subTest(name=name):
                self.assertEqual(a["per_option"][name]["source_sha256"],
                                 b["per_option"][name]["source_sha256"])
                self.assertEqual(a["per_option"][name]["zero_page_bytes"],
                                 b["per_option"][name]["zero_page_bytes"])

    def test_full_linked_image_frontier_is_at_least_as_good_as_old_extremes(self):
        summary = summarize(self.report)
        self.assertEqual(summary["operations"], list(OPS))
        self.assertEqual(len(summary["per_option"]), 16)
        self.assertGreaterEqual(len(frontier(summary)), 1)
        for zp in (0, 31, 64):
            with self.subTest(zp=zp):
                selection = select(summary, 16000, zp, objective="peak")
                self.assertIn(selection["choice"], self.options)
                self.assertLessEqual(selection["measured_envelope"]["zero_page_bytes"], zp)
        # The old four candidates remain available in the extended set:
        old = min(summary["per_option"][name]["peak_frame_math_cycles"]
                  for name in BASELINE_MAP.values())
        best = select(summary, 16000, 64, objective="peak")
        self.assertLessEqual(best["measured_envelope"]["peak_frame_math_cycles"], old)


if __name__ == "__main__":
    unittest.main()
