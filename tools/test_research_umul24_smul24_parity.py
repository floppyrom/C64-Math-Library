#!/usr/bin/env python3
"""24-bit signed/unsigned donor selection must validate public product ABI."""
import unittest
import research_umul24_smul24_parity as research


class Mul24DonorResearch(unittest.TestCase):
    def test_signed_and_unsigned_wrap_and_24bit_edge_cases(self):
        cases=[
            ("MATH_UMUL24",0xffffff,0xffffff,0xfffffe000001),
            ("MATH_SMUL24",0xffffff,1,0xffffffffffff),
            ("MATH_SMUL24",0x800000,1,0xffffff800000),
            ("MATH_SMUL24",0x800000,0xffffff,0x000000800000),
            ("MATH_SMUL24",0x800000,0x800000,0x400000000000),
            ("MATH_UMUL24",0,0x800000,0),
        ]
        for api,x,y,want in cases:
            with self.subTest(api=api,x=x,y=y):
                self.assertEqual(research.expected(api,x,y),want)

    def test_deterministic_dense_sign_corpus(self):
        a=research.corpus()
        self.assertEqual(len(a),384)
        self.assertEqual(a,research.corpus())
        self.assertIn((0x800000,0xffffff),a)
        self.assertIn((0xffffff,0xffffff),a)
        self.assertNotEqual(a,research.corpus(385))
        with self.assertRaises(ValueError):
            research.corpus(0)

    def test_legacy_and_independent_portable_full_public_calls(self):
        data=research.collect(8,profiles=["v1_balanced"],
                              placements=((0x8000,0xc000),))
        self.assertEqual(data["status"],"PASS")
        self.assertEqual(len(data["results"]),4)
        self.assertEqual(set(v["api"] for v in data["results"]),
                         set(research.OPS))
        self.assertTrue(all(v["calls"]==8 for v in data["results"]))
        self.assertTrue(all(v["mean_cycles"]>0 for v in data["results"]))


if __name__=="__main__":
    unittest.main()
