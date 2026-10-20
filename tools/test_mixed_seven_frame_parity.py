#!/usr/bin/env python3
"""Real source-linked mixed seven-API frame and resource qualification."""
from __future__ import annotations
import unittest
from mixed_seven_frame_parity import (
    BASIS, OPS, OPTIONS, CALLS, FRAMES, scenario, compare,
)
from mixed_frame_frontier import summarize
from mul32_frame_frontier import frontier, select


class MixedSevenFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = {
            "basis": BASIS, "operations": list(OPS),
            "placements": [compare(0x2000, 0xc000, 0x50),
                           compare(0x4123, 0xc040, 0x70)],
        }

    def test_complete_deterministic_workload_and_all_seven_apis(self):
        calls = scenario()
        self.assertEqual(len(calls), 150)
        self.assertEqual(len({c[-1] for c in calls}), 150)
        self.assertEqual({c[2] for c in calls}, set(OPS))
        self.assertEqual(len(OPS), 7)
        self.assertEqual(FRAMES, 24)
        self.assertEqual(CALLS, 150)

    def test_identical_source_linked_evidence_at_two_relocations(self):
        a, b = self.report["placements"]
        self.assertEqual(a["input_corpus_sha256"], b["input_corpus_sha256"])
        for place in self.report["placements"]:
            with self.subTest(origin=place["code"]):
                self.assertEqual(place["paired_calls"], CALLS)
                self.assertEqual(place["frames"], FRAMES)
                self.assertTrue(place["cpu_model_only"])
                self.assertFalse(place["native_pal_timing"])
                self.assertEqual(set(place["per_option"]), set(OPTIONS))
                for name, item in place["per_option"].items():
                    with self.subTest(candidate=name):
                        self.assertEqual(item["variant_map"], OPTIONS[name])
                        self.assertEqual(set(item["source_sha256"]), set(OPS))
                        self.assertGreater(item["linked_source_count"], 0)
                        self.assertEqual(len(item["linked_prg_sha256"]), 64)
                        self.assertGreater(item["main_ram_total_bytes"], 0)
                        self.assertGreater(item["peak_frame_math_cycles"], 0)
                        self.assertLessEqual(item["p95_frame_math_cycles"],
                                             item["peak_frame_math_cycles"])
                        self.assertEqual(len(item["per_operation"]), 7)
                        self.assertEqual(sum(op["calls"] for op in item["per_operation"]), CALLS)
                self.assertEqual(
                    place["per_option"]["compact-everywhere"]["zero_page_bytes"], 0)

    def test_whole_project_frontier_respects_actual_shared_ram_zp(self):
        report = summarize(self.report)
        self.assertFalse(report["physical_pal_feasibility_claim"])
        self.assertEqual(report["operations"], list(OPS))
        self.assertGreaterEqual(len(frontier(report)), 1)
        fast = select(report, ram_budget=16000, zp_budget=64, objective="peak")
        small = select(report, ram_budget=16000, zp_budget=0, objective="ram")
        self.assertIn(fast["choice"], OPTIONS)
        self.assertEqual(small["choice"], "compact-everywhere")
        self.assertEqual(small["measured_envelope"]["zero_page_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
