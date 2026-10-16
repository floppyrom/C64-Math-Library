#!/usr/bin/env python3
"""Matched-input unsigned 8-bit division speed-selector and resource gates."""
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
import selective_speed_udiv8


class MatchedUDIV8SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, ops, ram=462, zp=1, pins=None, objective="speed"):
        return math_builder.create_plan(self.index, ops,
                                        objective=objective, zp_budget=zp,
                                        ram_budget=ram, pins=pins)

    def test_corpus_sha_seed_edges_and_division_by_zero(self):
        cases = selective_speed_udiv8.corpus()
        self.assertEqual(len(cases), 1000)
        checksum = hashlib.sha256(bytes(v for n,d in cases for v in (n,d))).hexdigest()
        self.assertEqual(checksum, selective_speed_udiv8.EXPECTED_CORPUS_SHA256)
        self.assertIn((0, 0), cases)
        self.assertIn((255, 255), cases)
        self.assertTrue(any(d == 0 for n,d in cases))
        self.assertTrue(any(d == 1 for n,d in cases))

    def test_measured_speed_winner_abi_and_manifest_provenance(self):
        with tempfile.TemporaryDirectory() as folder:
            man = selective_linker.build(self.plan(["UDIV8"]), Path(folder))
            m = man["cycle_model_benchmark"]
            self.assertEqual(m["basis"], selective_speed_udiv8.BASIS)
            self.assertEqual(m["corpus_sha256"],
                             selective_speed_udiv8.EXPECTED_CORPUS_SHA256)
            self.assertEqual(m["cases"], 1000)
            self.assertTrue(m["cpu_model_only"])
            self.assertEqual(set(m["mean_cycles"]),
                             selective_speed_udiv8.EXPECTED_VARIANTS)
            self.assertEqual(m["code_bytes"], {
                "link:v1-resident-fast": 294,
                "link:v2-v5-fast": 430})
            self.assertGreater(m["mean_cycles"]["link:v1-resident-fast"], 0)
            self.assertGreater(m["mean_cycles"]["link:v2-v5-fast"], 0)
            fastest = min(m["mean_cycles"],
                          key=lambda candidate: (m["mean_cycles"][candidate],
                                                 m["code_bytes"][candidate],
                                                 candidate))
            self.assertEqual(man["operations"][0]["variant"], fastest)
            self.assertEqual(man["selection_basis"],
                             "same-corpus measured CPU-model cycles for MATH_UDIV8")
            self.assertEqual(man["selection_objective"], "speed")
            for variant, digest in m["source_sha256"].items():
                source = selective_linker.MODULES["MATH_UDIV8"][variant]["source"]
                self.assertEqual(digest,hashlib.sha256((ROOT/source).read_bytes()).hexdigest())
            self.assertEqual(man["toolchain_sha256"]["tools/selective_speed_udiv8.py"],
                             hashlib.sha256((ROOT/"tools/selective_speed_udiv8.py")
                                            .read_bytes()).hexdigest())
            self.assertEqual(json.loads((Path(folder)/"selective_manifest.json")
                                        .read_text())["cycle_model_benchmark"], m)

    def test_ram_tiers_pins_and_zero_page(self):
        for budget in (326, 327, 461):
            with self.subTest(ram=budget), tempfile.TemporaryDirectory() as folder:
                man = selective_linker.build(
                    self.plan(["UDIV8"],ram=budget),Path(folder))
                self.assertEqual(man["operations"][0]["variant"],
                                 "link:v1-resident-fast")
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],326)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],1)
        with tempfile.TemporaryDirectory() as folder:
            selected = selective_linker.build(
                self.plan(["UDIV8"],pins={"UDIV8":"link:v2-v5-fast"}),
                Path(folder))
            self.assertEqual(selected["resource_use"]["main_ram_total_bytes"],462)
            self.assertEqual(selected["operations"][0]["variant"],"link:v2-v5-fast")
            small = selective_linker.build(
                self.plan(["UDIV8"],objective="size"),Path(folder))
            self.assertEqual(small["operations"][0]["variant"],"link:v1-resident-fast")
        for ram,zp in ((325,1),(462,0)):
            with self.subTest(ram=ram,zp=zp), tempfile.TemporaryDirectory() as folder:
                out=Path(folder)/"reject"
                with self.assertRaises(selective_linker.LinkError):
                    selective_linker.build(self.plan(["UDIV8"],ram=ram,zp=zp),out)
                self.assertFalse(out.exists())

    def test_exact_requested_relocation_and_determinism(self):
        with tempfile.TemporaryDirectory() as folder:
            cfg={"code_base":0x7123,"math_io":0xc040,"zp_base":0x70}
            plan=self.plan(["UDIV8"])
            first=selective_linker.build(plan,Path(folder),memory=cfg)
            second=selective_linker.build(plan,Path(folder),memory=cfg)
            self.assertEqual(first["prg_sha256"], second["prg_sha256"])
            self.assertEqual(first["cycle_model_benchmark"],second["cycle_model_benchmark"])
            self.assertEqual(first["cycle_model_benchmark"]["code_origin"],"$7123")
            self.assertEqual(first["cycle_model_benchmark"]["io_origin"],"$C040")
            self.assertEqual(first["cycle_model_benchmark"]["zp_origin"],"$70")
            means=first["cycle_model_benchmark"]["mean_cycles"]
            self.assertEqual(first["operations"][0]["variant"],
                             min(means,key=means.get))

    def test_unqualified_mixed_speed_and_cli(self):
        for ops in (["UDIV8","UMOD8"],["UDIV8","UMUL8"],["UDIV8","SDIV8"]):
            with self.subTest(ops=ops), tempfile.TemporaryDirectory() as folder:
                out=Path(folder)/"reject"
                with self.assertRaisesRegex(selective_linker.LinkError,
                                            "UDIV8 alone"):
                    selective_linker.build(self.plan(ops,ram=4096),out)
                self.assertFalse(out.exists())
        with tempfile.TemporaryDirectory() as folder:
            p=subprocess.run(
                [sys.executable,str(ROOT/"tools/math_builder.py"),
                 "--operation","UDIV8","--objective","speed","--zp-budget","1",
                 "--ram-budget","462","--build","--out",str(Path(folder)/"plan.json")],
                cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            man=json.loads((Path(folder)/"selective_manifest.json").read_text())
            self.assertTrue(man["cycle_model_benchmark"]["cpu_model_only"])
            self.assertEqual(man["selection_objective"],"speed")


if __name__=="__main__":
    unittest.main()
