#!/usr/bin/env python3
"""Exact signed24 x signed24 => signed48 independently relocated kernel test."""
from __future__ import annotations
import random
import tempfile
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
import math_builder
import selective_linker as linker

EDGE=(0,1,2,3,7,127,255,256,257,0xffff,0x10000,
      0x7ffffe,0x7fffff,0x800000,0x800001,0xfffffe,0xffffff)
def signed24(x):return x-(1<<24) if x&0x800000 else x

def cases():
    rng=random.Random(0x5C6424)
    return [(x,y) for x in EDGE for y in EDGE]+[
        (rng.randrange(1<<24),rng.randrange(1<<24)) for _ in range(1600)]

class Signed24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()

    def plan(self,ops=("SMUL24",),ram=268):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=ram)

    def test_signed_48bit_three_relocations(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],227)
                self.assertEqual(use["private_ram_scratch_bytes"],9)
                self.assertEqual(use["main_ram_total_bytes"],268)
                self.assertEqual(use["zero_page_bytes"],0)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),229)
                self.assertEqual(prg[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536);mem[code:code+227]=prg[2:]
                orig=bytes(mem[code:code+227])
                cpu=CPU(mem)
                ep=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(ep,code+156)
                sp=cpu.sp
                for x,y in cases():
                    xb=x.to_bytes(3,"little")+bytes([0xa5])
                    yb=y.to_bytes(3,"little")+bytes([0x6a])
                    mem[io:io+4]=xb;mem[io+4:io+8]=yb
                    mem[io+8:io+16]=bytes([0xdd])*8
                    cpu.d=0;cpu.c=(x^y)&1
                    cpu.call(ep,90000)
                    got=int.from_bytes(mem[io+8:io+14],"little")
                    expected=(signed24(x)*signed24(y)) & ((1<<48)-1)
                    self.assertEqual(got,expected,(code,x,y))
                    self.assertEqual(bytes(mem[io+14:io+16]),bytes([0xdd])*2)
                    self.assertEqual(bytes(mem[io:io+4]),xb)
                    self.assertEqual(bytes(mem[io+4:io+8]),yb)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+227]),orig)

    def test_multi_operation_lifetime_and_limits(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(
                ("SMUL24","UMUL24","SMUL16_SHR8","URECIP16_Q16"),
                ram=707),Path(td))
            use=man["resource_use"]
            self.assertEqual(use["main_ram_total_bytes"],707)
            self.assertEqual(use["private_ram_scratch_bytes"],9)
            self.assertEqual(use["zero_page_bytes"],0)
            entry={v["api"]:int(v["entry"][1:],16) for v in man["operations"]}
            image=(Path(td)/"math_selective.prg").read_bytes()
            mem=bytearray(65536);mem[0x8000:0x8000+len(image)-2]=image[2:]
            cpu=CPU(mem)
            rng=random.Random(0x64245C6)
            for _ in range(260):
                x,y=rng.randrange(1<<24),rng.randrange(1<<24)
                mem[0xc000:0xc003]=x.to_bytes(3,"little")
                mem[0xc004:0xc007]=y.to_bytes(3,"little")
                cpu.d=0
                cpu.call(entry["MATH_SMUL24"],90000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00e],"little"),
                                 (signed24(x)*signed24(y))&((1<<48)-1))
                cpu.call(entry["MATH_UMUL24"],90000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00e],"little"),x*y)
                cpu.call(entry["MATH_SMUL16_SHR8"],50000)
                sx=(x&0xffff)-(65536 if x&0x8000 else 0)
                sy=(y&0xffff)-(65536 if y&0x8000 else 0)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00b],"little"),
                                 (sx*sy>>8)&0xffffff)
                d=rng.randrange(65536)
                mem[0xc014:0xc016]=d.to_bytes(2,"little")
                cpu.call(entry["MATH_URECIP16_Q16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc018:0xc01b],"little"),
                                 65536//d if d else 0)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=267),Path(td)/"no_room")

if __name__=="__main__":
    unittest.main()
