#!/usr/bin/env python3
"""Certified logarithmic-ratio VEC2_NORMALIZE_Q8_8 source-link regression."""
from __future__ import annotations
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU
from normalize_model import normalized_reference

DESIGN=json.loads((ROOT/"validation/normalize/LOG_RATIO_TABLE_DESIGN.json").read_text())
EDGE=(-32768,-32767,-16384,-4096,-256,-255,-128,-2,-1,0,
      1,2,127,128,255,256,4096,16384,32766,32767)
def pairs():
    r=random.Random(0x56454332)
    return [(x,y) for x in EDGE for y in EDGE]+[
        (r.randrange(-32768,32768),r.randrange(-32768,32768)) for _ in range(1024)]

class Vec2SelectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ops=("VEC2_NORMALIZE_Q8_8",),ram=4000):
        return math_builder.create_plan(self.index,list(ops),
                      objective="size",zp_budget=4,ram_budget=ram)

    def test_model_parity_relocated_maps_and_zero_carry(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x61),
                           (0x830f,0xc100,0x76)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=selective_linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"zp_base":zp})
                expected_start=(code+255)&~255
                entry=next(int(x["entry"][1:],16) for x in man["operations"]
                           if x["api"]=="MATH_VEC2_NORMALIZE_Q8_8")
                self.assertEqual(entry,expected_start+0x0E00)
                span=expected_start+3587-code
                self.assertEqual(man["resource_use"]["image_span_bytes"],span)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],span+32)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],4)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),span+2)
                mem=bytearray(65536);mem[code:code+span]=prg[2:]
                before=bytes(mem[code:code+span])
                cpu=CPU(mem);sp=cpu.sp
                for i,(x,y) in enumerate(pairs()):
                    xb=(x&65535).to_bytes(2,"little")
                    yb=(y&65535).to_bytes(2,"little")
                    mem[io:io+2]=xb;mem[io+4:io+6]=yb
                    mem[io+8:io+12]=bytes((0xdd,0xee,0xaa,0x55))
                    cpu.d=0;cpu.c=i&1
                    cpu.call(entry,120000)
                    ox=int.from_bytes(mem[io+8:io+10],"little",signed=True)
                    oy=int.from_bytes(mem[io+10:io+12],"little",signed=True)
                    ex,ey=normalized_reference(x,y,DESIGN)
                    self.assertEqual((ox,oy),(ex,ey),(code,x,y))
                    self.assertEqual(cpu.c,int(not(x or y)),(code,x,y))
                    self.assertEqual(bytes(mem[io:io+2]),xb)
                    self.assertEqual(bytes(mem[io+4:io+6]),yb)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+span]),before)

    def test_zp_budget_and_aligned_mixed_link(self):
        with tempfile.TemporaryDirectory() as td:
            man=selective_linker.build(self.plan(("VEC2_NORMALIZE_Q8_8","UMUL16")),
                                         Path(td))
            use=man["resource_use"]
            self.assertEqual(use["zero_page_bytes"],4)
            self.assertEqual(use["private_ram_scratch_bytes"],6)
            self.assertLessEqual(use["main_ram_total_bytes"],4000)
            self.assertEqual(len(man["operations"]),2)
            with self.assertRaises(selective_linker.LinkError):
                plan=math_builder.create_plan(self.index,["VEC2_NORMALIZE_Q8_8"],
                                    objective="size",zp_budget=3,ram_budget=4000)
                selective_linker.build(plan,Path(td)/"bad")

if __name__=="__main__":
    unittest.main()
