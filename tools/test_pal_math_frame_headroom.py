#!/usr/bin/env python3
"""Resource and capacity tests of the PAL math-only necessary preflight."""
from __future__ import annotations

import unittest

from mixed_frame_frontier import summarize
from mixed_seven_cross_pareto import complete_report
from pal_math_frame_headroom import PAL_FRAME_SLOTS, model_headroom


class PalMathFrameHeadroomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Exact physical linked sources and identical 150-call history at two maps.
        cls.report = complete_report()
        cls.summary = summarize(cls.report)

    def test_real_sixteen_way_measured_pal_bound(self):
        result = model_headroom(self.summary)
        self.assertEqual(PAL_FRAME_SLOTS, 19656)
        self.assertEqual(result["eligible_plans"], 16)
        self.assertEqual(result["plans_with_nonnegative_model_headroom"], 1)
        self.assertEqual(result["plans_exceeding_nominal_math_budget"], 15)
        winner = result["plans"][0]
        self.assertEqual(winner["choice"], "mul-fast31+sqrt-table+udiv-v2+sdiv-v2")
        self.assertEqual(winner["measured_peak_math_cycles"], 16172)
        self.assertEqual(winner["nominal_slots_left_after_math_and_reserve"], 3484)
        self.assertFalse(result["physical_pal_timing_certified"])
        self.assertTrue(all("PAL-unverified" in p["classification"]
                            for p in result["plans"] if p["nominal_slots_left_after_math_and_reserve"] >= 0))

    def test_reserve_and_resource_budgets_cannot_invent_headroom(self):
        reserved = model_headroom(self.summary, reserve_cycles=3500)
        self.assertEqual(reserved["plans_with_nonnegative_model_headroom"], 0)
        self.assertEqual(reserved["plans_exceeding_nominal_math_budget"], 16)
        no_zp = model_headroom(self.summary, ram_budget=16000, zp_budget=0)
        self.assertEqual(no_zp["eligible_plans"], 2)
        self.assertEqual(no_zp["plans_with_nonnegative_model_headroom"], 0)
        enough_zp = model_headroom(self.summary, ram_budget=9000, zp_budget=31)
        self.assertEqual(enough_zp["plans_with_nonnegative_model_headroom"], 1)
        self.assertEqual(enough_zp["eligible_plans"], 16)

    def test_reject_invalid_reserve_budgets_and_unqualified_basis(self):
        for invalid in (True, -1, 19656, 19657, 3.5, "100"):
            with self.subTest(reserve=invalid), self.assertRaises(ValueError):
                model_headroom(self.summary, reserve_cycles=invalid)
        with self.assertRaises(ValueError):
            model_headroom(self.summary, ram_budget=4000)
        with self.assertRaises(ValueError):
            model_headroom(self.summary, ram_budget=4000, zp_budget=-1)
        with self.assertRaises(ValueError):
            model_headroom({**self.summary, "physical_pal_feasibility_claim": True})


if __name__ == "__main__":
    unittest.main()
