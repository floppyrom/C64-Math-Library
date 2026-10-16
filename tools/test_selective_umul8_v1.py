#!/usr/bin/env python3
"""Original V1 unsigned 8x8 multiplier: exhaustive relocations and ABI proof."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
import selective_umul8_v1 as original
from mini6502 import CPU


class OriginalV1UMUL8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def make_plan(self, **kwargs):
        return math_builder.create_plan(
            self.index, ["UMUL8"], pins={"UMUL8": "link:v1-resident-fast"}, **kwargs)

    def test_original_511_entry_tables_match_released_v1(self):
        path = ROOT / "v1_balanced/resident/math_v1_balanced_game_math.prg"
        prg = path.read_bytes()
        load = int.from_bytes(prg[:2], "little")
        low, high = original.table_bytes()
        self.assertEqual(len(low), 511)
        self.assertEqual(len(high), 511)
        self.assertEqual(prg[2+0x8000-load:2+0x8000-load+511], low)
        self.assertEqual(prg[2+0x8200-load:2+0x8200-load+511], high)

    def test_all_65536_operands_at_two_independent_relocations(self):
        for start, io, zp in ((0x8000, 0xc000, 0x50),
                              (0x7123, 0xc040, 0x70)):
            with self.subTest(base=start), tempfile.TemporaryDirectory() as folder:
                plan = self.make_plan(zp_budget=4, ram_budget=1311)
                man = selective_linker.build(
                    plan, Path(folder),
                    memory={"code_base":start,"math_io":io,"zp_base":zp})
                use = man["resource_use"]
                self.assertEqual(use["zero_page_bytes"], 4)
                self.assertEqual(use["private_ram_scratch_bytes"], 0)
                self.assertEqual(use["code_and_tables_bytes"], 1073)
                self.assertLessEqual(use["main_ram_total_bytes"], 1311)
                self.assertEqual(man["operations"][0]["entry"], "$%04X" % start)
                prg = (Path(folder) / "math_selective.prg").read_bytes()
                cpu = CPU(bytearray(65536))
                cpu.mem[start:start+len(prg)-2] = prg[2:]
                original_binary = bytes(cpu.mem[start:start+len(prg)-2])
                stack = cpu.sp
                for x in range(256):
                    for y in range(256):
                        cpu.mem[io:io+4] = bytes((x,0x33,0x44,0x55))
                        cpu.mem[io+4:io+8] = bytes((y,0x66,0x77,0x88))
                        cpu.mem[io+8:io+12] = b"\xAA"*4
                        cpu.d = 0
                        cpu.c = (x^y)&1
                        cpu.call(start, 2000)
                        got = cpu.mem[io+8] | cpu.mem[io+9] << 8
                        self.assertEqual(got, x*y, (start,x,y))
                        self.assertEqual(cpu.c, 0, (start,x,y,"carry"))
                        self.assertEqual(cpu.sp, stack, (start,x,y,"stack"))
                        self.assertEqual(cpu.mem[io:io+4], bytes((x,0x33,0x44,0x55)))
                        self.assertEqual(cpu.mem[io+4:io+8], bytes((y,0x66,0x77,0x88)))
                        self.assertEqual(cpu.mem[io+10:io+12], b"\xAA\xAA")
                self.assertEqual(bytes(cpu.mem[start:start+len(prg)-2]), original_binary)

    def test_resource_limits_mixed_linking_and_source_provenance(self):
        with tempfile.TemporaryDirectory() as folder:
            too_little = self.make_plan(zp_budget=3,ram_budget=1311)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(too_little,Path(folder))
            self.assertFalse((Path(folder)/"math_selective.prg").exists())
            original = self.make_plan(zp_budget=4,ram_budget=1310)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(original,Path(folder))
        variant = next(v for v in selective_linker.available_variants()["MATH_UMUL8"]
                       if v["id"] == "link:v1-resident-fast")
        self.assertEqual(variant["validation_path"],"tools/test_selective_umul8_v1.py")
        self.assertEqual(list(variant["dependency_sha256"]),["tools/selective_umul8_v1.py"])
        with tempfile.TemporaryDirectory() as folder:
            plan = self.make_plan(zp_budget=4, ram_budget=2000)
            plan["operations"][0]["available_source_variants"][-1]["source_sha256"] = "0"*64
            # Explicitly reject a changed *selected* source; order is not fixed.
            selected = next(v for v in plan["operations"][0]["available_source_variants"]
                            if v["id"]=="link:v1-resident-fast")
            selected["source_sha256"]="0"*64
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(plan, Path(folder))


if __name__=="__main__":
    unittest.main()
