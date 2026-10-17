#!/usr/bin/env python3
"""Matched public 32/16 quotient/remainder weighted selector and safety tests."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_u3216 as speed

APIS=("UDIV32_16","UMOD32_16")
FAST="link:accumulator-remainder"

class U3216SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=APIS,ram=197,zp=0,pins=None,calls=None):
        return math_builder.create_plan(
            self.index,list(ops),objective="speed",
            zp_budget=zp,ram_budget=ram,pins=pins,
            workload_calls=calls if calls is not None else
                ({op:(900 if op=="UDIV32_16" else 100) for op in ops}
                 if len(ops)>1 else None))

    def test_each_api_two_maps_complete_matched_q_and_r(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080)):
            for op in APIS:
                with self.subTest(code=code,op=op),tempfile.TemporaryDirectory() as td:
                    memory={"code_base":code,"math_io":io,"scratch_base":scratch}
                    man=linker.build(self.plan((op,)),Path(td),memory=memory)
                    model=man["cycle_model_benchmark"]
                    self.assertEqual(model["cases"],speed.COUNT)
                    self.assertEqual(model["corpus_sha256"],speed.CORPUS_SHA256)
                    self.assertTrue(model["cpu_model_only"])
                    means=model["mean_cycles"]
                    self.assertEqual(set(means),speed.EXPECTED)
                    self.assertLess(means[FAST],means["link:portable-restoring"])
                    self.assertEqual(man["operations"][0]["variant"],FAST)
                    self.assertEqual(man["resource_use"]["main_ram_total_bytes"],164)
                    self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                    print("U3216 PUBLIC SPEED",op,hex(code),means,flush=True)

    def test_weighted_two_api_shared_kernel_exact_ram(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(ram=164),Path(td))
            self.assertEqual(len(man["link_order"]),1)
            self.assertEqual({r["variant"] for r in man["operations"]},{FAST})
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],164)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],1)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(set(man["cycle_model_benchmark"]["operations"]),
                             {"MATH_"+x for x in APIS})
            self.assertEqual(man["cycle_model_benchmark"]["workload_calls"],{
                "MATH_UDIV32_16":900,"MATH_UMOD32_16":100})
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=163),Path(td)/"insufficient")

    def test_pins_still_honored_and_changed_candidates_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            pinned=linker.build(self.plan(ram=197,pins={
                op:"link:portable-restoring" for op in APIS}),Path(td)/"pinned")
            self.assertEqual({row["variant"] for row in pinned["operations"]},
                             {"link:portable-restoring"})
            self.assertEqual(pinned["resource_use"]["main_ram_total_bytes"],197)
            for op in APIS:
                key="MATH_"+op
                backup=dict(linker.MODULES[key])
                try:
                    del linker.MODULES[key]["link:portable-restoring"]
                    with self.assertRaisesRegex(linker.LinkError,
                                                 "cycle-model measurement failed"):
                        linker.build(self.plan((op,)),Path(td)/op)
                finally:
                    linker.MODULES[key]=backup
            key="MATH_UMOD32_16"
            backup=dict(linker.MODULES[key])
            try:
                linker.MODULES[key][FAST]=dict(backup[FAST],scratch=2)
                with self.assertRaisesRegex(linker.LinkError,
                                             "cycle-model measurement failed"):
                    linker.build(self.plan(("UMOD32_16",)),Path(td)/"tamper")
            finally:
                linker.MODULES[key]=backup

if __name__=="__main__":
    unittest.main()
