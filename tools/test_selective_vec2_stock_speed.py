#!/usr/bin/env python3
"""Authenticate original V1/V5 signed VEC2 normalized public source cycles."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_vec2_stock as speed


class Vec2HistoricalSpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,zp=4,ram=4000,objective="speed"):
        return math_builder.create_plan(
            self.index,["VEC2_NORMALIZE_Q8_8"],objective=objective,
            pins={"VEC2_NORMALIZE_Q8_8":speed.VARIANT},
            workload_calls={"VEC2_NORMALIZE_Q8_8":100}
                           if objective=="speed" else None,
            ram_budget=ram,zp_budget=zp)

    def test_same_source_512_complete_public_calls_two_origins(self):
        variants=linker.MODULES["MATH_VEC2_NORMALIZE_Q8_8"]
        self.assertEqual(set(variants),{speed.VARIANT})
        self.assertTrue(variants[speed.VARIANT]["requires_writable_code"])
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            with self.subTest(code=code):
                m=speed.bench_vec2_normalize(
                    variants,code,io,io+0x40,math_builder.ROOT,zp=zp)
                self.assertEqual(m["cases"],512)
                self.assertEqual(m["corpus_sha256"],speed.CORPUS_SHA256)
                self.assertGreater(m["mean_cycles"][speed.VARIANT],0)
                self.assertGreaterEqual(m["maximum_cycles"][speed.VARIANT],
                                        m["p95_cycles"][speed.VARIANT])
                print("VEC2_STOCK_SAME_PUBLIC",hex(code),
                      m["mean_cycles"],m["maximum_cycles"],
                      m["p95_cycles"],flush=True)

    def test_speed_build_selects_exact_only_source(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(),Path(td),memory={
                "code_base":0x7123,"math_io":0xc040,"zp_base":0x70})
            self.assertEqual(man["operations"][0]["variant"],speed.VARIANT)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],4)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
            self.assertEqual(man["cycle_model_benchmark"]["cases"],512)
            self.assertIn("MATH_VEC2_NORMALIZE_Q8_8",
                          man["cycle_model_benchmark"]["mean_cycles"])

    def test_too_few_zp_bytes_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(zp=3,objective="size"),
                             Path(td)/"bad")


if __name__=="__main__":
    unittest.main()
