#!/usr/bin/env python3
"""Relocated canonical unsigned-QS signed16 model and Pareto resource gates."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smul16 as speed

FAST=speed.FAST
SMALL=speed.SMALL


class SignedQuarterSquare16(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,variant=FAST,objective="size",ram=1387):
        return math_builder.create_plan(
            self.index,["SMUL16"],objective=objective,
            pins={"SMUL16":variant} if variant else {},
            zp_budget=0,ram_budget=ram,
            workload_calls={"SMUL16":100} if objective=="speed" else None)

    def test_full_public_signed32_two_origins(self):
        for code,io,scratch in ((0x8000,0xc000,0xc040),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(origin=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,
                    "scratch_base":scratch})
                self.assertEqual(man["operations"][0]["variant"],FAST)
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],1351)
                self.assertEqual(use["zero_page_bytes"],0)
                self.assertEqual(use["private_ram_scratch_bytes"],4)
                self.assertEqual(use["main_ram_total_bytes"],1387)
                image=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(image),1353)
                self.assertEqual(image[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536)
                mem[code:code+1351]=image[2:]
                immutable=bytes(mem[code:code+1351])
                cpu=CPU(mem)
                sp=cpu.sp
                entry=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(entry,code+1255)
                for x,y in speed.corpus():
                    xb=x.to_bytes(2,"little")+b"\xa5\x5a"
                    yb=y.to_bytes(2,"little")+b"\x6b\x7c"
                    mem[io:io+4]=xb
                    mem[io+4:io+8]=yb
                    mem[io+8:io+16]=b"\x99\x88\x77\x66\xdd\xdd\xdd\xdd"
                    cpu.d=0
                    cpu.c=(x^y)&1
                    cpu.call(entry,60000)
                    expected=(speed.signed(x)*speed.signed(y))&0xffffffff
                    self.assertEqual(int.from_bytes(mem[io+8:io+12],"little"),
                                     expected,(code,x,y))
                    self.assertEqual(bytes(mem[io:io+4]),xb)
                    self.assertEqual(bytes(mem[io+4:io+8]),yb)
                    self.assertEqual(bytes(mem[io+12:io+16]),b"\xdd"*4)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+1351]),immutable)

    def test_same_corpus_cycle_model_and_resource_selection(self):
        for code,io,scratch in ((0x8000,0xc000,0xc040),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(origin=code):
                model=speed.bench_smul16(
                    linker.MODULES["MATH_SMUL16"],
                    code,io,scratch,math_builder.ROOT)
                print("SMUL16_SIGNED_QS_MATCHED",hex(code),
                      model["mean_cycles"],model["maximum_cycles"],
                      model["p95_cycles"],flush=True)
                self.assertEqual(model["cases"],512)
                self.assertLess(model["mean_cycles"][FAST],
                                model["mean_cycles"][SMALL])
        for ram,winner in ((1387,FAST),(199,SMALL)):
            with tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(None,"speed",ram),Path(td))
                self.assertEqual(man["operations"][0]["variant"],winner)
                self.assertEqual(man["cycle_model_benchmark"]["cases"],512)

    def test_pinned_fast_fails_under_ram_limit(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=1386),Path(td)/"bad")

if __name__=="__main__":
    unittest.main()
