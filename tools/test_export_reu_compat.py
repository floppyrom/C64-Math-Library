#!/usr/bin/env python3
"""Real V3/V4 resident+REU copy integrity, ABI and hard fail-closed checks."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import export_reu_compat as compat

class REUCompatibilityBundleTests(unittest.TestCase):
    def test_original_complete_profiles_are_exported_unchanged(self):
        for profile in compat.PROFILES:
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as td:
                out = Path(td) / "whole-resident"
                manifest = compat.export(profile, out)
                self.assertEqual(len(manifest["public_reu_lifecycle"]),
                                 9 if profile == "v4_reu_16m" else 6)
                self.assertEqual(len(manifest["public_stock_nonoperation_symbols"]), 13)
                self.assertFalse(manifest["may_mix_with_operation_first_prg"])
                self.assertFalse(manifest["new_reu_backend_implemented"])
                self.assertEqual(json.loads((out/"compat_manifest.json").read_text()),
                                 manifest)
                for name, info in manifest["sources"].items():
                    self.assertEqual(compat.digest(out/name), info["sha256"])
                    self.assertEqual((out/name).stat().st_size, info["bytes"])
                self.assertIn("BEGIN/CALL/END", (out/"COMPATIBILITY.txt").read_text())
                with self.assertRaisesRegex(compat.LegacyREUError, "already exists"):
                    compat.export(profile, out)

    def test_reject_unlocked_or_broken_sources(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(compat.LegacyREUError):
                compat.export("stock_c64", Path(td)/"not_a_profile")
            locked = compat.manifest_hashes(compat.ROOT)
            original = compat.PROFILES["v3_reu_512k"]["resident"]
            locked[original] = "f" * 64
            with patch.object(compat, "manifest_hashes", return_value=locked):
                with self.assertRaisesRegex(compat.LegacyREUError, "checksum drift"):
                    compat.export("v3_reu_512k", Path(td)/"not_exported")
            self.assertFalse((Path(td)/"not_exported").exists())

if __name__ == "__main__":
    unittest.main()
