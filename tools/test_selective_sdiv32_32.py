#!/usr/bin/env python3
"""Exact signed 32/32 DIV/MOD public ABI and shared-code CPU-model tests."""
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
from test_selective_sdiv32_16 import reference as reference16

N_EDGE=(0,1,2,3,127,255,65535,65536,65537,0x7fffffff,
        0x80000000,0x80000001,0xfffffffe,0xffffffff)
D_EDGE=(0,1,2,3,127,128,255,65535,65536,0x7fffffff,0x80000000,0xffffffff)
def signed32(v):return v-(1<<32) if v&0x80000000 else v
def reference(n,d):
    n,d=signed32(n),signed32(d)
    if d==0:return 0,0,1
    q=abs(n)//abs(d)
    if (n<0)!=(d<0):q=-q
    r=n-q*d
    return q&0xffffffff,r&0xffffffff,0

def corpus():
    rng=random.Random(0x5D3232)
    return [(n,d) for n in N_EDGE for d in D_EDGE]+[
        (rng.getrandbits(32),rng.getrandbits(32)) for _ in range(1150)]

class SDIV32x32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ops=("SDIV32_32","SMOD32_32"),ram=453):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=ram)

    def test_both_entries_full_result_three_relocations(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                m=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                u=m["resource_use"]
                self.assertEqual(u["image_span_bytes"],412)
                self.assertEqual(u["main_ram_total_bytes"],453)
                self.assertEqual(u["private_ram_scratch_bytes"],9)
                self.assertEqual(u["zero_page_bytes"],0)
                self.assertEqual(len(m["link_order"]),1)
                entry={v["api"]:int(v["entry"][1:],16) for v in m["operations"]}
                self.assertEqual(entry["MATH_SDIV32_32"],entry["MATH_SMOD32_32"])
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),414)
                self.assertEqual(prg[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536)
                mem[code:code+412]=prg[2:]
                original=bytes(mem[code:code+412])
                cpu=CPU(mem);sp=cpu.sp
                for i,(n,d) in enumerate(corpus()):
                    nbytes=n.to_bytes(4,"little")
                    dbytes=d.to_bytes(4,"little")
                    mem[io+16:io+20]=nbytes
                    mem[io+20:io+24]=dbytes
                    mem[io+24:io+28]=bytes([0xcc])*4
                    mem[io+28:io+32]=bytes([0xdd])*4
                    cpu.d=0;cpu.c=(n^d^i)&1
                    cpu.call(entry["MATH_SDIV32_32" if i&1 else "MATH_SMOD32_32"],110000)
                    result=(int.from_bytes(mem[io+24:io+28],"little"),
                            int.from_bytes(mem[io+28:io+32],"little"),cpu.c)
                    self.assertEqual(result,reference(n,d),(code,n,d))
                    self.assertEqual(bytes(mem[io+16:io+20]),nbytes)
                    self.assertEqual(bytes(mem[io+20:io+24]),dbytes)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+412]),original)

    def test_independent_and_mixed_link_abi_and_ram_budget(self):
        with tempfile.TemporaryDirectory() as td:
            for api in ("SDIV32_32","SMOD32_32"):
                m=linker.build(self.plan((api,)),Path(td)/api)
                self.assertEqual(m["resource_use"]["main_ram_total_bytes"],453)
            mixed=linker.build(self.plan(
                ("SDIV32_32","SMOD32_32","SDIV32_16","SMOD32_16","UMUL16"),
                ram=821),Path(td)/"mixed")
            self.assertEqual(mixed["resource_use"]["main_ram_total_bytes"],821)
            self.assertEqual(mixed["resource_use"]["private_ram_scratch_bytes"],9)
            self.assertEqual(mixed["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(len(mixed["link_order"]),3)
            entry={v["api"]:int(v["entry"][1:],16) for v in mixed["operations"]}
            prg=(Path(td)/"mixed"/"math_selective.prg").read_bytes()
            mem=bytearray(65536);mem[0x8000:0x8000+len(prg)-2]=prg[2:]
            cpu=CPU(mem);rng=random.Random(0x5D32326)
            for i in range(300):
                n,d=rng.getrandbits(32),rng.getrandbits(32)
                mem[0xc010:0xc014]=n.to_bytes(4,"little")
                mem[0xc014:0xc018]=d.to_bytes(4,"little")
                cpu.d=0
                cpu.call(entry["MATH_SDIV32_32" if i&1 else "MATH_SMOD32_32"],110000)
                self.assertEqual((int.from_bytes(mem[0xc018:0xc01c],"little"),
                                  int.from_bytes(mem[0xc01c:0xc020],"little"),cpu.c),
                                 reference(n,d))
                cpu.call(entry["MATH_SDIV32_16" if i&1 else "MATH_SMOD32_16"],110000)
                self.assertEqual((int.from_bytes(mem[0xc018:0xc01c],"little"),
                                  int.from_bytes(mem[0xc01c:0xc01e],"little"),cpu.c),
                                 reference16(n,d&65535))
                x,y=rng.randrange(65536),rng.randrange(65536)
                mem[0xc000:0xc002]=x.to_bytes(2,"little")
                mem[0xc004:0xc006]=y.to_bytes(2,"little")
                cpu.call(entry["MATH_UMUL16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00c],"little"),x*y)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=452),Path(td)/"no_space")
if __name__=="__main__":
    unittest.main()
