#!/usr/bin/env python3
"""Exact unsigned 24/24 DIV/MOD shared public ABI, two relocations and budgets."""
from __future__ import annotations
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU

FAMILY=("MATH_UDIV24","MATH_UMOD24")
MASK=(1<<24)-1


def cases():
    edge=(0,1,2,3,7,15,127,255,256,257,65535,65536,65537,
          8388607,8388608,16777214,16777215)
    items=[(n,d) for n in edge for d in edge]
    rng=random.Random(0x2431017)
    items.extend((rng.getrandbits(24),rng.getrandbits(24)) for _ in range(600))
    items.extend((rng.getrandbits(24),0) for _ in range(64))
    items.extend((rng.getrandbits(24),1<<rng.randrange(24)) for _ in range(64))
    return items


class SelectiveU24Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def build(self,folder,apis=FAMILY,code=0x8000,io=0xc000,budget=226,**kw):
        p=math_builder.create_plan(self.index,list(apis),
           zp_budget=0,ram_budget=budget,**kw)
        return selective_linker.build(p,Path(folder),memory={
            "code_base":code,"math_io":io})

    def test_shared_public_divmod_kernel_alias_and_resources(self):
        with tempfile.TemporaryDirectory() as d:
            for apis in (FAMILY,FAMILY[:1],FAMILY[1:]):
                manifest=self.build(d,apis=apis)
                r=manifest["resource_use"]
                self.assertEqual(r["code_and_tables_bytes"],190)
                self.assertEqual(r["image_span_bytes"],190)
                self.assertEqual(r["private_ram_scratch_bytes"],4)
                self.assertEqual(r["zero_page_bytes"],0)
                self.assertEqual(r["main_ram_total_bytes"],226)
                self.assertEqual(len(manifest["link_order"]),1)
                self.assertEqual(set(manifest["link_exports"]),set(apis))
                self.assertEqual({o["variant"] for o in manifest["operations"]},
                                 {"link:portable-restoring"})
            manifest=self.build(d)
            exports=[item["entry"] for item in manifest["operations"]]
            self.assertEqual(len(set(exports)),1)
            self.assertEqual(exports[0],"$8000")

    def test_24bit_unsigned_arithmetic_preservation_and_relocation(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as d:
                manifest=self.build(d,code=code,io=io)
                prg=(Path(d)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),192)
                cpu=CPU(bytearray(65536))
                cpu.mem[code:code+190]=prg[2:]
                original=bytes(cpu.mem[code:code+190])
                entries=[int(row["entry"][1:],16) for row in manifest["operations"]]
                stack=cpu.sp
                for i,(n,divisor) in enumerate(cases()):
                    for entry in entries:
                        cpu.mem[io+16:io+20]=n.to_bytes(3,"little")+b"\x6A"
                        cpu.mem[io+20:io+24]=divisor.to_bytes(3,"little")+b"\xA9"
                        cpu.mem[io+24:io+28]=b"\x55"*4
                        cpu.mem[io+28:io+32]=b"\x66"*4
                        cpu.c=i&1;cpu.d=0
                        cpu.call(entry,18000)
                        q=int.from_bytes(cpu.mem[io+24:io+27],"little")
                        r=int.from_bytes(cpu.mem[io+28:io+31],"little")
                        self.assertEqual((q,r,cpu.c),
                            (n//divisor if divisor else 0,
                             n%divisor if divisor else 0,int(divisor==0)),
                            (hex(n),hex(divisor),hex(code)))
                        self.assertEqual(cpu.mem[io+16:io+20],n.to_bytes(3,"little")+b"\x6A")
                        self.assertEqual(cpu.mem[io+20:io+24],divisor.to_bytes(3,"little")+b"\xA9")
                        self.assertEqual(cpu.mem[io+27],0x55)
                        self.assertEqual(cpu.mem[io+31],0x66)
                        self.assertEqual(cpu.sp,stack)
                self.assertEqual(bytes(cpu.mem[code:code+190]),original)

    def test_budget_and_disjoint_multifamily(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(selective_linker.LinkError):
                self.build(d,budget=225)
            self.assertFalse((Path(d)/"math_selective.prg").exists())
            p=("MATH_UDIV24","MATH_UMOD24","MATH_UDIV32_16")
            mixed=self.build(d,apis=p,budget=357)
            self.assertEqual(len(mixed["link_order"]),2)
            self.assertEqual(mixed["resource_use"]["code_and_tables_bytes"],321)
            self.assertEqual(mixed["resource_use"]["private_ram_scratch_bytes"],4)
            self.assertEqual(mixed["resource_use"]["main_ram_total_bytes"],357)


if __name__=="__main__":
    unittest.main()
