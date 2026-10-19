#!/usr/bin/env python3
"""Exact read-only signed8 QS public source and historical SMC preservation."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_smul8_qs_readonly as source

FAST="link:qs-readonly"
OLD="link:v1-resident-smc"


class StockSigned8QS(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.index=math_builder.operation_index()

    def plan(self,variant=FAST,ram=1193):
        return math_builder.create_plan(
            self.index,["SMUL8"],objective="size",
            pins={"SMUL8":variant},zp_budget=0,ram_budget=ram)

    def test_all_65536_signed_pairs_on_two_ram_maps(self):
        for code,io,scratch in ((0x8000,0xc000,0xc040),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                res=man["resource_use"]
                self.assertEqual(man["operations"][0]["variant"],FAST)
                self.assertEqual(res["image_span_bytes"],1159)
                self.assertEqual(res["zero_page_bytes"],0)
                self.assertEqual(res["private_ram_scratch_bytes"],2)
                self.assertEqual(res["main_ram_total_bytes"],1193)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(prg[:2],code.to_bytes(2,"little"))
                self.assertEqual(len(prg),1161)
                mem=bytearray(65536)
                mem[code:code+1159]=prg[2:]
                before=bytes(mem[code:code+1159])
                cpu=CPU(mem)
                sp=cpu.sp
                entry=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(entry,code+1095)
                for x in range(256):
                    mem[io]=x
                    mem[io+1]=0xa5
                    for y in range(256):
                        mem[io+4]=y
                        mem[io+5]=0x5a
                        mem[io+8:io+12]=bytes((0xcc,0xdd,0x42,0x43))
                        cpu.a=(x+y)&255
                        cpu.x=(x^y)&255
                        cpu.y=y
                        cpu.c=(x+y)&1
                        cpu.d=0
                        cpu.call(entry,3000)
                        sx=x-(256 if x&128 else 0)
                        sy=y-(256 if y&128 else 0)
                        got=int.from_bytes(mem[io+8:io+10],"little")
                        self.assertEqual(got,(sx*sy)&0xffff,(code,x,y))
                        self.assertEqual(cpu.c,0)
                        self.assertEqual(mem[io+10:io+12],
                                         bytes((0x42,0x43)))
                        self.assertEqual((mem[io],mem[io+1],mem[io+4],mem[io+5]),
                                         (x,0xa5,y,0x5a))
                        self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+1159]),before)

    def test_authentic_full_public_speed_selection_respects_ram(self):
        for ram in (1193,2336):
            with self.subTest(ram=ram),tempfile.TemporaryDirectory() as td:
                plan=math_builder.create_plan(
                    self.index,["SMUL8"],objective="speed",
                    zp_budget=0,ram_budget=ram,
                    workload_calls={"SMUL8":100})
                man=linker.build(plan,Path(td))
                model=man["cycle_model_benchmark"]
                self.assertEqual(model["cases"],512)
                self.assertTrue(model["cpu_model_only"])
                self.assertEqual(set(model["mean_cycles"]),{FAST,OLD})
                self.assertEqual(set(model["source_sha256"]),{FAST,OLD})
                if ram==1193:
                    self.assertEqual(man["operations"][0]["variant"],FAST)
                else:
                    fastest=min(model["mean_cycles"],
                                key=model["mean_cycles"].get)
                    self.assertEqual(man["operations"][0]["variant"],fastest)
                self.assertLessEqual(
                    man["resource_use"]["main_ram_total_bytes"],ram)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)

    def test_historical_smc_stays_accessible_and_ram_bounds_fail_closed(self):
        variants=linker.available_variants()["MATH_SMUL8"]
        self.assertEqual({v["id"] for v in variants},{FAST,OLD})
        historical=next(v for v in variants if v["id"]==OLD)
        portable=next(v for v in variants if v["id"]==FAST)
        self.assertTrue(historical["requires_writable_code"])
        self.assertFalse(portable["requires_writable_code"])
        self.assertEqual(portable["zp_bytes_reported"],0)
        self.assertEqual(set(portable["dependency_sha256"]),{
            "tools/selective_fast_umul8.py",
            "tools/selective_smul8_qs_readonly.py"})
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=1192),Path(td)/"over_budget")
            man=linker.build(self.plan(variant=OLD,ram=2336),Path(td)/"smc")
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],2336)
            self.assertEqual(man["operations"][0]["variant"],OLD)


if __name__=="__main__":
    unittest.main()
