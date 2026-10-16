#!/usr/bin/env python3
"""Exhaustive qualified source port of historical V1 unsigned modulo fast/fallback."""
from __future__ import annotations
import hashlib
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU

SMC_OPERANDS=(146,150)
VARIANT="link:v1-fast-fallback"


class HistoricalUMOD8(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,operations,ram=1024,zp=2):
        return math_builder.create_plan(
            self.index,operations,zp_budget=zp,ram_budget=ram,
            pins={"UMOD8":VARIANT})

    def test_all_65536_pairs_at_two_code_and_zp_origins(self):
        for origin,io,zb in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(origin=origin),tempfile.TemporaryDirectory() as folder:
                result=selective_linker.build(
                    self.plan(["UMOD8"],ram=189),Path(folder),
                    memory={"code_base":origin,"math_io":io,"zp_base":zb})
                resource=result["resource_use"]
                self.assertEqual(resource["zero_page_bytes"],2)
                self.assertEqual(resource["private_ram_scratch_bytes"],0)
                self.assertEqual(resource["image_span_bytes"],157)
                self.assertEqual(resource["main_ram_total_bytes"],189)
                self.assertEqual(result["operations"][0]["entry"],"$%04X"%origin)
                image=(Path(folder)/"math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(image).hexdigest(),result["prg_sha256"])
                cpu=CPU(bytearray(65536))
                cpu.mem[origin:origin+len(image)-2]=image[2:]
                before=bytes(cpu.mem[origin:origin+157])
                stack=cpu.sp
                for db in range(256):
                    for nb in range(256):
                        cpu.mem[io+16:io+20]=bytes((nb,0x10,0x11,0x12))
                        cpu.mem[io+20:io+24]=bytes((db,0x20,0x21,0x22))
                        cpu.mem[io+24:io+28]=b"\x33"*4
                        cpu.mem[io+28:io+32]=b"\x44"*4
                        cpu.d=0
                        cpu.c=(nb^db)&1
                        cpu.call(origin,20000)
                        want_r=nb%db if db else 0
                        self.assertEqual((cpu.mem[io+28],cpu.c),
                                         (want_r,int(db==0)),(origin,nb,db))
                        self.assertEqual(cpu.mem[io+24:io+28],b"\x33"*4,
                                         "UMOD must not clobber quotient")
                        self.assertEqual(cpu.mem[io+29:io+32],b"\x44"*3)
                        self.assertEqual(cpu.mem[io+16:io+20],
                                         bytes((nb,0x10,0x11,0x12)))
                        self.assertEqual(cpu.mem[io+20:io+24],
                                         bytes((db,0x20,0x21,0x22)))
                        self.assertEqual(cpu.sp,stack)
                    differences={i for i in range(157)
                                 if cpu.mem[origin+i]!=before[i]}
                    self.assertTrue(differences<=set(SMC_OPERANDS),differences)
                self.assertEqual(bytes(cpu.mem[origin:origin+146]),before[:146])

    def test_zero_budget_and_mixed_public_call_abi(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(selective_linker.LinkError,"budget"):
                selective_linker.build(
                    self.plan(["UMOD8"],ram=188),Path(folder))
            self.assertFalse((Path(folder)/"math_selective.prg").exists())
        with tempfile.TemporaryDirectory() as folder:
            result=selective_linker.build(
                self.plan(["UMOD8","UDIV8","SDIV8","SMOD8"],ram=1013),
                Path(folder))
            self.assertEqual(result["resource_use"]["zero_page_bytes"],2)
            self.assertEqual(result["resource_use"]["main_ram_total_bytes"],1013)
            self.assertEqual(result["resource_use"]["code_and_tables_bytes"],
                             157+294+530)
            self.assertEqual(set(result["link_exports"]),
                             {"MATH_UMOD8","MATH_UDIV8","MATH_SDIV8","MATH_SMOD8"})
            self.assertEqual(len(result["link_order"]),3)

    def test_source_qualification_and_modulo_side_effect_contract(self):
        one=next(v for v in selective_linker.available_variants()["MATH_UMOD8"] if v["id"] == VARIANT)
        self.assertEqual(one["validation_path"],"tools/test_selective_umod8.py")
        self.assertEqual(one["resources_reported"]["code_and_table_bytes"],157)
        self.assertEqual(one["zp_bytes_reported"],2)
        self.assertTrue(one["requires_writable_code"])
        self.assertEqual(one["historical_provenance"],
                         "Original V1 fast >=32 divide and small-divisor SMC fallback, Q preserved")


if __name__=="__main__":
    unittest.main()
