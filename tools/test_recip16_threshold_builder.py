#!/usr/bin/env python3
"""Native-safe public reciprocal threshold source and budget qualification."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU

import math_builder
import selective_linker as linker
import selective_speed_recip16 as speed

FAST= speed.FAST
SMALL= speed.SMALL


class RecipThresholdQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,objective="size",pin=FAST,ram=481):
        return math_builder.create_plan(
            self.index,["URECIP16_Q16"],objective=objective,
            pins=({"URECIP16_Q16":pin} if pin else {}),
            zp_budget=0,ram_budget=ram,
            workload_calls=({"URECIP16_Q16":100}
                            if objective=="speed" else None))

    def test_relocated_public_source_and_no_zp(self):
        for code,io,scratch in (
                (0x8000,0xc000,0xc020),
                (0x7123,0xc040,0xc080)):
            with self.subTest(origin=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),
                   memory={"code_base":code,"math_io":io,
                           "scratch_base":scratch})
                self.assertEqual(man["operations"][0]["variant"],FAST)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],1)
                self.assertEqual(man["resource_use"]["image_span_bytes"],448)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],481)
                data=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(data),450)
                entry=int(man["operations"][0]["entry"][1:],16)
                mem=bytearray(65536)
                mem[code:code+448]=data[2:]
                immutable=bytes(mem[code:code+448])
                cpu=CPU(mem)
                sp=cpu.sp
                # Include near every threshold, tiny denominators and large
                # denominators, at both code placements.
                for d in speed.corpus():
                    mem[io+20:io+24]=d.to_bytes(2,"little")+b"\x5a\xa5"
                    mem[io+16:io+20]=b"\xde\xad\xbe\xef"
                    mem[io+24:io+28]=b"\x55\xaa\x77\xcc"
                    mem[io+28:io+32]=b"\x12\x34\x56\x78"
                    cpu.d=0
                    cpu.c=(d^code)&1
                    cpu.call(entry,50000)
                    self.assertEqual(int.from_bytes(mem[io+24:io+27],"little"),
                                     65536//d if d else 0,(code,d))
                    self.assertEqual(cpu.c,int(d==0))
                    self.assertEqual(mem[io+27],0xcc)
                    self.assertEqual(mem[io+20:io+24],
                                     d.to_bytes(2,"little")+b"\x5a\xa5")
                    self.assertEqual(mem[io+16:io+20],b"\xde\xad\xbe\xef")
                    self.assertEqual(mem[io+28:io+32],b"\x12\x34\x56\x78")
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+448]),immutable)

    def test_same_corpus_speed_and_resource_fallback(self):
        mod=linker.MODULES["MATH_URECIP16_Q16"]
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(code=code):
                result=speed.bench_urecip16_q16(mod,code,io,scratch,
                                                math_builder.ROOT)
                print("RECIP16_THRESHOLD_MATCHED",hex(code),
                      result["mean_cycles"],result["maximum_cycles"],
                      result["p95_cycles"],flush=True)
                self.assertEqual(result["cases"],512)
                self.assertLess(result["mean_cycles"][FAST],
                                result["mean_cycles"][SMALL])
        for ram,winner in ((481,FAST),(132,SMALL)):
            with tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan("speed",None,ram),Path(td))
                self.assertEqual(man["operations"][0]["variant"],winner)
                self.assertEqual(man["cycle_model_benchmark"]["cases"],512)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)

    def test_exact_budget_failure_for_pinned_fast(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=480),Path(td)/"short")


if __name__=="__main__":
    unittest.main()
