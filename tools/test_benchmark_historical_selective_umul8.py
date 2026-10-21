#!/usr/bin/env python3
"""Direct original-resident vs operation-first public UMUL8 speed/correctness."""
import json
import unittest
from unittest.mock import patch
import benchmark_historical_selective_umul8 as bench

class UMUL8HistoricalPublicParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=bench.compare()
    def test_old_resident_matches_selected_full_public_abi(self):
        r=self.result
        self.assertEqual(r["api"],"MATH_UMUL8")
        self.assertEqual(r["cases"],1000)
        self.assertTrue(r["hist_to_selective_same_input"])
        self.assertFalse(r["native_vice_verified"])
        self.assertFalse(r["all_56_historical_speed_parity"])
        self.assertEqual(len(r["relocated_selective_observations"]),2)
        sha=r["historical_observation"]["public_result_carry_sha256"]
        for layout in r["relocated_selective_observations"]:
            self.assertEqual(set(layout["variants"]),{
                "link:v1-resident-fast","link:quarter-square","link:compact-zerozp"})
            for name, observation in layout["variants"].items():
                with self.subTest(layout=layout["code_origin"],variant=name):
                    self.assertEqual(observation["public_result_carry_sha256"],sha)
                    self.assertEqual(observation["cases"],1000)
                    self.assertLessEqual(observation["min_cycles"],observation["p95_cycles"])
                    self.assertLessEqual(observation["p95_cycles"],observation["max_cycles"])
                    self.assertTrue(observation["stack_restored"])
                    self.assertTrue(observation["input_bytes_preserved"])
    def test_repeated_report_is_deterministic(self):
        self.assertEqual(json.dumps(self.result,sort_keys=True),
                         json.dumps(bench.compare(),sort_keys=True))
    def test_frozen_reference_source_hash_is_mandatory(self):
        with patch.object(bench.hashlib,"sha256") as bogus:
            bogus.return_value.hexdigest.return_value="0"*64
            with self.assertRaisesRegex(bench.ComparisonError,
                                        "Frozen V1 resident SHA256 changed"):
                bench.frozen_source()

if __name__=="__main__":unittest.main()
