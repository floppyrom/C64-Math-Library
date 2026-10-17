#!/usr/bin/env python3
"""Portable SMUL16 full-domain sign correction, relocations, and scratch-sharing."""
from __future__ import annotations
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker as linker
from mini6502 import CPU

EDGE=(0,1,2,3,7,127,128,255,256,257,32767,32768,32769,
      65534,65535,0x8001,0xff00,0x7f00,0x100,0x101)

def signed(v): return v-65536 if v&32768 else v

def corpus():
    rng=random.Random(0x5C6416)
    return [(x,y) for x in EDGE for y in EDGE]+[
        (rng.randrange(65536),rng.randrange(65536)) for _ in range(1800)]

class Signed16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=("SMUL16",),ram=199):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=ram)

    def test_full_signed_32_result_and_relocation(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],161)
                self.assertEqual(use["private_ram_scratch_bytes"],6)
                self.assertEqual(use["main_ram_total_bytes"],199)
                self.assertEqual(use["zero_page_bytes"],0)
                image=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(image),163)
                self.assertEqual(image[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536)
                mem[code:code+161]=image[2:]
                orig=bytes(mem[code:code+161])
                cpu=CPU(mem)
                entry=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(entry,code+108)
                stack=cpu.sp
                for x,y in corpus():
                    xbytes=x.to_bytes(2,"little")+bytes((0xa5,0x5a))
                    ybytes=y.to_bytes(2,"little")+bytes((0x6b,0x7c))
                    mem[io:io+4]=xbytes
                    mem[io+4:io+8]=ybytes
                    mem[io+8:io+16]=bytes([0xdd])*8
                    cpu.d=0
                    cpu.c=(x^y)&1
                    cpu.call(entry,50000)
                    expected=(signed(x)*signed(y))&0xffffffff
                    got=int.from_bytes(mem[io+8:io+12],"little")
                    self.assertEqual(got,expected,(code,hex(x),hex(y)))
                    self.assertEqual(bytes(mem[io+12:io+16]),bytes([0xdd])*4)
                    self.assertEqual(bytes(mem[io:io+4]),xbytes)
                    self.assertEqual(bytes(mem[io+4:io+8]),ybytes)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,stack)
                self.assertEqual(bytes(mem[code:code+161]),orig)

    def test_global_scratch_lifetime_and_budget(self):
        with tempfile.TemporaryDirectory() as td:
            plan=self.plan(("SMUL16","UMUL24","URECIP16_Q16"),ram=457)
            man=linker.build(plan,Path(td))
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],457)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],9)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            entry={v["api"]:int(v["entry"][1:],16) for v in man["operations"]}
            image=(Path(td)/"math_selective.prg").read_bytes()
            mem=bytearray(65536)
            mem[0x8000:0x8000+len(image)-2]=image[2:]
            cpu=CPU(mem)
            rng=random.Random(0x5C6416A)
            for _ in range(360):
                x,y=rng.randrange(65536),rng.randrange(65536)
                mem[0xc000:0xc002]=x.to_bytes(2,"little")
                mem[0xc004:0xc006]=y.to_bytes(2,"little")
                cpu.d=0
                cpu.call(entry["MATH_SMUL16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00c],"little"),
                                 (signed(x)*signed(y))&0xffffffff)
                a,b=rng.randrange(1<<24),rng.randrange(1<<24)
                mem[0xc000:0xc003]=a.to_bytes(3,"little")
                mem[0xc004:0xc007]=b.to_bytes(3,"little")
                cpu.call(entry["MATH_UMUL24"],75000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00e],"little"),a*b)
                d=rng.randrange(65536)
                mem[0xc014:0xc016]=d.to_bytes(2,"little")
                cpu.call(entry["MATH_URECIP16_Q16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc018:0xc01b],"little"),
                                 65536//d if d else 0)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=198),Path(td)/"no_room")

if __name__=="__main__":
    unittest.main()
