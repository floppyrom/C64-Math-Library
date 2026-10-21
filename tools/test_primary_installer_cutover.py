#!/usr/bin/env python3
"""Regress the stock-C64 installer cutover without mutating historical binaries."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")


def make_commands(*targets):
    result=subprocess.run(("make","--no-print-directory","-n",*targets),
                          cwd=ROOT,capture_output=True,text=True,check=False)
    if result.returncode:
        raise AssertionError("Makefile target failed:\n"+result.stderr)
    return result.stdout


class RetiredProfileInterfaceTests(unittest.TestCase):
    def test_default_make_is_operation_first_not_historical(self):
        script=make_commands("all")
        self.assertIn("tools/math_builder.py --config",script)
        self.assertIn("--build",script)
        for old in ("tools/assemble_sources.py","tools/build_hybrid.py",
                    "tools/build_pareto.py","tools/generate_sources.py"):
            self.assertNotIn(old,script)

    def test_legacy_verification_is_explicit_and_preserved(self):
        script=make_commands("legacy-validate")
        for required in ("tools/assemble_sources.py","tools/build_hybrid.py",
                         "tools/validate_hybrid.py","tools/validate_pareto.py"):
            self.assertIn(required,script)
        self.assertNotEqual(script,make_commands("all"))
        self.assertIn("tools/configure_math.py",make_commands("builder-setup"))

    def test_supported_public_docs_consistently_route_new_users(self):
        for file in ("README.md","QUICK_START.md","USER_MANUAL.md"):
            with self.subTest(file=file):
                contents=(ROOT/file).read_text(encoding="utf-8")
                self.assertIn("make builder-setup",contents)
                self.assertIn("math_selective.prg",contents)
        release=(ROOT/"docs/BUILDER_RELEASE_ACCEPTANCE.md").read_text()
        self.assertIn("COMPLETED",release)
        self.assertIn("PR #372",release)
        old=(ROOT/"docs/README_RESEARCH_ARCHIVE_2026-10-21.md").read_text()
        self.assertIn("Historical README snapshot",old)
        self.assertIn("C64 Math Library",old)

    def test_historical_profile_docs_are_explicitly_archived(self):
        for folder in PROFILES:
            with self.subTest(folder=folder):
                text=(ROOT/folder/"README.md").read_text(encoding="utf-8")
                self.assertTrue(text.startswith("> **ARCHIVED RESIDENT"))
                self.assertIn("make builder-setup",text)
        for p in ("docs/REU_COMPAT_EXPORT.md",
                  "docs/PROFILE_RETIREMENT_EVIDENCE.md"):
            data=(ROOT/p).read_text(encoding="utf-8")
            self.assertIn("compatibility",data.lower())

    def test_machine_audit_still_does_not_claim_full_reu_and_speed_parity(self):
        from sys import path
        import sys
        sys.path.insert(0,str(ROOT/"tools"))
        try:
            import profile_retirement_audit
            result=profile_retirement_audit.audit()
        finally:
            sys.path.remove(str(ROOT/"tools"))
        self.assertFalse(result["ready_to_retire_all_v1_v5_profiles"])
        self.assertEqual(result["stock_public_operations"],56)
        self.assertEqual(result["hardware_backend_status"]["reu_16m"],
                         "legacy_profile_compatibility_only")

    def test_release_status_distinguishes_installer_from_elimination(self):
        data=json.loads((ROOT/"RELEASE_STATUS.json").read_text(encoding="utf-8"))
        mark=data["operation_first_installer_cutover_2026_10_21"]
        self.assertEqual(mark["stock_public_operations"],56)
        self.assertFalse(mark["historical_profiles_user_selectable"])
        self.assertTrue(mark["historical_frozen_profiles_preserved"])
        self.assertFalse(mark["stronger_full_historical_binary_elimination"])
        self.assertFalse(mark["public_numbered_release_created_by_cutover"])


if __name__=="__main__":
    unittest.main()
