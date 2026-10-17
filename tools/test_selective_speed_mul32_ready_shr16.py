#!/usr/bin/env python3
"""Four matched-source READY/SHR16 speed selectors and global sharing contracts."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import math_builder
import selective_linker as linker
import selective_speed_mul32_ready_shr16 as speed
import selective_speed_umul32 as u32
import selective_speed_smul32 as s32

FAST="link:fast31-shared-full64"
OPS=("UMUL32_READY","SMUL32_READY","UMUL32_SHR16","SMUL32_SHR16")
EXPECTED_SMALL={
    "UMUL32_READY":248,
    "SMUL32_READY":337,
    "UMUL32_SHR16":289,
    "SMUL32_SHR16":378,
}

class Extra32SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops,zp=31,ram=3000,pins=None,calls=None):
        return math_builder.create_plan(
            self.index,list(ops),objective="speed",
            zp_budget=zp,ram_budget=ram,pins=pins,
            workload_calls=calls if calls is not None else
                ({op:1 for op in ops} if len(ops)>1 else None))

    def test_all_four_pure_speed_models_and_memory_constrained_fallback(self):
        for code,io,scratch,zp in ((0x8000,0xc000,0xc020,0x50),
                                   (0x7123,0xc040,0xc080,0x70)):
            memory={"code_base":code,"math_io":io,
                    "scratch_base":scratch,"zp_base":zp}
            for op in OPS:
                with self.subTest(op=op,code=code),tempfile.TemporaryDirectory() as td:
                    out=Path(td)
                    man=linker.build(self.plan((op,)),out,memory=memory)
                    model=man["cycle_model_benchmark"]
                    self.assertTrue(model["cpu_model_only"])
                    self.assertEqual(model["cases"],192)
                    self.assertEqual(model["corpus_sha256"],
                        s32.CORPUS_SHA256 if op.startswith("SMUL") else u32.CORPUS_SHA256)
                    self.assertEqual(set(model["mean_cycles"]),speed.EXPECTED)
                    cycles=model["mean_cycles"]
                    self.assertLess(cycles[FAST],cycles["link:compact-zerozp"])
                    self.assertLess(cycles[FAST],cycles["link:unified-375"])
                    self.assertEqual(man["operations"][0]["variant"],FAST)
                    self.assertEqual(man["resource_use"]["zero_page_bytes"],31)
                    self.assertEqual(man["resource_use"]["main_ram_total_bytes"],2592)
                    constrained=linker.build(
                        self.plan((op,),zp=0,ram=EXPECTED_SMALL[op]),
                        out/"compact",memory=memory)
                    self.assertEqual(constrained["operations"][0]["variant"],
                                     "link:compact-zerozp")
                    self.assertEqual(constrained["resource_use"]["zero_page_bytes"],0)
                    print("FAST31 EXTRA SPEED",op,hex(code),cycles,flush=True)

    def test_four_operations_global_weighted_selection_shares_one_image(self):
        with tempfile.TemporaryDirectory() as td:
            calls={op:100-i*19 for i,op in enumerate(OPS)}
            plan=self.plan(OPS,zp=31,ram=2592,calls=calls)
            man=linker.build(plan,Path(td))
            self.assertEqual({r["variant"] for r in man["operations"]},{FAST})
            self.assertEqual(len(man["link_order"]),1)
            use=man["resource_use"]
            self.assertEqual(use["image_span_bytes"],2560)
            self.assertEqual(use["main_ram_total_bytes"],2592)
            self.assertEqual(use["zero_page_bytes"],31)
            model=man["cycle_model_benchmark"]
            self.assertTrue(model["cpu_model_only"])
            self.assertEqual(set(model["operations"]),{"MATH_"+op for op in OPS})
            for op in OPS:
                item=model["operations"]["MATH_"+op]
                self.assertEqual(item["cases"],192)
                self.assertEqual(set(item["mean_cycles"]),speed.EXPECTED)
            self.assertEqual(model["workload_calls"],
                             {"MATH_"+op:value for op,value in calls.items()})

    def test_fail_closed_source_and_candidate_set(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for op in OPS:
                api="MATH_"+op
                before=dict(linker.MODULES[api])
                try:
                    del linker.MODULES[api]["link:unified-375"]
                    with self.assertRaisesRegex(linker.LinkError,
                                                "cycle-model measurement failed"):
                        linker.build(self.plan((op,)),root/op)
                finally:
                    linker.MODULES[api]=before
            bad=dict(linker.MODULES["MATH_UMUL32_SHR16"])
            try:
                damaged=dict(bad[FAST],zp=30)
                linker.MODULES["MATH_UMUL32_SHR16"][FAST]=damaged
                with self.assertRaisesRegex(linker.LinkError,
                                             "cycle-model measurement failed"):
                    linker.build(self.plan(("UMUL32_SHR16",)),root/"bad_resource")
            finally:
                linker.MODULES["MATH_UMUL32_SHR16"]=bad

if __name__=="__main__":
    unittest.main()
