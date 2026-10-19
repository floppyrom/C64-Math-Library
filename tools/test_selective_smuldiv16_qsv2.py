#!/usr/bin/env python3
"""Signed QS plus V2 signed 32/16 Q/R source-link public regression."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smuldiv16_qsv2 as speed

FAST=speed.FAST
SMALL=speed.SMALL

class Fused16QSV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()

    def plan(self,variant=FAST,objective="size",ram=4299,zp=12):
        return math_builder.create_plan(
            self.index,["SMULDIV16"],objective=objective,
            pins={"SMULDIV16":variant} if variant else {},
            workload_calls={"SMULDIV16":100} if objective=="speed" else None,
            zp_budget=zp,ram_budget=ram)

    def test_both_origin_complete_q32_r16_and_operands(self):
        for code,io,zp,scratch in (
                (0x8000,0xc000,0x50,0xc040),
                (0x7123,0xc040,0x70,0xc080)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,
                    "zp_base":zp,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],4263)
                self.assertEqual(use["private_ram_scratch_bytes"],4)
                self.assertEqual(use["zero_page_bytes"],12)
                self.assertEqual(use["main_ram_total_bytes"],4299)
                self.assertEqual(man["operations"][0]["variant"],FAST)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),4265)
                self.assertEqual(prg[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536)
                mem[code:code+4263]=prg[2:]
                immutable=bytes(mem[code:code+4263])
                cpu=CPU(mem)
                entry=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(entry,code+4231)
                sp=cpu.sp
                for x,y,d in speed.corpus():
                    xb=x.to_bytes(2,"little")+bytes((0xa5,0x5a))
                    yb=y.to_bytes(2,"little")+bytes((0x6b,0x7c))
                    db=d.to_bytes(2,"little")+bytes((0xe1,0xe2))
                    mem[io:io+4]=xb
                    mem[io+4:io+8]=yb
                    mem[io+8:io+12]=bytes((0x88,))*4
                    mem[io+16:io+20]=bytes((0x77,))*4
                    mem[io+20:io+24]=db
                    mem[io+24:io+28]=bytes((0x99,))*4
                    mem[io+28:io+32]=bytes((0x21,0x43,0x65,0x87))
                    cpu.d=0
                    cpu.c=(x+y+d)&1
                    cpu.call(entry,100000)
                    product,q,rem,carry=speed.oracle(x,y,d)
                    actual=(int.from_bytes(mem[io+8:io+12],"little"),
                            int.from_bytes(mem[io+16:io+20],"little"),
                            int.from_bytes(mem[io+24:io+28],"little"),
                            int.from_bytes(mem[io+28:io+30],"little"),cpu.c)
                    self.assertEqual(actual,(product,product,q,rem,carry),
                                     (code,x,y,d))
                    self.assertEqual(bytes(mem[io:io+4]),xb)
                    self.assertEqual(bytes(mem[io+4:io+8]),yb)
                    self.assertEqual(bytes(mem[io+20:io+24]),db)
                    self.assertEqual(bytes(mem[io+30:io+32]),
                                     bytes((0x65,0x87)))
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+4263]),immutable)

    def test_matched_public_cycles_and_pareto_budget(self):
        for code,io,scratch,zp in (
                (0x8000,0xc000,0xc040,0x50),
                (0x7123,0xc040,0xc080,0x70)):
            m=speed.bench_smuldiv16(
                linker.MODULES["MATH_SMULDIV16"],
                code,io,scratch,math_builder.ROOT,zp)
            print("SMULDIV16_QS_V2_MATCHED",hex(code),
                  m["mean_cycles"],m["maximum_cycles"],
                  m["p95_cycles"],flush=True)
            self.assertEqual(m["cases"],512)
            self.assertLess(m["mean_cycles"][FAST],m["mean_cycles"][SMALL])
            self.assertLess(m["maximum_cycles"][FAST],m["maximum_cycles"][SMALL])
        for ram,zp,expected in ((4299,12,FAST),(477,0,SMALL),(477,12,SMALL)):
            with tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(None,"speed",ram,zp),Path(td))
                self.assertEqual(man["operations"][0]["variant"],expected)
                self.assertEqual(man["cycle_model_benchmark"]["cases"],512)

    def test_pinned_fast_fails_precise_resource_shortage(self):
        with tempfile.TemporaryDirectory() as td:
            for ram,zp in ((4298,12),(4299,11)):
                with self.subTest(ram=ram,zp=zp):
                    with self.assertRaises(linker.LinkError):
                        linker.build(self.plan(ram=ram,zp=zp),
                                     Path(td)/"fail")

if __name__=="__main__":
    unittest.main()
