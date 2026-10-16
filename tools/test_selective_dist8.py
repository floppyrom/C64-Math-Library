#!/usr/bin/env python3
"""Exhaustive CPU-model qualification of the transplanted historical DIST8_FAST."""
from __future__ import annotations

from pathlib import Path
import hashlib
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
from mini6502 import CPU


def fast_distance(x: int, y: int) -> int:
    """Exact resident V1 semantics, including signed -128 and u8 wraparound."""
    sx = x if x < 128 else x - 256
    sy = y if y < 128 else y - 256
    hi, lo = sorted((abs(sx), abs(sy)), reverse=True)
    return (hi + (lo >> 1)) & 255


class HistoricalDIST8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, ops, **kw):
        return math_builder.create_plan(self.index, ops, **kw)

    def test_exact_reference_and_metadata(self):
        candidates = selective_linker.available_variants()
        option, = candidates["MATH_DIST8_FAST"]
        self.assertEqual(option["validation_path"], "tools/test_selective_dist8.py")
        self.assertEqual(option["resources_reported"]["code_and_table_bytes"], 61)
        self.assertEqual(option["resources_reported"]["scratch_bytes"], 2)
        self.assertEqual(option["zp_bytes_reported"], 0)
        root, = candidates["MATH_ISQRT16"]
        self.assertEqual(root["validation_path"], "tools/test_selective_isqrt16.py")
        self.assertEqual(fast_distance(128, 128), 192)
        self.assertEqual(fast_distance(255, 1), 1)
        self.assertEqual(fast_distance(127, 127), 190)

    def test_all_signed_input_pairs_two_memory_placements(self):
        for origin, io in ((0x8000, 0xc000), (0x7123, 0xc040)):
            with self.subTest(origin=origin), tempfile.TemporaryDirectory() as folder:
                plan = self.plan(["DIST8_FAST"], zp_budget=0, ram_budget=95,
                                 pins={"DIST8_FAST": "link:resident-approx"})
                result = selective_linker.build(
                    plan, Path(folder),
                    memory={"code_base": origin, "math_io": io})
                use = result["resource_use"]
                self.assertEqual(use["code_and_tables_bytes"], 61)
                self.assertEqual(use["main_ram_total_bytes"], 95)
                self.assertEqual(use["zero_page_bytes"], 0)
                self.assertEqual(use["private_ram_scratch_bytes"], 2)
                self.assertEqual(result["operations"][0]["entry"], "$%04X" % origin)
                self.assertEqual(result["operations"][0]["scratch_lifetime"], "exclusive_call")
                image = (Path(folder) / "math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(image).hexdigest(), result["prg_sha256"])
                cpu = CPU(bytearray(65536))
                cpu.mem[origin:origin+len(image)-2] = image[2:]
                before = bytes(cpu.mem[origin:origin+len(image)-2])
                sp = cpu.sp
                for x in range(256):
                    cpu.mem[io] = x
                    for y in range(256):
                        cpu.mem[io+4] = y
                        cpu.mem[io+8] = 0xA5
                        cpu.mem[io+9] = 0x5A
                        cpu.d = 0
                        cpu.c = (x ^ y) & 1
                        cpu.call(origin, 3000)
                        self.assertEqual(cpu.mem[io+8], fast_distance(x, y),
                                         (origin, x, y))
                        self.assertEqual(cpu.mem[io+9], 0x5A)
                        self.assertEqual((cpu.mem[io], cpu.mem[io+4]), (x, y))
                        self.assertEqual(cpu.c, 0, (origin, x, y, "carry"))
                        self.assertEqual(cpu.sp, sp)
                self.assertEqual(bytes(cpu.mem[origin:origin+len(image)-2]),
                                 before, "source kernel mutated during execution")

    def test_mixed_public_abi_and_tight_budgets(self):
        with tempfile.TemporaryDirectory() as folder:
            plan = self.plan(["DIST8_FAST", "ISQRT16", "UMUL16"],
                             zp_budget=0, ram_budget=1400)
            result = selective_linker.build(plan, Path(folder))
            self.assertEqual(set(result["link_exports"]), {
                "MATH_DIST8_FAST", "MATH_ISQRT16", "MATH_UMUL16"})
            self.assertEqual(result["resource_use"]["private_ram_scratch_bytes"], 6)
            io = int(result["memory_map"]["math_io_start"][1:], 16)
            binary = (Path(folder)/"math_selective.prg").read_bytes()
            start = int.from_bytes(binary[:2], "little")
            cpu = CPU(bytearray(65536))
            cpu.mem[start:start+len(binary)-2] = binary[2:]
            entry = int(next(r["entry"][1:] for r in result["operations"]
                             if r["api"] == "MATH_DIST8_FAST"), 16)
            rng = random.Random(0xD158)
            for _ in range(2000):
                x, y = rng.randrange(256), rng.randrange(256)
                cpu.mem[io], cpu.mem[io+4] = x, y
                cpu.d = 0
                cpu.call(entry, 3000)
                self.assertEqual(cpu.mem[io+8], fast_distance(x, y))
                self.assertEqual(cpu.c, 0)

        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(selective_linker.LinkError,
                                        "fits RAM/ZP budgets"):
                selective_linker.build(
                    self.plan(["DIST8_FAST"], zp_budget=0, ram_budget=94),
                    Path(folder))
            self.assertFalse((Path(folder)/"math_selective.prg").exists())


if __name__ == "__main__":
    unittest.main()
