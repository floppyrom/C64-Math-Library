#!/usr/bin/env python3
"""24x24 => 48-bit unsigned source-linked CPU and ABI qualification."""
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

EDGE=(0,1,2,3,7,15,16,127,128,255,256,257,0xffff,
      0x10000,0x10001,0x7fffff,0x800000,0x800001,0xfffffe,0xffffff)

def corpus():
    rng=random.Random(0xC642448)
    return [(x,y) for x in EDGE for y in EDGE] + [
        (rng.randrange(1<<24),rng.randrange(1<<24)) for _ in range(1500)
    ]

class UMUL24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self, ops=("UMUL24",), budget=197):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=budget)

    def test_48_bit_abi_three_relocations(self):
        tests=corpus()
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],156)
                self.assertEqual(use["private_ram_scratch_bytes"],9)
                self.assertEqual(use["main_ram_total_bytes"],197)
                self.assertEqual(use["zero_page_bytes"],0)
                binary=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(binary),158)
                self.assertEqual(binary[:2],code.to_bytes(2,"little"))
                cpu=CPU(bytearray(65536))
                mem=cpu.mem
                mem[code:code+156]=binary[2:]
                original=bytes(mem[code:code+156])
                entry=int(man["operations"][0]["entry"][1:],16)
                stack=cpu.sp
                for x,y in tests:
                    xbytes=x.to_bytes(3,"little")+bytes([0xb5])
                    ybytes=y.to_bytes(3,"little")+bytes([0x6a])
                    mem[io:io+4]=xbytes
                    mem[io+4:io+8]=ybytes
                    mem[io+8:io+16]=bytes([0xa5])*8
                    cpu.d=0
                    cpu.c=(x^y)&1
                    cpu.call(entry,75000)
                    z=int.from_bytes(mem[io+8:io+14],"little")
                    self.assertEqual(z,x*y,(code,x,y))
                    self.assertEqual(bytes(mem[io+14:io+16]),bytes([0xa5,0xa5]))
                    self.assertEqual(bytes(mem[io:io+4]),xbytes)
                    self.assertEqual(bytes(mem[io+4:io+8]),ybytes)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,stack)
                self.assertEqual(bytes(mem[code:code+156]),original)

    def test_multi_operation_scratch_sharing_and_exact_budget(self):
        with tempfile.TemporaryDirectory() as td:
            m=linker.build(self.plan(
                ("UMUL24","UMUL16","URECIP16_Q16"),budget=404),Path(td))
            self.assertEqual(m["resource_use"]["private_ram_scratch_bytes"],9)
            self.assertEqual(m["resource_use"]["main_ram_total_bytes"],404)
            self.assertEqual(m["resource_use"]["zero_page_bytes"],0)
            entries={x["api"]:int(x["entry"][1:],16) for x in m["operations"]}
            prg=(Path(td)/"math_selective.prg").read_bytes()
            mem=bytearray(65536)
            mem[0x8000:0x8000+len(prg)-2]=prg[2:]
            cpu=CPU(mem)
            rng=random.Random(0x24C64)
            for _ in range(320):
                x=rng.randrange(1<<24)
                y=rng.randrange(1<<24)
                mem[0xc000:0xc003]=x.to_bytes(3,"little")
                mem[0xc004:0xc007]=y.to_bytes(3,"little")
                cpu.d=0
                cpu.call(entries["MATH_UMUL24"],75000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00e],"little"),x*y)
                x16,y16=x&0xffff,y&0xffff
                cpu.call(entries["MATH_UMUL16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00c],"little"),x16*y16)
                d=rng.randrange(65536)
                mem[0xc014:0xc016]=d.to_bytes(2,"little")
                cpu.call(entries["MATH_URECIP16_Q16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc018:0xc01b],"little"),
                                 65536//d if d else 0)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(budget=196),Path(td)/"too_small")

if __name__=="__main__":
    unittest.main()
