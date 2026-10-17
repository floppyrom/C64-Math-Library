#!/usr/bin/env python3
"""Qualified matched-operand cycle selector for UMUL16_SHR8 only."""
from __future__ import annotations
import hashlib
import json
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
import selective_speed_umul16_shr8 as bench

class Shift16SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, limit, pins=None):
        return math_builder.create_plan(
            self.index, ["UMUL16_SHR8"], objective="speed",
            zp_budget=0, ram_budget=limit, pins=pins)

    def test_speed_ranking_and_budget(self):
        with tempfile.TemporaryDirectory() as d:
            m = selective_linker.build(self.plan(1314),Path(d))
            c = m["cycle_model_benchmark"]
            self.assertEqual(c["basis"],bench.BASIS)
            self.assertEqual(c["cases"],bench.COUNT)
            self.assertTrue(c["cpu_model_only"])
            self.assertEqual(set(c["mean_cycles"]),
                             {"link:compact-zerozp","link:quarter-square"})
            fastest = min(c["mean_cycles"],key=c["mean_cycles"].get)
            self.assertEqual(m["operations"][0]["variant"],fastest)
            self.assertLess(c["mean_cycles"]["link:quarter-square"],
                            c["mean_cycles"]["link:compact-zerozp"])
            self.assertEqual(m["resource_use"]["main_ram_total_bytes"],1314)
            self.assertEqual(
                m["toolchain_sha256"]["tools/selective_speed_umul16_shr8.py"],
                hashlib.sha256((ROOT/"tools/selective_speed_umul16_shr8.py").read_bytes()).hexdigest())
            stored = json.loads((Path(d)/"selective_manifest.json").read_text())
            self.assertEqual(stored["cycle_model_benchmark"],c)

            small = selective_linker.build(self.plan(164),Path(d)/"small")
            self.assertEqual(small["operations"][0]["variant"],"link:compact-zerozp")
            self.assertEqual(small["resource_use"]["main_ram_total_bytes"],164)
            pinned = selective_linker.build(
                self.plan(1500,{"UMUL16_SHR8":"link:compact-zerozp"}),
                Path(d)/"pin")
            self.assertEqual(pinned["operations"][0]["variant"],"link:compact-zerozp")
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(self.plan(163),Path(d)/"no_ram")

    def test_relocation_and_mixed_speed_selection_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            reloc={"code_base":0x7123,"math_io":0xc040,"scratch_base":0xc080}
            a = selective_linker.build(self.plan(1314),Path(d),memory=reloc)
            b = selective_linker.build(self.plan(1314),Path(d),memory=reloc)
            self.assertEqual(a["cycle_model_benchmark"],b["cycle_model_benchmark"])
            self.assertEqual(a["prg_sha256"],b["prg_sha256"])
            with self.assertRaisesRegex(math_builder.SelectionError,"requires workload calls"):
                math_builder.create_plan(self.index,["UMUL16_SHR8","UMUL16"],
                    objective="speed",zp_budget=0,ram_budget=2000)

if __name__ == "__main__":
    unittest.main()
