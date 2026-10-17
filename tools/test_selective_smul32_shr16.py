#!/usr/bin/env python3
"""Signed arithmetic (X32*Y32)>>16 Q48 CPU ABI and independent relocation checks."""
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
from test_selective_umul32 import cases
from test_selective_smul32 import signed32

class SMUL32SHR16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ops=("SMUL32_SHR16",),ram=378):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=ram)

    def test_exact_signed_shift_48bit_three_memory_maps(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],334)
                self.assertEqual(use["main_ram_total_bytes"],378)
                self.assertEqual(use["private_ram_scratch_bytes"],12)
                self.assertEqual(use["zero_page_bytes"],0)
                image=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(image),336)
                self.assertEqual(image[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536)
                mem[code:code+334]=image[2:]
                original=bytes(mem[code:code+334])
                cpu=CPU(mem)
                entry=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(entry,code+293)
                stack=cpu.sp
                for i,(x,y) in enumerate(cases()):
                    xb=x.to_bytes(4,"little")
                    yb=y.to_bytes(4,"little")
                    mem[io:io+4]=xb
                    mem[io+4:io+8]=yb
                    mem[io+8:io+16]=bytes([0xcc])*8
                    cpu.d=0;cpu.c=(x^y^i)&1
                    cpu.call(entry,125000)
                    z=int.from_bytes(mem[io+8:io+14],"little")
                    self.assertEqual(z,((signed32(x)*signed32(y)) & ((1<<64)-1))>>16,(code,x,y))
                    self.assertEqual(bytes(mem[io:io+4]),xb)
                    self.assertEqual(bytes(mem[io+4:io+8]),yb)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,stack)
                self.assertEqual(bytes(mem[code:code+334]),original)

    def test_ordinary_scratch_lifetime_and_ram_boundaries(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(("SMUL32_SHR16","UMUL32"),
                                       ram=582),Path(td))
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],582)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],12)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(len(man["link_order"]),2)
            entry={r["api"]:int(r["entry"][1:],16) for r in man["operations"]}
            image=(Path(td)/"math_selective.prg").read_bytes()
            mem=bytearray(65536)
            mem[0x8000:0x8000+len(image)-2]=image[2:]
            cpu=CPU(mem)
            rng=random.Random(0x326416)
            for _ in range(290):
                x,y=rng.getrandbits(32),rng.getrandbits(32)
                mem[0xc000:0xc004]=x.to_bytes(4,"little")
                mem[0xc004:0xc008]=y.to_bytes(4,"little")
                cpu.d=0
                cpu.call(entry["MATH_SMUL32_SHR16"],125000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00e],"little"),
                                 ((signed32(x)*signed32(y)) & ((1<<64)-1))>>16)
                cpu.call(entry["MATH_UMUL32"],125000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc010],"little"),x*y)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=377),Path(td)/"too_small")
if __name__=="__main__":
    unittest.main()
