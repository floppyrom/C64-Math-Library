#!/usr/bin/env python3
"""End-to-end replay-attested UDIV32_32/UMOD32_32 frame installer."""
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
from u3232_joint_frame_parity import BASIS, OPS, complete_report, OPTIONS

ROOT = Path(__file__).resolve().parents[1]


class U3232FrameInstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = complete_report()

    def test_registered_public_q_r_replay(self):
        fresh = replay(self.report)
        self.assertEqual(fresh, self.report)
        self.assertEqual(fresh["basis"], BASIS)
        self.assertEqual(len(fresh["placements"]), 2)
        self.assertEqual(len(fresh["placements"][0]["per_option"]), len(OPTIONS))

    def config(self, zp=12):
        return {
            "target": "c64", "objective": "frame",
            "operations": list(OPS),
            "constraints": {"max_ram_bytes": 12000, "max_zp_bytes": zp},
            "memory": {"code_base": 0x8000, "math_io": 0xc000,
                       "scratch_base": 0xc040, "zp_base": 0x50},
            "frame_optimize": "peak",
        }

    def invoke(self, folder, report, config):
        folder = Path(folder)
        evidence_path = folder / "measured.json"
        evidence_path.write_text(json.dumps(report) + "\n", encoding="utf-8")
        config_path = folder / "config.json"
        config_path.write_text(json.dumps(config) + "\n", encoding="utf-8")
        output = folder / "build"
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools/math_builder.py"),
             "--objective", "frame", "--config", str(config_path),
             "--frame-report", str(evidence_path), "--build",
             "--out", str(output / "selection_manifest.json")],
            cwd=ROOT, capture_output=True, text=True, timeout=240,
        )
        return proc, output

    def test_qualified_full_divmod_image_rebuild_at_full_and_zero_zp(self):
        for zp in (12, 0):
            with self.subTest(zp_budget=zp), tempfile.TemporaryDirectory() as td:
                proc, path = self.invoke(td, self.report, self.config(zp))
                self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
                provenance = json.loads((path / "frame_qualified_evidence.json").read_text())
                pinned = json.loads((path / "frame_qualified_config.json").read_text())
                manifest = json.loads((path / "selective_manifest.json").read_text())
                prg = (path / "math_selective.prg").read_bytes()
                self.assertEqual(hashlib.sha256(prg).hexdigest(),
                                 provenance["qualified_prg_sha256"])
                self.assertEqual(manifest["prg_sha256"], provenance["qualified_prg_sha256"])
                self.assertEqual(set(pinned["pins"]), set(OPS))
                self.assertEqual(set(manifest["link_exports"]), set(OPS))
                self.assertEqual(provenance["locations_tested"], 2)
                self.assertEqual(provenance["public_calls_per_location"], 150)
                self.assertEqual(provenance["frames_per_location"], 24)
                self.assertLessEqual(provenance["worst_placement_measured_envelope"]
                                     ["zero_page_bytes"], zp)
                self.assertFalse(provenance["physical_pal_feasibility_claim"])

    def test_tampered_math_frame_latency_is_never_trusted(self):
        edited = copy.deepcopy(self.report)
        for location in edited["placements"]:
            for option in location["per_option"].values():
                option["peak_frame_math_cycles"] += 200
        with self.assertRaisesRegex(EvidenceError, "source-linked public-call replay"):
            replay(edited)
        with tempfile.TemporaryDirectory() as td:
            result, destination = self.invoke(td, edited, self.config())
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((destination / "math_selective.prg").exists())

    def test_reject_wrong_operation_set_or_unregistered_basis(self):
        bad = copy.deepcopy(self.report)
        bad["basis"] = "unsigned32 imported nonreplayable external aggregate"
        with self.assertRaises(EvidenceError):
            replay(bad)
        with tempfile.TemporaryDirectory() as td:
            cfg = self.config()
            cfg["operations"] = ["UDIV32_32"]
            result, out = self.invoke(td, self.report, cfg)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((out / "math_selective.prg").exists())


if __name__ == "__main__":
    unittest.main()
