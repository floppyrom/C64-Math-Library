#!/usr/bin/env python3
"""Same-corpus UMUL16 speed selection and qualifier regression."""
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
import selective_speed_umul16 as speed16


class UMUL16SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,budget,pins=None):
        return math_builder.create_plan(
            self.index,["UMUL16"],objective="speed",
            zp_budget=0,ram_budget=budget,pins=pins)

    def test_measured_source_cycles_choose_faster_with_memory(self):
        with tempfile.TemporaryDirectory() as d:
            plan=self.plan(1291)
            man=selective_linker.build(plan,Path(d))
            self.assertEqual(man["operations"][0]["variant"],"link:quarter-square")
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],1291)
            metric=man["cycle_model_benchmark"]
            self.assertEqual(metric["basis"],speed16.BASIS)
            self.assertEqual(metric["cases"],speed16.COUNT)
            self.assertTrue(metric["cpu_model_only"])
            means=metric["mean_cycles"]
            self.assertEqual(set(means),{"link:compact-zerozp","link:quarter-square"})
            self.assertLess(means["link:quarter-square"],means["link:compact-zerozp"])
            self.assertIn("UMUL16",man["selection_basis"])
            self.assertEqual(man["toolchain_sha256"]["tools/selective_speed_umul16.py"],
                             hashlib.sha256(
                                (ROOT/"tools/selective_speed_umul16.py").read_bytes()
                             ).hexdigest())
            saved=json.loads((Path(d)/"selective_manifest.json").read_text())
            self.assertEqual(saved["cycle_model_benchmark"],metric)

    def test_budget_and_pin_selection(self):
        with tempfile.TemporaryDirectory() as d:
            compact=selective_linker.build(self.plan(146),Path(d))
            self.assertEqual(compact["operations"][0]["variant"],"link:compact-zerozp")
            pinned=selective_linker.build(
                self.plan(1500,{"UMUL16":"link:compact-zerozp"}),Path(d))
            self.assertEqual(pinned["operations"][0]["variant"],"link:compact-zerozp")
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(self.plan(145),Path(d)/"too_small")
            self.assertFalse((Path(d)/"too_small").exists())

    def test_deterministic_under_custom_relocation(self):
        with tempfile.TemporaryDirectory() as d:
            kwargs={"code_base":0x7123,"math_io":0xc040,"scratch_base":0xc080}
            one=selective_linker.build(self.plan(1300),Path(d),memory=kwargs)
            two=selective_linker.build(self.plan(1300),Path(d),memory=kwargs)
            self.assertEqual(one["cycle_model_benchmark"],two["cycle_model_benchmark"])
            self.assertEqual(one["prg_sha256"],two["prg_sha256"])

    def test_cli_speed_flags_compact_if_budget_small(self):
        with tempfile.TemporaryDirectory() as d:
            args=[sys.executable,str(ROOT/"tools/math_builder.py"),
                  "--operation","UMUL16","--objective","speed",
                  "--zp-budget","0","--ram-budget","146",
                  "--build","--out",str(Path(d)/"plan.json")]
            res=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(res.returncode,0,res.stderr)
            saved=json.loads((Path(d)/"selective_manifest.json").read_text())
            self.assertEqual(saved["operations"][0]["variant"],"link:compact-zerozp")


if __name__=="__main__":
    unittest.main()
