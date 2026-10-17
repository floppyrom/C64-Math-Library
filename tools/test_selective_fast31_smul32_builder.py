#!/usr/bin/env python3
"""Builder-linked signed FAST31: full64 ABI, relocation, ZP/page budget and mixing."""
from __future__ import annotations
import random
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_fast31_umul32 as fast31

IDENT="link:fast31-v2-signed"
UNSIGNED="link:fast31-v2-public"
MASK=(1<<64)-1

def signed(x):
    return x-(1<<32) if x&0x80000000 else x

class SignedFAST31BuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=("SMUL32",),zp=31,ram=3000,pins=None):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=zp,ram_budget=ram,
            pins=pins or {"SMUL32":IDENT})

    def test_signed_two_maps_exact_full64_and_qualified_source(self):
        rng=random.Random(0x64325131)
        edges=(0,1,2,255,256,65535,0x7fffffff,0x80000000,0xffffffff)
        pairs=[(x,y) for x in edges for y in edges]
        pairs.extend((rng.getrandbits(32),rng.getrandbits(32)) for _ in range(192))
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"zp_base":zp})
                end=fast31.layout(code)[1]
                self.assertEqual(man["operations"][0]["variant"],IDENT)
                self.assertEqual(man["resource_use"]["image_span_bytes"],end-code)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],31)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],end-code+32)
                deps={x["source_path"] for x in man["operations"][0]["dependencies"]}
                self.assertEqual(deps,{"tools/selective_fast31_umul32.py",
                    "v2_pareto_fast/resident/modules/pareto_umul32.a"})
                ep=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(ep,code)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                mem=bytearray(65536)
                mem[code:end]=prg[2:]
                cpu=CPU(mem);sp=cpu.sp
                for i,(x,y) in enumerate(pairs):
                    xb=x.to_bytes(4,"little");yb=y.to_bytes(4,"little")
                    mem[io:io+4]=xb;mem[io+4:io+8]=yb
                    mem[io+8:io+16]=b"\xa5"*8
                    cpu.d=0;cpu.c=i&1
                    cpu.call(ep,12000)
                    self.assertEqual(int.from_bytes(mem[io+8:io+16],"little"),
                                      (signed(x)*signed(y))&MASK,(code,x,y))
                    self.assertEqual(mem[io:io+4],xb)
                    self.assertEqual(mem[io+4:io+8],yb)
                    self.assertEqual(cpu.sp,sp)
                    self.assertEqual(cpu.c,0)

    def test_resource_guards_and_mixed_fast31_zp_reuse(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=2591),folder/"ram")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(zp=30),folder/"zp")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(),folder/"reserved",memory={
                    "zp_reserved":[{"start":"$60","end":"$60"}]})
            plan=self.plan(ops=("SMUL32","UMUL32"),ram=5152,pins={
                "SMUL32":IDENT,"UMUL32":UNSIGNED})
            man=linker.build(plan,folder/"both")
            self.assertEqual(man["resource_use"]["zero_page_bytes"],31)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],5152)
            entries={r["api"]:int(r["entry"][1:],16) for r in man["operations"]}
            prg=(folder/"both"/"math_selective.prg").read_bytes()
            mem=bytearray(65536);mem[0x8000:0x8000+len(prg)-2]=prg[2:]
            cpu=CPU(mem);rng=random.Random(0x3156432)
            for i in range(96):
                x=rng.getrandbits(32);y=rng.getrandbits(32)
                xb=x.to_bytes(4,"little");yb=y.to_bytes(4,"little")
                mem[0xc000:0xc004]=xb;mem[0xc004:0xc008]=yb
                api="MATH_SMUL32" if i&1 else "MATH_UMUL32"
                cpu.c=i&1;cpu.d=0
                cpu.call(entries[api],12000)
                want=((signed(x)*signed(y))&MASK) if api=="MATH_SMUL32" else x*y
                self.assertEqual(int.from_bytes(mem[0xc008:0xc010],"little"),want)
                self.assertEqual(mem[0xc000:0xc004],xb)
                self.assertEqual(mem[0xc004:0xc008],yb)
                self.assertEqual(cpu.c,0)

if __name__=="__main__":
    unittest.main()
