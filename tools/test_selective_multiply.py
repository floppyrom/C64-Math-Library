#!/usr/bin/env python3
"""Arithmetic and mixed-call validation for selectively linked UMUL16."""
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

EDGES = (0, 1, 2, 3, 7, 15, 16, 127, 128, 255, 256, 257, 511,
         1023, 32767, 32768, 32769, 65534, 65535)


class SelectiveMultiplyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def corpus(self):
        rng = random.Random(0xC64F16)
        return ([(x, y) for x in EDGES for y in EDGES] +
                [(rng.randrange(65536), rng.randrange(65536))
                 for _ in range(3200)] +
                [(x, 0) for x in EDGES] +
                [(0xffff, x) for x in EDGES])

    def test_complete_result_and_scratch_relocations(self):
        cases = self.corpus()
        for code, io, scratch in ((0x8000, 0xc000, 0xc020),
                                  (0x7123, 0xc040, 0xc080),
                                  (0x830f, 0xc100, 0xc180)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as d:
                plan = math_builder.create_plan(
                    self.index, ["UMUL16"], objective="size",
                    zp_budget=0, ram_budget=146)
                manifest = selective_linker.build(
                    plan, Path(d),
                    memory={"code_base": code, "math_io": io,
                            "scratch_base": scratch})
                self.assertEqual(manifest["resource_use"], {
                    "code_and_tables_bytes": 108,
                    "image_span_bytes": 108,
                    "shared_table_bytes": 0,
                    "alignment_padding_bytes": 0,
                    "public_io_bytes": 32,
                    "private_ram_scratch_bytes": 6,
                    "main_ram_total_bytes": 146,
                    "zero_page_bytes": 0,
                    "persistent_stack_page_bytes": 0,
                })
                image = (Path(d) / "math_selective.prg").read_bytes()
                self.assertEqual(len(image), 110)
                self.assertEqual(image[:2], code.to_bytes(2, "little"))
                mem = bytearray(65536)
                mem[code:code+108] = image[2:]
                original = bytes(mem[code:code+108])
                cpu = CPU(mem)
                entry = int(manifest["operations"][0]["entry"][1:], 16)
                sp = cpu.sp
                for x, y in cases:
                    mem[io:io+2] = x.to_bytes(2, "little")
                    mem[io+4:io+6] = y.to_bytes(2, "little")
                    mem[io+8:io+12] = b"\x55" * 4
                    cpu.d = 0
                    cpu.c = (x ^ y) & 1
                    cpu.call(entry, 50000)
                    self.assertEqual(
                        int.from_bytes(mem[io+8:io+12], "little"),
                        x*y, (code, x, y))
                    self.assertEqual(int.from_bytes(mem[io:io+2], "little"), x)
                    self.assertEqual(int.from_bytes(mem[io+4:io+6], "little"), y)
                    self.assertEqual(cpu.c, 0)
                self.assertEqual(cpu.sp, sp)
                self.assertEqual(bytes(mem[code:code+108]), original)

    def test_multiply_divide_atan2_interleaving(self):
        rng = random.Random(0x16A7A2)
        with tempfile.TemporaryDirectory() as d:
            plan = math_builder.create_plan(
                self.index, ["UMUL16", "UDIV16", "ATAN2_8"],
                objective="size", zp_budget=2, ram_budget=1700)
            manifest = selective_linker.build(plan, Path(d))
            self.assertEqual(manifest["resource_use"]["zero_page_bytes"], 2)
            self.assertEqual(manifest["resource_use"]["private_ram_scratch_bytes"], 6)
            load = int(manifest["memory_map"]["code_start"][1:], 16)
            image = (Path(d) / "math_selective.prg").read_bytes()[2:]
            mem = bytearray(65536)
            mem[load:load+len(image)] = image
            before = bytes(mem[load:load+len(image)])
            cpu = CPU(mem)
            entries = {x["api"]: int(x["entry"][1:], 16)
                       for x in manifest["operations"]}
            sp = cpu.sp
            for _ in range(600):
                x = rng.randrange(65536)
                y = rng.randrange(65536)
                mem[0xc000:0xc002] = x.to_bytes(2, "little")
                mem[0xc004:0xc006] = y.to_bytes(2, "little")
                cpu.d = 0
                cpu.call(entries["MATH_UMUL16"], 50000)
                self.assertEqual(
                    int.from_bytes(mem[0xc008:0xc00c], "little"), x*y)
                mem[0xc010:0xc012] = x.to_bytes(2, "little")
                mem[0xc014:0xc016] = y.to_bytes(2, "little")
                cpu.call(entries["MATH_UDIV16"], 200000)
                self.assertEqual(
                    int.from_bytes(mem[0xc018:0xc01a], "little"),
                    x//y if y else 0)
                self.assertEqual(
                    int.from_bytes(mem[0xc01c:0xc01e], "little"),
                    x%y if y else 0)
                cpu.call(entries["MATH_ATAN2_8"], 20000)
                self.assertEqual(cpu.c, 0)
                self.assertEqual(cpu.sp, sp)
            self.assertEqual(bytes(mem[load:load+len(image)]), before)

    def test_atan2_module_can_pack_between_arithmetic_modules(self):
        # The globally optimal layout is not ATAN2-first or ATAN2-last:
        # 108-byte UMUL16 precedes ATAN2 and the 323-byte UDIV16 follows it.
        with tempfile.TemporaryDirectory() as d:
            plan = math_builder.create_plan(
                self.index, ["UDIV16", "UMUL16", "ATAN2_8"],
                objective="size", zp_budget=2, ram_budget=1129,
                pins={"ATAN2_8": "link:compact"})
            man = selective_linker.build(plan, Path(d))
            self.assertEqual(man["link_order"],
                             ["MATH_UMUL16", "MATH_ATAN2_8", "MATH_UDIV16"])
            resources = man["resource_use"]
            self.assertEqual(resources["code_and_tables_bytes"], 1037)
            self.assertEqual(resources["alignment_padding_bytes"], 54)
            self.assertEqual(resources["image_span_bytes"], 1091)
            self.assertEqual(resources["main_ram_total_bytes"], 1129)
            self.assertEqual(resources["zero_page_bytes"], 2)
            failed = math_builder.create_plan(
                self.index, ["UDIV16", "UMUL16", "ATAN2_8"],
                objective="size", zp_budget=2, ram_budget=1128)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(failed, Path(d) / "bad")

    def test_small_memory_and_no_zp(self):
        with tempfile.TemporaryDirectory() as d:
            plan = math_builder.create_plan(
                self.index, ["UMUL16"], objective="zp",
                zp_budget=0, ram_budget=146)
            manifest = selective_linker.build(plan, Path(d))
            self.assertEqual(manifest["resource_use"]["main_ram_total_bytes"], 146)
            failed = math_builder.create_plan(
                self.index, ["UMUL16"], zp_budget=0, ram_budget=145)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(failed, Path(d) / "fail")


if __name__ == "__main__":
    unittest.main()
