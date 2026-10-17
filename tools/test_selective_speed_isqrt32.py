#!/usr/bin/env python3
"""ISQRT32 speed selection: immutable same-input corpus and strict budgets."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
import selective_speed_isqrt32 as speed

class ISQRT32SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ram=992,zp=7,objective="speed",pins=None,operations=("ISQRT32",)):
        return math_builder.create_plan(self.index,list(operations),
            objective=objective,zp_budget=zp,ram_budget=ram,pins=pins)

    def test_exact_corpus_provenance_and_unrestricted_samples(self):
        inputs=speed.corpus()
        self.assertEqual(len(inputs),512)
        self.assertEqual(hashlib.sha256(b"".join(n.to_bytes(4,"little") for n in inputs)).hexdigest(),
                         speed.EXPECTED_CORPUS_SHA256)
        self.assertEqual(len(inputs),len(set(inputs)))
        self.assertIn(0,inputs)
        self.assertIn(0xffffffff,inputs)
        self.assertIn(0x80000000,inputs)
        self.assertIn(0x10000,inputs)

    def test_speed_winner_cycle_basis_and_sha_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            m=selective_linker.build(self.plan(),Path(td))
            self.assertEqual(m["operations"][0]["variant"],"link:v2-highword-source")
            self.assertEqual(m["selection_objective"],"speed")
            self.assertEqual(m["selection_basis"],
                "same-corpus measured CPU-model cycles for MATH_ISQRT32")
            result=m["cycle_model_benchmark"]
            self.assertEqual(result["basis"],speed.BASIS)
            self.assertEqual(result["cases"],512)
            self.assertEqual(result["corpus_sha256"],speed.EXPECTED_CORPUS_SHA256)
            self.assertEqual(set(result["mean_cycles"]),speed.EXPECTED_VARIANTS)
            self.assertEqual(result["code_bytes"],
                             {"link:radix4-zerozp":204,"link:v2-highword-source":960})
            self.assertTrue(result["cpu_model_only"])
            self.assertLess(result["mean_cycles"]["link:v2-highword-source"],
                            result["mean_cycles"]["link:radix4-zerozp"])
            self.assertEqual(m["resource_use"]["zero_page_bytes"],7)
            self.assertEqual(m["resource_use"]["main_ram_total_bytes"],992)
            self.assertEqual(result["code_origin"],"$8000")
            self.assertEqual(result["io_origin"],"$C000")
            self.assertEqual(result["zp_origin"],"$50")
            for variant,digest in result["source_sha256"].items():
                source=selective_linker.MODULES["MATH_ISQRT32"][variant]["source"]
                self.assertEqual(digest,hashlib.sha256((ROOT/source).read_bytes()).hexdigest())
            self.assertEqual(m["toolchain_sha256"]["tools/selective_speed_isqrt32.py"],
                             hashlib.sha256((ROOT/"tools/selective_speed_isqrt32.py").read_bytes()).hexdigest())
            self.assertEqual(json.loads((Path(td)/"selective_manifest.json").read_text())
                             ["cycle_model_benchmark"],result)

    def test_zp_and_ram_cutoffs_are_enforced_after_measuring_both(self):
        for ram,zp in ((991,7),(992,0),(246,7)):
            with self.subTest(ram=ram,zp=zp),tempfile.TemporaryDirectory() as td:
                m=selective_linker.build(self.plan(ram=ram,zp=zp),Path(td))
                self.assertEqual(m["operations"][0]["variant"],"link:radix4-zerozp")
                self.assertEqual(m["resource_use"]["main_ram_total_bytes"],246)
                self.assertEqual(m["resource_use"]["zero_page_bytes"],0)
                self.assertEqual(set(m["cycle_model_benchmark"]["mean_cycles"]),
                                 speed.EXPECTED_VARIANTS)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(self.plan(ram=245,zp=7),Path(td))
            self.assertFalse((Path(td)/"math_selective.prg").exists())

    def test_advanced_pins_and_relocated_corpus(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.plan(pins={"ISQRT32":"link:radix4-zerozp"})
            portable=selective_linker.build(p,Path(td))
            self.assertEqual(portable["operations"][0]["variant"],"link:radix4-zerozp")
            p=self.plan(pins={"ISQRT32":"link:v2-highword-source"})
            fast=selective_linker.build(p,Path(td),memory={
                "code_base":0x7123,"math_io":0xc040,"zp_base":0xb0})
            self.assertEqual(fast["operations"][0]["variant"],"link:v2-highword-source")
            self.assertEqual(fast["cycle_model_benchmark"]["code_origin"],"$7123")
            self.assertEqual(fast["cycle_model_benchmark"]["io_origin"],"$C040")
            self.assertEqual(fast["cycle_model_benchmark"]["zp_origin"],"$B0")
            self.assertLess(fast["cycle_model_benchmark"]["mean_cycles"]["link:v2-highword-source"],
                            fast["cycle_model_benchmark"]["mean_cycles"]["link:radix4-zerozp"])

    def test_mixed_ops_fail_closed_and_variant_set_drift(self):
        with self.assertRaisesRegex(math_builder.SelectionError,"requires workload calls"):
            self.plan(operations=("ISQRT32","ISQRT16"),ram=2200)
        bad=dict(selective_linker.MODULES["MATH_ISQRT32"])
        bad["unverified-source"]=bad["link:v2-highword-source"]
        with self.assertRaisesRegex(ValueError,"candidate set changed"):
            speed.bench_isqrt32(bad,0x8000,0xc000,0xc020,ROOT,zp=0x50)

if __name__=="__main__":unittest.main()
