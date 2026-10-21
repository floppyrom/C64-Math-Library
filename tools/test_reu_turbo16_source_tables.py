#!/usr/bin/env python3
"""Actual REU Turbo16 table bytes from source, cross-check frozen V3/V4 PRGs."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import reu_turbo16_source_tables as subject

REFS = (
    Path("v3_reu_512k/resident/math_v3_reu_512k_game_math.prg"),
    Path("v4_reu_16m/resident/math_v4_reu_16m_game_math.prg"),
)


class Turbo16TableSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report, cls.tables = subject.materialize()

    def test_two_historical_sources_yield_four_identical_planes(self):
        self.assertEqual(len(self.tables), 4)
        self.assertEqual(self.report["total_bytes"], 2048)
        self.assertEqual(self.report["plane_names"], list(subject.NAMES))
        self.assertTrue(self.report["byte_identical_v3_v4_source_tables"])
        self.assertFalse(self.report["independent_math_generated_tables"])
        self.assertFalse(self.report["legacy_prg_required_to_materialize"])
        self.assertFalse(self.report["native_reu_backend_available"])
        for name, data in self.tables.items():
            with self.subTest(name=name):
                self.assertEqual(len(data), 512)
                self.assertEqual(hashlib.sha256(data).hexdigest(),
                                 self.report["plane_sha256"][name])

    def test_source_planes_equal_original_v3_and_v4_frozen_binary_bytes(self):
        manifest = subject.source_manifest(subject.ROOT)
        for ref in REFS:
            with self.subTest(ref=str(ref)):
                data = (subject.ROOT / ref).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(),
                                 manifest[ref.as_posix()])
                load = data[0] | (data[1] << 8)
                for offset, name in zip(subject.OFFSETS, subject.NAMES):
                    start = 0x6000 + offset - load + 2
                    self.assertEqual(data[start:start+512],
                                     self.tables[name], (str(ref), name))

    def test_mutation_fails_closed(self):
        altered = dict(subject.source_manifest(subject.ROOT))
        altered[subject.SOURCES[0].as_posix()] = "f" * 64
        with patch.object(subject, "source_manifest", return_value=altered):
            with self.assertRaisesRegex(subject.TableError, "source drift"):
                subject.materialize()

    def test_cli_creates_rebuildable_binaries_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "source_tables"
            cmd = [sys.executable, str(subject.ROOT / "tools" /
                                        "reu_turbo16_source_tables.py"),
                   "--out", str(out)]
            run = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            a = json.loads((out / "source_table_manifest.json").read_text())
            self.assertEqual(a["plane_sha256"], self.report["plane_sha256"])
            for name, data in self.tables.items():
                self.assertEqual((out / name).read_bytes(), data)
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("destination exists", second.stderr)

    def test_output_is_reproducible(self):
        self.assertEqual(
            json.dumps(subject.materialize()[0], sort_keys=True),
            json.dumps(self.report, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
