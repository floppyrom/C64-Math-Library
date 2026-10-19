#!/usr/bin/env python3
"""Same-source UMOD8 speed selector qualification with hard RAM/ZP constraints."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
import selective_speed_umod8
import test_selective_umod8_speed as historical_proof


class QualifiedUMOD8SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, names, ram=261, zp=2, pins=None, objective="speed"):
        return math_builder.create_plan(self.index, names,
                                        objective=objective, zp_budget=zp,
                                        ram_budget=ram, pins=pins)

    def test_exact_matched_corpus_is_not_silently_changed(self):
        original = historical_proof.corpus()
        self.assertEqual(selective_speed_umod8.corpus(), original)
        self.assertEqual(len(original), 1000)
        digest = hashlib.sha256(bytes(z for n,d in original for z in (n,d))).hexdigest()
        self.assertEqual(digest, selective_speed_umod8.EXPECTED_CORPUS_SHA256)

    def test_fastest_feasible_source_picked_and_comparable_evidence_sealed(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = selective_linker.build(self.plan(["UMOD8"]), Path(d))
            self.assertEqual(manifest["operations"][0]["variant"],
                             "link:v2-unrolled-fallback")
            self.assertEqual(manifest["resource_use"]["main_ram_total_bytes"],261)
            self.assertEqual(manifest["resource_use"]["zero_page_bytes"],2)
            model = manifest["cycle_model_benchmark"]
            self.assertEqual(model["basis"],selective_speed_umod8.BASIS)
            self.assertEqual(model["cases"],1000)
            self.assertEqual(model["corpus_sha256"],
                             selective_speed_umod8.EXPECTED_CORPUS_SHA256)
            self.assertTrue(model["cpu_model_only"])
            self.assertEqual(set(model["mean_cycles"]),
                             selective_speed_umod8.EXPECTED_VARIANTS)
            self.assertAlmostEqual(model["mean_cycles"]["link:v1-fast-fallback"],
                                   95.635,places=3)
            self.assertAlmostEqual(model["mean_cycles"]["link:v2-unrolled-fallback"],
                                   90.893,places=3)
            self.assertAlmostEqual(model["mean_cycles"]["link:v5-unrolled-hybrid"],
                                   94.165,places=3)
            self.assertEqual(manifest["selection_objective"],"speed")
            self.assertEqual(manifest["selection_basis"],
                             "same-corpus measured CPU-model cycles for MATH_UMOD8")
            self.assertEqual(model["code_bytes"],{
                "link:v1-fast-fallback":157,
                "link:v2-unrolled-fallback":229,
                "link:v5-unrolled-hybrid":205})
            for ident, source_hash in model["source_sha256"].items():
                source = selective_linker.MODULES["MATH_UMOD8"][ident]["source"]
                self.assertEqual(source_hash,
                                 hashlib.sha256((ROOT/source).read_bytes()).hexdigest())
            self.assertEqual(manifest["toolchain_sha256"]["tools/selective_speed_umod8.py"],
                             hashlib.sha256((ROOT/"tools/selective_speed_umod8.py").read_bytes()).hexdigest())
            saved = json.loads((Path(d)/"selective_manifest.json").read_text())
            self.assertEqual(saved["cycle_model_benchmark"], model)

    def test_speed_vs_memory_pareto_tiers_and_explicit_override(self):
        for budget, expected, used in (
            (261,"link:v2-unrolled-fallback",261),
            (260,"link:v5-unrolled-hybrid",237),
            (237,"link:v5-unrolled-hybrid",237),
            (236,"link:v1-fast-fallback",189),
            (189,"link:v1-fast-fallback",189)):
            with self.subTest(ram=budget),tempfile.TemporaryDirectory() as d:
                man=selective_linker.build(self.plan(["UMOD8"],ram=budget),Path(d))
                self.assertEqual(man["operations"][0]["variant"],expected)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],used)
        with tempfile.TemporaryDirectory() as d:
            pinned = selective_linker.build(
                self.plan(["UMOD8"],pins={"UMOD8":"link:v1-fast-fallback"}),
                Path(d))
            self.assertEqual(pinned["operations"][0]["variant"],"link:v1-fast-fallback")
            smallest = selective_linker.build(
                self.plan(["UMOD8"],objective="size"),Path(d))
            self.assertEqual(smallest["operations"][0]["variant"],
                             "link:v1-fast-fallback")
        for ram,zp in ((188,2),(261,1)):
            with tempfile.TemporaryDirectory() as d:
                target=Path(d)/"fail"
                with self.assertRaises(selective_linker.LinkError):
                    selective_linker.build(self.plan(["UMOD8"],ram=ram,zp=zp),target)
                self.assertFalse(target.exists())

    def test_relocated_source_verified_and_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            plan=self.plan(["UMOD8"])
            memory={"code_base":0x7123,"math_io":0xc040,"zp_base":0x70}
            first=selective_linker.build(plan,Path(d),memory=memory)
            second=selective_linker.build(plan,Path(d),memory=memory)
            self.assertEqual(first["cycle_model_benchmark"],second["cycle_model_benchmark"])
            self.assertEqual(first["prg_sha256"],second["prg_sha256"])
            expected=min(first["cycle_model_benchmark"]["mean_cycles"],
                         key=first["cycle_model_benchmark"]["mean_cycles"].get)
            self.assertEqual(first["operations"][0]["variant"],expected)

    def test_mixed_operations_require_explicit_calls_and_corpus(self):
        for ops in (["UMOD8","UMUL8"],["UMOD8","UDIV8"],["SMUL8","UMOD8"]):
            with self.subTest(ops=ops):
                with self.assertRaisesRegex(math_builder.SelectionError,
                                            "requires workload calls"):
                    self.plan(ops,ram=4096)
        # SMUL8 became source-authenticated when its historical-SMC and
        # read-only QS variants gained a matched full-public-call corpus.
        # Mixed speed selection must now succeed rather than be rejected.
        with tempfile.TemporaryDirectory() as d:
            p=math_builder.create_plan(self.index,["SMUL8","UMOD8"],
                  objective="speed",workload_calls={"SMUL8":1,"UMOD8":1})
            man=selective_linker.build(p,Path(d))
            self.assertEqual(man["selection_objective"],"speed")
            self.assertEqual({op["api"] for op in man["operations"]},
                             {"MATH_SMUL8","MATH_UMOD8"})
            self.assertIn(man["operations"][0]["variant"],
                          selective_linker.MODULES[man["operations"][0]["api"]])
            self.assertIn(man["operations"][1]["variant"],
                          selective_linker.MODULES[man["operations"][1]["api"]])

    def test_cli_uses_certified_source_but_does_not_claim_hardware_timing(self):
        with tempfile.TemporaryDirectory() as d:
            args=[sys.executable,str(ROOT/"tools/math_builder.py"),
                  "--operation","UMOD8","--objective","speed",
                  "--zp-budget","2","--ram-budget","261",
                  "--build","--out",str(Path(d)/"builder.json")]
            proc=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            man=json.loads((Path(d)/"selective_manifest.json").read_text())
            self.assertEqual(man["operations"][0]["variant"],
                             "link:v2-unrolled-fallback")
            self.assertTrue(man["cycle_model_benchmark"]["cpu_model_only"])


if __name__=="__main__":
    unittest.main()
