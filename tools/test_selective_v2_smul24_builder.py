#!/usr/bin/env python3
"""Independent full-public signed 24-bit builder and shared unsigned producer.

Check same linked image and ZP/table ownership, exact 512-case public ABI for
interleaved UMUL24/SMUL24, matched signed cycle model and compact fallback.
"""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smul24 as speed
import selective_v2_fast_umul24 as v2

FAST=speed.FAST
COMPACT=speed.COMPACT
OPS=("UMUL24","SMUL24")


class SharedSignedV2UMUL24(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,obj="speed",zp=24,ram=3000,pinned=False):
        return math_builder.create_plan(self.index,list(OPS),
            objective=obj,zp_budget=zp,ram_budget=ram,
            pins={api:FAST for api in OPS} if pinned else None,
            workload_calls={api:100 for api in OPS} if obj=="speed" else None)

    def test_speed_selection_shared_image_and_interleaved_correctness(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                result=speed.bench_smul24(linker.MODULES["MATH_SMUL24"],
                    code,io,io+0x40,linker.ROOT,zp)
                self.assertEqual(result["cases"],512)
                self.assertEqual(result["corpus_sha256"],speed.CORPUS_SHA256)
                self.assertLess(result["mean_cycles"][FAST],
                                result["mean_cycles"][COMPACT])
                print("SMUL24_BIASED_PAIRED_SPEED",hex(code),
                      round(result["mean_cycles"][FAST],3),
                      round(result["mean_cycles"][COMPACT],3),flush=True)
                folder=Path(td)
                man=linker.build(self.plan(),folder,memory={
                    "code_base":code,"math_io":io,"zp_base":zp,
                    "scratch_base":io+0x40})
                self.assertEqual(len(man["link_order"]),1)
                self.assertEqual({e["variant"] for e in man["operations"]},
                                 {FAST})
                self.assertEqual(man["resource_use"]["zero_page_bytes"],24)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
                positions,end=v2.layout(code)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],
                                 end-code+32)
                img=(folder/"math_selective.prg").read_bytes()
                self.assertEqual(img[:2],code.to_bytes(2,"little"))
                self.assertEqual(len(img),2+end-code)
                entries={e["api"]:int(e["entry"][1:],16)
                         for e in man["operations"]}
                self.assertEqual(entries["MATH_UMUL24"],code)
                self.assertTrue(code<entries["MATH_SMUL24"]<code+512)
                mem=bytearray(65536)
                mem[code:end]=img[2:]
                cpu=CPU(mem)
                sp=cpu.sp
                for i,(x,y) in enumerate(speed.corpus()):
                    xb=x.to_bytes(3,"little")
                    yb=y.to_bytes(3,"little")
                    for name in ("MATH_UMUL24","MATH_SMUL24"):
                        mem[io:io+4]=xb+bytes([0x6a])
                        mem[io+4:io+8]=yb+bytes([0xa5])
                        mem[io+8:io+16]=bytes([0xcc]*6+[0x49,0x59])
                        cpu.a=(x^i)&255;cpu.x=(y>>8)&255
                        cpu.y=(i*19)&255;cpu.c=i&1;cpu.d=0
                        cpu.call(entries[name],100000)
                        a= speed.signed(x) if name=="MATH_SMUL24" else x
                        b= speed.signed(y) if name=="MATH_SMUL24" else y
                        self.assertEqual(
                            int.from_bytes(mem[io+8:io+14],"little"),
                            (a*b)&speed.MASK48,(name,i,x,y))
                        self.assertEqual(cpu.c,0)
                        self.assertEqual(cpu.sp,sp)
                        self.assertEqual(bytes(mem[io:io+4]),xb+bytes([0x6a]))
                        self.assertEqual(bytes(mem[io+4:io+8]),yb+bytes([0xa5]))
                        self.assertEqual(bytes(mem[io+14:io+16]),bytes([0x49,0x59]))

    def test_zero_zp_compact_and_pin_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            compact=linker.build(self.plan(obj="size",zp=0,ram=1000),
                                 Path(td))
            self.assertEqual({e["variant"] for e in compact["operations"]},
                             {COMPACT})
            self.assertEqual(compact["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(len(compact["link_order"]),2)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(obj="size",zp=0,ram=3000,pinned=True),
                             Path(td)/"nozp")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(obj="size",ram=2500,pinned=True),
                             Path(td)/"no_ram")


if __name__=="__main__":
    unittest.main()
