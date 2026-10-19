#!/usr/bin/env python3
"""Historical V2 16/16 full signed quotient/remainder public ABI qualification."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU

import math_builder
import selective_linker as linker
import selective_speed_sdiv16_shared as speed

FAST=speed.FAST
SMALL=speed.SMALL


class HistoricalSharedSigned16(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,names=("SDIV16","SMOD16"),pin=FAST,
             objective="size",ram=1745):
        return math_builder.create_plan(
            self.index,list(names),objective=objective,
            pins={n:pin for n in names} if pin else {},
            zp_budget=0,ram_budget=ram,
            workload_calls={n:100 for n in names} if objective=="speed" else None)

    def test_source_shared_two_public_entries_at_both_origins(self):
        for code,io,scratch in ((0x8000,0xc000,0xc040),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(origin=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,
                    "scratch_base":scratch})
                self.assertEqual(len(man["link_order"]),1)
                ops={op["api"]:op for op in man["operations"]}
                self.assertEqual(set(ops),{"MATH_SDIV16","MATH_SMOD16"})
                self.assertEqual({op["variant"] for op in ops.values()},{FAST})
                self.assertEqual(len({op["entry"] for op in ops.values()}),1)
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],1705)
                self.assertEqual(use["main_ram_total_bytes"],1745)
                self.assertEqual(use["zero_page_bytes"],0)
                self.assertEqual(use["private_ram_scratch_bytes"],8)
                image=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(image),1707)
                memory=bytearray(65536)
                memory[code:code+1705]=image[2:]
                original=bytes(memory[code:code+1705])
                cpu=CPU(memory)
                sp=cpu.sp
                entry=int(next(iter(ops.values()))["entry"][1:],16)
                self.assertEqual(entry,code+1481)
                for n,d in speed.corpus():
                    num=n.to_bytes(2,"little")+bytes((0x5a,0xa5))
                    den=d.to_bytes(2,"little")+bytes((0x7c,0x6b))
                    memory[io+16:io+20]=num
                    memory[io+20:io+24]=den
                    memory[io+24:io+28]=bytes((0x55,0x44,0x33,0x22))
                    memory[io+28:io+32]=bytes((0x99,0x88,0x77,0x66))
                    cpu.d=0
                    cpu.c=(n+d)&1
                    cpu.call(entry,40000)
                    actual=(int.from_bytes(memory[io+24:io+26],"little"),
                            int.from_bytes(memory[io+28:io+30],"little"),cpu.c)
                    self.assertEqual(actual,speed.oracle(n,d),(code,n,d))
                    self.assertEqual(bytes(memory[io+16:io+20]),num)
                    self.assertEqual(bytes(memory[io+20:io+24]),den)
                    self.assertEqual(bytes(memory[io+26:io+28]),bytes((0x33,0x22)))
                    self.assertEqual(bytes(memory[io+30:io+32]),bytes((0x77,0x66)))
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(memory[code:code+1705]),original)

    def test_full_public_speed_on_matched_inputs_and_ram_fallback(self):
        for code,io,scratch in ((0x8000,0xc000,0xc040),
                                (0x7123,0xc040,0xc080)):
            for api in ("MATH_SDIV16","MATH_SMOD16"):
                with self.subTest(code=code,api=api):
                    m=speed.bench_sdiv16(linker.MODULES[api],code,io,scratch,
                                         math_builder.ROOT)
                    print("V2_SIGNED16_SHARED_MATCHED",api,hex(code),
                          m["mean_cycles"],m["maximum_cycles"],
                          m["p95_cycles"],flush=True)
                    self.assertEqual(m["cases"],384)
                    self.assertLess(m["mean_cycles"][FAST],
                                    m["mean_cycles"][SMALL])
        for ram,expected in ((1745,FAST),(241,SMALL)):
            with tempfile.TemporaryDirectory() as td:
                man=linker.build(
                    self.plan(objective="speed",pin=None,ram=ram),Path(td))
                self.assertEqual({op["variant"] for op in man["operations"]},
                                 {expected})
                self.assertEqual(
                    man["cycle_model_benchmark"]["operations"]["MATH_SDIV16"]["cases"],384)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=1744),Path(td)/"too_small")


if __name__=="__main__":
    unittest.main()
