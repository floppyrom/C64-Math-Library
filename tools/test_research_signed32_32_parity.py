#!/usr/bin/env python3
"""Ensure signed32/32 donor research compares actual ABI, not old averages."""
from __future__ import annotations
import unittest
import research_signed32_32_parity as research


class Signed3232DonorResearch(unittest.TestCase):
    def test_signed_quotient_and_remainder_reference(self):
        for n,d,q,rem,c in (
            (0,0,0,0,1), (0,1,0,0,0),
            (0x80000000,0xffffffff,0x80000000,0,0),
            (0xffffffff,2,0,0xffffffff,0),
            (0xfffffffd,2,0xffffffff,0xffffffff,0),
            (0x7fffffff,0x80000000,0,0x7fffffff,0),
        ):
            self.assertEqual(research.expected(n,d),(q,rem,c))

    def test_deterministic_unique_input_corpus(self):
        a=research.corpus()
        self.assertEqual(len(a),192)
        self.assertEqual(a,research.corpus())
        self.assertIn((0,0),a)
        self.assertIn((0x80000000,0xffffffff),a)
        self.assertNotEqual(a,research.corpus(193))
        with self.assertRaises(ValueError):
            research.corpus(0)

    def test_portable_and_one_historical_profile_use_same_abi(self):
        x=research.collect(6,profiles=["v1_balanced"],
                           placements=((0x8000,0xc000),))
        self.assertEqual(x["status"],"PASS")
        self.assertEqual(x["cases"],6)
        self.assertEqual(len(x["measurements"]),4)
        self.assertEqual({s["api"] for s in x["measurements"]},
                         set(research.OPS))
        self.assertEqual({s["variant"] for s in x["measurements"]},
                         {"resident:v1_balanced","link:portable-zerozp"})
        self.assertTrue(all(row["calls"]==6 for row in x["measurements"]))
        self.assertTrue(all(row["mean_cycles"]>0 for row in x["measurements"]))


if __name__=="__main__":
    unittest.main()
