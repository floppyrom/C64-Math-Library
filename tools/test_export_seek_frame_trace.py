#!/usr/bin/env python3
"""Reproducible source-linked SEEK mixed object/frame timing smoke."""
import csv
from pathlib import Path
import tempfile
import unittest

from export_seek_frame_trace import OPS, export, should_retarget
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

    def test_staggered_retarget_schedule(self):
        expected = {0:16,9:4,10:4,11:4,12:4,18:4,19:4,20:4,21:4}
        observed = {frame:sum(should_retarget(frame,family,slot,"staggered")
                             for family in ("SEEK8","SEEK16")
                             for slot in range(8))
                    for frame in range(24)}
        self.assertEqual({f:n for f,n in observed.items() if n}, expected)
        for family in ("SEEK8","SEEK16"):
            self.assertEqual(sum(should_retarget(f,family,slot,"staggered")
                                 for f in range(9,18) for slot in range(8)),8)

    def test_same_kernel_call_counts_and_later_frame_peak(self):
        import json
        from collections import Counter
        for base,io in ((0x8000,0xc000),(0x7123,0xc100)):
            with self.subTest(code=base), tempfile.TemporaryDirectory() as td:
                a,b=Path(td)/"burst.csv",Path(td)/"staggered.csv"
                old=export(a,frames=24,code=base,io=io)
                new=export(b,frames=24,code=base,io=io,
                           retarget_policy="staggered")
                self.assertEqual(old["calls"],new["calls"])
                self.assertEqual(old["calls"],432)
                self.assertEqual((old["init_calls"],new["init_calls"]),(48,48))
                self.assertEqual(old["cold_start_frame_math_cycles"],
                                 new["cold_start_frame_math_cycles"])
                self.assertLess(new["post_cold_start_peak_frame_math_cycles"],
                                old["post_cold_start_peak_frame_math_cycles"])
                expected=({0:16,9:16,18:16},
                          {0:16,9:4,10:4,11:4,12:4,18:4,19:4,20:4,21:4})
                for path,ref in zip((a,b),expected):
                    with path.open(newline="") as stream:
                        rows=list(csv.DictReader(stream))
                    init=Counter(int(r["frame"]) for r in rows
                                 if r["operation"].endswith("_INIT"))
                    self.assertEqual(dict(init),ref)
                    for frame in range(24):
                        self.assertEqual(sum(int(r["frame"])==frame
                                             and not r["operation"].endswith("_INIT")
                                             for r in rows),16)
                oldmeta=json.loads(a.with_suffix(".manifest.json").read_text())
                newmeta=json.loads(b.with_suffix(".manifest.json").read_text())
                self.assertEqual(oldmeta["manifest"]["prg_sha256"],
                                 newmeta["manifest"]["prg_sha256"])
                self.assertNotEqual(oldmeta["trace_sha256"],newmeta["trace_sha256"])
                print("SEEK retarget schedule",hex(base),
                      "cold",old["cold_start_frame_math_cycles"],
                      "warm burst",old["post_cold_start_peak_frame_math_cycles"],
                      "warm stagger",new["post_cold_start_peak_frame_math_cycles"],
                      flush=True)

    def test_invalid_policy_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                export(Path(td)/"bad.csv",retarget_policy="unknown")

    def test_frame_count_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            for n in (0,201):
                with self.assertRaises(ValueError):
                    export(Path(td)/"bad.csv",frames=n)


if __name__ == "__main__":
    unittest.main()
