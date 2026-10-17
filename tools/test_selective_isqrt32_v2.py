#!/usr/bin/env python3
"""V2 source-derived highword ISQRT32: exact relocation and matched CPU cycles."""
from __future__ import annotations
import hashlib
from math import isqrt
import random
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU,Assembler

PORTABLE="link:radix4-zerozp"
FAST="link:v2-highword-source"

def operands():
    data=[0,1,2,3,4,7,8,9,15,16,17,24,25,26,255,256,257,
          65534,65535,65536,65537,0x7fffffff,0x80000000,
          0xfffffffe,0xffffffff]
    for x in (0,1,2,3,15,16,127,128,255,256,257,32767,32768,
              65534,65535):
        data.extend(y for y in range(x*x-2,x*x+3) if 0<=y<2**32)
    rng=random.Random(0x3215A2)
    data.extend(rng.getrandbits(32) for _ in range(900))
    data.extend(((rng.getrandbits(16)<<16)|rng.randrange(256)) for _ in range(100))
    return list(dict.fromkeys(data))


class HistoricalV2Root32Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def build(self,path,variant,code,io,zp):
        p=math_builder.create_plan(self.index,["ISQRT32"],
            pins={"ISQRT32":variant},zp_budget=7,ram_budget=1100)
        return selective_linker.build(p,Path(path),memory={
            "code_base":code,"math_io":io,"zp_base":zp})

    def test_full_range_relocations_source_tables_and_exact_cycles(self):
        values=operands()
        self.assertGreater(len(values),1050)
        for code,io,zp in ((0x8000,0xc000,0x90),
                           (0x7123,0xc040,0xb0)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                totals={}
                for variant in (PORTABLE,FAST):
                    m=self.build(td,variant,code,io,zp)
                    r=m["resource_use"]
                    self.assertEqual((r["code_and_tables_bytes"],r["zero_page_bytes"],
                        r["private_ram_scratch_bytes"]),
                        (960,7,0) if variant==FAST else (204,0,10))
                    self.assertEqual(r["main_ram_total_bytes"],992 if variant==FAST else 246)
                    self.assertEqual(len(m["link_order"]),1)
                    self.assertEqual(m["operations"][0]["variant"],variant)
                    if variant==FAST:
                        self.assertEqual(m["operations"][0]["dependencies"][0]["source_path"],
                            "relocatable_source/v2_pareto_fast/isqrt32_direct_highword_normal.inc")
                        self.assertEqual(len(m["operations"][0]["dependencies"]),2)
                        self.assertEqual([x["bytes"] for x in m["operations"][0]["segments"]],
                                         [192,256,256,256])
                    prg=(Path(td)/"math_selective.prg").read_bytes()
                    self.assertEqual(hashlib.sha256(prg).hexdigest(),m["prg_sha256"])
                    cpu=CPU(bytearray(65536))
                    cpu.mem[code:code+len(prg)-2]=prg[2:]
                    before=bytes(cpu.mem[code:code+len(prg)-2])
                    entry=int(m["operations"][0]["entry"][1:],16)
                    self.assertEqual(entry,code)
                    sp=cpu.sp
                    total=0
                    for j,n in enumerate(values):
                        cpu.mem[io+16:io+20]=n.to_bytes(4,"little")
                        cpu.mem[io+8:io+12]=b"\x55\x55\x96\x69"
                        cpu.x=j&255;cpu.y=(j*37)&255
                        x,y=cpu.x,cpu.y
                        cpu.c=j&1;cpu.d=0
                        cycle=cpu.call(entry,90000)
                        got=int.from_bytes(cpu.mem[io+8:io+10],"little")
                        self.assertEqual(got,isqrt(n),(variant,hex(n),hex(code)))
                        self.assertEqual(cpu.mem[io+8:io+12][2:],b"\x96\x69")
                        self.assertEqual(cpu.mem[io+16:io+20],n.to_bytes(4,"little"))
                        self.assertEqual((cpu.x,cpu.y,cpu.sp,cpu.c),(x,y,sp,0))
                        total+=cycle
                    self.assertEqual(bytes(cpu.mem[code:code+len(prg)-2]),before)
                    totals[variant]=total
                print("ISQRT32 paired exact cycles",hex(code),len(values),totals,
                      "fast mean",totals[FAST]/len(values),flush=True)
                self.assertLess(totals[FAST],totals[PORTABLE])

    def test_v2_table_math_and_source_accounting(self):
        # Tables recomputed from the mathematical contract, not a resident PRG.
        with tempfile.TemporaryDirectory() as td:
            m=self.build(td,FAST,0x8000,0xc000,0x90)
            prg=(Path(td)/"math_selective.prg").read_bytes()[2:]
            self.assertEqual(len(prg),960)
            # 192 code bytes then three contiguous 256-byte lookup pages.
            for x in range(256):
                self.assertEqual(prg[192+x],x*x&255)
                self.assertEqual(prg[448+x],x*x>>8)
                self.assertEqual(prg[704+x],isqrt((x<<8)|255))
            self.assertFalse(next(v for v in selective_linker.available_variants()["MATH_ISQRT32"]
                if v["id"]==FAST)["requires_writable_code"])
            with self.assertRaises(selective_linker.LinkError):
                plan=math_builder.create_plan(self.index,["ISQRT32"],
                    pins={"ISQRT32":FAST},zp_budget=6)
                selective_linker.build(plan,Path(td)/"reject")
            with self.assertRaises(selective_linker.LinkError):
                plan=math_builder.create_plan(self.index,["ISQRT32"],
                    pins={"ISQRT32":FAST},zp_budget=7,ram_budget=991)
                selective_linker.build(plan,Path(td)/"reject2")

    def test_mixed_root16_and_root32_selection(self):
        with tempfile.TemporaryDirectory() as td:
            p=math_builder.create_plan(self.index,["ISQRT16","ISQRT32"],
                pins={"ISQRT32":FAST},zp_budget=7,ram_budget=3500)
            m=selective_linker.build(p,Path(td),memory={
                "code_base":0x7123,"math_io":0xc040,"zp_base":0xb0})
            self.assertEqual(set(m["link_exports"]),{"MATH_ISQRT16","MATH_ISQRT32"})
            self.assertEqual(m["resource_use"]["zero_page_bytes"],7)
            self.assertEqual(len(m["link_order"]),2)


if __name__=="__main__":unittest.main()
