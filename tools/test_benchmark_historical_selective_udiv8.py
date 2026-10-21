#!/usr/bin/env python3
"""Original five-profile UDIV8 versus selective, full same-input public replay."""
import json
import unittest
from unittest.mock import patch
import benchmark_historical_selective_udiv8 as b

class HistoricalUDIV8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=b.compare()

    def test_public_abi_and_1000_shared_cases(self):
        result=self.report
        self.assertEqual(result["api"],"MATH_UDIV8")
        self.assertEqual(result["cases"],1000)
        self.assertEqual(len(result["historic_original_residents"]),5)
        self.assertEqual(len(result["selective_two_physical_placements"]),2)
        self.assertTrue(result["all_seven_source_paths_identical_input"])
        self.assertFalse(result["native_vice_certified"])
        self.assertFalse(result["all_56_speed_parity_certified"])
        hashes={r["public_result_sha256"]
                for r in result["historic_original_residents"].values()}
        for layout in result["selective_two_physical_placements"]:
            self.assertEqual(len(layout["variants"]),2)
            hashes.update(x["public_result_sha256"]
                          for x in layout["variants"].values())
        self.assertEqual(len(hashes),1)
        for v in [*result["historic_original_residents"].values(),
                  *(v for row in result["selective_two_physical_placements"]
                    for v in row["variants"].values())]:
            self.assertEqual(v["cases"],1000)
            self.assertLessEqual(v["min_cycles"],v["p95_cycles"])
            self.assertLessEqual(v["p95_cycles"],v["max_cycles"])
            self.assertTrue(v["stack_and_inputs_preserved"])

    def test_report_deterministic(self):
        self.assertEqual(json.dumps(self.report,sort_keys=True),
                         json.dumps(b.compare(),sort_keys=True))

    def test_original_resident_hash_must_match_frozen_manifest(self):
        with patch.object(b.hashlib,"sha256") as fake:
            fake.return_value.hexdigest.return_value="0"*64
            with self.assertRaisesRegex(b.ParityError,"Frozen file SHA changed"):
                b.source_sha("v1_balanced/resident/math_v1_balanced_game_math.prg")

if __name__=="__main__":
    unittest.main()
