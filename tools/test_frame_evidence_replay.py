#!/usr/bin/env python3
"""Test registered synthetic frame replay and rejection of forged peaks."""
from __future__ import annotations

import copy
import unittest

from frame_evidence_replay import REGISTERED_BASIS, replay
from mixed_frame_frontier import EvidenceError
from mixed3_frame_parity import compare, OPS


class FrameEvidenceReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = {"basis": REGISTERED_BASIS,
                        "operations": list(OPS),
                        "placements": [compare(0x8000, 0xc000, 0x50),
                                       compare(0x7123, 0xc040, 0x70)]}

    def test_replay_every_plan_at_each_relocation(self):
        again = replay(self.original)
        self.assertEqual(self.original, again)
        self.assertEqual(len(again["placements"][0]["per_option"]), 8)

    def test_corrupt_peak_p95_total_and_main_ram_fail(self):
        for key, change in (
            ("peak_frame_math_cycles", 2),
            ("p95_frame_math_cycles", 1),
            ("total_math_cycles", 1),
            ("main_ram_total_bytes", 1),
        ):
            with self.subTest(key=key):
                altered = copy.deepcopy(self.original)
                data = altered["placements"][0]["per_option"]["fast31-shared+table"]
                data[key] += change
                with self.assertRaises(EvidenceError):
                    replay(altered)

    def test_corrupt_corpus_source_or_prg_fail(self):
        for key in ("input_corpus_sha256", "source_sha256", "linked_prg_sha256"):
            with self.subTest(key=key):
                altered = copy.deepcopy(self.original)
                if key == "input_corpus_sha256":
                    altered["placements"][0][key] = "f"*64
                else:
                    row = altered["placements"][1]["per_option"]["fast31-shared+table"]
                    if key == "source_sha256":
                        row[key]["MATH_SMUL32"] = "0"*64
                    else:
                        row[key] = "0"*64
                with self.assertRaises(EvidenceError):
                    replay(altered)

    def test_unknown_producer_and_duplicate_relocations_fail(self):
        for kind in ("basis", "operations", "duplicate"):
            altered = copy.deepcopy(self.original)
            if kind == "basis":
                altered["basis"] = "user-uploaded-unreproducible-benchmark"
            elif kind == "operations":
                altered["operations"].append("MATH_UDIV16")
            else:
                altered["placements"][1]["code"] = altered["placements"][0]["code"]
                altered["placements"][1]["io"] = altered["placements"][0]["io"]
                altered["placements"][1]["zp_base"] = altered["placements"][0]["zp_base"]
                altered["placements"][1]["scratch_base"] = altered["placements"][0]["scratch_base"]
            with self.subTest(kind=kind), self.assertRaises(EvidenceError):
                replay(altered)


if __name__ == "__main__":
    unittest.main()
