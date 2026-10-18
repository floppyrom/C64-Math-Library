#!/usr/bin/env python3
"""Source-locked, matched-input global 32/32 public DIV/MOD speed regression."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import math_builder
import selective_linker as linker
import selective_speed_u3232 as speed

DIV="UDIV32_32"
MOD="UMOD32_32"

class U3232SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=(DIV,),ram=4000,zp=4,pins=None):
        return math_builder.create_plan(
            self.index,list(ops),objective="speed",ram_budget=ram,
            zp_budget=zp,pins=pins,
            workload_calls={DIV:1000,MOD:500} if len(ops)>1 else None)

    def test_individual_384_identical_input_public_call_proofs(self):
        for base,io,scratch,zp in ((0x8000,0xc000,0xc020,0x50),
                                   (0x7123,0xc040,0xc080,0x70)):
            memory={"code_base":base,"math_io":io,"scratch_base":scratch,
                    "zp_base":zp}
            for op in (DIV,MOD):
                with self.subTest(code=base,api=op),tempfile.TemporaryDirectory() as td:
                    manifest=linker.build(self.plan((op,)),Path(td),memory=memory)
                    model=manifest["cycle_model_benchmark"]
                    self.assertEqual(model["cases"],speed.COUNT)
                    self.assertEqual(model["corpus_sha256"],speed.CORPUS_SHA256)
                    self.assertTrue(model["cpu_model_only"])
                    self.assertEqual(set(model["mean_cycles"]),speed.EXPECTED["MATH_"+op])
                    self.assertTrue(all(v>0 for v in model["mean_cycles"].values()))
                    eligible={ident:value for ident,value in model["mean_cycles"].items()
                              if linker.MODULES["MATH_"+op][ident]["zp"]<=4
                              and (sum(n for _,n in linker.MODULES["MATH_"+op][ident]["segments"])
                                   +32+linker.MODULES["MATH_"+op][ident]["scratch"])<=4000}
                    self.assertEqual(manifest["operations"][0]["variant"],
                                     min(eligible,key=eligible.get))
                    print("U3232 MATCHED PUBLIC",op,hex(base),
                          model["mean_cycles"],flush=True)

    def test_no_zero_page_selects_aligned_div_and_mod(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan((DIV,),zp=0),Path(td)/"zerozp")
            self.assertEqual(man["operations"][0]["variant"],
                             "link:aligned-zerozp")
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            mm=linker.build(self.plan((DIV,MOD)),Path(td)/"mixed")
            self.assertEqual(len(mm["operations"]),2)
            self.assertEqual(mm["resource_use"]["private_ram_scratch_bytes"],4)
            self.assertEqual(set(mm["cycle_model_benchmark"]["operations"]),
                             {"MATH_"+DIV,"MATH_"+MOD})
            self.assertEqual(mm["cycle_model_benchmark"]["workload_calls"],
                             {"MATH_"+DIV:1000,"MATH_"+MOD:500})

    def test_candidates_and_memory_contract_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            for op in (DIV,MOD):
                api="MATH_"+op
                original=dict(linker.MODULES[api])
                victim=next(iter(original))
                try:
                    del linker.MODULES[api][victim]
                    with self.assertRaisesRegex(linker.LinkError,
                                                 "cycle-model measurement failed"):
                        linker.build(self.plan((op,)),Path(td)/op)
                finally:
                    linker.MODULES[api]=original
            api="MATH_UDIV32_32"
            original=dict(linker.MODULES[api])
            try:
                linker.MODULES[api]["link:zptail"]=dict(original["link:zptail"],
                                                          zp=5)
                with self.assertRaisesRegex(linker.LinkError,
                                             "cycle-model measurement failed"):
                    linker.build(self.plan((DIV,)),Path(td)/"wrong_zp")
            finally:
                linker.MODULES[api]=original

if __name__=="__main__":
    unittest.main()
