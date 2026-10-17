#!/usr/bin/env python3
"""Full-width unsigned ISQRT32 selective-source correctness and resource gates."""
from __future__ import annotations
from math import isqrt
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


def cases():
    values=[0,1,2,3,4,7,8,9,15,16,17,24,25,26,255,256,257,
        65534,65535,65536,65537,0x7fffffff,0x80000000,
        0xfffffffe,0xffffffff]
    for x in (0,1,2,3,15,16,127,128,255,256,257,32767,32768,
              65534,65535):
        v=x*x
        values.extend(y for y in range(v-2,v+3) if 0<=y<=0xffffffff)
    rng=random.Random(0x15A20326)
    values.extend(rng.getrandbits(32) for _ in range(1150))
    return list(dict.fromkeys(values))


class SelectiveISQRT32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,apis=("ISQRT32",),**kw):
        return math_builder.create_plan(self.index,list(apis),**kw)

    def test_source_binary_full_domain_and_relocations(self):
        for origin,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(origin=origin),tempfile.TemporaryDirectory() as d:
                plan=self.plan(zp_budget=0,ram_budget=246)
                manifest=selective_linker.build(plan,Path(d),memory={
                    "code_base":origin,"math_io":io})
                resources=manifest["resource_use"]
                self.assertEqual(resources["code_and_tables_bytes"],204)
                self.assertEqual(resources["image_span_bytes"],204)
                self.assertEqual(resources["private_ram_scratch_bytes"],10)
                self.assertEqual(resources["zero_page_bytes"],0)
                self.assertEqual(resources["main_ram_total_bytes"],246)
                self.assertEqual(manifest["operations"][0]["variant"],"link:radix4-zerozp")
                prg=(Path(d)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),206)
                self.assertEqual(prg[:2],origin.to_bytes(2,"little"))
                cpu=CPU(bytearray(65536))
                cpu.mem[origin:origin+204]=prg[2:]
                before=bytes(cpu.mem[origin:origin+204])
                entry=int(manifest["operations"][0]["entry"][1:],16)
                self.assertEqual(entry,origin)
                sp=cpu.sp
                for index,n in enumerate(cases()):
                    cpu.mem[io+16:io+20]=n.to_bytes(4,"little")
                    cpu.mem[io+8:io+12]=b"\x55\x55\x96\x69"
                    cpu.x=index&255;cpu.y=(index*31)&255
                    oldx,oldy=cpu.x,cpu.y
                    cpu.c=index&1;cpu.d=0
                    cpu.call(entry,18000)
                    root=int.from_bytes(cpu.mem[io+8:io+10],"little")
                    self.assertEqual(root,isqrt(n),(origin,hex(n)))
                    self.assertEqual(cpu.mem[io+8:io+12][2:],b"\x96\x69")
                    self.assertEqual(cpu.mem[io+16:io+20],n.to_bytes(4,"little"))
                    self.assertEqual((cpu.c,cpu.x,cpu.y,cpu.sp),(0,oldx,oldy,sp))
                self.assertEqual(bytes(cpu.mem[origin:origin+204]),before)

    def test_global_memory_budget_and_mixed_isqrt16(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(self.plan(zp_budget=0,ram_budget=245),Path(d))
            self.assertFalse((Path(d)/"math_selective.prg").exists())
            mixed=selective_linker.build(self.plan(
                ("ISQRT32","ISQRT16"),zp_budget=0,ram_budget=1800),
                Path(d))
            self.assertEqual(set(mixed["link_exports"]),{"MATH_ISQRT32","MATH_ISQRT16"})
            self.assertEqual(mixed["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(mixed["resource_use"]["private_ram_scratch_bytes"],10)
            self.assertEqual(len(mixed["link_order"]),2)
            self.assertEqual(sum(op["api"]=="MATH_ISQRT32"
                                 for op in mixed["operations"]),1)

    def test_pin_and_reserved_scratch(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.plan(pins={"ISQRT32":"link:radix4-zerozp"},zp_budget=0)
            manifest=selective_linker.build(p,Path(d))
            self.assertEqual(manifest["operations"][0]["variant"],"link:radix4-zerozp")
            rejected=Path(d)/"overlap"
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(p,rejected,memory={"reserved":[
                    {"start":"$C020","end":"$C029"}]})
            self.assertFalse((rejected/"math_selective.prg").exists())


if __name__=="__main__":
    unittest.main()
