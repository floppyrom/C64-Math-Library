#!/usr/bin/env python3
"""Exact table-backed Q16 reciprocal: all 65,536 divisors and two relocations."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_recip16 as speed


class TableRecipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,objective="size",pin=speed.TABLE,ram=1576):
        return math_builder.create_plan(
            self.index,["URECIP16_Q16"],objective=objective,
            pins={"URECIP16_Q16":pin} if pin else {},
            workload_calls=({"URECIP16_Q16":100}
                            if objective=="speed" else None),
            zp_budget=0,ram_budget=ram)

    def test_complete_public_two_maps(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],1544)
                self.assertEqual(use["zero_page_bytes"],0)
                self.assertEqual(use["private_ram_scratch_bytes"],0)
                self.assertEqual(use["main_ram_total_bytes"],1576)
                self.assertEqual(man["operations"][0]["variant"],speed.TABLE)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),1546)
                mem=bytearray(65536)
                mem[code:code+1544]=prg[2:]
                original=bytes(mem[code:code+1544])
                cpu=CPU(mem)
                sp=cpu.sp
                entry=int(man["operations"][0]["entry"][1:],16)
                for d in speed.corpus():
                    mem[io+20:io+24]=d.to_bytes(2,"little")+b"\x5a\xa5"
                    mem[io+16:io+20]=b"\xde\xad\xbe\xef"
                    mem[io+24:io+28]=b"\x55\xaa\x77\xcc"
                    mem[io+28:io+32]=b"\x12\x34\x56\x78"
                    cpu.d=0
                    cpu.c=d&1
                    cpu.call(entry,50000)
                    self.assertEqual(int.from_bytes(mem[io+24:io+27],"little"),
                                     65536//d if d else 0,(hex(code),d))
                    self.assertEqual(cpu.c,int(d==0))
                    self.assertEqual(mem[io+27],0xcc)
                    self.assertEqual(mem[io+20:io+24],
                                     d.to_bytes(2,"little")+b"\x5a\xa5")
                    self.assertEqual(mem[io+16:io+20],b"\xde\xad\xbe\xef")
                    self.assertEqual(mem[io+28:io+32],b"\x12\x34\x56\x78")
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+1544]),original)

    def test_match_speed_and_pareto_selection(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080)):
            m=speed.bench_urecip16_q16(
                linker.MODULES["MATH_URECIP16_Q16"],code,io,scratch,
                math_builder.ROOT)
            print("RECIP16 THREE-WAY MATCHED",hex(code),
                  m["mean_cycles"],m["maximum_cycles"],
                  m["p95_cycles"],flush=True)
            self.assertLess(m["mean_cycles"][speed.TABLE],
                            m["mean_cycles"][speed.FAST])
            self.assertLess(m["maximum_cycles"][speed.TABLE],
                            m["maximum_cycles"][speed.SMALL])
        for ram,winner in ((1576,speed.TABLE),(481,speed.FAST),
                            (132,speed.SMALL)):
            with tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan("speed",None,ram),Path(td))
                self.assertEqual(man["operations"][0]["variant"],winner)
                self.assertEqual(man["cycle_model_benchmark"]["cases"],512)

    def test_exhaustive_public_domain(self):
        # This is intentionally source-model exhaustive; native VICE separately
        # proves real CPU semantics in both relocated layouts.
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(),Path(td))
            data=(Path(td)/"math_selective.prg").read_bytes()
            mem=bytearray(65536)
            mem[0x8000:0x8000+1544]=data[2:]
            cpu=CPU(mem)
            entry=int(man["operations"][0]["entry"][1:],16)
            sp=cpu.sp
            for d in range(65536):
                mem[0xc014:0xc016]=d.to_bytes(2,"little")
                mem[0xc018:0xc01c]=bytes((0x66,0x66,0x66,0xbe))
                mem[0xc01c:0xc020]=bytes((0x12,0x34,0x56,0x78))
                cpu.d=0
                cpu.call(entry,50000)
                got=int.from_bytes(mem[0xc018:0xc01b],"little")
                if ((got,cpu.c)!=(65536//d if d else 0,int(d==0))
                    or mem[0xc01b]!=0xbe
                    or mem[0xc01c:0xc020]!=bytes((0x12,0x34,0x56,0x78))
                    or cpu.sp!=sp):
                    self.fail("Exhaustive reciprocal failed: D=%d result=%d C=%d"%(d,got,cpu.c))
            print("EXHAUSTIVE RECIP16 TABLE PASS 65536",flush=True)


if __name__=="__main__":
    unittest.main()
