#!/usr/bin/env python3
"""Source-locked, two-relocation speed qualification of all eight SEEK APIs."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import math_builder
import selective_linker as linker
import selective_speed_seek as speed


APIS = tuple("MATH_" + family + "_" + suffix
             for family in ("SEEK8", "SEEK16")
             for suffix in speed.SUFFIXES)


class SeekPublicSpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def test_identical_movement_corpus_at_two_independent_placements(self):
        for api in APIS:
            saved = None
            for code, io, scratch in ((0x8000, 0xc000, 0xc020),
                                      (0x7123, 0xc100, 0xc121)):
                with self.subTest(api=api, code=code):
                    model = speed.benchmark(
                        api, linker.MODULES[api], code, io, scratch,
                        math_builder.ROOT)
                    self.assertEqual(model["fixtures"], speed.FIXTURES)
                    self.assertGreaterEqual(model["cases"], speed.FIXTURES)
                    self.assertEqual(set(model["mean_cycles"]), {speed.VARIANT})
                    self.assertTrue(model["cpu_model_only"])
                    self.assertFalse(model["native_hardware_timing"])
                    self.assertGreater(model["mean_cycles"][speed.VARIANT], 0)
                    self.assertLessEqual(model["p95_cycles"][speed.VARIANT],
                                         model["maximum_cycles"][speed.VARIANT])
                    self.assertEqual(model["source_sha256"][speed.VARIANT],
                                     speed.SPECS[api.split("_")[1]][4])
                    if saved is not None:
                        self.assertEqual(model["corpus_sha256"], saved)
                    saved = model["corpus_sha256"]
                    print("SEEK SAME PUBLIC", api, hex(code),
                          model["cases"], model["mean_cycles"],
                          flush=True)

    def test_weighted_eight_operation_speed_build_shares_two_producers(self):
        calls = {api: (2 if api.endswith("_INIT") else 120) for api in APIS}
        plan = math_builder.create_plan(
            self.index, list(APIS), objective="speed",
            zp_budget=0, ram_budget=2400, workload_calls=calls)
        with tempfile.TemporaryDirectory() as d:
            man = linker.build(plan, Path(d))
            self.assertEqual(set(x["api"] for x in man["operations"]), set(APIS))
            self.assertEqual({x["variant"] for x in man["operations"]},
                             {speed.VARIANT})
            self.assertEqual(len(man["link_order"]), 2)
            self.assertEqual(man["resource_use"]["zero_page_bytes"], 0)
            self.assertEqual(man["resource_use"]["code_and_tables_bytes"], 1549)
            self.assertEqual(man["resource_use"]["persistent_state_bytes"], 408)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"], 19)
            self.assertLessEqual(man["resource_use"]["main_ram_total_bytes"], 2400)
            models = man["cycle_model_benchmark"]["operations"]
            self.assertEqual(set(models), set(APIS))
            for api in APIS:
                self.assertEqual(models[api]["basis"], speed.BASIS)
                self.assertEqual(models[api]["fixtures"], speed.FIXTURES)
                self.assertTrue(models[api]["source_sha256"][speed.VARIANT])
            self.assertTrue(man["cycle_model_benchmark"]["cpu_model_only"])

    def test_fail_closed_when_state_or_scratch_cannot_fit(self):
        plan = math_builder.create_plan(
            self.index, ["SEEK16_INIT"], objective="speed",
            zp_budget=0, ram_budget=100)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(plan, Path(td) / "too_small")
            self.assertFalse((Path(td) / "too_small").exists())

    def test_pinned_source_and_integer_call_weights(self):
        plan = math_builder.create_plan(
            self.index, ["SEEK8_INIT", "SEEK8_STEP1"],
            objective="speed", pins={"SEEK8_STEP1": speed.VARIANT},
            zp_budget=0, ram_budget=1000,
            workload_calls={"SEEK8_INIT": 2, "SEEK8_STEP1": 120})
        with tempfile.TemporaryDirectory() as td:
            result = linker.build(plan, Path(td))
            self.assertEqual(len(result["link_order"]), 1)
            self.assertEqual(result["resource_use"]["zero_page_bytes"], 0)
            self.assertEqual(result["workload_calls"]["MATH_SEEK8_STEP1"], 120)


if __name__ == "__main__":
    unittest.main()
