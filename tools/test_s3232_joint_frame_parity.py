#!/usr/bin/env python3
"""Signed 32/32 shared full-public Q/R/C synthetic frame source qualification."""
import unittest
from mixed_frame_frontier import summarize
from mul32_frame_frontier import frontier, select
from s3232_joint_frame_parity import OPS, OPTIONS, FRAMES, CALLS, BASIS, scenario, compare


class S3232FrameEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = {"basis": BASIS, "operations": list(OPS),
                      "placements": [compare(0x8000, 0xc000, 0x50),
                                     compare(0x7123, 0xc040, 0x70)]}

    def test_true_signed_negatives_and_divisor_zero_in_identical_frames(self):
        calls = scenario()
        self.assertEqual(len(calls), CALLS)
        self.assertEqual(len({c[-1] for c in calls}), CALLS)
        self.assertEqual({c[2] for c in calls}, set(OPS))
        self.assertTrue(any(d == 0 for _, _, _, n, d, *_ in calls))
        self.assertTrue(any(n & 0x80000000 for _, _, _, n, d, *_ in calls))
        self.assertTrue(any(d & 0x80000000 for _, _, _, n, d, *_ in calls))

    def test_source_linked_abi_relocation_and_shared_producer(self):
        a, b = self.report["placements"]
        self.assertEqual(a["input_corpus_sha256"], b["input_corpus_sha256"])
        for location in self.report["placements"]:
            with self.subTest(location=location["code"]):
                self.assertEqual(location["frames"], FRAMES)
                self.assertEqual(location["paired_calls"], CALLS)
                self.assertEqual(set(location["per_option"]), set(OPTIONS))
                self.assertTrue(location["cpu_model_only"])
                self.assertFalse(location["native_pal_timing"])
                for name, row in location["per_option"].items():
                    self.assertEqual(row["variant_map"], OPTIONS[name])
                    self.assertEqual(set(row["source_sha256"]), set(OPS))
                    self.assertEqual(row["linked_source_count"], 1)
                    self.assertEqual(len(row["linked_prg_sha256"]), 64)
                    self.assertGreater(row["peak_frame_math_cycles"], 0)
                    self.assertLessEqual(row["p95_frame_math_cycles"], row["peak_frame_math_cycles"])
                    self.assertEqual(sum(x["calls"] for x in row["per_operation"]), CALLS)
                self.assertEqual(location["per_option"]["signed-portable-shared-zerozp"]["zero_page_bytes"], 0)
                self.assertEqual(location["per_option"]["signed-v2-hybrid-shared"]["zero_page_bytes"], 12)
                self.assertLess(
                    location["per_option"]["signed-portable-shared-zerozp"]["main_ram_total_bytes"],
                    location["per_option"]["signed-v2-hybrid-shared"]["main_ram_total_bytes"])

    def test_measured_full_image_pareto_and_no_zp_selection(self):
        summary = summarize(self.report)
        self.assertEqual(summary["operations"], list(OPS))
        self.assertFalse(summary["physical_pal_feasibility_claim"])
        self.assertGreaterEqual(len(frontier(summary)), 1)
        best = select(summary, 12000, 12, objective="peak")
        self.assertIn(best["choice"], OPTIONS)
        small = select(summary, 12000, 0, objective="ram")
        self.assertEqual(small["choice"], "signed-portable-shared-zerozp")
        self.assertEqual(small["measured_envelope"]["zero_page_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
