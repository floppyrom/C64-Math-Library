#!/usr/bin/env python3
"""All six C64 full64, READY and Q48 FAST31 APIs share one builder-emitted image."""
from __future__ import annotations
import random
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
from test_selective_fast31_six_source import OPS,ENTRIES,signed
import selective_fast31_umul32 as fast

ID="link:fast31-shared-full64"
MASK=(1<<64)-1

class FAST31SixBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=OPS,ram=3000,zp=31):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",
            zp_budget=zp,ram_budget=ram,
            pins={op:ID for op in ops})

    def test_one_code_table_image_six_public_entrypoints(self):
        rng=random.Random(0xC6436A)
        edges=(0,1,2,255,256,65535,0x7fffffff,0x80000000,0xffffffff)
        pairs=[(a,b) for a in edges for b in edges]
        pairs.extend((rng.getrandbits(32),rng.getrandbits(32)) for _ in range(160))
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                out=Path(td)
                man=linker.build(self.plan(),out,memory={
                    "code_base":code,"math_io":io,"zp_base":zp})
                end=fast.layout(code)[1]
                self.assertEqual(len(man["link_order"]),1)
                self.assertEqual(man["resource_use"]["image_span_bytes"],end-code)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],end-code+32)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],31)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
                self.assertEqual({x["variant"] for x in man["operations"]},{ID})
                self.assertEqual(len(man["operations"]),6)
                entry={x["api"].removeprefix("MATH_"):int(x["entry"][1:],16)
                       for x in man["operations"]}
                self.assertEqual(entry["UMUL32"],entry["UMUL32_READY"])
                self.assertEqual(entry["SMUL32"],entry["SMUL32_READY"])
                self.assertEqual(len(set(entry.values())),4)
                self.assertTrue(all(code<=p<code+512 for p in entry.values()))
                prg=(out/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),end-code+2)
                mem=bytearray(65536);mem[code:end]=prg[2:]
                cpu=CPU(mem);sp=cpu.sp
                for i,(x,y) in enumerate(pairs):
                    for op in OPS:
                        xb=x.to_bytes(4,"little");yb=y.to_bytes(4,"little")
                        mem[io:io+4]=xb;mem[io+4:io+8]=yb
                        mem[io+8:io+16]=b"\xa5"*8
                        cpu.c=(i^x^y)&1;cpu.d=0
                        cpu.call(entry[op],12000)
                        prod=((signed(x)*signed(y))&MASK) if op.startswith("SMUL") else x*y
                        expected=prod>>16 if op.endswith("SHR16") else prod
                        width=6 if op.endswith("SHR16") else 8
                        self.assertEqual(int.from_bytes(mem[io+8:io+8+width],"little"),
                                         expected,(op,code,x,y))
                        self.assertEqual(bytes(mem[io:io+4]),xb)
                        self.assertEqual(bytes(mem[io+4:io+8]),yb)
                        self.assertEqual(cpu.c,0)
                        self.assertEqual(cpu.sp,sp)

    def test_exact_budget_and_original_compact_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            a=linker.build(self.plan(ram=2592),root/"one")
            self.assertEqual(a["resource_use"]["main_ram_total_bytes"],2592)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=2591),root/"insufficient_ram")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(zp=30),root/"insufficient_zp")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(),root/"reserved_zp",memory={
                    "zp_reserved":[{"start":"$60","end":"$61"}]})
            # No implicit change to the lightweight stock six-entry producer:
            fallback=math_builder.create_plan(self.index,list(OPS),objective="size",
                                               zp_budget=0,ram_budget=419)
            b=linker.build(fallback,root/"low_ram")
            self.assertEqual(b["resource_use"]["main_ram_total_bytes"],419)
            self.assertEqual({x["variant"] for x in b["operations"]},{"link:unified-375"})

if __name__=="__main__":
    unittest.main()
