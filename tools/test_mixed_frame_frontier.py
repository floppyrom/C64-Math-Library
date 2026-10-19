#!/usr/bin/env python3
"""Fail-closed arbitrary multi-operation frame resource and peak frontier."""
from __future__ import annotations

import copy
import unittest

from mixed_frame_frontier import EvidenceError, summarize, frontier, select

OPS = ("MATH_UMUL32", "MATH_SMUL32", "MATH_ISQRT16")

def sample():
    original = {
        "compact": (450, 0, 100, 85, 500),
        "shared": (2600, 31, 38, 30, 200),
        "independent": (5300, 31, 35, 28, 190),
    }
    places = []
    for i, (code, io) in enumerate((("$8000", "$C000"), ("$7123", "$C040"))):
        choices = {}
        for name, (ram, zp, peak, p95, total) in original.items():
            variants = {op: name for op in OPS}
            sources = {op: chr(97 + n) * 64 for n, op in enumerate(OPS)}
            choices[name] = {
                "variant_map": variants, "source_sha256": sources,
                "linked_prg_sha256": chr(100 + i) * 64,
                "linked_source_count": 2 if name == "shared" else 3,
                "main_ram_total_bytes": ram + 10*i, "zero_page_bytes": zp,
                "peak_frame_math_cycles": peak + i,
                "p95_frame_math_cycles": p95 + i,
                "total_math_cycles": total + i,
                "per_operation": [{"operation": op, "calls": 2} for op in OPS],
            }
        places.append({"code": code, "io": io,
                       "paired_calls": 6, "frames": 3,
                       "cpu_model_only": True, "native_pal_timing": False,
                       "input_corpus_sha256": "f" * 64,
                       "per_option": choices})
    return {"operations": list(OPS), "placements": places}

class MixedFrontierTests(unittest.TestCase):
    def test_retains_sharing_and_worst_placement(self):
        s = summarize(sample())
        self.assertEqual(s["operations"], list(OPS))
        self.assertEqual(s["per_option"]["shared"]["main_ram_total_bytes"], 2610)
        self.assertEqual(s["per_option"]["shared"]["peak_frame_math_cycles"], 39)
        self.assertEqual(frontier(s), ["compact", "independent", "shared"])
        self.assertFalse(s["physical_pal_feasibility_claim"])

    def test_budgets_apply_to_combined_source_images(self):
        s = summarize(sample())
        self.assertEqual(select(s, 6000, 31)["choice"], "independent")
        self.assertEqual(select(s, 3000, 31)["choice"], "shared")
        self.assertEqual(select(s, 3000, 0)["choice"], "compact")
        self.assertEqual(select(s, 6000, 31, objective="ram")["choice"], "compact")
        self.assertEqual(select(s, 6000, 31, max_peak_cycles=37)["choice"], "independent")
        with self.assertRaises(EvidenceError):
            select(s, 3000, 31, max_peak_cycles=37)

    def test_reject_noncomparable_or_unverified_evidence(self):
        changes = (
            lambda d: d["placements"].pop(),
            lambda d: d["operations"].append("MATH_UMUL32"),
            lambda d: d["placements"][1].__setitem__("input_corpus_sha256", "e"*64),
            lambda d: d["placements"][1].__setitem__("frames", 4),
            lambda d: d["placements"][1].__setitem__("native_pal_timing", True),
            lambda d: d["placements"][1]["per_option"].pop("shared"),
            lambda d: d["placements"][1]["per_option"]["shared"]["source_sha256"].__setitem__("MATH_SMUL32", "e"*64),
            lambda d: d["placements"][0]["per_option"]["compact"]["variant_map"].pop("MATH_ISQRT16"),
            lambda d: d["placements"][0]["per_option"]["independent"].__setitem__("peak_frame_math_cycles", -1),
            lambda d: d["placements"][0]["per_option"]["shared"]["per_operation"][0].__setitem__("calls", 5),
            lambda d: d["placements"][0]["per_option"]["shared"].__setitem__("linked_prg_sha256", "invalid"),
        )
        for mutation in changes:
            with self.subTest(case=str(mutation)):
                datum = copy.deepcopy(sample())
                mutation(datum)
                with self.assertRaises(EvidenceError):
                    summarize(datum)

if __name__ == "__main__":
    unittest.main()
