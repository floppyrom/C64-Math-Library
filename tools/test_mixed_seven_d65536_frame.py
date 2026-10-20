#!/usr/bin/env python3
"""Fail-closed nine-plan D65536 installer frame evidence regression."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

import mixed_seven_d65536_frame as d655
import mixed_seven_cross_pareto as crossed
import mixed_seven_frame_parity as seven
from frame_evidence_replay import replay
from frame_qualified_config import export_config
from mixed_frame_frontier import EvidenceError, summarize
from mul32_frame_frontier import select


class D65536FrameChoicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.choices=d655.options()
        cls.report=d655.complete_report()
        cls.summary=summarize(cls.report)

    def test_pareto_provenance_and_original_pinned_sources_unchanged(self):
        self.assertEqual(len(self.choices),9)
        self.assertEqual(set(self.choices),set(self.report["placements"][0]["per_option"]))
        self.assertEqual(len(d655.OPS),7)
        for label,pins in self.choices.items():
            with self.subTest(plan=label):
                self.assertEqual(set(pins),set(d655.OPS))
                self.assertEqual(pins[d655.UOPS[0]],pins[d655.UOPS[1]])
                self.assertEqual(pins[d655.SOPS[0]],pins[d655.SOPS[1]])
        self.assertEqual(self.choices["compact-zerozp"],
                         seven.OPTIONS["compact-everywhere"])
        self.assertEqual(self.choices["fast31-stock-v2"],
                         seven.OPTIONS["fast-everywhere"])
        self.assertEqual(self.report["candidate_count"],9)
        self.assertEqual(self.report["placements"][0]["paired_calls"],150)
        self.assertFalse(self.report["physical_pal_frame_qualified"])
        self.assertEqual(self.report["placements"][0]["input_corpus_sha256"],
                         self.report["placements"][1]["input_corpus_sha256"])
        self.assertLess(
            self.summary["per_option"]["fast31-u65536-s65536"]
                ["peak_frame_math_cycles"],
            self.summary["per_option"]["fast31-stock-v2"]
                ["peak_frame_math_cycles"])

    def test_signed_only_d65536_is_better_than_both_for_this_exact_trace(self):
        rows=self.summary["per_option"]
        signed=rows["fast31-uv2-s65536"]
        both=rows["fast31-u65536-s65536"]
        stock=rows["fast31-stock-v2"]
        self.assertLess(signed["peak_frame_math_cycles"],both["peak_frame_math_cycles"])
        self.assertLess(signed["peak_frame_math_cycles"],stock["peak_frame_math_cycles"])
        self.assertEqual(signed["main_ram_total_bytes"],stock["main_ram_total_bytes"])
        self.assertLess(signed["main_ram_total_bytes"],both["main_ram_total_bytes"])
        self.assertEqual(signed["zero_page_bytes"],31)
        winner=select(self.summary,stock["main_ram_total_bytes"],31,
                      objective="peak")
        self.assertEqual(winner["choice"],"fast31-uv2-s65536")
        self.assertEqual(winner["measured_envelope"]["peak_frame_math_cycles"],
                         signed["peak_frame_math_cycles"])
        with self.assertRaises(EvidenceError):
            select(self.summary,stock["main_ram_total_bytes"],31,
                   max_peak_cycles=1,objective="peak")

    def test_budget_pareto_keeps_compact_without_extra_zp(self):
        for zp in (0,12,31):
            with self.subTest(zp=zp):
                choice=select(self.summary,16000,zp,objective="peak")
                self.assertIn(choice["choice"],self.choices)
                self.assertLessEqual(
                    choice["measured_envelope"]["zero_page_bytes"],zp)
                if zp==0:
                    self.assertEqual(choice["choice"],"compact-zerozp")

    def test_full_replay_rejects_corrupt_source_and_clock_evidence(self):
        self.assertEqual(replay(self.report),self.report)
        corrupt=copy.deepcopy(self.report)
        corrupt["placements"][0]["per_option"]["fast31-u65536-s65536"][
            "peak_frame_math_cycles"]+=1
        with self.assertRaises(EvidenceError):
            replay(corrupt)
        corrupt=copy.deepcopy(self.report)
        corrupt["placements"][1]["per_option"]["lowzp-u65536-s65536"][
            "source_sha256"]["MATH_SMOD32_32"]="0"*64
        with self.assertRaises(EvidenceError):
            replay(corrupt)

    def test_real_cli_publishes_only_the_source_replayed_frame_binary(self):
        from math_builder import ROOT
        zp=31
        memory={"code_base":0x4123,"math_io":0xc040,
                "zp_base":0x70,"scratch_base":0xc080}
        config,proof=export_config(
            self.report,ram_budget=16000,zp_budget=zp,
            code_base=memory["code_base"],math_io=memory["math_io"],
            zp_base=memory["zp_base"],scratch_base=memory["scratch_base"],
            objective="peak")
        with tempfile.TemporaryDirectory(prefix="d65536_frame_cli_") as td:
            folder=Path(td)
            report_path=folder/"registered_source_evidence.json"
            config_path=folder/"project.json"
            out=folder/"published"/"selection_manifest.json"
            report_path.write_text(json.dumps(self.report,sort_keys=True)+"\n")
            config_path.write_text(json.dumps({
                "target":"c64",
                "objective":"frame",
                "operations":list(d655.OPS),
                "constraints":{"max_ram_bytes":16000,"max_zp_bytes":zp},
                "memory":memory,
                "frame_optimize":"peak",
            },sort_keys=True)+"\n")
            done=subprocess.run([
                sys.executable,str(ROOT/"tools/math_builder.py"),
                "--objective","frame","--config",str(config_path),
                "--frame-report",str(report_path),"--build","--out",str(out)
            ],cwd=ROOT,capture_output=True,text=True,timeout=420)
            self.assertEqual(done.returncode,0,done.stderr[-2500:])
            installed=out.parent/"math_selective.prg"
            manifest=json.loads((out.parent/"selective_manifest.json").read_text())
            evidence=json.loads((out.parent/"frame_qualified_evidence.json").read_text())
            pinned=json.loads((out.parent/"frame_qualified_config.json").read_text())
            self.assertEqual(hashlib.sha256(installed.read_bytes()).hexdigest(),
                             proof["qualified_prg_sha256"])
            self.assertEqual(manifest["prg_sha256"],proof["qualified_prg_sha256"])
            self.assertEqual(evidence["choice"],proof["choice"])
            self.assertEqual(pinned["pins"],config["pins"])
            self.assertEqual({entry["api"]:entry["variant"]
                              for entry in manifest["operations"]},config["pins"])
            self.assertFalse(evidence["physical_pal_feasibility_claim"])
            self.assertTrue(evidence["cpu_model_only"])

    def test_actual_frame_objective_builds_source_identical_public_prg(self):
        for zp in (0,12,31):
            with self.subTest(zp=zp):
                config,proof=export_config(
                    self.report,ram_budget=16000,zp_budget=zp,
                    code_base=0x4123,math_io=0xc040,zp_base=0x70,
                    scratch_base=0xc080,objective="peak")
                self.assertEqual(set(config["pins"]),set(d655.OPS))
                self.assertIn(proof["choice"],self.choices)
                self.assertEqual(len(proof["qualified_prg_sha256"]),64)
                self.assertTrue(proof["cpu_model_only"])
                self.assertFalse(proof["physical_pal_feasibility_claim"])
                self.assertLessEqual(
                    proof["worst_placement_measured_envelope"]["zero_page_bytes"],zp)


if __name__=="__main__":
    unittest.main()
