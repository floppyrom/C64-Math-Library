#!/usr/bin/env python3
"""Exact V1 table-parity and exhaustive signed DIST8_ACCURATE selective tests."""
from __future__ import annotations

from pathlib import Path
import hashlib
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"tools"))
import math_builder
import selective_linker
import selective_dist8_accurate as accurate
from mini6502 import CPU


def reference_tables():
    """Independent oracle: published V1 PRG, not the selective table emitter."""
    b=(ROOT/"v1_balanced/resident/math_v1_balanced_game_math.prg").read_bytes()
    load=int.from_bytes(b[:2],"little")
    assert load==0x1000
    start=lambda addr: addr-load+2
    return b[start(0x9a00):start(0x9b00)],b[start(0x9b00):start(0x9c00)]


def oracle(x,y,table=None):
    a=abs(x if x<128 else x-256)
    b=abs(y if y<128 else y-256)
    hi,lo=max(a,b),min(a,b)
    first,second=table if table is not None else reference_tables()
    return (first[hi]+second[lo])&255


class SelectiveAccurateDistanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()
        cls.table=reference_tables()

    def plan(self,ops,**kw):
        return math_builder.create_plan(self.index,ops,**kw)

    def test_byte_for_byte_original_tables_and_symbol_contract(self):
        self.assertEqual(accurate.tables(),self.table)
        self.assertEqual(tuple(map(len,self.table)),(256,256))
        self.assertEqual(accurate.CODE_BYTES,66)
        self.assertEqual(oracle(128,128,self.table),
                         (self.table[0][128]+self.table[1][128])&255)
        item,=selective_linker.available_variants()["MATH_DIST8_ACCURATE"]
        self.assertEqual(item["source_path"],"routines/game/dist8_accurate.asm")
        self.assertEqual(item["validation_path"],"tools/test_selective_dist8_accurate.py")
        self.assertEqual(item["dependency_sha256"].keys(),
                         {"tools/selective_dist8_accurate.py"})
        self.assertEqual(item["resources_reported"]["code_and_table_bytes"],578)
        self.assertEqual(item["resources_reported"]["scratch_bytes"],2)
        self.assertEqual(item["zp_bytes_reported"],0)

    def test_exhaustive_pair_domain_two_relocations(self):
        for origin,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(origin=origin),tempfile.TemporaryDirectory() as d:
                plan=self.plan(["DIST8_ACCURATE"],zp_budget=0,ram_budget=850,
                               pins={"DIST8_ACCURATE":"link:v1-accurate-table"})
                man=selective_linker.build(plan,Path(d),memory={
                    "code_base":origin,"math_io":io})
                use=man["resource_use"]
                self.assertEqual(use["zero_page_bytes"],0)
                self.assertEqual(use["code_and_tables_bytes"],578)
                self.assertEqual(use["private_ram_scratch_bytes"],2)
                self.assertEqual(use["alignment_padding_bytes"],(-origin-66)%256)
                self.assertEqual(use["main_ram_total_bytes"],
                                 578+(-origin-66)%256+34)
                self.assertEqual(man["operations"][0]["variant"],"link:v1-accurate-table")
                self.assertEqual(man["operations"][0]["entry"],"$%04X"%origin)
                self.assertEqual(man["operations"][0]["dependencies"][0]["source_path"],
                                 "tools/selective_dist8_accurate.py")
                prg=(Path(d)/"math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(prg).hexdigest(),man["prg_sha256"])
                cpu=CPU(bytearray(65536))
                cpu.mem[origin:origin+len(prg)-2]=prg[2:]
                before=bytes(cpu.mem[origin:origin+len(prg)-2])
                old_stack=cpu.sp
                tab0,tab1=self.table
                # Keep the oracle independent of the source-table emitter.
                mags=[abs(n if n<128 else n-256) for n in range(256)]
                for x in range(256):
                    cpu.mem[io]=x
                    a=mags[x]
                    for y in range(256):
                        cpu.mem[io+4]=y
                        cpu.mem[io+8:io+10]=b"\xa5\x5a"
                        cpu.d=0
                        cpu.c=(x^y)&1
                        cpu.call(origin,3000)
                        b=mags[y]
                        expected=(tab0[max(a,b)]+tab1[min(a,b)])&255
                        self.assertEqual(cpu.mem[io+8],expected,(origin,x,y))
                        self.assertEqual(cpu.mem[io+9],0x5a)
                        self.assertEqual((cpu.mem[io],cpu.mem[io+4]),(x,y))
                        self.assertEqual(cpu.c,0)
                        self.assertEqual(cpu.sp,old_stack)
                self.assertEqual(bytes(cpu.mem[origin:origin+len(prg)-2]),
                                 before,"compiled kernel or data modified")

    def test_multiple_aligned_modules_and_ram_guard(self):
        for names in (["DIST8_ACCURATE","ISQRT16"],
                      ["DIST8_ACCURATE","ATAN2_8"],
                      ["DIST8_ACCURATE","DIST8_FAST","ISQRT16"]):
            with self.subTest(names=names),tempfile.TemporaryDirectory() as d:
                man=selective_linker.build(
                    self.plan(names,zp_budget=0,ram_budget=4000),Path(d))
                self.assertEqual(set(man["link_exports"]),{"MATH_"+x for x in names})
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],
                                 2 if "DIST8_FAST" in names else 2)
                self.assertEqual(len((Path(d)/"math_selective.prg").read_bytes())-2,
                                 man["resource_use"]["image_span_bytes"])
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(
                    self.plan(["DIST8_ACCURATE"],zp_budget=0,ram_budget=801),
                    Path(d))
            self.assertFalse((Path(d)/"math_selective.prg").exists())


if __name__=="__main__":
    unittest.main()
