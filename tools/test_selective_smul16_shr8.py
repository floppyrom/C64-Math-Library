#!/usr/bin/env python3
"""Exact signed Q8.8 scaled product, full CPU-model/ABI/relocation qualification."""
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

EDGES=(0,1,2,3,7,127,255,256,257,32767,32768,32769,65534,
       65535,0x8001,0xff00,0x7f00)
def signed(v):return v-65536 if v&32768 else v
def corpus():
    rng=random.Random(0x5C641608)
    return [(x,y) for x in EDGES for y in EDGES]+[
        (rng.randrange(65536),rng.randrange(65536)) for _ in range(1800)]

class SMUL16SHR8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.index=math_builder.operation_index()
    def plan(self,ops=("SMUL16_SHR8",),ram=222):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=ram)

    def test_signed_24bit_three_relocations(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                res=man["resource_use"]
                self.assertEqual(res["image_span_bytes"],184)
                self.assertEqual(res["main_ram_total_bytes"],222)
                self.assertEqual(res["zero_page_bytes"],0)
                self.assertEqual(res["private_ram_scratch_bytes"],6)
                img=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(img),186)
                self.assertEqual(img[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536);mem[code:code+184]=img[2:]
                before=bytes(mem[code:code+184])
                cpu=CPU(mem)
                ep=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(ep,code+161)
                stack=cpu.sp
                for x,y in corpus():
                    xb=x.to_bytes(2,"little")+bytes([0xa5,0x5a])
                    yb=y.to_bytes(2,"little")+bytes([0x6b,0x7c])
                    mem[io:io+4]=xb;mem[io+4:io+8]=yb
                    mem[io+8:io+16]=bytes([0xdd])*8
                    cpu.c=(x^y)&1;cpu.d=0
                    cpu.call(ep,50000)
                    expected=(signed(x)*signed(y)>>8)&0xffffff
                    actual=int.from_bytes(mem[io+8:io+11],"little")
                    self.assertEqual(actual,expected,(code,x,y))
                    self.assertEqual(bytes(mem[io+12:io+16]),bytes([0xdd])*4)
                    self.assertEqual(bytes(mem[io:io+4]),xb)
                    self.assertEqual(bytes(mem[io+4:io+8]),yb)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,stack)
                self.assertEqual(bytes(mem[code:code+184]),before)

    def test_independent_sources_mixed_calls_and_minimum_budget(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(
                ("SMUL16_SHR8","SMUL16","UMUL24","URECIP16_Q16"),ram=641),
                Path(td))
            res=man["resource_use"]
            self.assertEqual(res["main_ram_total_bytes"],641)
            self.assertEqual(res["private_ram_scratch_bytes"],9)
            self.assertEqual(res["zero_page_bytes"],0)
            image=(Path(td)/"math_selective.prg").read_bytes()
            mem=bytearray(65536);mem[0x8000:0x8000+len(image)-2]=image[2:]
            cpu=CPU(mem)
            entry={row["api"]:int(row["entry"][1:],16)
                   for row in man["operations"]}
            rng=random.Random(0x1685C64)
            for _ in range(260):
                x,y=rng.randrange(65536),rng.randrange(65536)
                mem[0xc000:0xc002]=x.to_bytes(2,"little")
                mem[0xc004:0xc006]=y.to_bytes(2,"little")
                cpu.d=0
                cpu.call(entry["MATH_SMUL16_SHR8"],50000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00b],"little"),
                                 (signed(x)*signed(y)>>8)&0xffffff)
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
                linker.build(self.plan(ram=221),Path(td)/"no_room")

if __name__=="__main__":
    unittest.main()
