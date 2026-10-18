#!/usr/bin/env python3
"""Builder public UMUL24 V2 source, full memory accounting and speed selection."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_v2_fast_umul24 as v2
import selective_speed_umul24 as speed


class SelectiveV2UMUL24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,zp=24,ram=3000,objective="speed",pin=None):
        return math_builder.create_plan(
            self.index,["UMUL24"],objective=objective,
            zp_budget=zp,ram_budget=ram,
            pins={"UMUL24":pin} if pin else None)

    def test_same_512_input_public_cycles_and_best_feasible_variant(self):
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                metrics=speed.bench_umul24(linker.MODULES["MATH_UMUL24"],
                                          code,io,io+0x40,linker.ROOT,zp)
                self.assertEqual(metrics["cases"],512)
                self.assertEqual(metrics["corpus_sha256"],speed.CORPUS_SHA256)
                self.assertLess(metrics["mean_cycles"][speed.FAST],
                                metrics["mean_cycles"][speed.COMPACT])
                folder=Path(td)
                manifest=linker.build(self.plan(),folder,memory={
                    "code_base":code,"math_io":io,"zp_base":zp,
                    "scratch_base":io+0x40})
                self.assertEqual(len(manifest["operations"]),1)
                self.assertEqual(manifest["operations"][0]["variant"],speed.FAST)
                self.assertEqual(manifest["resource_use"]["zero_page_bytes"],24)
                self.assertEqual(manifest["resource_use"]["private_ram_scratch_bytes"],0)
                _,end=v2.layout(code)
                self.assertEqual(manifest["resource_use"]["main_ram_total_bytes"],
                                 (end-code)+32)
                image=(folder/"math_selective.prg").read_bytes()
                self.assertEqual(image[:2],code.to_bytes(2,"little"))
                self.assertEqual(len(image),2+end-code)
                cpu=CPU(bytearray(65536))
                cpu.mem[code:end]=image[2:]
                sp=cpu.sp
                entry=int(manifest["operations"][0]["entry"][1:],16)
                for i,(x,y) in enumerate(speed.corpus()[::3]):
                    xb=x.to_bytes(3,"little");yb=y.to_bytes(3,"little")
                    cpu.mem[io:io+4]=xb+bytes([0x6a])
                    cpu.mem[io+4:io+8]=yb+bytes([0xa5])
                    cpu.mem[io+8:io+16]=bytes([0xcc]*6+[0x49,0x59])
                    cpu.d=0;cpu.c=i&1
                    cpu.call(entry,100000)
                    self.assertEqual(int.from_bytes(cpu.mem[io+8:io+14],"little"),
                                     (x*y)&((1<<48)-1))
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,sp)
                    self.assertEqual(bytes(cpu.mem[io:io+4]),xb+bytes([0x6a]))
                    self.assertEqual(bytes(cpu.mem[io+4:io+8]),yb+bytes([0xa5]))
                    self.assertEqual(bytes(cpu.mem[io+14:io+16]),bytes([0x49,0x59]))
                print("UMUL24 SELECTED SOURCE-LINKED V2",hex(code),
                      round(metrics["mean_cycles"][speed.FAST],3),
                      round(metrics["mean_cycles"][speed.COMPACT],3),
                      flush=True)

    def test_compact_zero_zp_retained(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            m=linker.build(self.plan(zp=0,ram=256,objective="size"),
                           folder)
            self.assertEqual(m["operations"][0]["variant"],speed.COMPACT)
            self.assertEqual(m["resource_use"]["zero_page_bytes"],0)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(zp=0,pin=speed.FAST),
                             folder/"no_zp")


if __name__=="__main__":
    unittest.main()
