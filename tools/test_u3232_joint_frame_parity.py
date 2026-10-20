#!/usr/bin/env python3
"""Full linked public UDIV/UMOD 32/32 matched synthetic frame and Pareto tests."""
from __future__ import annotations

import unittest

from mixed_frame_frontier import summarize
from mul32_frame_frontier import frontier, select
from u3232_joint_frame_parity import BASIS, CALLS, FRAMES, OPS, OPTIONS, compare, scenario


class U3232FrameResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = {"basis": BASIS, "operations": list(OPS),
                      "placements": [compare(0x8000, 0xc000, 0x50),
                                     compare(0x7123, 0xc040, 0x70)]}

    def test_divisor_edges_and_deterministic_public_call_history(self):
        calls = scenario()
        self.assertEqual(len(calls), CALLS)
        self.assertEqual(FRAMES, 24)
        self.assertEqual(len(set(x[-1] for x in calls)), CALLS)
        self.assertEqual({x[2] for x in calls}, set(OPS))
        self.assertGreaterEqual(sum(x[4] == 0 for x in calls), 1)
        self.assertGreaterEqual(sum(x[4] > 65535 for x in calls), 1)

    def test_all_linked_pairs_relocated_and_source_authenticated(self):
        p0, p1 = self.report["placements"]
        self.assertEqual(p0["input_corpus_sha256"], p1["input_corpus_sha256"])
        for placement in self.report["placements"]:
            with self.subTest(origin=placement["code"]):
                self.assertEqual(placement["frames"], 24)
                self.assertEqual(placement["paired_calls"], 150)
                self.assertEqual(set(placement["per_option"]), set(OPTIONS))
                self.assertTrue(placement["cpu_model_only"])
                self.assertFalse(placement["native_pal_timing"])
                for label, item in placement["per_option"].items():
                    with self.subTest(label=label):
                        self.assertEqual(item["variant_map"], OPTIONS[label])
                        self.assertEqual(set(item["source_sha256"]), set(OPS))
                        self.assertEqual(len(item["linked_prg_sha256"]), 64)
                        self.assertGreater(item["main_ram_total_bytes"], 0)
                        self.assertGreater(item["peak_frame_math_cycles"], 0)
                        self.assertLessEqual(item["p95_frame_math_cycles"],
                                             item["peak_frame_math_cycles"])
                        self.assertEqual(len(item["per_operation"]), 2)
                        self.assertEqual(sum(op["calls"] for op in item["per_operation"]), 150)
                self.assertEqual(
                    placement["per_option"]["aligned-shared-zerozp"]["linked_source_count"], 1)
                self.assertEqual(
                    placement["per_option"]["v2-lowdivisor-shared"]["linked_source_count"], 1)
                self.assertEqual(
                    placement["per_option"]["aligned-independent-zerozp"]["linked_source_count"], 2)
                self.assertLess(
                    placement["per_option"]["aligned-shared-zerozp"]["main_ram_total_bytes"],
                    placement["per_option"]["aligned-independent-zerozp"]["main_ram_total_bytes"])
                self.assertEqual(
                    placement["per_option"]["aligned-shared-zerozp"]["zero_page_bytes"], 0)
                self.assertEqual(
                    placement["per_option"]["v2-lowdivisor-shared"]["zero_page_bytes"], 12)

    def test_complete_image_frontier_uses_real_peak_frame_costs(self):
        result = summarize(self.report)
        self.assertEqual(result["paired_calls"], CALLS)
        self.assertEqual(result["frames"], FRAMES)
        self.assertEqual(result["operations"], list(OPS))
        self.assertFalse(result["physical_pal_feasibility_claim"])
        front = frontier(result)
        self.assertGreaterEqual(len(front), 1)
        self.assertTrue(set(front).issubset(set(OPTIONS)))
        chosen = select(result, 12000, 12, objective="peak")
        self.assertIn(chosen["choice"], OPTIONS)
        self.assertLessEqual(chosen["measured_envelope"]["main_ram_total_bytes"], 12000)
        self.assertLessEqual(chosen["measured_envelope"]["zero_page_bytes"], 12)
        lowzp = select(result, 12000, 0, objective="ram")
        self.assertEqual(lowzp["measured_envelope"]["zero_page_bytes"], 0)
        self.assertNotEqual(lowzp["choice"], "v2-lowdivisor-shared")


if __name__ == "__main__":
    unittest.main()
