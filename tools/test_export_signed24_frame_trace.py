#!/usr/bin/env python3
"""Paired public-call mixed-frame cycles for signed24 compact versus Q0 donors."""
from __future__ import annotations
import csv
import json
import tempfile
import unittest
from pathlib import Path

from export_wide_frame_trace import SIGNED24_OPS, SIGNED24_VARIANTS, export
from frame_cycle_budget import analyze, load_trace


class Signed24FrameTraceTests(unittest.TestCase):
    def test_matched_bursty_signed_wide_frame_traces_two_memory_maps(self):
        for code, io in ((0x8000, 0xC000), (0x7123, 0xC040)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                paths = [target / ("signed24_%d.csv" % i) for i in range(2)]
                summaries = [
                    export(paths[i], frames=24, code=code, io=io, signed24_variant=variant)
                    for i, variant in enumerate(SIGNED24_VARIANTS)
                ]
                original, bm = load_trace(paths[0])
                guarded, gm = load_trace(paths[1])
                self.assertEqual(len(original), len(guarded))
                self.assertEqual({r.key for r in original}, {r.key for r in guarded})
                self.assertGreater(sum(r.operation == "MATH_SDIV24" for r in original), 0)
                self.assertGreater(sum(r.operation == "MATH_SMOD24" for r in original), 0)
                self.assertEqual(
                    {bm["variants"]["MATH_" + op] for op in SIGNED24_OPS},
                    {SIGNED24_VARIANTS[0]})
                self.assertEqual(
                    {gm["variants"]["MATH_" + op] for op in SIGNED24_OPS},
                    {SIGNED24_VARIANTS[1]})
                self.assertEqual(bm["measurement_basis"], "cpu-model-public-entry-through-rts")
                self.assertEqual(bm["placement"], gm["placement"])
                for path in paths:
                    provenance = json.loads(path.with_suffix(".manifest.json").read_text())
                    self.assertTrue(provenance["synthetic_not_real_game"])
                    self.assertTrue(provenance["trace_sha256"])
                result = analyze(paths[0], paths[1], frame_count=24)
                self.assertEqual(result["comparison"]["paired_calls"], len(original))
                self.assertEqual(summaries[0]["peak_frame_math_cycles"],
                                 result["baseline"]["peak_frame_math_cycles"])
                self.assertEqual(summaries[1]["peak_frame_math_cycles"],
                                 result["candidate"]["peak_frame_math_cycles"])
                # Improvements are workload-dependent, but this particular
                # fixed synthetic corpus must benefit from Q0 shortcuts.
                self.assertGreater(result["comparison"]["total_math_cycles_saved"], 0)
                self.assertEqual(
                    result["baseline"]["frames"], result["candidate"]["frames"])
                non24 = set(bm["variants"]) - {"MATH_SDIV24", "MATH_SMOD24"}
                # A longer source changes linked addresses, so non24 calls
                # can experience 6502 page-crossing cycle differences even
                # with identical source bytes. Verify *source identity*, but
                # retain observed secondary cycle costs in the frame score.
                for op in non24:
                    self.assertEqual(bm["variants"][op], gm["variants"][op])
                signed24_saved = sum(
                    before.cycles - after.cycles
                    for before, after in zip(original, guarded)
                    if before.operation in ("MATH_SDIV24", "MATH_SMOD24"))
                others_saved = sum(
                    before.cycles - after.cycles
                    for before, after in zip(original, guarded)
                    if before.operation not in ("MATH_SDIV24", "MATH_SMOD24"))
                self.assertEqual(signed24_saved + others_saved,
                                 result["comparison"]["total_math_cycles_saved"])
                breakdown = {**result["comparison"],
                             "signed24_cycles_saved": signed24_saved,
                             "other_signed_wide_cycles_saved": others_saved}
                print("SIGNED24_FRAME_PAIRED", hex(code),
                      json.dumps(breakdown, sort_keys=True), flush=True)

    def test_refuse_unknown_source_and_changed_memory_map(self):
        with tempfile.TemporaryDirectory() as directory:
            t = Path(directory)
            with self.assertRaisesRegex(ValueError, "Unqualified"):
                export(t / "invalid.csv", frames=1, signed24_variant="link:unmeasured")
            first, second = t / "a.csv", t / "b.csv"
            export(first, frames=8, signed24_variant=SIGNED24_VARIANTS[0])
            export(second, frames=8, code=0x7123, io=0xC040,
                   signed24_variant=SIGNED24_VARIANTS[1])
            with self.assertRaisesRegex(ValueError, "timing bases or placements"):
                analyze(first, second, frame_count=8)


if __name__ == "__main__":
    unittest.main()
