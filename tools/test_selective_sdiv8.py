#!/usr/bin/env python3
"""Exhaustive signed V1 8-bit DIV/MOD, shared producer, alias, ZP and ABI tests."""
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


def signed(b):
    return b if b < 128 else b-256


def reference(nbyte,dbyte):
    n,d=signed(nbyte),signed(dbyte)
    if d==0:
        return 0,0,1
    q=(abs(n)//abs(d)) * (-1 if (n<0) != (d<0) else 1)
    r=n-q*d
    return q&255,r&255,0


class SharedSignedDivision8(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def build(self,ops,d,**kwargs):
        plan=math_builder.create_plan(
            self.index,ops,zp_budget=1,ram_budget=562,**{
                k:v for k,v in kwargs.items() if k in ("pins",)})
        memory={k:v for k,v in kwargs.items() if k in ("code_base","math_io","zp_base")}
        return selective_linker.build(plan,Path(d),memory=memory)

    def test_complete_signed_input_space_at_two_relocations(self):
        for origin,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(origin=origin), tempfile.TemporaryDirectory() as folder:
                result=self.build(["SDIV8"],folder,code_base=origin,
                                  math_io=io,zp_base=zp)
                res=result["resource_use"]
                self.assertEqual(res["code_and_tables_bytes"],530)
                self.assertEqual(res["main_ram_total_bytes"],562)
                self.assertEqual(res["zero_page_bytes"],1)
                self.assertEqual(res["private_ram_scratch_bytes"],0)
                self.assertEqual(result["operations"][0]["entry"],"$%04X"%(origin+8))
                image=(Path(folder)/"math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(image).hexdigest(),result["prg_sha256"])
                cpu=CPU(bytearray(65536))
                cpu.mem[origin:origin+len(image)-2]=image[2:]
                before=bytes(cpu.mem[origin:origin+len(image)-2])
                stack=cpu.sp
                for db in range(256):
                    for nb in range(256):
                        cpu.mem[io+16:io+20]=bytes((nb,0x56,0x78,0x9a))
                        cpu.mem[io+20:io+24]=bytes((db,0xab,0xcd,0xef))
                        cpu.mem[io+24:io+28]=b"\x11"*4
                        cpu.mem[io+28:io+32]=b"\x22"*4
                        cpu.c=(nb^db)&1
                        cpu.d=0
                        cpu.call(origin+8,100000)
                        q,r,carry=reference(nb,db)
                        self.assertEqual((cpu.mem[io+24],cpu.mem[io+28],cpu.c),
                                         (q,r,carry),(origin,nb,db))
                        self.assertEqual(cpu.mem[io+25:io+28],b"\x11"*3)
                        self.assertEqual(cpu.mem[io+29:io+32],b"\x22"*3)
                        self.assertEqual(cpu.mem[io+16:io+20],
                                         bytes((nb,0x56,0x78,0x9a)))
                        self.assertEqual(cpu.mem[io+20:io+24],
                                         bytes((db,0xab,0xcd,0xef)))
                        self.assertEqual(cpu.sp,stack)
                self.assertEqual(bytes(cpu.mem[origin:origin+len(image)-2]),
                                 before)

    def test_both_public_names_share_one_physical_code_image(self):
        for ops in (["SDIV8","SMOD8"],["SMOD8","SDIV8"],["SMOD8"]):
            with self.subTest(ops=ops),tempfile.TemporaryDirectory() as folder:
                result=self.build(ops,folder)
                self.assertEqual(result["resource_use"]["image_span_bytes"],530)
                self.assertEqual(result["resource_use"]["main_ram_total_bytes"],562)
                self.assertEqual(result["resource_use"]["zero_page_bytes"],1)
                exports=(Path(folder)/"math_api.inc").read_text()
                for name in ops:
                    self.assertIn("MATH_"+name+" =",exports)
                if len(ops)==2:
                    self.assertEqual(set(result["link_exports"]),
                                     {"MATH_SDIV8","MATH_SMOD8"})
                    self.assertEqual(len(result["link_order"]),1)
                    self.assertEqual(len(result["operations"]),2)
                    self.assertEqual(result["operations"][0]["entry"],
                                     result["operations"][1]["entry"])
                    self.assertEqual(result["operations"][1].get("shared_kernel_of"),
                                     "MATH_SDIV8")
                cpu=CPU(bytearray(65536))
                image=(Path(folder)/"math_selective.prg").read_bytes()
                cpu.mem[0x8000:0x8000+len(image)-2]=image[2:]
                entry=int(result["operations"][0]["entry"][1:],16)
                randomizer=random.Random(0x5D180)
                for nb,db in [(0,0),(128,255),(127,128),(128,1),
                              (255,255),(128,128)]+[
                              (randomizer.randrange(256),randomizer.randrange(256))
                              for _ in range(4096)]:
                    cpu.mem[0xc010]=nb
                    cpu.mem[0xc014]=db
                    cpu.d=0
                    cpu.call(entry,100000)
                    self.assertEqual((cpu.mem[0xc018],cpu.mem[0xc01c],cpu.c),
                                     reference(nb,db))

    def test_size_budget_alias_must_count_producer_once(self):
        with tempfile.TemporaryDirectory() as folder:
            plan=math_builder.create_plan(self.index,["SDIV8","SMOD8"],
                                          zp_budget=1,ram_budget=561)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(plan,Path(folder))
            self.assertFalse((Path(folder)/"math_selective.prg").exists())

    def test_metadata_and_independent_source_hashes(self):
        for api in ("MATH_SDIV8","MATH_SMOD8"):
            variants=selective_linker.available_variants()[api]
            v,=variants
            self.assertEqual(v["validation_path"],"tools/test_selective_sdiv8.py")
            self.assertEqual(v["resources_reported"]["code_and_table_bytes"],530)
            self.assertEqual(v["zp_bytes_reported"],1)
        with tempfile.TemporaryDirectory() as folder:
            plan=math_builder.create_plan(self.index,["SMOD8","SDIV8"],
                                          zp_budget=1,ram_budget=562)
            plan["operations"][1]["available_source_variants"][-1]["source_sha256"]="0"*64
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(plan,Path(folder))
            self.assertFalse((Path(folder)/"math_selective.prg").exists())


if __name__=="__main__":
    unittest.main()
