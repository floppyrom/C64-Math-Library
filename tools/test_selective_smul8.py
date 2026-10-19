#!/usr/bin/env python3
"""Exhaustive source-built historical 46-byte self-modifying signed UMUL8 peer."""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
import selective_smul8 as tab
from mini6502 import CPU

PROFILES = (
    "v1_balanced", "v2_pareto_fast", "v3_reu_512k",
    "v4_reu_16m", "v5_hybrid_lowzp",
)
TABLE_ADDRESSES = (
    (0x9c00,0x9e00,0x8800,0x8a00),
    (0x9c00,0x9e00,0x6400,0x6600),
    (0x9c00,0x9e00,0x6400,0x6600),
    (0x9c00,0x9e00,0x6400,0x6600),
    (0x9c00,0x9e00,0x8800,0x8a00),
)
SMC_OPERAND_BYTES = (27,30,36,39)


class HistoricalSMUL8(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, names, zp=0, ram=2336):
        return math_builder.create_plan(
            self.index, names, zp_budget=zp, ram_budget=ram,
            pins={"SMUL8":"link:v1-resident-smc"})

    def test_all_five_original_tables_binary_exact(self):
        self.assertEqual(len(tab.NAMES),4)
        self.assertEqual(sum(len(tab.TABLES[x]) for x in tab.NAMES),2044)
        self.assertEqual(tab.ALIGNED_SPAN,2048)
        for profile, addresses in zip(PROFILES,TABLE_ADDRESSES):
            data=(ROOT/profile/"resident"/("math_"+profile+"_game_math.prg")).read_bytes()
            origin=int.from_bytes(data[:2],"little")
            for table_name, address in zip(tab.NAMES,addresses):
                offset=address-origin+2
                self.assertEqual(data[offset:offset+511],tab.TABLES[table_name],
                                 (profile,table_name))

    def test_all_65536_reference_pairs(self):
        for x in range(256):
            for y in range(256):
                self.assertEqual(tab.original_table_math(x,y),
                                 tab.signed_reference(x,y),(x,y))

    def test_source_exact_opcode_structure_and_all_pairs_in_6502(self):
        for origin,io in ((0x8000,0xc000),(0x80d2,0xc040)):
            with self.subTest(origin=origin), tempfile.TemporaryDirectory() as d:
                result=selective_linker.build(
                    self.plan(["SMUL8"],ram=2336),Path(d),
                    memory={"code_base":origin,"math_io":io})
                resource=result["resource_use"]
                self.assertEqual(resource["zero_page_bytes"],0)
                self.assertEqual(resource["private_ram_scratch_bytes"],0)
                self.assertEqual(resource["code_and_tables_bytes"],2090)
                self.assertEqual(resource["shared_table_bytes"],2044)
                self.assertEqual(len(result["shared_tables"]),1)
                tables,=result["shared_tables"]
                table_origin=int(tables["start"][1:],16)
                self.assertEqual(table_origin & 255,0)
                self.assertEqual(tables["sha256"],
                                 hashlib.sha256(tab.digest_data()).hexdigest())
                prg=(Path(d)/"math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(prg).hexdigest(),result["prg_sha256"])
                cpu=CPU(bytearray(65536))
                start=int.from_bytes(prg[:2],"little")
                cpu.mem[start:start+len(prg)-2]=prg[2:]
                original=bytes(cpu.mem[origin:origin+46])
                self.assertEqual((original[0],original[3],original[-2:]),
                                 (0xad,0x49,b"\x18\x60"))
                allowed=set(SMC_OPERAND_BYTES)
                for offset,name in enumerate(tab.NAMES):
                    taddr=table_origin + offset*tab.PAGE_STRIDE
                    self.assertEqual(cpu.mem[taddr:taddr+511],tab.TABLES[name])
                sp=cpu.sp
                for x in range(256):
                    cpu.mem[io]=x
                    cpu.mem[io+1]=0xb6
                    for y in range(256):
                        cpu.mem[io+4]=y
                        cpu.mem[io+5]=0xc7
                        cpu.mem[io+8:io+12]=b"\x5a"*4
                        cpu.d=0
                        cpu.c=(x+y)&1
                        cpu.call(origin,2000)
                        value=int.from_bytes(cpu.mem[io+8:io+10],"little")
                        self.assertEqual((value,cpu.c),(tab.signed_reference(x,y),0),
                                         (origin,x,y))
                        self.assertEqual(cpu.mem[io+10:io+12],b"\x5a"*2)
                        self.assertEqual((cpu.mem[io],cpu.mem[io+1],
                                          cpu.mem[io+4],cpu.mem[io+5]),(x,0xb6,y,0xc7))
                        self.assertEqual(cpu.sp,sp)
                    self.assertEqual({j for j in range(46)
                                      if cpu.mem[origin+j]!=original[j]} <= allowed,True)
                for k,expected in zip(SMC_OPERAND_BYTES,
                                      ((255^128),(255^128)^255,
                                       (255^128),((255^128)^255))):
                    self.assertEqual(cpu.mem[origin+k],expected)
                self.assertEqual(bytes(cpu.mem[table_origin:table_origin+511]),
                                 tab.TABLES[tab.NAMES[0]])

    def test_global_shared_tables_and_budget(self):
        with tempfile.TemporaryDirectory() as d:
            r=selective_linker.build(self.plan(["SMUL8"]),Path(d))
            self.assertEqual(r["resource_use"]["image_span_bytes"],2304)
            self.assertEqual(r["resource_use"]["alignment_padding_bytes"],214)
            self.assertEqual(r["resource_use"]["main_ram_total_bytes"],2336)
            self.assertEqual(r["shared_tables"][0]["bytes"],2044)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(selective_linker.LinkError,"budget"):
                selective_linker.build(self.plan(["SMUL8"],ram=2335),Path(d))
            self.assertFalse((Path(d)/"math_selective.prg").exists())
        with tempfile.TemporaryDirectory() as d:
            r=selective_linker.build(
                self.plan(["SMUL8","SIN8","COS8","DIST8_ACCURATE"],ram=3600),
                Path(d))
            self.assertEqual(r["resource_use"]["shared_table_bytes"],
                             2044+256+512)
            self.assertEqual({t["name"] for t in r["shared_tables"]},
                             {"SMUL8_V1_ORIGINAL_PAGES",
                              "SINE8_SHARED","DIST8_ACCURATE_SHARED"})
            self.assertEqual(set(r["link_exports"]),{
                "MATH_SMUL8","MATH_SIN8","MATH_COS8","MATH_DIST8_ACCURATE"})

    def test_provenance_and_write_ram_contract(self):
        available=selective_linker.available_variants()["MATH_SMUL8"]
        (one,) = (v for v in available if v["id"] == "link:v1-resident-smc")
        self.assertEqual(one["validation_path"],"tools/test_selective_smul8.py")
        self.assertEqual(set(one["dependency_sha256"]),{"tools/selective_smul8.py"})
        self.assertEqual(one["zp_bytes_reported"],0)
        self.assertEqual(one["requires_writable_code"],True)


if __name__=="__main__":
    unittest.main()
