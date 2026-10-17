#!/usr/bin/env python3
"""Exact signed32x32 full64 product, legal-NMOS selective source and mixed calls."""
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

def signed32(v):
    return v-(1<<32) if v&0x80000000 else v

def expected(x,y):
    return (signed32(x)*signed32(y))&((1<<64)-1)

class SMUL32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ops=("SMUL32",),ram=337):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=ram)

    def test_full_signed64_at_three_code_and_io_relocations(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],293)
                self.assertEqual(use["private_ram_scratch_bytes"],12)
                self.assertEqual(use["main_ram_total_bytes"],337)
                self.assertEqual(use["zero_page_bytes"],0)
                image=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(image),295)
                self.assertEqual(image[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536)
                mem[code:code+293]=image[2:]
                original=bytes(mem[code:code+293])
                cpu=CPU(mem)
                ep=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(ep,code+204)
                sp=cpu.sp
                for i,(x,y) in enumerate(cases()):
                    xb=x.to_bytes(4,"little")
                    yb=y.to_bytes(4,"little")
                    mem[io:io+4]=xb
                    mem[io+4:io+8]=yb
                    mem[io+8:io+16]=bytes([0xa5])*8
                    cpu.d=0
                    cpu.c=(i^x^y)&1
                    cpu.call(ep,135000)
                    self.assertEqual(int.from_bytes(mem[io+8:io+16],"little"),
                                     expected(x,y),(code,x,y))
                    self.assertEqual(bytes(mem[io:io+4]),xb)
                    self.assertEqual(bytes(mem[io+4:io+8]),yb)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+293]),original)

    def test_zero_zp_and_shared_scratch_across_signed_and_unsigned(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(
                ("SMUL32","UMUL32_SHR16"),ram=582),Path(td))
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],582)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],12)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(len(man["link_order"]),2)
            entry={o["api"]:int(o["entry"][1:],16) for o in man["operations"]}
            img=(Path(td)/"math_selective.prg").read_bytes()
            mem=bytearray(65536)
            mem[0x8000:0x8000+len(img)-2]=img[2:]
            cpu=CPU(mem)
            rng=random.Random(0x5C6432)
            for _ in range(240):
                x,y=rng.getrandbits(32),rng.getrandbits(32)
                mem[0xc000:0xc004]=x.to_bytes(4,"little")
                mem[0xc004:0xc008]=y.to_bytes(4,"little")
                cpu.d=0
                cpu.call(entry["MATH_SMUL32"],135000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc010],"little"),
                                 expected(x,y))
                cpu.call(entry["MATH_UMUL32_SHR16"],125000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00e],"little"),
                                 (x*y)>>16)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=336),Path(td)/"no_ram")

if __name__=="__main__":
    unittest.main()
