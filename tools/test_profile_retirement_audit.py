#!/usr/bin/env python3
"""Fail-closed C64 profile-retirement evidence contract."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import profile_retirement_audit as audited


class RetirementEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audited.audit()

    def test_current_source_and_legacy_scope(self):
        result = self.report
        self.assertEqual(result["stock_public_operations"], 56)
        self.assertEqual(result["source_cycle_model_declarations"], 56)
        self.assertEqual(result["selectable_variants_per_operation"],
                         {"1": 15, "2": 24, "3": 11, "4": 4, "5": 2})
        self.assertEqual(len(result["legacy_hardware_services"]), 9)
        self.assertEqual(len(result["stock_nonoperation_public_symbols"]), 13)
        self.assertIn("MATH_INIT", result["stock_nonoperation_public_symbols"])
        self.assertEqual(set(result["stock_operations"]),
                         set(audited.selective_linker.MODULES))
        self.assertFalse(result["ready_to_retire_all_v1_v5_profiles"])
        self.assertTrue(result["blocking_gates"])

    def test_legacy_reu_abi_overlay_ownership(self):
        s = self.report["legacy_hardware_services"]
        for name,record in s.items():
            if "UMUL16" in name:
                self.assertEqual(record["exclusive_mode_zp_bytes"],122)
                self.assertEqual(len(record["legacy_profiles"]),2)
            if "UMUL32" in name:
                self.assertEqual(record["exclusive_mode_zp_bytes"],135)
                self.assertEqual(len(record["legacy_profiles"]),2)
            if "QS16" in name:
                self.assertEqual(record["exclusive_mode_zp_bytes"],16)
                self.assertEqual(record["legacy_profiles"],["v4_reu_16m"])
            self.assertFalse(record["stock_operation_first_available"])

    def test_profile_export_loss_fails_closed(self):
        original = audited.profile_symbols
        def missing(root):
            symbols = original(root)
            symbols["v4_reu_16m"].remove("MATH_REU_QS16_END")
            return symbols
        with patch.object(audited,"profile_symbols",side_effect=missing):
            with self.assertRaisesRegex(audited.RetirementAuditError,
                                        "Historical REU service"):
                audited.audit()

    def test_absent_source_model_fails_closed(self):
        source = audited.source_speed_keys
        with patch.object(audited,"source_speed_keys",
                          side_effect=lambda:source()-{"MATH_SEEK16_INIT"}):
            with self.assertRaisesRegex(audited.RetirementAuditError,
                                        "lack declared speed models"):
                audited.audit()

    def test_cli_report_deterministic_and_retirement_refusal(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/"cutover.json"
            args=[sys.executable,str(audited.ROOT/"tools/profile_retirement_audit.py"),
                  "--out",str(out)]
            good=subprocess.run(args,capture_output=True,text=True,
                                cwd=audited.ROOT)
            self.assertEqual(good.returncode,0,good.stderr)
            first=out.read_bytes()
            self.assertEqual(json.loads(first)["stock_public_operations"],56)
            good=subprocess.run(args,capture_output=True,text=True,
                                cwd=audited.ROOT)
            self.assertEqual(good.returncode,0,good.stderr)
            self.assertEqual(first,out.read_bytes())
            blocked=subprocess.run(args+["--require-retirement-ready"],
                                   capture_output=True,text=True,
                                   cwd=audited.ROOT)
            self.assertEqual(blocked.returncode,2)
            self.assertIn("BLOCKED",blocked.stderr)


if __name__ == "__main__":
    unittest.main()
