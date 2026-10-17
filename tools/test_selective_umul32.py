#!/usr/bin/env python3
"""Independent 32x32 -> 64-bit unsigned source and mixed-call regression."""
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

EDGES=(0,1,2,3,7,127,255,256,257,65535,65536,
       0x7fffffff,0x80000000,0x80000001,0xfffffffe,0xffffffff)

def cases():
    rng=random.Random(0x64C632)
    return [(x,y) for x in EDGES for y in EDGES]+[
        (rng.getrandbits(32),rng.getrandbits(32)) for _ in range(1100)]

class UMUL32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ops=("UMUL32",),ram=248):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=ram)

    def test_unsigned_64bit_result_three_memory_maps(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],204)
                self.assertEqual(use["private_ram_scratch_bytes"],12)
                self.assertEqual(use["main_ram_total_bytes"],248)
                self.assertEqual(use["zero_page_bytes"],0)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),206)
                self.assertEqual(prg[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536);mem[code:code+204]=prg[2:]
                cpu=CPU(mem);original=bytes(mem[code:code+204])
                entry=int(man["operations"][0]["entry"][1:],16)
                stack=cpu.sp
                for x,y in cases():
                    xb=x.to_bytes(4,"little");yb=y.to_bytes(4,"little")
                    mem[io:io+4]=xb;mem[io+4:io+8]=yb
                    mem[io+8:io+16]=bytes([0xdd])*8
                    cpu.d=0;cpu.c=(x^y)&1
                    cpu.call(entry,125000)
                    self.assertEqual(int.from_bytes(mem[io+8:io+16],"little"),
                                     x*y,(code,x,y))
                    self.assertEqual(bytes(mem[io:io+4]),xb)
                    self.assertEqual(bytes(mem[io+4:io+8]),yb)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,stack)
                self.assertEqual(bytes(mem[code:code+204]),original)

    def test_mixed_producers_no_aliases_and_budget(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(
                ("UMUL32","UMUL24","SMUL24","URECIP16_Q16"),ram=730),
                Path(td))
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],730)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],12)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            entry={o["api"]:int(o["entry"][1:],16) for o in man["operations"]}
            prg=(Path(td)/"math_selective.prg").read_bytes()
            mem=bytearray(65536);mem[0x8000:0x8000+len(prg)-2]=prg[2:]
            cpu=CPU(mem);rng=random.Random(0x32C643)
            for _ in range(230):
                x,y=rng.getrandbits(32),rng.getrandbits(32)
                mem[0xc000:0xc004]=x.to_bytes(4,"little")
                mem[0xc004:0xc008]=y.to_bytes(4,"little")
                cpu.d=0;cpu.call(entry["MATH_UMUL32"],125000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc010],"little"),x*y)
                xa,ya=x&0xffffff,y&0xffffff
                cpu.call(entry["MATH_UMUL24"],100000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00e],"little"),xa*ya)
                cpu.call(entry["MATH_SMUL24"],100000)
                sx=xa-(1<<24) if xa&0x800000 else xa
                sy=ya-(1<<24) if ya&0x800000 else ya
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00e],"little"),
                                 (sx*sy)&((1<<48)-1))
                d=rng.randrange(65536)
                mem[0xc014:0xc016]=d.to_bytes(2,"little")
                cpu.call(entry["MATH_URECIP16_Q16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc018:0xc01b],"little"),
                                 65536//d if d else 0)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=247),Path(td)/"reject")

if __name__=="__main__":
    unittest.main()
