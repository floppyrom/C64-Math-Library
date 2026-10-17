#!/usr/bin/env python3
"""Signed fixed-point 16/16 shifted dividend, Q24/R16, ABI and relocations."""
from __future__ import annotations
import random
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
import math_builder
import selective_linker as linker
from test_selective_sdiv16 import corpus,reference as div16_reference

def signed16(x):return x-65536 if x&32768 else x
def reference(n,d):
    n=signed16(n)<<8
    d=signed16(d)
    if d==0:return 0,0,1
    quotient=abs(n)//abs(d)
    if (n<0)!=(d<0):quotient=-quotient
    remainder=n-quotient*d
    return quotient&0xffffff,remainder&0xffff,0

class SDIV16SHL8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ops=("SDIV16_SHL8",),ram=272):
        return math_builder.create_plan(self.index,list(ops),
            objective="size",zp_budget=0,ram_budget=ram)

    def test_signed_q24_remainder_and_public_memory_three_relocations(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],237)
                self.assertEqual(use["main_ram_total_bytes"],272)
                self.assertEqual(use["private_ram_scratch_bytes"],3)
                self.assertEqual(use["zero_page_bytes"],0)
                image=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(image),239)
                self.assertEqual(image[:2],code.to_bytes(2,"little"))
                memory=bytearray(65536)
                memory[code:code+237]=image[2:]
                original=bytes(memory[code:code+237])
                cpu=CPU(memory)
                entry=int(man["operations"][0]["entry"][1:],16)
                stack=cpu.sp
                for index,(n,d) in enumerate(corpus()):
                    nbytes=n.to_bytes(2,"little")+bytes((0xa5,0x5a))
                    dbytes=d.to_bytes(2,"little")+bytes((0x6b,0x7c))
                    memory[io+16:io+20]=nbytes
                    memory[io+20:io+24]=dbytes
                    memory[io+24:io+28]=bytes((0x42,0x43,0x44,0x45))
                    memory[io+28:io+32]=bytes((0x51,0x52,0x53,0x54))
                    cpu.c=(index^n^d)&1
                    cpu.d=0
                    cpu.call(entry,65000)
                    got=(int.from_bytes(memory[io+24:io+27],"little"),
                         int.from_bytes(memory[io+28:io+30],"little"),cpu.c)
                    self.assertEqual(got,reference(n,d),(code,n,d))
                    self.assertEqual(memory[io+27],0x45)
                    self.assertEqual(bytes(memory[io+30:io+32]),bytes((0x53,0x54)))
                    self.assertEqual(bytes(memory[io+16:io+20]),nbytes)
                    self.assertEqual(bytes(memory[io+20:io+24]),dbytes)
                    self.assertEqual(cpu.sp,stack)
                self.assertEqual(bytes(memory[code:code+237]),original)

    def test_single_and_mixed_ram_scratch_and_budget(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(
                ("SDIV16_SHL8","SDIV16","SMOD16","UMUL16"),ram=589),
                Path(td))
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],589)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],6)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(len(man["link_order"]),3)
            entry={x["api"]:int(x["entry"][1:],16) for x in man["operations"]}
            prg=(Path(td)/"math_selective.prg").read_bytes()
            mem=bytearray(65536)
            mem[0x8000:0x8000+len(prg)-2]=prg[2:]
            cpu=CPU(mem)
            rng=random.Random(0x5D1688)
            for i in range(360):
                n,d=rng.randrange(65536),rng.randrange(65536)
                mem[0xc010:0xc012]=n.to_bytes(2,"little")
                mem[0xc014:0xc016]=d.to_bytes(2,"little")
                cpu.d=0
                cpu.call(entry["MATH_SDIV16_SHL8"],65000)
                self.assertEqual((int.from_bytes(mem[0xc018:0xc01b],"little"),
                                  int.from_bytes(mem[0xc01c:0xc01e],"little"),cpu.c),
                                 reference(n,d))
                cpu.call(entry["MATH_SDIV16" if i&1 else "MATH_SMOD16"],50000)
                self.assertEqual((int.from_bytes(mem[0xc018:0xc01a],"little"),
                                  int.from_bytes(mem[0xc01c:0xc01e],"little"),cpu.c),
                                 div16_reference(n,d))
                x,y=rng.randrange(65536),rng.randrange(65536)
                mem[0xc000:0xc002]=x.to_bytes(2,"little")
                mem[0xc004:0xc006]=y.to_bytes(2,"little")
                cpu.call(entry["MATH_UMUL16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00c],"little"),x*y)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=271),Path(td)/"no_ram")
if __name__=="__main__":
    unittest.main()
