#!/usr/bin/env python3
"""One Q32/R32 zero-ZP producer serving both complete public DIV and MOD APIs."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_u3232 as speed

FAST="link:shared-aligned-zerozp"
APIS=("UDIV32_32","UMOD32_32")
IMAGE_BYTES=576
RAM=IMAGE_BYTES+32+4

class SharedU3232Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ram=RAM,objective="size",calls=None):
        return math_builder.create_plan(
            self.index,list(APIS),objective=objective,zp_budget=0,
            ram_budget=ram,pins={op:FAST for op in APIS}
            if objective!="speed" else None,
            workload_calls=calls if calls is not None else
              ({APIS[0]:500,APIS[1]:1000} if objective=="speed" else None))

    def test_one_code_image_two_entries_two_maps_full_q_r(self):
        pairs=speed.corpus()
        self.assertEqual(len(pairs),384)
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                out=Path(td)
                man=linker.build(self.plan(),out,memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                self.assertEqual(len(man["link_order"]),1)
                self.assertEqual(man["resource_use"]["image_span_bytes"],IMAGE_BYTES)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],RAM)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],4)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                self.assertEqual({x["variant"] for x in man["operations"]},{FAST})
                entries={x["api"]:int(x["entry"][1:],16) for x in man["operations"]}
                self.assertEqual(len(set(entries.values())),1)
                prg=(out/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),IMAGE_BYTES+2)
                mem=bytearray(65536)
                mem[code:code+IMAGE_BYTES]=prg[2:]
                cpu=CPU(mem)
                sp=cpu.sp
                for i,(n,d) in enumerate(pairs):
                    for api in ("MATH_UDIV32_32","MATH_UMOD32_32"):
                        nb=n.to_bytes(4,"little");db=d.to_bytes(4,"little")
                        mem[io+16:io+20]=nb
                        mem[io+20:io+24]=db
                        mem[io+24:io+28]=b"\x55"*4
                        mem[io+28:io+32]=b"\x66"*4
                        cpu.d=0
                        cpu.c=(n^d^i)&1
                        cpu.call(entries[api],150000)
                        self.assertEqual(int.from_bytes(mem[io+24:io+28],"little"),
                                         n//d if d else 0,(api,n,d))
                        self.assertEqual(int.from_bytes(mem[io+28:io+32],"little"),
                                         n%d if d else 0,(api,n,d))
                        self.assertEqual(cpu.c,int(d==0))
                        self.assertEqual(cpu.sp,sp)
                        self.assertEqual(mem[io+16:io+20],nb)
                        self.assertEqual(mem[io+20:io+24],db)
                self.assertEqual(bytes(mem[code:code+IMAGE_BYTES]),prg[2:])

    def test_budget_rejects_one_byte_short_and_global_speed_can_share(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=RAM-1),out/"small")
            plan=self.plan(objective="speed")
            chosen=linker.build(plan,out/"weighted")
            self.assertEqual(set(chosen["cycle_model_benchmark"]["operations"]),
                             {"MATH_"+op for op in APIS})
            self.assertEqual(set(chosen["cycle_model_benchmark"]["operations"]
                                  ["MATH_UMOD32_32"]["mean_cycles"]),speed.EXPECTED[
                                  "MATH_UMOD32_32"])
            self.assertLessEqual(chosen["resource_use"]["main_ram_total_bytes"],RAM)
            self.assertEqual({x["variant"] for x in chosen["operations"]},{FAST})
            self.assertEqual(chosen["resource_use"]["zero_page_bytes"],0)

if __name__=="__main__":
    unittest.main()
