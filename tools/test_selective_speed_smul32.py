#!/usr/bin/env python3
"""Same-corpus signed FAST31 SMUL32 speed selector, pins and fail-closed behavior."""
from __future__ import annotations
from pathlib import Path
import tempfile
import unittest
import math_builder
import selective_linker
import selective_speed_smul32 as bench

FAST="link:fast31-v2-signed"

class SignedSpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ram,zp,pins=None):
        return math_builder.create_plan(
            self.index,["SMUL32"],objective="speed",zp_budget=zp,
            ram_budget=ram,pins=pins)

    def test_signed_means_and_fast31_speed_choice(self):
        for code,io,scratch,zp in ((0x8000,0xc000,0xc020,0x50),
                                   (0x7123,0xc040,0xc080,0x70)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                memory={"code_base":code,"math_io":io,
                        "scratch_base":scratch,"zp_base":zp}
                man=selective_linker.build(self.plan(3000,31),Path(td),
                                           memory=memory)
                metrics=man["cycle_model_benchmark"]
                self.assertTrue(metrics["cpu_model_only"])
                self.assertEqual(metrics["cases"],192)
                self.assertEqual(metrics["corpus_sha256"],bench.CORPUS_SHA256)
                self.assertEqual(set(metrics["mean_cycles"]),set(bench.EXPECTED))
                mean=metrics["mean_cycles"]
                self.assertLess(mean[FAST],mean["link:compact-zerozp"])
                self.assertLess(mean[FAST],mean["link:unified-375"])
                self.assertEqual(man["operations"][0]["variant"],FAST)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],31)
                small=selective_linker.build(
                    self.plan(337,0),Path(td)/"small",memory=memory)
                self.assertEqual(small["operations"][0]["variant"],
                                 "link:compact-zerozp")
                print("SMUL32 SPEED",hex(code),mean,flush=True)

    def test_pin_resource_rejection_and_candidate_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            pinned=selective_linker.build(
                self.plan(3000,31,pins={"SMUL32":FAST}),Path(td))
            self.assertEqual(pinned["operations"][0]["variant"],FAST)
            modules=dict(selective_linker.MODULES["MATH_SMUL32"])
            try:
                del selective_linker.MODULES["MATH_SMUL32"][FAST]
                with self.assertRaisesRegex(selective_linker.LinkError,
                                            "cycle-model measurement failed"):
                    selective_linker.build(self.plan(3000,31),Path(td)/"changed")
            finally:
                selective_linker.MODULES["MATH_SMUL32"]=modules

if __name__=="__main__":
    unittest.main()
