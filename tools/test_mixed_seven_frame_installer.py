#!/usr/bin/env python3
"""Replay-attested complete 7-API operation-first frame installer qualification."""
from __future__ import annotations
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from frame_evidence_replay import replay
from mixed_frame_frontier import EvidenceError
from mixed_seven_frame_parity import BASIS, OPS, OPTIONS, complete_report

ROOT = Path(__file__).resolve().parents[1]


class SevenAPIFrameInstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = complete_report()

    def config(self, zp=64):
        return {
            "target": "c64", "objective": "frame",
            "operations": list(OPS),
            "constraints": {"max_ram_bytes": 16000, "max_zp_bytes": zp},
            "memory": {"code_base": 0x2000, "math_io": 0xc000,
                       "zp_base": 0x50, "scratch_base": 0xc040},
            "frame_optimize": "peak",
        }

    def invoke(self, folder, report, config, extra=()):
        folder = Path(folder)
        reportpath = folder / "seven.json"
        reportpath.write_text(json.dumps(report) + "\n", encoding="utf-8")
        configpath = folder / "config.json"
        configpath.write_text(json.dumps(config) + "\n", encoding="utf-8")
        destination = folder / "installed"
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/math_builder.py"),
             "--objective", "frame", "--config", str(configpath),
             "--frame-report", str(reportpath), "--build",
             "--out", str(destination / "selection_manifest.json"), *extra],
            cwd=ROOT, capture_output=True, text=True, timeout=240)
        return result, destination

    def test_replay_is_exact_for_four_full_project_source_candidates(self):
        original = self.report
        self.assertEqual(replay(original), original)
        self.assertEqual(original["basis"], BASIS)
        self.assertEqual(len(original["placements"]), 2)
        self.assertEqual(set(original["placements"][0]["per_option"]), set(OPTIONS))

    def test_build_qualifies_both_low_resource_and_fast_project(self):
        for zp in (64, 0):
            with self.subTest(zp=zp), tempfile.TemporaryDirectory() as tmp:
                result, folder = self.invoke(tmp, self.report, self.config(zp=zp))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                binary = (folder / "math_selective.prg").read_bytes()
                proof = json.loads((folder / "frame_qualified_evidence.json").read_text())
                pins = json.loads((folder / "frame_qualified_config.json").read_text())
                manifest = json.loads((folder / "selective_manifest.json").read_text())
                self.assertEqual(hashlib.sha256(binary).hexdigest(),
                                 proof["qualified_prg_sha256"])
                self.assertEqual(set(manifest["link_exports"]), set(OPS))
                self.assertEqual(set(pins["pins"]), set(OPS))
                self.assertEqual(proof["public_calls_per_location"], 150)
                self.assertEqual(proof["frames_per_location"], 24)
                self.assertEqual(proof["locations_tested"], 2)
                self.assertLessEqual(proof["worst_placement_measured_envelope"]
                                     ["zero_page_bytes"], zp)
                self.assertLessEqual(proof["worst_placement_measured_envelope"]
                                     ["main_ram_total_bytes"], 16000)
                self.assertFalse(proof["physical_pal_feasibility_claim"])
                if zp == 0:
                    self.assertEqual(proof["choice"], "compact-everywhere")

    def test_forged_math_cycles_fail_despite_valid_source_prg_hash(self):
        forged = copy.deepcopy(self.report)
        for location in forged["placements"]:
            for option in location["per_option"].values():
                option["peak_frame_math_cycles"] -= 1000
        with self.assertRaises(EvidenceError):
            replay(forged)
        with tempfile.TemporaryDirectory() as tmp:
            result, directory = self.invoke(tmp, forged, self.config())
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((directory / "math_selective.prg").exists())

    def test_reject_unmeasured_location_and_wrong_operations(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = self.config()
            bad["operations"].pop()
            result, folder = self.invoke(tmp, self.report, bad)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((folder / "math_selective.prg").exists())
        with tempfile.TemporaryDirectory() as tmp:
            bad = self.config()
            bad["memory"]["code_base"] = 0x8000
            result, folder = self.invoke(tmp, self.report, bad)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((folder / "math_selective.prg").exists())

    def test_hard_peak_limit_rejects_compact_zero_zp_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, directory = self.invoke(
                tmp, self.report, self.config(zp=0),
                extra=("--frame-max-cycles", "20000"))
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((directory / "math_selective.prg").exists())


if __name__ == "__main__":
    unittest.main()
