#!/usr/bin/env python3
"""V1-V5 byte parity and mixed-link CPU ABI proof for shared SIN/COS/SINCOS8."""
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
import selective_trig8
from mini6502 import CPU

TRIG = ("SIN8", "COS8", "SINCOS8")
PROFILES = ("v1_balanced", "v2_pareto_fast", "v3_reu_512k",
            "v4_reu_16m", "v5_hybrid_lowzp")


class TrigSharedTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, ops, **kw):
        return math_builder.create_plan(self.index, ops, **kw)

    def test_every_shipped_prg_uses_identical_lookup_bytes(self):
        table = selective_trig8.SINE_BYTES
        self.assertEqual(len(table), 256)
        self.assertEqual(tuple(table[:4]), (0, 3, 6, 9))
        self.assertEqual(table[64], 127)
        self.assertEqual(table[128], 0)
        self.assertEqual(table[192], 129)
        for profile in PROFILES:
            path = ROOT / profile / "resident" / ("math_" + profile + "_game_math.prg")
            image = path.read_bytes()
            origin = int.from_bytes(image[:2], "little")
            low = 0x9400 - origin + 2
            self.assertEqual(image[low:low+256], table, profile)

    def test_shared_256_byte_table_exhaustive_abi_two_relocations(self):
        for origin, io in ((0x8000, 0xc000), (0x7123, 0xc040)):
            with self.subTest(origin=origin), tempfile.TemporaryDirectory() as folder:
                plan = self.plan(TRIG, zp_budget=0, ram_budget=600)
                result = selective_linker.build(
                    plan, Path(folder),
                    memory={"code_base":origin, "math_io":io})
                self.assertEqual(result["resource_use"]["zero_page_bytes"], 0)
                self.assertEqual(result["resource_use"]["private_ram_scratch_bytes"], 0)
                self.assertEqual(result["resource_use"]["shared_table_bytes"], 256)
                self.assertEqual(result["resource_use"]["code_and_tables_bytes"], 304)
                self.assertEqual(result["resource_use"]["alignment_padding_bytes"],
                                 ((-origin-48) % 256))
                self.assertEqual(len(result["shared_tables"]), 1)
                shared, = result["shared_tables"]
                self.assertEqual(shared["users"], ["MATH_COS8", "MATH_SIN8", "MATH_SINCOS8"])
                self.assertEqual(shared["bytes"], 256)
                self.assertEqual(shared["sha256"],
                                 hashlib.sha256(selective_trig8.SINE_BYTES).hexdigest())
                binary = (Path(folder)/"math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(binary).hexdigest(), result["prg_sha256"])
                start = int.from_bytes(binary[:2], "little")
                cpu = CPU(bytearray(65536))
                cpu.mem[start:start+len(binary)-2] = binary[2:]
                base = int(shared["start"][1:], 16)
                self.assertEqual(base % 256, 0)
                self.assertEqual(cpu.mem[base:base+256], selective_trig8.SINE_BYTES)
                old_code = bytes(cpu.mem[start:start+len(binary)-2])
                entries = {r["api"]:int(r["entry"][1:], 16)
                           for r in result["operations"]}
                initial_sp = cpu.sp
                for x in range(256):
                    for name in TRIG:
                        cpu.mem[io] = x
                        cpu.mem[io+4] = 0x5f
                        cpu.mem[io+8] = 0x55
                        cpu.mem[io+9] = 0x5a
                        cpu.d = 0
                        cpu.c = x & 1
                        cpu.call(entries["MATH_"+name], 3000)
                        ref = selective_trig8.SINE_BYTES
                        expected_low = ref[(x+64)&255] if name == "COS8" else ref[x]
                        expected_high = ref[(x+64)&255] if name == "SINCOS8" else 0x5a
                        self.assertEqual((cpu.mem[io+8], cpu.mem[io+9]),
                                         (expected_low, expected_high),
                                         (origin, name, x))
                        self.assertEqual((cpu.mem[io], cpu.mem[io+4]), (x, 0x5f))
                        self.assertEqual(cpu.c, 0)
                        self.assertEqual(cpu.sp, initial_sp)
                self.assertEqual(bytes(cpu.mem[start:start+len(binary)-2]), old_code)

    def test_single_selects_only_one_entry_and_one_shared_page(self):
        for selected in TRIG:
            with self.subTest(operation=selected), tempfile.TemporaryDirectory() as folder:
                result = selective_linker.build(
                    self.plan([selected], zp_budget=0, ram_budget=544), Path(folder))
                self.assertEqual(result["link_exports"], ["MATH_"+selected])
                self.assertEqual(result["resource_use"]["shared_table_bytes"], 256)
                self.assertEqual(len(result["shared_tables"]), 1)
                self.assertEqual(result["shared_tables"][0]["users"], ["MATH_"+selected])

    def test_mixed_aligned_modules_and_low_budget_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            result = selective_linker.build(
                self.plan(["SIN8","SINCOS8","ISQRT16","ATAN2_8","UMUL8"],
                          zp_budget=0,ram_budget=4200),Path(folder))
            self.assertEqual(set(result["link_exports"]),
                             {"MATH_SIN8","MATH_SINCOS8","MATH_ISQRT16",
                              "MATH_ATAN2_8","MATH_UMUL8"})
            self.assertEqual(len(result["shared_tables"]), 1)
            self.assertEqual(result["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(result["resource_use"]["shared_table_bytes"],256)
            self.assertEqual(result["resource_use"]["main_ram_total_bytes"],
                             result["resource_use"]["image_span_bytes"] +
                             result["resource_use"]["public_io_bytes"] +
                             result["resource_use"]["private_ram_scratch_bytes"])
        with tempfile.TemporaryDirectory() as folder:
            plan=self.plan(TRIG,zp_budget=0,ram_budget=543)
            with self.assertRaisesRegex(selective_linker.LinkError,
                                        "fits RAM/ZP budgets"):
                selective_linker.build(plan,Path(folder))
            self.assertFalse((Path(folder)/"math_selective.prg").exists())

    def test_source_dependencies_verified(self):
        for operation in TRIG:
            variant, = selective_linker.available_variants()["MATH_"+operation]
            self.assertEqual(variant["validation_path"], "tools/test_selective_trig8.py")
            self.assertEqual(set(variant["dependency_sha256"]),
                             {"tools/selective_trig8.py"})


if __name__ == "__main__":
    unittest.main()
