#!/usr/bin/env python3
"""Two-map signed full Q8.8 product checks and exact resource selection."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smul16_shr8 as speed

FAST=speed.FAST
SMALL=speed.SMALL


class SignedSHR8QuarterSquare(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.index=math_builder.operation_index()

    def plan(self,pin=FAST,objective="size",ram=1419):
        return math_builder.create_plan(
            self.index,["SMUL16_SHR8"],objective=objective,
            pins={"SMUL16_SHR8":pin} if pin else {},
            zp_budget=0,ram_budget=ram,
            workload_calls={"SMUL16_SHR8":100} if objective=="speed" else None)

    def test_q24_public_zerozp_two_origins(self):
        for code,io,scratch in ((0x8000,0xc000,0xc040),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],1383)
                self.assertEqual(use["zero_page_bytes"],0)
                self.assertEqual(use["private_ram_scratch_bytes"],4)
                self.assertEqual(use["main_ram_total_bytes"],1419)
                self.assertEqual(man["operations"][0]["variant"],FAST)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),1385)
                image=bytearray(65536)
                image[code:code+1383]=prg[2:]
                pristine=bytes(image[code:code+1383])
                cpu=CPU(image)
                sp=cpu.sp
                entry=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(entry,code+1351)
                for x,y in speed.corpus():
                    xb=x.to_bytes(2,"little")+bytes((0xa5,0x5a))
                    yb=y.to_bytes(2,"little")+bytes((0x6b,0x7c))
                    image[io:io+4]=xb
                    image[io+4:io+8]=yb
                    image[io+8:io+16]=bytes((0xdd,))*8
                    cpu.d=0
                    cpu.c=(x^y)&1
                    cpu.call(entry,60000)
                    self.assertEqual(int.from_bytes(image[io+8:io+11],"little"),
                                     speed.oracle(x,y),(code,x,y))
                    self.assertEqual(bytes(image[io:io+4]),xb)
                    self.assertEqual(bytes(image[io+4:io+8]),yb)
                    self.assertEqual(bytes(image[io+12:io+16]),bytes((0xdd,))*4)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(image[code:code+1383]),pristine)

    def test_paired_source_speed_and_resource_fallback(self):
        for code,io,scratch in ((0x8000,0xc000,0xc040),
                                (0x7123,0xc040,0xc080)):
            model=speed.bench_smul16_shr8(
                linker.MODULES["MATH_SMUL16_SHR8"],
                code,io,scratch,math_builder.ROOT)
            print("SMUL16_SHR8_QS_MATCHED",hex(code),
                  model["mean_cycles"],model["maximum_cycles"],
                  model["p95_cycles"],flush=True)
            self.assertEqual(model["cases"],512)
            self.assertLess(model["mean_cycles"][FAST],
                            model["mean_cycles"][SMALL])
        for ram,winner in ((1419,FAST),(222,SMALL)):
            with tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(None,"speed",ram),Path(td))
                self.assertEqual(man["operations"][0]["variant"],winner)
                self.assertEqual(man["cycle_model_benchmark"]["cases"],512)

    def test_pinned_fast_fails_insufficient_ram(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=1418),Path(td)/"short")

if __name__=="__main__":
    unittest.main()
