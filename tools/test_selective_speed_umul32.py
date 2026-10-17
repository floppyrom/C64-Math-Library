#!/usr/bin/env python3
"""UMUL32 matched-input speed selection and fail-closed provenance."""
from __future__ import annotations
from pathlib import Path
import tempfile
import unittest
import math_builder
import selective_linker
import selective_speed_umul32 as bench


class UMUL32SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self, ram, pins=None):
        return math_builder.create_plan(
            self.index,["UMUL32"],objective="speed",
            zp_budget=0,ram_budget=ram,pins=pins)

    def test_matched_source_means_and_auto_selection(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=selective_linker.build(
                    self.plan(2086),Path(td),
                    memory={"code_base":code,"math_io":io,"scratch_base":scratch})
                model=man["cycle_model_benchmark"]
                self.assertEqual(model["cases"],192)
                self.assertEqual(model["corpus_sha256"],bench.CORPUS_SHA256)
                self.assertTrue(model["cpu_model_only"])
                cycles=model["mean_cycles"]
                self.assertEqual(set(cycles),set(bench.EXPECTED))
                self.assertLess(cycles["link:quarter-square-32"],
                                cycles["link:compact-zerozp"])
                self.assertLess(cycles["link:quarter-square-32"],
                                cycles["link:unified-375"])
                self.assertEqual(man["operations"][0]["variant"],
                                 "link:quarter-square-32")
                constrained=selective_linker.build(
                    self.plan(248),Path(td)/"constrained",
                    memory={"code_base":code,"math_io":io,"scratch_base":scratch})
                self.assertEqual(constrained["operations"][0]["variant"],
                                 "link:compact-zerozp")

    def test_explicit_pins_and_fail_closed_candidate_set(self):
        with tempfile.TemporaryDirectory() as td:
            man=selective_linker.build(
                self.plan(2500,pins={"UMUL32":"link:unified-375"}),Path(td))
            self.assertEqual(man["operations"][0]["variant"],"link:unified-375")
            modules=dict(selective_linker.MODULES["MATH_UMUL32"])
            try:
                del selective_linker.MODULES["MATH_UMUL32"]["link:quarter-square-32"]
                with self.assertRaisesRegex(selective_linker.LinkError,
                                            "cycle-model measurement failed"):
                    selective_linker.build(self.plan(2500),Path(td)/"changed")
            finally:
                selective_linker.MODULES["MATH_UMUL32"]=modules


if __name__=="__main__":
    unittest.main()
