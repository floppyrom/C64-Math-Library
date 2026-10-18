#!/usr/bin/env python3
"""Matched complete six-operation busy-frame test for signed32/16 V2 donor.

This is deterministic CPU-model whole-public-call timing, not a physical
PAL VIC-II/IRQ/SID/REU timing claim. Preserve non-peak regressions.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from export_wide_frame_trace import export
from frame_cycle_budget import analyze, load_trace


class SignedV2BusyFrameTests(unittest.TestCase):
    def test_paired_busy_frame_donor_at_two_code_origins(self):
        for code, io in ((0x8000, 0xc000), (0x7123, 0xc040)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as td:
                folder = Path(td)
                compact, donor = folder / "compact.csv", folder / "v2.csv"
                export(compact, frames=24, code=code, io=io,
                       signed32_16_variant="link:portable-zerozp")
                export(donor, frames=24, code=code, io=io,
                       signed32_16_variant="link:v2-signed-magnitude")
                before, bm = load_trace(compact)
                after, am = load_trace(donor)
                self.assertEqual([v.key for v in before],
                                 [v.key for v in after])
                self.assertTrue(any(v.operation in ("MATH_SDIV32_16",
                                                    "MATH_SMOD32_16")
                                    for v in before))
                selected = {x["api"]: x["variant"]
                            for x in json.loads(
                                donor.with_suffix(".manifest.json").read_text()
                            )["manifest"]["operations"]}
                self.assertEqual(selected["MATH_SDIV32_16"],
                                 "link:v2-signed-magnitude")
                self.assertEqual(selected["MATH_SMOD32_16"],
                                 "link:v2-signed-magnitude")
                compared = analyze(compact, donor, frame_count=24)
                cmp = compared["comparison"]
                self.assertEqual(cmp["paired_calls"], len(before))
                self.assertGreater(cmp["total_math_cycles_saved"], 0)
                self.assertGreater(cmp["peak_frame_math_cycles_saved"], 0)
                print("SIGNED32_16_V2_WORST_FRAME", hex(code),
                      json.dumps(cmp, sort_keys=True), flush=True)

if __name__ == "__main__":
    unittest.main()
