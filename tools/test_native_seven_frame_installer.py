#!/usr/bin/env python3
"""Check exact seven-export frame-installed PRG identities before native x64sc."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from mixed_seven_frame_parity import OPS
from native_seven_frame_installer import (
    BUDGETS, CODE, IO, N, OPS as NATIVE_OPS,
    build_exact_frame_prg, check_native_map, qualified_cases,
)


class SevenExactNativeInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = qualified_cases()

    def test_source_corpus_and_memory_harness_contract(self):
        self.assertEqual(tuple(OPS), NATIVE_OPS)
        self.assertEqual(len(OPS), 7)
        self.assertEqual(len(BUDGETS), 2)
        self.assertEqual(N, 96)
        self.assertEqual(CODE, 0x4123)
        self.assertEqual(IO, 0xC040)
        self.assertEqual(len(self.report["placements"]), 2)
        self.assertEqual(self.report["placements"][1]["code"], "$4123")
        self.assertTrue(self.report["placements"][1]["cpu_model_only"])

    def test_exact_cli_frame_outputs_two_distinct_complete_projects(self):
        hashes = set()
        for objective, budget in BUDGETS:
            with self.subTest(goal=objective), tempfile.TemporaryDirectory() as td:
                prg, entries, proof = build_exact_frame_prg(
                    self.report, Path(td), zp_budget=budget)
                digest = hashlib.sha256(prg).hexdigest()
                self.assertEqual(digest, proof["qualified_prg_sha256"])
                self.assertEqual(set(entries), set(OPS))
                self.assertEqual(proof["locations_tested"], 2)
                self.assertEqual(proof["frames_per_location"], 24)
                self.assertEqual(proof["public_calls_per_location"], 150)
                self.assertEqual(check_native_map(prg), CODE + len(prg)-2)
                self.assertFalse(proof["physical_pal_feasibility_claim"])
                self.assertLessEqual(
                    proof["worst_placement_measured_envelope"]["zero_page_bytes"],
                    budget)
                if budget == 0:
                    self.assertEqual(proof["choice"], "compact-everywhere")
                hashes.add(digest)
        self.assertEqual(len(hashes), 2)

    def test_native_oracle_harness_rejects_overlap_with_measured_image(self):
        # This is why we qualify the already-measured $4123 binary first,
        # rather than overwriting an exact $2000 binary with the test stub.
        with self.assertRaises(AssertionError):
            check_native_map(bytes((CODE & 255, CODE >> 8)) + bytes(33000))


if __name__ == "__main__":
    unittest.main()
