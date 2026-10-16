#!/usr/bin/env python3
"""Exhaustive 8x8 multiply and cross-width sequential-call qualification."""
from __future__ import annotations

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


class SelectiveUMUL8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def build(self, out, ops, code=0x8000, io=0xc000):
        plan = math_builder.create_plan(self.index, ops, objective="size",
                                        zp_budget=0, ram_budget=350)
        manifest = selective_linker.build(
            plan, out, memory={"code_base": code, "math_io": io})
        payload = (out / "math_selective.prg").read_bytes()
        self.assertEqual(payload[:2], code.to_bytes(2, "little"))
        cpu = CPU(bytearray(65536))
        cpu.mem[code:code+len(payload)-2] = payload[2:]
        exports = {op["api"]: int(op["entry"][1:], 16)
                   for op in manifest["operations"]}
        return cpu, exports, manifest

    def test_exhaustive_8_by_8_with_carry_and_inputs(self):
        for code, io in ((0x8000, 0xc000), (0x7123, 0xc040)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as d:
                cpu, exports, man = self.build(Path(d), ["UMUL8"], code, io)
                res = man["resource_use"]
                self.assertEqual(res["code_and_tables_bytes"], 60)
                self.assertEqual(res["image_span_bytes"], 60)
                self.assertEqual(res["zero_page_bytes"], 0)
                self.assertEqual(res["private_ram_scratch_bytes"], 3)
                self.assertEqual(res["main_ram_total_bytes"], 95)
                address = exports["MATH_UMUL8"]
                original_image = bytes(cpu.mem[code:code+60])
                stack = cpu.sp
                for x in range(256):
                    for y in range(256):
                        cpu.mem[io], cpu.mem[io+4] = x, y
                        cpu.mem[io+8:io+10] = b"\xaa\xaa"
                        cpu.d = 0
                        cpu.c = (x+y) & 1
                        cpu.call(address, 30000)
                        result = cpu.mem[io+8] | cpu.mem[io+9] << 8
                        self.assertEqual(result, x*y, (code, x, y))
                        self.assertEqual(cpu.c, 0, (code, x, y, "C"))
                        self.assertEqual(cpu.mem[io], x)
                        self.assertEqual(cpu.mem[io+4], y)
                        self.assertEqual(cpu.sp, stack)
                self.assertEqual(bytes(cpu.mem[code:code+60]), original_image)

    def test_combined_umul8_and_umul16_shared_scratch(self):
        rng = random.Random(0xC64816)
        with tempfile.TemporaryDirectory() as d:
            cpu, exports, man = self.build(Path(d), ["UMUL8", "UMUL16"])
            self.assertEqual(man["resource_use"]["image_span_bytes"], 168)
            self.assertEqual(man["resource_use"]["zero_page_bytes"], 0)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"], 6)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"], 206)
            before = bytes(cpu.mem[0x8000:0x8000+168])
            for _ in range(1200):
                x, y = rng.randrange(65536), rng.randrange(65536)
                cpu.mem[0xc000:0xc002] = x.to_bytes(2, "little")
                cpu.mem[0xc004:0xc006] = y.to_bytes(2, "little")
                cpu.d = 0
                cpu.c = 1
                cpu.call(exports["MATH_UMUL8"], 20000)
                self.assertEqual(int.from_bytes(cpu.mem[0xc008:0xc00a], "little"),
                                 (x & 255)*(y & 255))
                self.assertEqual(cpu.c, 0)
                cpu.c = 1
                cpu.call(exports["MATH_UMUL16"], 50000)
                self.assertEqual(int.from_bytes(cpu.mem[0xc008:0xc00c], "little"),
                                 x*y)
                self.assertEqual(cpu.c, 0)
                self.assertEqual(int.from_bytes(cpu.mem[0xc000:0xc002], "little"),
                                 x)
                self.assertEqual(int.from_bytes(cpu.mem[0xc004:0xc006], "little"),
                                 y)
                self.assertEqual(cpu.sp, 0xfd)
            self.assertEqual(bytes(cpu.mem[0x8000:0x8000+168]), before)

    def test_budget_rejection_and_explicit_size(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            good = math_builder.create_plan(
                self.index, ["UMUL8"], zp_budget=0, ram_budget=95)
            man = selective_linker.build(good, out)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"], 95)
            bad = math_builder.create_plan(
                self.index, ["UMUL8"], zp_budget=0, ram_budget=94)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(bad, out / "bad")


if __name__ == "__main__":
    unittest.main()
