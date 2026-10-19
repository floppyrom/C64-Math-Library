#!/usr/bin/env python3
"""Mixed three-API relocation, public-ABI and shared-producer frame evidence."""
from __future__ import annotations
import unittest
from mixed3_frame_parity import CALLS, FRAMES, OPTIONS, compare, scenario

class MixedThreeFrameTests(unittest.TestCase):
    def test_deterministic_three_operation_corpus(self):
        rows = scenario()
        self.assertEqual(len(rows), CALLS)
        self.assertEqual(len({r[-1] for r in rows}), CALLS)
        self.assertEqual(len({r[2] for r in rows}), 3)
        self.assertEqual(FRAMES, 24)
        self.assertEqual(len(OPTIONS), 8)

    def test_complete_linked_public_calls_at_two_placements(self):
        reports = [compare(0x8000, 0xc000, 0x50),
                   compare(0x7123, 0xc040, 0x70)]
        self.assertEqual(reports[0]["input_corpus_sha256"],
                         reports[1]["input_corpus_sha256"])
        for report in reports:
            with self.subTest(code=report["code"]):
                self.assertTrue(report["cpu_model_only"])
                self.assertFalse(report["native_pal_timing"])
                self.assertEqual(report["zp_base"], "$%04X" %
                                 (0x50 if report["code"] == "$8000" else 0x70))
                self.assertEqual(report["scratch_base"], "$%04X" %
                                 (int(report["io"][1:], 16) + 0x40))
                self.assertEqual(report["paired_calls"], 150)
                self.assertEqual(report["frames"], 24)
                self.assertEqual(set(report["per_option"]), set(OPTIONS))
                for name, data in report["per_option"].items():
                    self.assertEqual(data["variant_map"], OPTIONS[name])
                    self.assertEqual(set(data["source_sha256"]),
                        {"MATH_UMUL32", "MATH_SMUL32", "MATH_ISQRT16"})
                    self.assertEqual(len(data["linked_prg_sha256"]), 64)
                    self.assertEqual(len(data["per_operation"]), 3)
                    self.assertGreater(data["main_ram_total_bytes"], 0)
                    self.assertGreater(data["peak_frame_math_cycles"], 0)
                    self.assertLessEqual(data["p95_frame_math_cycles"],
                                         data["peak_frame_math_cycles"])
                self.assertEqual(
                    report["per_option"]["fast31-shared+table"]["linked_source_count"], 2)
                self.assertEqual(
                    report["per_option"]["fast31-independent+table"]["linked_source_count"], 3)
                self.assertLess(
                    report["per_option"]["fast31-shared+table"]["main_ram_total_bytes"],
                    report["per_option"]["fast31-independent+table"]["main_ram_total_bytes"])
                self.assertLess(
                    report["per_option"]["unified375+tableless"]["main_ram_total_bytes"],
                    report["per_option"]["unified375+table"]["main_ram_total_bytes"])

if __name__ == "__main__":
    unittest.main()
