#!/usr/bin/env python3
"""Four-operation whole-image signed + unsigned public DIV/MOD frame evidence."""
import unittest

from mixed_frame_frontier import summarize
from mul32_frame_frontier import frontier, select
from mixed_four_divmod_frame_parity import BASIS, OPS, OPTIONS, FRAMES, CALLS, scenario, compare


class MixedFourDivModFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = {"basis": BASIS, "operations": list(OPS),
                      "placements": [compare(0x8000, 0xc000, 0x50),
                                     compare(0x7123, 0xc040, 0x70)]}

    def test_deterministic_four_way_workload(self):
        rows = scenario()
        self.assertEqual(len(rows), CALLS)
        self.assertEqual(len({r[-1] for r in rows}), CALLS)
        self.assertEqual({r[2] for r in rows}, set(OPS))
        self.assertTrue(any(r[4] == 0 for r in rows))
        self.assertTrue(any(r[3] & 0x80000000 and r[2] in OPS[2:] for r in rows))
        self.assertTrue(any(r[4] & 0x80000000 and r[2] in OPS[2:] for r in rows))

    def test_qualified_complete_public_source_images(self):
        loc0, loc1 = self.report["placements"]
        self.assertEqual(loc0["input_corpus_sha256"], loc1["input_corpus_sha256"])
        for location in self.report["placements"]:
            with self.subTest(origin=location["code"]):
                self.assertTrue(location["cpu_model_only"])
                self.assertFalse(location["native_pal_timing"])
                self.assertEqual(location["frames"], FRAMES)
                self.assertEqual(location["paired_calls"], CALLS)
                self.assertEqual(set(location["per_option"]), set(OPTIONS))
                for label, item in location["per_option"].items():
                    self.assertEqual(item["variant_map"], OPTIONS[label])
                    self.assertEqual(set(item["source_sha256"]), set(OPS))
                    self.assertEqual(item["linked_source_count"], 2)
                    self.assertEqual(len(item["linked_prg_sha256"]), 64)
                    self.assertGreater(item["main_ram_total_bytes"], 0)
                    self.assertGreater(item["peak_frame_math_cycles"], 0)
                    self.assertLessEqual(item["p95_frame_math_cycles"],
                                         item["peak_frame_math_cycles"])
                    self.assertEqual(sum(x["calls"] for x in item["per_operation"]), CALLS)
                self.assertEqual(location["per_option"]["both-compact-zerozp"]["zero_page_bytes"], 0)
                self.assertEqual(location["per_option"]["both-v2-hybrid"]["zero_page_bytes"], 12)

    def test_measured_four_operation_pareto(self):
        summary = summarize(self.report)
        self.assertEqual(summary["operations"], list(OPS))
        self.assertEqual(summary["frames"], FRAMES)
        self.assertFalse(summary["physical_pal_feasibility_claim"])
        self.assertGreaterEqual(len(frontier(summary)), 1)
        best = select(summary, 12000, 31, objective="peak")
        self.assertIn(best["choice"], OPTIONS)
        lowzp = select(summary, 12000, 0, objective="ram")
        self.assertEqual(lowzp["choice"], "both-compact-zerozp")
        self.assertEqual(lowzp["measured_envelope"]["zero_page_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
