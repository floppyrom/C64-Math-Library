#!/usr/bin/env python3
"""Exhaustive 65536-input source-built ISQRT16 and mixed-link qualification."""
from __future__ import annotations

import hashlib
from math import isqrt
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
import selective_isqrt16
from mini6502 import CPU


class SelectiveISQRT16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, names, **kw):
        return math_builder.create_plan(self.index, names, **kw)

    def test_exact_generated_tables(self):
        lo, hi, seeds = selective_isqrt16.tables()
        self.assertEqual(tuple(len(x) for x in (lo, hi, seeds)), (256,)*3)
        for r in range(256):
            self.assertEqual(lo[r] | hi[r] << 8, r*r)
            self.assertEqual(seeds[r], isqrt((r << 8) | 255))

    def test_exhaustive_binary_two_relocations(self):
        for origin, io in ((0x8000, 0xc000), (0x7123, 0xc040)):
            with self.subTest(origin=origin), tempfile.TemporaryDirectory() as d:
                result = selective_linker.build(
                    self.plan(["ISQRT16"], zp_budget=0, ram_budget=1100, pins={"ISQRT16":"link:square-table"}),
                    Path(d), memory={"code_base": origin, "math_io": io})
                resource = result["resource_use"]
                self.assertEqual(resource["code_and_tables_bytes"], 806)
                self.assertEqual(resource["zero_page_bytes"], 0)
                self.assertEqual(resource["private_ram_scratch_bytes"], 0)
                self.assertEqual(resource["alignment_padding_bytes"],
                                 (-origin - 38) % 256)
                self.assertEqual(resource["main_ram_total_bytes"],
                                 resource["image_span_bytes"] + 32)
                self.assertEqual(result["operations"][0]["variant"], "link:square-table")
                self.assertEqual(result["operations"][0]["dependencies"][0]["source_path"],
                                 "tools/selective_isqrt16.py")
                prg = (Path(d) / "math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(prg).hexdigest(),
                                 result["prg_sha256"])
                cpu = CPU(bytearray(65536))
                cpu.mem[origin:origin+len(prg)-2] = prg[2:]
                before = bytes(cpu.mem[origin:origin+len(prg)-2])
                entry = int(result["operations"][0]["entry"][1:], 16)
                stack = cpu.sp
                for n in range(65536):
                    cpu.mem[io+16:io+18] = n.to_bytes(2, "little")
                    cpu.mem[io+8:io+10] = b"\x55\x55"
                    cpu.d = 0
                    cpu.c = n & 1
                    cpu.call(entry, 10000)
                    self.assertEqual(cpu.mem[io+8] | cpu.mem[io+9] << 8,
                                     isqrt(n), (origin, n))
                    self.assertEqual(cpu.mem[io+16] | cpu.mem[io+17] << 8, n)
                    self.assertEqual(cpu.c, 0, (origin, n, "C"))
                    self.assertEqual(cpu.sp, stack)
                self.assertEqual(bytes(cpu.mem[origin:origin+len(prg)-2]),
                                 before, "kernel/tables unexpectedly modified")

    def test_shared_aligned_module_and_safe_budgets(self):
        for names in (["ISQRT16", "UMUL16"], ["ISQRT16", "ATAN2_8"]):
            with self.subTest(names=names), tempfile.TemporaryDirectory() as d:
                result = selective_linker.build(
                    self.plan(names, zp_budget=0, ram_budget=2800), Path(d))
                self.assertEqual(set(result["link_exports"]),
                                 {"MATH_"+s for s in names})
                self.assertEqual(result["resource_use"]["zero_page_bytes"], 0)
                self.assertEqual(len((Path(d)/"math_selective.prg").read_bytes()) - 2,
                                 result["resource_use"]["image_span_bytes"])
        with tempfile.TemporaryDirectory() as d:
            self.assertRaises(selective_linker.LinkError,
                selective_linker.build,
                self.plan(["ISQRT16"], zp_budget=0, ram_budget=1055, pins={"ISQRT16":"link:square-table"}),
                Path(d))
            self.assertFalse((Path(d)/"math_selective.prg").exists())

    def test_explicit_pin_and_unavailable_source(self):
        variant = "link:square-table"
        with tempfile.TemporaryDirectory() as d:
            result = selective_linker.build(
                self.plan(["ISQRT16"], pins={"ISQRT16": variant}), Path(d))
            self.assertEqual(result["operations"][0]["variant"], variant)


if __name__ == "__main__":
    unittest.main()
