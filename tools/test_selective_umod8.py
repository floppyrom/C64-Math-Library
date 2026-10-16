#!/usr/bin/env python3
"""Exhaustive 6502 CPU qualification of the original self-modifying V1 UMOD8."""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
from mini6502 import Assembler, CPU

VARIANT = "link:v1-resident-smc"
SIZE = 157


class V1UnsignedMod8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, names, **kwargs):
        return math_builder.create_plan(self.index, names, **kwargs)

    def test_exhaustive_65536_pairs_at_two_relocations(self):
        for origin, io, zp in ((0x8000, 0xc000, 0x50),
                               (0x7123, 0xc040, 0x70)):
            with self.subTest(origin=origin), tempfile.TemporaryDirectory() as tmp:
                plan = self.plan(["UMOD8"], pins={"UMOD8": VARIANT},
                                 zp_budget=2, ram_budget=189)
                result = selective_linker.build(
                    plan, Path(tmp),
                    memory={"code_base":origin, "math_io":io, "zp_base":zp})
                self.assertEqual(result["resource_use"]["code_and_tables_bytes"], SIZE)
                self.assertEqual(result["resource_use"]["main_ram_total_bytes"], 189)
                self.assertEqual(result["resource_use"]["zero_page_bytes"], 2)
                self.assertEqual(result["resource_use"]["private_ram_scratch_bytes"], 0)
                self.assertEqual(result["operations"][0]["entry"], "$%04X" % origin)
                image = (Path(tmp) / "math_selective.prg").read_bytes()
                self.assertEqual(int.from_bytes(image[:2], "little"), origin)
                self.assertEqual(hashlib.sha256(image).hexdigest(),
                                 result["prg_sha256"])
                self.assertEqual(len(image) - 2, SIZE)

                # Identify precisely the only two bytes that the historical
                # implementation is allowed to self-modify (SBC/ADC immediates).
                source = selective_linker.relocate_source(
                    selective_linker.MODULES["MATH_UMOD8"][VARIANT],
                    {"KERNEL_CODE":origin, "INPUT_NUM":io+16,
                     "INPUT_DIV":io+20, "OUTPUT_QUOT":io+24,
                     "OUTPUT_REM":io+28, "TEMP_ZP":zp},
                    ROOT)
                memory, labels, _ = Assembler().assemble(source)
                self.assertEqual(len(memory), SIZE)
                mutable = {labels["L4636"]+1, labels["L463A"]+1}
                self.assertEqual({memory[p] for p in mutable}, {0})
                self.assertEqual(memory[labels["L4636"]], 0xE9) # SBC #imm
                self.assertEqual(memory[labels["L463A"]], 0x69) # ADC #imm

                cpu = CPU(bytearray(65536))
                cpu.mem[origin:origin+SIZE] = image[2:]
                pristine = bytes(cpu.mem[origin:origin+SIZE])
                stack = cpu.sp
                for denominator in range(256):
                    for numerator in range(256):
                        cpu.mem[io+16:io+20] = bytes((numerator,0xAB,0xCD,0xEF))
                        cpu.mem[io+20:io+24] = bytes((denominator,0xBA,0xDC,0xFE))
                        cpu.mem[io+24:io+28] = b"\x55"*4
                        cpu.mem[io+28:io+32] = b"\x66"*4
                        cpu.c = (numerator ^ denominator)&1
                        cpu.d = 0
                        cpu.call(origin, 12000)
                        want = numerator % denominator if denominator else 0
                        self.assertEqual((cpu.mem[io+28], cpu.c),
                                         (want, int(denominator==0)),
                                         (origin, numerator, denominator))
                        self.assertEqual(cpu.mem[io+24:io+28], b"\x55"*4,
                                         (origin,numerator,denominator,"quotient"))
                        self.assertEqual(cpu.mem[io+29:io+32], b"\x66"*3)
                        self.assertEqual(cpu.mem[io+16:io+20],
                                         bytes((numerator,0xAB,0xCD,0xEF)))
                        self.assertEqual(cpu.mem[io+20:io+24],
                                         bytes((denominator,0xBA,0xDC,0xFE)))
                        self.assertEqual(cpu.sp, stack)

                changed = {origin+i for i,(a,b) in enumerate(
                    zip(pristine,cpu.mem[origin:origin+SIZE])) if a != b}
                self.assertTrue(changed <= mutable, (origin,changed,mutable))
                self.assertTrue(changed, "Expected actual code-operand modification")

    def test_metadata_mixed_modules_and_fail_closed_constraints(self):
        variant, = selective_linker.available_variants()["MATH_UMOD8"]
        self.assertEqual(variant["id"], VARIANT)
        self.assertEqual(variant["validation_path"], "tools/test_selective_umod8.py")
        self.assertEqual(variant["resources_reported"]["code_and_table_bytes"], SIZE)
        self.assertEqual(variant["zp_bytes_reported"], 2)
        self.assertEqual(variant["build_targets"], ["c64"])
        self.assertIn("writable", variant["notes"])
        with tempfile.TemporaryDirectory() as tmp:
            plan = self.plan(["UMOD8","UDIV8","SDIV8","SMOD8"],
                             zp_budget=2,ram_budget=1200)
            result = selective_linker.build(plan,Path(tmp))
            self.assertEqual(set(result["link_exports"]),{
                "MATH_UMOD8","MATH_UDIV8","MATH_SDIV8","MATH_SMOD8"})
            self.assertEqual(result["resource_use"]["zero_page_bytes"], 2)
            self.assertEqual(result["resource_use"]["code_and_tables_bytes"],
                             SIZE+294+530)
        for zp_budget, ram_budget in ((1,189),(2,188)):
            with tempfile.TemporaryDirectory() as tmp:
                plan = self.plan(["UMOD8"], zp_budget=zp_budget,
                                 ram_budget=ram_budget)
                with self.assertRaises(selective_linker.LinkError):
                    selective_linker.build(plan, Path(tmp))
                self.assertFalse((Path(tmp)/"math_selective.prg").exists())


if __name__ == "__main__":
    unittest.main()
