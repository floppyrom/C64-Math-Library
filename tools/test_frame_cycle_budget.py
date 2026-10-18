#!/usr/bin/env python3
"""Frame trace comparison and strict benchmark-compatibility regression tests."""
import csv
import tempfile
import unittest
from pathlib import Path

from frame_cycle_budget import COLUMNS, analyze, load_trace, score


class FrameBudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def trace(self, name, rows, basis="cpu-model-public-entry-through-rts",
              placement="$8000/$C000"):
        path = self.root / name
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()
            for frame, ordinal, op, input_id, cycles, variant in rows:
                writer.writerow({"frame": frame, "call": ordinal, "operation": op,
                                 "input_id": input_id, "cycles": cycles,
                                 "variant": variant, "measurement_basis": basis,
                                 "placement": placement})
        return path

    @staticmethod
    def fixture():
        return [(0, 0, "SMUL32", "a", 200, "old"),
                (0, 1, "SDIV32_32", "b", 800, "old"),
                (1, 0, "SMUL32", "c", 100, "old"),
                (3, 0, "SDIV32_32", "d", 1200, "old")]

    def test_peak_and_empty_frames(self):
        path = self.trace("baseline.csv", self.fixture())
        calls, meta = load_trace(path)
        result = score(calls, meta, frame_count=5, budget=1000)
        self.assertEqual(result["frame_math_cycles"], [1012, 106, 0, 1206, 0])
        self.assertEqual(result["peak_frame"], 3)
        self.assertEqual(result["p95_frame_math_cycles"], 1206)
        self.assertEqual(result["over_budget_frames"], 2)
        self.assertEqual(result["peak_hotspots"][0]["operation"], "SDIV32_32")
        self.assertEqual(result["total_math_cycles"], 2324)
        self.assertEqual(result["peak_frame_math_headroom_cycles"], -206)

    def test_paired_comparison(self):
        rows = self.fixture()
        a = self.trace("a.csv", rows)
        b = self.trace("b.csv", [(*row[:4], row[4] - 100, "new") for row in rows])
        result = analyze(a, b, frame_count=5, budget=1000)
        comparison = result["comparison"]
        self.assertEqual(comparison["paired_calls"], 4)
        self.assertEqual(comparison["total_math_cycles_saved"], 400)
        self.assertEqual(comparison["peak_frame_math_cycles_saved"], 100)
        self.assertFalse(comparison["peak_frame_changed"])
        self.assertEqual(comparison["over_budget_frames_saved"], 1)
        self.assertEqual(comparison["baseline_peak_frame_cycles_saved"], 100)
        self.assertEqual(comparison["regressed_frames"], 0)
        self.assertEqual(comparison["max_frame_regression_cycles"], 0)
        self.assertEqual(comparison["max_public_call_regression_cycles"], 0)

    def test_nonpeak_frame_and_single_call_regression_not_hidden_by_better_peak(self):
        baseline = self.trace("baseline.csv", [
            (0, 0, "SDIV32_16", "a", 1000, "old"),
            (1, 0, "SMOD32_16", "b", 800, "old"),
            (1, 1, "SMUL32", "c", 100, "old")])
        candidate = self.trace("candidate.csv", [
            (0, 0, "SDIV32_16", "a", 800, "new"),
            (1, 0, "SMOD32_16", "b", 840, "new"),
            (1, 1, "SMUL32", "c", 90, "new")])
        cmp = analyze(baseline, candidate, frame_count=3)["comparison"]
        self.assertEqual(cmp["peak_frame_math_cycles_saved"], 64)
        self.assertEqual(cmp["baseline_peak_frame_cycles_saved"], 200)
        self.assertEqual(cmp["regressed_frames"], 1)
        self.assertEqual(cmp["max_frame_regression_cycles"], 30)
        self.assertEqual(cmp["max_public_call_regression_cycles"], 40)

    def test_reject_changed_operands_and_incompatible_measurements(self):
        rows = self.fixture()
        a = self.trace("a.csv", rows)
        b = self.trace("b.csv", [(*row[:3], row[3] + "!", *row[4:]) for row in rows])
        with self.assertRaisesRegex(ValueError, "identical calls"):
            analyze(a, b)
        c = self.trace("c.csv", rows, basis="native-vice")
        with self.assertRaisesRegex(ValueError, "timing bases"):
            analyze(a, c)
        d = self.trace("d.csv", rows, placement="$7123/$C040")
        with self.assertRaisesRegex(ValueError, "placements"):
            analyze(a, d)

    def test_reject_duplicate_slots_and_variant_mix(self):
        rows = self.fixture()
        with self.assertRaisesRegex(ValueError, "duplicate call"):
            load_trace(self.trace("dupe.csv", rows + [rows[0]]))
        with self.assertRaisesRegex(ValueError, "inconsistent variant"):
            load_trace(self.trace("mix.csv", rows + [(4, 0, "SMUL32", "e", 3, "new")]))

    def test_reject_bad_budgets_and_missing_frames(self):
        with self.assertRaisesRegex(ValueError, "negative"):
            load_trace(self.trace("negative.csv", [(0, 0, "A", "x", -1, "v")]))
        calls, meta = load_trace(self.trace("valid.csv", self.fixture()))
        with self.assertRaisesRegex(ValueError, "cover"):
            score(calls, meta, frame_count=3)
        with self.assertRaisesRegex(ValueError, "positive"):
            score(calls, meta, budget=0)
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            score(calls, meta, jsr_cycles=-1)


if __name__ == "__main__":
    unittest.main()
