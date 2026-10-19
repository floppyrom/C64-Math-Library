#!/usr/bin/env python3
"""Public speed installer proof for the exact V1–V5 shared SINE8 table."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_trig8 as timing
import selective_trig8

TRIG=("SIN8","COS8","SINCOS8")
VARIANT="link:resident-shared-table"


class TrigPublicSpeedQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops,ram=600):
        return math_builder.create_plan(
            self.index,list(ops),objective="speed",
            workload_calls={k:100 for k in ops},
            zp_budget=0,ram_budget=ram)

    def test_256_phase_public_cycle_provenance_two_origins(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            for api,bench in (
               ("MATH_SIN8",timing.bench_sin8),
               ("MATH_COS8",timing.bench_cos8),
               ("MATH_SINCOS8",timing.bench_sincos8)):
                with self.subTest(code=code,api=api):
                    measured=bench(linker.MODULES[api],code,io,0,math_builder.ROOT)
                    self.assertEqual(measured["cases"],256)
                    self.assertTrue(measured["cpu_model_only"])
                    self.assertEqual(set(measured["mean_cycles"]),{VARIANT})
                    self.assertEqual(measured["corpus_sha256"],
                                     hashlib.sha256(bytes(range(256))).hexdigest())
                    self.assertEqual(measured["table_sha256"],
                                     hashlib.sha256(selective_trig8.SINE_BYTES).hexdigest())
                    self.assertGreater(measured["mean_cycles"][VARIANT],0)
                    self.assertGreaterEqual(measured["maximum_cycles"][VARIANT],
                                            measured["p95_cycles"][VARIANT])
                    print("TRIG8 SOURCE PUBLIC SPEED",api,hex(code),
                          measured["mean_cycles"],measured["maximum_cycles"],
                          flush=True)

    def test_three_operation_speed_mode_retains_single_shared_table(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as folder:
                output=Path(folder)
                plan=self.plan(TRIG)
                man=linker.build(plan,output,memory={
                    "code_base":code,"math_io":io})
                self.assertEqual(set(man["link_exports"]),{
                    "MATH_SIN8","MATH_COS8","MATH_SINCOS8"})
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
                self.assertEqual(man["resource_use"]["shared_table_bytes"],256)
                self.assertEqual(man["resource_use"]["code_and_tables_bytes"],304)
                self.assertEqual(len(man["shared_tables"]),1)
                self.assertEqual(man["shared_tables"][0]["users"],
                                 ["MATH_COS8","MATH_SIN8","MATH_SINCOS8"])
                model=man["cycle_model_benchmark"]
                self.assertEqual(set(model["operations"]),{
                    "MATH_SIN8","MATH_COS8","MATH_SINCOS8"})
                for api in model["operations"]:
                    self.assertEqual(model["operations"][api]["cases"],256)
                image=(output/"math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(image).hexdigest(),man["prg_sha256"])

    def test_single_speed_and_insufficient_ram_fail_closed(self):
        for op in TRIG:
            with self.subTest(op=op),tempfile.TemporaryDirectory() as folder:
                man=linker.build(self.plan([op],544),Path(folder))
                self.assertEqual(man["link_exports"],["MATH_"+op])
                self.assertEqual(man["cycle_model_benchmark"]["cases"],256)
                self.assertEqual(man["resource_use"]["shared_table_bytes"],256)
                with self.assertRaises(linker.LinkError):
                    linker.build(self.plan([op],0),Path(folder)/"insufficient")


if __name__=="__main__":
    unittest.main()
