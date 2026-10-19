#!/usr/bin/env python3
"""Exercise actual pinned math_builder config output against measured linked PRGs."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from frame_qualified_config import EvidenceError, export_config
from mixed3_frame_parity import OPS, compare
from mixed_frame_frontier import summarize

ROOT = Path(__file__).resolve().parents[1]


class FrameQualifiedConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = {"operations": list(OPS),
                      "placements": [compare(0x8000, 0xc000, 0x50),
                                     compare(0x7123, 0xc040, 0x70)]}

    def export(self, report=None, **overrides):
        opts = {"ram_budget": 12000, "zp_budget": 31,
                "code_base": 0x8000, "math_io": 0xc000,
                "zp_base": 0x50, "scratch_base": 0xc040}
        opts.update(overrides)
        return export_config(self.report if report is None else report, **opts)

    def test_exact_builder_rebuild_and_evidence(self):
        for code, io, zp, scratch in ((0x8000, 0xc000, 0x50, 0xc040),
                                     (0x7123, 0xc040, 0x70, 0xc080)):
            with self.subTest(code=hex(code)), tempfile.TemporaryDirectory() as d:
                cfg, evidence = self.export(code_base=code, math_io=io,
                                            zp_base=zp, scratch_base=scratch)
                self.assertEqual(set(cfg["pins"]), set(OPS))
                self.assertEqual(set(cfg["operations"]), set(OPS))
                self.assertEqual(cfg["objective"], "size")
                self.assertTrue(evidence["cpu_model_only"])
                self.assertFalse(evidence["physical_pal_feasibility_claim"])
                self.assertEqual(evidence["locations_tested"], 2)
                self.assertEqual(evidence["public_calls_per_location"], 150)
                self.assertEqual(evidence["frames_per_location"], 24)
                base = Path(d)
                confpath = base / "project.json"
                confpath.write_text(json.dumps(cfg) + "\n", encoding="utf-8")
                target = base / "built" / "manifest.json"
                output = subprocess.run(
                    [sys.executable, str(ROOT / "tools/math_builder.py"),
                     "--config", str(confpath), "--build", "--out", str(target)],
                    cwd=ROOT, capture_output=True, text=True, timeout=120)
                self.assertEqual(output.returncode, 0, output.stderr + output.stdout)
                binary = (target.parent / "math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(binary).hexdigest(),
                                 evidence["qualified_prg_sha256"])
                self.assertEqual(cfg["memory"]["code_base"], code)

    def test_reject_wrong_memory_mapping_and_drift(self):
        with self.assertRaises(EvidenceError):
            self.export(code_base=0x9000)
        with self.assertRaises(EvidenceError):
            self.export(zp_base=0x70)
        with self.assertRaises(EvidenceError):
            self.export(scratch_base=0xc080)
        with self.assertRaises(EvidenceError):
            self.export(ram_budget=1)
        with self.assertRaises(EvidenceError):
            self.export(zp_budget=-1)
        selected = self.export()[1]["choice"]
        for mutate in (
            lambda r: r["placements"][0]["per_option"][selected].__setitem__(
                "linked_prg_sha256", "f"*64),
            lambda r: r["placements"][0]["per_option"][selected]["source_sha256"].__setitem__(
                "MATH_SMUL32", "f"*64),
            lambda r: r["placements"][0].__setitem__("input_corpus_sha256", "e"*64),
            lambda r: r["placements"][0]["per_option"][selected].__setitem__(
                "main_ram_total_bytes", 1),
        ):
            tampered = copy.deepcopy(self.report)
            mutate(tampered)
            with self.assertRaises(EvidenceError):
                self.export(tampered)

    def test_pinned_config_uses_all_three_public_sources(self):
        summary = summarize(self.report)
        self.assertEqual(len(summary["per_option"]), 8)
        config, evidence = self.export(objective="ram", ram_budget=12000, zp_budget=0)
        self.assertEqual(config["constraints"]["max_zp_bytes"], 0)
        self.assertEqual(config["pins"]["MATH_ISQRT16"], "link:radix4-zerozp")
        self.assertEqual(evidence["worst_placement_measured_envelope"]["zero_page_bytes"], 0)
        self.assertEqual(len(evidence["selected_source_sha256"]), 3)

if __name__ == "__main__":
    unittest.main()
