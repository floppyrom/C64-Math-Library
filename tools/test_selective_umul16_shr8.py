#!/usr/bin/env python3
"""Source-linked unsigned 16x16 >> 8: full ABI, relocation, budget and mixed calls."""
from __future__ import annotations

import random
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
from mini6502 import CPU

EDGE = (0, 1, 2, 3, 127, 128, 255, 256, 257, 32767,
        32768, 32769, 65534, 65535)

def corpus():
    rng = random.Random(0x16A8F00D)
    return [(x, y) for x in EDGE for y in EDGE] + [
        (rng.randrange(65536), rng.randrange(65536)) for _ in range(1024)
    ]

class ShiftedMultiplyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def test_full_abi_at_relocations(self):
        for code, io, scratch in ((0x8000, 0xC000, 0xC020),
                                  (0x7123, 0xC040, 0xC080)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as tmp:
                plan = math_builder.create_plan(
                    self.index, ["UMUL16_SHR8"], objective="size",
                    zp_budget=0, ram_budget=164)
                man = selective_linker.build(
                    plan, Path(tmp), memory={"code_base": code,
                    "math_io": io, "scratch_base": scratch})
                size = man["resource_use"]
                self.assertEqual(size["image_span_bytes"], 126)
                self.assertEqual(size["private_ram_scratch_bytes"], 6)
                self.assertEqual(size["zero_page_bytes"], 0)
                self.assertEqual(size["main_ram_total_bytes"], 164)
                prg = (Path(tmp) / "math_selective.prg").read_bytes()
                self.assertEqual(prg[:2], code.to_bytes(2, "little"))
                mem = bytearray(65536)
                mem[code:code+126] = prg[2:]
                before = bytes(mem[code:code+126])
                cpu = CPU(mem)
                entry = int(man["operations"][0]["entry"][1:], 16)
                sp = cpu.sp
                for x, y in corpus():
                    mem[io:io+2] = x.to_bytes(2, "little")
                    mem[io+4:io+6] = y.to_bytes(2, "little")
                    mem[io+8:io+12] = b"\\xA5" * 4
                    cpu.d = 0
                    cpu.c = (x ^ y) & 1
                    cpu.call(entry, 50000)
                    self.assertEqual(
                        int.from_bytes(mem[io+8:io+11], "little"),
                        (x*y) >> 8, (code, x, y))
                    self.assertEqual(mem[io:io+2], x.to_bytes(2, "little"))
                    self.assertEqual(mem[io+4:io+6], y.to_bytes(2, "little"))
                    self.assertEqual(cpu.c, 0)
                    self.assertEqual(cpu.sp, sp)
                self.assertEqual(bytes(mem[code:code+126]), before)

    def test_zero_zp_budget_and_shared_scratch(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = math_builder.create_plan(
                self.index, ["UMUL16_SHR8", "UMUL16"],
                objective="size", zp_budget=0, ram_budget=272,
                pins={"UMUL16": "link:compact-zerozp",
                      "UMUL16_SHR8": "link:compact-zerozp"})
            man = selective_linker.build(plan, Path(tmp))
            use = man["resource_use"]
            self.assertEqual(use["main_ram_total_bytes"], 272)
            self.assertEqual(use["private_ram_scratch_bytes"], 6)
            self.assertEqual(use["zero_page_bytes"], 0)
            entries = {item["api"]: int(item["entry"][1:], 16)
                       for item in man["operations"]}
            load = int(man["memory_map"]["code_start"][1:], 16)
            prg = (Path(tmp) / "math_selective.prg").read_bytes()[2:]
            mem = bytearray(65536)
            mem[load:load+len(prg)] = prg
            cpu = CPU(mem)
            rng = random.Random(0x1608)
            for _ in range(320):
                x, y = rng.randrange(65536), rng.randrange(65536)
                mem[0xC000:0xC002] = x.to_bytes(2, "little")
                mem[0xC004:0xC006] = y.to_bytes(2, "little")
                cpu.d = 0
                cpu.call(entries["MATH_UMUL16"], 50000)
                self.assertEqual(
                    int.from_bytes(mem[0xC008:0xC00C], "little"), x*y)
                cpu.call(entries["MATH_UMUL16_SHR8"], 50000)
                self.assertEqual(
                    int.from_bytes(mem[0xC008:0xC00B], "little"), (x*y)>>8)
                self.assertEqual(cpu.c, 0)
            small = math_builder.create_plan(
                self.index, ["UMUL16_SHR8"], zp_budget=0, ram_budget=163)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(small, Path(tmp)/"reject")

if __name__ == "__main__":
    unittest.main()
