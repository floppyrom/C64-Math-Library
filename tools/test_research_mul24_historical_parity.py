#!/usr/bin/env python3
"""Ensure 24-bit donor comparison is deterministic, signed-exact, ABI-matched."""
from __future__ import annotations
import unittest
import research_mul24_historical_parity as q


class HistoricalMultiply24Research(unittest.TestCase):
    def test_sign_and_low48_product(self):
        for x,y in ((0,0),(1,1),(0x800000,0xffffff),
                    (0xffffff,2),(0x7fffff,0x800000)):
            self.assertEqual(q.expected(x,y,"MATH_UMUL24"),(x*y)&q.MASK48)
            sx=q.signed(x);sy=q.signed(y)
            self.assertEqual(q.expected(x,y,"MATH_SMUL24"),
                             (sx*sy)&q.MASK48)

    def test_corpus_is_deterministic_and_has_edges(self):
        a=q.corpus()
        self.assertEqual(len(a),512)
        self.assertEqual(a,q.corpus())
        self.assertIn((0,0),a)
        self.assertIn((0x800000,0xffffff),a)

    def test_one_initialized_resident_and_linked_compact(self):
        p=q.collect(profiles=["v1_balanced"],
                    placements=((0x8000,0xc000),))
        self.assertEqual(p["status"],"PASS")
        self.assertEqual(p["cases_per_api"],512)
        self.assertEqual(len(p["measurements"]),4)
        self.assertEqual({x["api"] for x in p["measurements"]},set(q.OPS))
        self.assertEqual({x["variant"] for x in p["measurements"]},
                         {"resident:v1_balanced","link:compact-zerozp"})
        self.assertTrue(all(x["calls"]==512 for x in p["measurements"]))


if __name__=="__main__":
    unittest.main()
