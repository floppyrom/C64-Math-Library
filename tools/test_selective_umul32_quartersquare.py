#!/usr/bin/env python3
"""Relocated UMUL32 quarter-square transplant: exact full64 and resource proof."""
from __future__ import annotations
import random
import tempfile
import unittest
from pathlib import Path
import math_builder as mb
import selective_linker as linker
from mini6502 import CPU

EDGES=(0,1,2,255,256,65535,0x80000000,0xffffffff)


class UMUL32QuarterSquareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=mb.operation_index()

    def plan(self, ram=2086, ops=("UMUL32",), pins=None):
        return mb.create_plan(self.index,list(ops),objective="size",
                              zp_budget=0,ram_budget=ram,
                              pins=pins or {"UMUL32":"link:quarter-square-32"})

    def test_two_relocations_full64_and_binary_integrity(self):
        rng=random.Random(0xC643200)
        corpus=[(x,y) for x in EDGES for y in EDGES]
        corpus += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(192)]
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                resources=man["resource_use"]
                self.assertEqual(resources["image_span_bytes"],2050)
                self.assertEqual(resources["zero_page_bytes"],0)
                self.assertEqual(resources["private_ram_scratch_bytes"],4)
                self.assertEqual(resources["main_ram_total_bytes"],2086)
                self.assertEqual(man["operations"][0]["variant"],"link:quarter-square-32")
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),2052)
                mem=bytearray(65536)
                mem[code:code+2050]=prg[2:]
                image=bytes(mem[code:code+2050])
                cpu=CPU(mem)
                sp=cpu.sp
                entry=int(man["operations"][0]["entry"][1:],16)
                for i,(x,y) in enumerate(corpus):
                    xb=x.to_bytes(4,"little")
                    yb=y.to_bytes(4,"little")
                    mem[io:io+4]=xb
                    mem[io+4:io+8]=yb
                    mem[io+8:io+16]=b"\\xa5"*8
                    cpu.c=i&1
                    cpu.d=0
                    cpu.call(entry,120000)
                    self.assertEqual(int.from_bytes(mem[io+8:io+16],"little"),
                                     x*y,(code,x,y))
                    self.assertEqual(mem[io:io+4],xb)
                    self.assertEqual(mem[io+4:io+8],yb)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+2050]),image)

    def test_resource_boundary_and_opt_in(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=2085),Path(td)/"tight")
            normal=mb.create_plan(self.index,["UMUL32"],objective="size",
                                  zp_budget=0,ram_budget=248)
            manifest=linker.build(normal,Path(td)/"small")
            self.assertEqual(manifest["operations"][0]["variant"],"link:compact-zerozp")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=2049),Path(td)/"too_small")

if __name__=="__main__":
    unittest.main()
