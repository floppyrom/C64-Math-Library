#!/usr/bin/env python3
"""Reproducible source-linked SEEK mixed object/frame timing smoke."""
import csv
from pathlib import Path
import tempfile
import unittest

from export_seek_frame_trace import OPS, export
from frame_cycle_budget import COLUMNS, load_trace, score


class MixedSeekFrameTests(unittest.TestCase):
    def test_two_relocations_complete_frame_input_and_cycle_trace(self):
        for base,io in ((0x8000,0xc000),(0x7123,0xc100)):
            with self.subTest(base=base),tempfile.TemporaryDirectory() as td:
                trace=Path(td)/"seek_frames.csv"
                report=export(trace,frames=12,code=base,io=io)
                calls,meta=load_trace(trace)
                self.assertEqual(len(calls),16*12+16*2)
                self.assertEqual(report["calls"],len(calls))
                self.assertGreater(report["peak_frame_math_cycles"],0)
                self.assertGreater(report["p95_frame_math_cycles"],0)
                self.assertTrue(trace.with_suffix(".manifest.json").exists())
                with trace.open(newline="") as f:
                    rows=list(csv.DictReader(f))
                self.assertEqual(set(rows[0]),set(COLUMNS))
                self.assertEqual(set(x["operation"] for x in rows),
                                 {"MATH_"+op for op in OPS})
                self.assertEqual({x["variant"] for x in rows},
                                 {"link:generated-dda"})
                self.assertEqual({x["measurement_basis"] for x in rows},
                                 {"cpu-model-public-entry-through-rts"})
                self.assertEqual(report["peak_frame_math_cycles"],
                                 score(calls,meta,frame_count=12)["peak_frame_math_cycles"])

    def test_exact_source_trace_repeat_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            a,b=Path(td)/"first.csv",Path(td)/"second.csv"
            r1=export(a,frames=3)
            r2=export(b,frames=3)
            self.assertEqual(r1,r2)
            self.assertEqual(a.read_bytes(),b.read_bytes())

    def test_frame_count_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            for n in (0,201):
                with self.assertRaises(ValueError):
                    export(Path(td)/"bad.csv",frames=n)


if __name__ == "__main__":
    unittest.main()
