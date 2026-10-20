#!/usr/bin/env python3
"""Exact sixteen-plan replay/CLI/native-image selection; no physical PAL claim."""
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
from frame_qualified_config import export_config
from mixed_frame_frontier import EvidenceError
from mixed_seven_cross_pareto import BASIS, LOCATIONS, OPS, options, complete_report
from mixed_seven_frame_parity import complete_report as legacy_report
from native_seven_frame_installer import build_exact_frame_prg, check_native_map

ROOT = Path(__file__).resolve().parents[1]
ZERO = "mul-compact+sqrt-table+udiv-compact+sdiv-compact"
MIXED = "mul-compact+sqrt-table+udiv-v2+sdiv-v2"


class CrossFrameInstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = complete_report()

    def test_complete_exact_source_and_original_provenance(self):
        self.assertEqual(self.report["basis"], BASIS)
        self.assertEqual(len(options()), 16)
        self.assertEqual(len(self.report["placements"]), 2)
        self.assertEqual(replay(self.report), self.report)
        # Existing four-choice production report remains independently registered.
        old = legacy_report()
        self.assertEqual(len(old["placements"][0]["per_option"]), 4)
        self.assertEqual(replay(old), old)
        for row, (code, io, zp) in zip(self.report["placements"], LOCATIONS):
            self.assertEqual(row["code"], "$%04X" % code)
            self.assertEqual(row["io"], "$%04X" % io)
            self.assertEqual(row["zp_base"], "$%04X" % zp)
            self.assertEqual(row["paired_calls"], 150)
            self.assertEqual(row["frames"], 24)

    def test_budgeted_zero_and_twelve_zp_are_exact_reproducible_binaries(self):
        for budget, selected, peak in ((0, ZERO, 59933), (12, MIXED, 40109)):
            with self.subTest(zp=budget), tempfile.TemporaryDirectory() as temp:
                prg, entry, proof = build_exact_frame_prg(
                    self.report, Path(temp), zp_budget=budget, frame_optimize="peak")
                self.assertEqual(proof["choice"], selected)
                self.assertEqual(proof["worst_placement_measured_envelope"]
                                 ["peak_frame_math_cycles"], peak)
                self.assertEqual(set(entry), set(OPS))
                self.assertEqual(len(entry), 7)
                self.assertEqual(proof["qualified_prg_sha256"],
                                 hashlib.sha256(prg).hexdigest())
                self.assertEqual(check_native_map(prg), 0x4123 + len(prg) - 2)
                self.assertLessEqual(proof["worst_placement_measured_envelope"]
                                     ["zero_page_bytes"], budget)
                self.assertFalse(proof["physical_pal_feasibility_claim"])
                self.assertEqual(proof["public_calls_per_location"], 150)
                self.assertEqual(proof["frames_per_location"], 24)

    def test_tampered_numbers_sources_or_maps_fail_closed(self):
        for kind in ("peak", "sha", "map", "candidate_count", "drop"):
            with self.subTest(kind=kind):
                forged = copy.deepcopy(self.report)
                if kind == "peak":
                    forged["placements"][1]["per_option"][ZERO]["peak_frame_math_cycles"] -= 9
                elif kind == "sha":
                    forged["placements"][0]["per_option"][ZERO]["linked_prg_sha256"] = "0" * 64
                elif kind == "map":
                    forged["placements"][1]["code"] = "$5000"
                elif kind == "candidate_count":
                    forged["candidate_count"] = 15
                else:
                    forged["placements"][0]["per_option"].pop(ZERO)
                with self.assertRaises(EvidenceError):
                    replay(forged)

    def test_extended_qualified_snapshot_respects_resource_envelopes(self):
        for budget, choice in ((0, ZERO), (12, MIXED)):
            cfg, proof = export_config(
                self.report, ram_budget=16000, zp_budget=budget,
                code_base=0x4123, math_io=0xc040, zp_base=0x70,
                scratch_base=0xc080, objective="peak")
            self.assertEqual(proof["choice"], choice)
            self.assertEqual(cfg["pins"], options()[choice])
            self.assertEqual(set(cfg["pins"]), set(OPS))
            self.assertTrue(proof["cpu_model_only"])
            self.assertLessEqual(proof["worst_placement_measured_envelope"]
                                 ["main_ram_total_bytes"], 16000)


if __name__ == "__main__":
    unittest.main()
