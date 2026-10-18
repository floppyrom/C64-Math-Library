#!/usr/bin/env python3
"""Public-call same-operand speed selection for all signed24 DIV/MOD variants."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_s24 as speeds

APIS = ("SDIV24", "SMOD24")


class Signed24SpeedSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = math_builder.operation_index()

    def plan(self, operations=APIS, zp=9, ram=2000, pins=None):
        return math_builder.create_plan(
            self.catalog, list(operations), objective="speed",
            zp_budget=zp, ram_budget=ram, pins=pins,
            workload_calls={api: 6 if api == "SDIV24" else 4
                            for api in operations})

    def test_same_512_public_calls_both_origins_and_automatic_best_choice(self):
        for code, io, scratch, zp in (
                (0x8000, 0xc000, 0xc040, 0x50),
                (0x7123, 0xc040, 0xc080, 0x70)):
            for operation in APIS:
                with self.subTest(code=code, operation=operation), tempfile.TemporaryDirectory() as td:
                    api = "MATH_" + operation
                    bench = speeds.benchmark(
                        api, linker.MODULES[api], code, io, scratch, linker.ROOT, zp)
                    self.assertEqual(bench["cases"], 512)
                    self.assertEqual(bench["corpus_sha256"], speeds.EXPECTED_CORPUS_SHA256)
                    self.assertEqual(set(bench["mean_cycles"]), speeds.VARIANTS)
                    self.assertEqual(set(bench["maximum_cycles"]), speeds.VARIANTS)
                    self.assertEqual(set(bench["source_sha256"]), speeds.VARIANTS)
                    plan = self.plan((operation,))
                    built = linker.build(plan, Path(td), memory={
                        "code_base": code, "math_io": io,
                        "scratch_base": scratch, "zp_base": zp})
                    selected = built["operations"][0]["variant"]
                    expected = min(bench["mean_cycles"],
                                   key=lambda variant: (bench["mean_cycles"][variant],
                                     # The old score model breaks equal means by
                                     # real linked resources and source identity.
                                     variant))
                    self.assertEqual(selected, expected)
                    self.assertLessEqual(built["resource_use"]["zero_page_bytes"], 9)
                    self.assertLessEqual(built["resource_use"]["main_ram_total_bytes"], 2000)
                    print("SIGNED24 PUBLIC SPEED", hex(code), operation,
                          bench["mean_cycles"], selected, flush=True)

    def test_zp_and_ram_constraints_choose_real_compact_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            for operation in APIS:
                with self.subTest(operation=operation):
                    built = linker.build(self.plan((operation,), zp=0, ram=364),
                                         Path(td) / operation)
                    self.assertEqual(built["operations"][0]["variant"],
                                     speeds.PORTABLE)
                    self.assertEqual(built["resource_use"]["zero_page_bytes"], 0)
                    self.assertEqual(built["resource_use"]["main_ram_total_bytes"], 364)
            result = linker.build(self.plan(), Path(td) / "mixed")
            self.assertEqual(set(op["api"] for op in result["operations"]),
                             {"MATH_SDIV24", "MATH_SMOD24"})
            self.assertLessEqual(result["resource_use"]["zero_page_bytes"], 9)
            self.assertLessEqual(result["resource_use"]["main_ram_total_bytes"], 2000)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(("SDIV24",), zp=0, ram=363),
                             Path(td) / "too_small")

    def test_speed_basis_refuses_missing_donor(self):
        api = "MATH_SDIV24"
        original = dict(linker.MODULES[api])
        try:
            del linker.MODULES[api][speeds.V3]
            with tempfile.TemporaryDirectory() as td:
                with self.assertRaisesRegex(linker.LinkError,
                                            "cycle-model measurement failed"):
                    linker.build(self.plan(("SDIV24",)), Path(td))
        finally:
            linker.MODULES[api] = original


if __name__ == "__main__":
    unittest.main()
