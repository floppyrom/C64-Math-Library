#!/usr/bin/env python3
"""First-class builder frame objective, exact same-source PRG and rejection gates."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mixed3_frame_parity import OPS, compare

ROOT = Path(__file__).resolve().parents[1]


class FrameObjectiveCLITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = {"basis": "three-operation same-input linked source math-only frames",
                     "operations": list(OPS),
                     "placements": [compare(0x8000, 0xc000, 0x50),
                                    compare(0x7123, 0xc040, 0x70)]}

    def config(self, *, zp=31, **overrides):
        config = {
            "target": "c64", "objective": "frame",
            "operations": list(OPS),
            "constraints": {"max_ram_bytes": 12000,
                            "max_zp_bytes": zp},
            "memory": {"code_base": 0x8000, "math_io": 0xc000,
                       "zp_base": 0x50, "scratch_base": 0xc040},
            "frame_optimize": "peak",
        }
        config.update(overrides)
        return config

    def invoke(self, folder, config, report=None, extra=()):
        folder = Path(folder)
        source = folder / "qualified.json"
        source.write_text(json.dumps(self.frame if report is None else report),
                          encoding="utf-8")
        cfg = folder / "project.json"
        cfg.write_text(json.dumps(config), encoding="utf-8")
        dest = folder / "output" / "selection_manifest.json"
        cmd = [sys.executable, str(ROOT / "tools/math_builder.py"),
               "--config", str(cfg), "--objective", "frame",
               "--frame-report", str(source), "--out", str(dest),
               "--build", *extra]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True,
                                text=True, timeout=240)
        return result, dest.parent

    def test_valid_peak_and_low_zero_page_configurations(self):
        for zp in (31, 0):
            with self.subTest(zp=zp), tempfile.TemporaryDirectory() as temp:
                r, out = self.invoke(temp, self.config(zp=zp))
                self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
                prg = (out / "math_selective.prg").read_bytes()
                evidence = json.loads((out / "frame_qualified_evidence.json").read_text())
                config = json.loads((out / "frame_qualified_config.json").read_text())
                manifest = json.loads((out / "selective_manifest.json").read_text())
                self.assertEqual(hashlib.sha256(prg).hexdigest(),
                                 evidence["qualified_prg_sha256"])
                self.assertEqual(manifest["prg_sha256"], evidence["qualified_prg_sha256"])
                self.assertEqual(manifest["link_exports"], sorted(OPS))
                self.assertEqual(config["pins"],
                                 {op["api"]: op["variant"] for op in manifest["operations"]})
                self.assertEqual(evidence["worst_placement_measured_envelope"]["zero_page_bytes"], zp)
                self.assertFalse(evidence["physical_pal_feasibility_claim"])
                self.assertEqual(evidence["public_calls_per_location"], 150)
                self.assertEqual(evidence["frames_per_location"], 24)

    def test_fail_closed_wrong_project_or_layout(self):
        bad = [
            self.config(operations=["UMUL32", "SMUL32"]),
            self.config(memory={"code_base": 0x9000, "math_io": 0xc000,
                                "zp_base": 0x50, "scratch_base": 0xc040}),
            self.config(memory={"code_base": 0x8000, "math_io": 0xc000,
                                "zp_base": 0x70, "scratch_base": 0xc040}),
            self.config(pins={"MATH_UMUL32": "link:compact-zerozp"}),
            self.config(constraints={"max_ram_bytes": 10, "max_zp_bytes": 31}),
        ]
        for config in bad:
            with self.subTest(config=config), tempfile.TemporaryDirectory() as temp:
                response, output = self.invoke(temp, config)
                self.assertNotEqual(response.returncode, 0)
                self.assertFalse((output / "math_selective.prg").exists())
                self.assertIn("frame evidence", response.stderr)

    def test_reject_false_synthetic_latency_even_with_valid_prg_and_source_sha(self):
        tampered = copy.deepcopy(self.frame)
        for placement in tampered["placements"]:
            for option in placement["per_option"].values():
                # A trusted-looking report can preserve the original code/
                # binary hashes while lying about synthetic peak frame costs.
                option["peak_frame_math_cycles"] += 1000
        with tempfile.TemporaryDirectory() as temp:
            response, output = self.invoke(temp, self.config(), report=tampered)
            self.assertNotEqual(response.returncode, 0)
            self.assertIn("source-linked public-call replay", response.stderr)
            self.assertFalse((output / "math_selective.prg").exists())

    def test_fail_closed_corrupt_source_or_peak_budget(self):
        corrupt = copy.deepcopy(self.frame)
        for place in corrupt["placements"]:
            for option in place["per_option"].values():
                option["linked_prg_sha256"] = "0"*64
        for report, extra in ((corrupt, ()), (self.frame, ("--frame-max-cycles", "100"))):
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as temp:
                response, output = self.invoke(temp, self.config(), report=report, extra=extra)
                self.assertNotEqual(response.returncode, 0)
                self.assertFalse((output / "math_selective.prg").exists())

    def test_frame_is_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            cfg = self.config()
            cfg["objective"] = "balanced"
            response, out = self.invoke(temp, cfg, extra=("--objective", "balanced"))
            # An explicit ordinary builder objective must not silently use frame evidence.
            self.assertNotEqual(response.returncode, 0)
            self.assertIn("Frame evidence flags require", response.stderr)
            self.assertFalse((out / "math_selective.prg").exists())

if __name__ == "__main__":
    unittest.main()
