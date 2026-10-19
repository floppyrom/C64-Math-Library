#!/usr/bin/env python3
"""Measured original V1 DIST8_FAST source, complete ABI and speed plan."""
from __future__ import annotations
import hashlib
import tempfile
import unittest
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_dist8_fast as speed

VARIANT=speed.ID

class OriginalV1DIST8FastSpeed(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.index=math_builder.operation_index()

    def plan(self,ram=95,zp=0):
        return math_builder.create_plan(
            self.index,["DIST8_FAST"],objective="speed",
            workload_calls={"DIST8_FAST":150},zp_budget=zp,ram_budget=ram)

    def test_complete_public512_two_source_origins(self):
        for code,io,scratch in ((0x8000,0xc000,0xc040),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(code=code):
                m=speed.bench_dist8_fast(linker.MODULES["MATH_DIST8_FAST"],
                         code,io,scratch,math_builder.ROOT)
                self.assertEqual(m["cases"],512)
                self.assertEqual(m["basis"],speed.BASIS)
                self.assertEqual(set(m["mean_cycles"]),{VARIANT})
                self.assertEqual(m["corpus_sha256"],hashlib.sha256(
                    bytes(v for pair in speed.corpus() for v in pair)
                ).hexdigest())
                self.assertTrue(m["cpu_model_only"])
                self.assertGreater(m["mean_cycles"][VARIANT],0)
                self.assertGreaterEqual(m["maximum_cycles"][VARIANT],
                                        m["p95_cycles"][VARIANT])
                print("DIST8_FAST HISTORICAL PUBLIC",hex(code),
                      m["mean_cycles"],m["maximum_cycles"],
                      m["p95_cycles"],flush=True)

    def test_speed_installer_one_original_kernel_no_zp(self):
        for code,io,scratch in ((0x8000,0xc000,0xc040),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                self.assertEqual(man["link_exports"],["MATH_DIST8_FAST"])
                self.assertEqual(man["operations"][0]["variant"],VARIANT)
                self.assertEqual(man["resource_use"]["image_span_bytes"],61)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],2)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],95)
                self.assertEqual(man["cycle_model_benchmark"]["cases"],512)
                binary=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(binary).hexdigest(),
                                 man["prg_sha256"])
                self.assertEqual(binary[:2],code.to_bytes(2,"little"))

    def test_ram_budget_rejected_before_emit(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=94),Path(td)/"small")
            self.assertFalse((Path(td)/"small").exists())

if __name__=="__main__":
    unittest.main()
