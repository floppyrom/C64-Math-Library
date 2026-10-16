#!/usr/bin/env python3
"""Exact V1/V2 accurate signed distance, all-byte-pair CPU and table provenance."""
from __future__ import annotations

from pathlib import Path
import hashlib
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
import selective_dist8_accurate as tables
from mini6502 import CPU

PROFILES = ("v1_balanced", "v2_pareto_fast", "v3_reu_512k",
            "v4_reu_16m", "v5_hybrid_lowzp")
VARIANTS = ("link:v1-ram-tables", "link:v2-zp-tables")


def ref(x: int, y: int) -> int:
    a = abs(x if x < 128 else x - 256)
    b = abs(y if y < 128 else y - 256)
    return (tables.MAJOR_BYTES[max(a,b)] +
            tables.MINOR_BYTES[min(a,b)]) & 255


class AccurateDist8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, selections, **kwargs):
        return math_builder.create_plan(self.index, selections, **kwargs)

    def test_tables_identical_exact_shipped_v1_to_v5(self):
        self.assertEqual((len(tables.MAJOR_BYTES),len(tables.MINOR_BYTES)), (256,256))
        for profile in PROFILES:
            data = (ROOT/profile/"resident"/("math_"+profile+"_game_math.prg")).read_bytes()
            base = int.from_bytes(data[:2],"little")
            for start, expected in ((0x9a00,tables.MAJOR_BYTES),
                                    (0x9b00,tables.MINOR_BYTES)):
                index = start-base+2
                self.assertEqual(data[index:index+256],expected,(profile,start))
        self.assertEqual(ref(0,0),0)
        self.assertEqual(ref(255,0),tables.MAJOR_BYTES[1])
        self.assertEqual(ref(128,0),tables.MAJOR_BYTES[128])

    def test_exhaustive_all_signed_pairs_each_variant_two_relocations(self):
        for variant in VARIANTS:
            for code,io,zb in ((0x8000,0xc000,0x50),
                               (0x80be,0xc040,0x70)):
                with self.subTest(variant=variant,code=code), tempfile.TemporaryDirectory() as tmp:
                    zpn=0 if variant.startswith("link:v1") else 2
                    scratch=2 if zpn==0 else 0
                    plan=self.plan(["DIST8_ACCURATE"],pins={"DIST8_ACCURATE":variant},
                                   zp_budget=zpn,ram_budget=802)
                    man=selective_linker.build(
                        plan,Path(tmp),
                        memory={"code_base":code,"math_io":io,"zp_base":zb})
                    self.assertEqual(man["resource_use"]["zero_page_bytes"],zpn)
                    self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],scratch)
                    self.assertEqual(man["resource_use"]["shared_table_bytes"],512)
                    self.assertEqual(len(man["shared_tables"]),1)
                    self.assertEqual(man["shared_tables"][0]["users"],["MATH_DIST8_ACCURATE"])
                    path=Path(tmp)/"math_selective.prg"
                    image=path.read_bytes()
                    start=int.from_bytes(image[:2],"little")
                    entry=int(man["operations"][0]["entry"][1:],16)
                    self.assertEqual(entry,code)
                    cpu=CPU(bytearray(65536))
                    cpu.mem[start:start+len(image)-2]=image[2:]
                    saved=bytes(cpu.mem[start:start+len(image)-2])
                    table_base=int(man["shared_tables"][0]["start"][1:],16)
                    self.assertEqual(cpu.mem[table_base:table_base+512],
                                     tables.MAJOR_BYTES+tables.MINOR_BYTES)
                    sp=cpu.sp
                    for x in range(256):
                        for y in range(256):
                            cpu.mem[io]=x
                            cpu.mem[io+1]=0xa1
                            cpu.mem[io+4]=y
                            cpu.mem[io+5]=0xb2
                            cpu.mem[io+8]=0x47
                            cpu.mem[io+9]=0x58
                            cpu.d=0
                            cpu.c=(x+y)&1
                            cpu.call(entry,3000)
                            self.assertEqual((cpu.mem[io+8],cpu.mem[io+9],cpu.c),
                                             (ref(x,y),0x58,0),(variant,code,x,y))
                            self.assertEqual((cpu.mem[io],cpu.mem[io+1],
                                              cpu.mem[io+4],cpu.mem[io+5]),
                                             (x,0xa1,y,0xb2))
                            self.assertEqual(cpu.sp,sp)
                    self.assertEqual(bytes(cpu.mem[start:start+len(image)-2]),saved)

    def test_budget_and_hardware_claims(self):
        options=selective_linker.available_variants()["MATH_DIST8_ACCURATE"]
        self.assertEqual({v["id"] for v in options},set(VARIANTS))
        for op in options:
            self.assertEqual(op["build_targets"],["c64"])
            self.assertEqual(op["validation_path"],"tools/test_selective_dist8_accurate.py")
            self.assertEqual(set(op["dependency_sha256"]),
                             {"tools/selective_dist8_accurate.py"})
        with tempfile.TemporaryDirectory() as tmp:
            for variant, minimum,zpn in (("link:v1-ram-tables",802,0),
                                         ("link:v2-zp-tables",800,2)):
                plan=self.plan(["DIST8_ACCURATE"],
                               pins={"DIST8_ACCURATE":variant},
                               zp_budget=zpn,ram_budget=minimum)
                man=selective_linker.build(plan,Path(tmp))
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],minimum)
                with self.assertRaisesRegex(selective_linker.LinkError,"budget"):
                    selective_linker.build(
                        self.plan(["DIST8_ACCURATE"],pins={"DIST8_ACCURATE":variant},
                                  zp_budget=zpn,ram_budget=minimum-1),Path(tmp))
        with tempfile.TemporaryDirectory() as tmp:
            plan=self.plan(["DIST8_ACCURATE","DIST8_FAST","SIN8",
                            "COS8","SINCOS8","ATAN2_8","ISQRT16"],
                           zp_budget=0,ram_budget=4400,
                           pins={"DIST8_ACCURATE":"link:v1-ram-tables"})
            man=selective_linker.build(plan,Path(tmp))
            self.assertEqual(set(man["link_exports"]),
                             {"MATH_DIST8_ACCURATE","MATH_DIST8_FAST","MATH_SIN8",
                              "MATH_COS8","MATH_SINCOS8","MATH_ATAN2_8",
                              "MATH_ISQRT16"})
            self.assertEqual(man["resource_use"]["shared_table_bytes"],768)
            self.assertEqual({t["name"] for t in man["shared_tables"]},
                             {"SINE8_SHARED","DIST8_ACCURATE_SHARED"})
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)


if __name__=="__main__":
    unittest.main()
