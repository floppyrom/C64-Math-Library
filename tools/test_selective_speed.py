#!/usr/bin/env python3
"""Qualification for narrowly scoped same-corpus UMUL8 speed optimization."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
import selective_speed


class MeasuredUMUL8SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self, names, budget, pins=None):
        return math_builder.create_plan(
            self.index,names,objective="speed",zp_budget=0,
            ram_budget=budget,pins=pins)

    def test_same_corpus_selects_fast_and_records_costs(self):
        with tempfile.TemporaryDirectory() as d:
            plan=self.plan(["UMUL8"],1129)
            result=selective_linker.build(plan,Path(d))
            self.assertEqual(result["operations"][0]["variant"],
                             "link:quarter-square")
            self.assertEqual(result["resource_use"]["main_ram_total_bytes"],1129)
            model=result["cycle_model_benchmark"]
            self.assertEqual(model["basis"],selective_speed.BASIS)
            self.assertEqual(model["cases"],1000)
            self.assertTrue(model["cpu_model_only"])
            self.assertEqual(set(model["mean_cycles"]),
                             {"link:compact-zerozp","link:quarter-square",
                              "link:v1-resident-fast"})
            self.assertLess(model["mean_cycles"]["link:quarter-square"],
                            model["mean_cycles"]["link:compact-zerozp"])
            self.assertEqual(result["selection_objective"],"speed")
            self.assertIn("CPU-model",result["selection_basis"])
            self.assertEqual(result["toolchain_sha256"]["tools/selective_speed.py"],
                             hashlib.sha256(
                                 (ROOT/"tools/selective_speed.py").read_bytes()
                             ).hexdigest())
            saved=json.loads((Path(d)/"selective_manifest.json").read_text())
            self.assertEqual(saved["cycle_model_benchmark"],model)

    def test_original_v1_variant_is_also_measured_and_pin_eligible(self):
        with tempfile.TemporaryDirectory() as folder:
            plan = math_builder.create_plan(self.index, ["UMUL8"],
                 objective="speed", zp_budget=4, ram_budget=1311,
                 pins={"UMUL8": "link:v1-resident-fast"})
            man = selective_linker.build(plan, Path(folder))
            self.assertEqual(man["operations"][0]["variant"],"link:v1-resident-fast")
            self.assertEqual(man["resource_use"]["zero_page_bytes"],4)
            self.assertIn("link:v1-resident-fast",man["cycle_model_benchmark"]["mean_cycles"])

    def test_budget_restricts_speed_choice_and_preserves_pins(self):
        with tempfile.TemporaryDirectory() as d:
            compact=selective_linker.build(
                self.plan(["UMUL8"],95),Path(d))
            self.assertEqual(compact["operations"][0]["variant"],
                             "link:compact-zerozp")
            self.assertEqual(compact["resource_use"]["main_ram_total_bytes"],95)
            pinned=selective_linker.build(
                self.plan(["UMUL8"],1200,
                          pins={"UMUL8":"link:compact-zerozp"}),Path(d))
            self.assertEqual(pinned["operations"][0]["variant"],
                             "link:compact-zerozp")
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(self.plan(["UMUL8"],94),
                                       Path(d)/"too_small")
            self.assertFalse((Path(d)/"too_small").exists())

    def test_other_operations_cannot_claim_unmeasured_speed(self):
        for operation in ("SEEK8_INIT", "SDIV16"):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as d:
                with self.assertRaisesRegex(selective_linker.LinkError,
                                            "No authenticated matched-input speed basis"):
                    selective_linker.build(self.plan([operation],4096),Path(d))
        with self.assertRaisesRegex(math_builder.SelectionError,
                                    "requires workload calls"):
            self.plan(["UMUL8","UDIV16"],4096)

    def test_benchmark_reproducible_across_repeat_builds(self):
        with tempfile.TemporaryDirectory() as d:
            plan=self.plan(["UMUL8"],1200)
            first=selective_linker.build(plan,Path(d),
                memory={"code_base":0x7123,"math_io":0xc040})
            second=selective_linker.build(plan,Path(d),
                memory={"code_base":0x7123,"math_io":0xc040})
            self.assertEqual(first["cycle_model_benchmark"],
                             second["cycle_model_benchmark"])
            self.assertEqual(first["prg_sha256"],second["prg_sha256"])

    def test_cli_exposes_faster_feasible_version(self):
        with tempfile.TemporaryDirectory() as d:
            args=[sys.executable,str(ROOT/"tools/math_builder.py"),
                  "--operation","UMUL8","--objective","speed",
                  "--zp-budget","0","--ram-budget","1129",
                  "--build","--out",str(Path(d)/"build_manifest.json")]
            proc=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            manifest=json.loads((Path(d)/"selective_manifest.json").read_text())
            self.assertEqual(manifest["operations"][0]["variant"],
                             "link:quarter-square")


if __name__=="__main__":
    unittest.main()
