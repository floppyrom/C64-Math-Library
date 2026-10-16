#!/usr/bin/env python3
"""Exhaustive two-relocation CPU proof of historical V1 UDIV8 source migration."""
from __future__ import annotations
import hashlib
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
from mini6502 import CPU


class NativeV1UDIV8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, ops, **kwargs):
        return math_builder.create_plan(cls.index, ops, **kwargs)

    def test_exact_all_pairs_two_relocations(self):
        for origin, io, zbase in ((0x8000, 0xc000, 0x50),
                                  (0x7123, 0xc040, 0x70)):
            with self.subTest(origin=origin), tempfile.TemporaryDirectory() as d:
                plan=math_builder.create_plan(
                    self.index, ["UDIV8"], pins={"UDIV8":"link:v1-resident-fast"},
                    zp_budget=1, ram_budget=326)
                result=selective_linker.build(
                    plan,Path(d),memory={"code_base":origin,
                                         "math_io":io,"zp_base":zbase})
                self.assertEqual(result["resource_use"]["code_and_tables_bytes"],294)
                self.assertEqual(result["resource_use"]["zero_page_bytes"],1)
                self.assertEqual(result["resource_use"]["main_ram_total_bytes"],326)
                self.assertEqual(result["operations"][0]["entry"],"$%04X"%(origin+8))
                self.assertEqual(result["operations"][0]["variant"],"link:v1-resident-fast")
                prg=(Path(d)/"math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(prg).hexdigest(),result["prg_sha256"])
                cpu=CPU(bytearray(65536))
                cpu.mem[origin:origin+len(prg)-2]=prg[2:]
                before=bytes(cpu.mem[origin:origin+len(prg)-2])
                sp=cpu.sp
                for dval in range(256):
                    for nval in range(256):
                        cpu.mem[io+16:io+20]=bytes((nval,0xAB,0xCD,0xEF))
                        cpu.mem[io+20:io+24]=bytes((dval,0xBA,0xDC,0xFE))
                        cpu.mem[io+24:io+28]=b"\x55"*4
                        cpu.mem[io+28:io+32]=b"\x66"*4
                        cpu.d=0
                        cpu.c=(nval^dval)&1
                        cpu.call(origin+8,100000)
                        want_q=nval//dval if dval else 0
                        want_r=nval%dval if dval else 0
                        self.assertEqual((cpu.mem[io+24],cpu.mem[io+28],cpu.c),
                                         (want_q,want_r,int(dval==0)),
                                         (origin,nval,dval))
                        self.assertEqual(cpu.mem[io+25:io+28],b"\x55"*3)
                        self.assertEqual(cpu.mem[io+29:io+32],b"\x66"*3)
                        self.assertEqual(cpu.mem[io+16:io+20],
                                         bytes((nval,0xAB,0xCD,0xEF)))
                        self.assertEqual(cpu.mem[io+20:io+24],
                                         bytes((dval,0xBA,0xDC,0xFE)))
                        self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(cpu.mem[origin:origin+len(prg)-2]),before)

    def test_mixed_zp_scratch_and_fail_closed_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            plan=math_builder.create_plan(
                self.index,["UDIV8","UDIV16","DIST8_FAST"],
                zp_budget=2,ram_budget=1100)
            result=selective_linker.build(plan,Path(folder))
            self.assertEqual(set(result["link_exports"]),
                             {"MATH_UDIV8","MATH_UDIV16","MATH_DIST8_FAST"})
            self.assertEqual(result["resource_use"]["zero_page_bytes"],2)
            self.assertEqual(result["resource_use"]["private_ram_scratch_bytes"],2)
        with tempfile.TemporaryDirectory() as folder:
            plan=math_builder.create_plan(self.index,["UDIV8"],
                                          zp_budget=0,ram_budget=326)
            with self.assertRaisesRegex(selective_linker.LinkError,
                                        "fits RAM/ZP budgets"):
                selective_linker.build(plan,Path(folder))
            self.assertFalse((Path(folder)/"math_selective.prg").exists())

    def test_canonical_variant_metadata(self):
        candidates=selective_linker.available_variants()["MATH_UDIV8"]
        variant,=candidates
        self.assertEqual(variant["validation_path"],"tools/test_selective_udiv8.py")
        self.assertEqual(variant["historical_provenance"],
                         "Exact V1 125-instruction UDIV8 fast chain, trampoline omitted")
        self.assertEqual(variant["resources_reported"]["code_and_table_bytes"],294)


if __name__=="__main__":
    unittest.main()
