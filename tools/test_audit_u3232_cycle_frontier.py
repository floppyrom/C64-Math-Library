#!/usr/bin/env python3
"""Deterministic public-ABI and cycle-tail checks for 32/32 divisor strata."""
from __future__ import annotations

import math
import unittest

import audit_u3232_cycle_frontier as audit
import selective_linker
import selective_speed_u3232 as speed


class StratifiedU3232Tests(unittest.TestCase):
    def test_case_generation_is_bounded_reproducible_and_meaningful(self):
        a=audit.corpus(16)
        self.assertEqual(a,audit.corpus(16))
        self.assertEqual(len(a),len(audit.BANDS))
        self.assertEqual(sum(len(seq) for seq in a.values()),16*len(audit.BANDS))
        self.assertTrue(all(d==0 for _,d in a["divisor_zero"]))
        self.assertTrue(all(d>0 and n<d for n,d in a["quotient_zero"]))
        self.assertTrue(all(d>0 and n//d==1 for n,d in a["quotient_one"]))
        self.assertTrue(all(d>0 and 2<=n//d<=15
                            for n,d in a["quotient_2_to_15"]))
        self.assertTrue(all(d>0 and d&(d-1)==0
                            for _,d in a["divisor_power_of_two"]))
        self.assertEqual(len(audit.fingerprint(a)),64)
        self.assertEqual(audit.fingerprint(a),audit.fingerprint(audit.corpus(16)))
        with self.assertRaises(ValueError):
            audit.corpus(0)
        with self.assertRaises(ValueError):
            audit.corpus(257)

    def test_quantiles_use_exact_nearest_rank(self):
        self.assertEqual(audit.describe([4,1,9,2,6]),
                         {"cases":5,"mean":4.4,"median":4,
                          "p95":9,"worst":9,"best":1})
        self.assertEqual(audit.describe([1]*19+[100])["p95"],1)
        with self.assertRaises(ValueError):
            audit.describe([])

    def test_both_division_apis_all_variants_two_code_maps(self):
        report=audit.audit(per_band=8)
        self.assertEqual(report["status"],
                         "QUALIFIED_CPU_MODEL_DIAGNOSTIC_NO_PROMOTION")
        self.assertEqual(set(report["locations"]),{"$8000","$7123"})
        self.assertEqual(report["corpus_sha256"],
                         audit.fingerprint(audit.corpus(8)))
        for place,apis in report["locations"].items():
            self.assertEqual(set(apis),set(audit.APIS))
            for api,record in apis.items():
                self.assertEqual(set(record["candidates"]),speed.EXPECTED[api])
                self.assertIn(record["baseline"],record["candidates"])
                for variant,measure in record["candidates"].items():
                    self.assertEqual(len(measure["source_sha256"]),64)
                    self.assertGreater(measure["code_bytes"],0)
                    self.assertEqual(set(measure["bands"]),set(audit.BANDS))
                    self.assertEqual(measure["overall"]["cases"],8*len(audit.BANDS))
                    for band,distribution in measure["bands"].items():
                        self.assertEqual(distribution["cases"],8)
                        self.assertLessEqual(distribution["best"],distribution["median"])
                        self.assertLessEqual(distribution["median"],distribution["p95"])
                        self.assertLessEqual(distribution["p95"],distribution["worst"])
                        self.assertTrue(math.isfinite(distribution["mean"]))
                self.assertEqual(set(record["paired_cycle_deltas"]),
                    set(record["candidates"])-{record["baseline"]})
                for variant,bands in record["paired_cycle_deltas"].items():
                    for band,deltas in bands.items():
                        self.assertEqual(
                            deltas["faster_cases"]+deltas["slower_cases"]+
                            deltas["equal_cases"],8)

    def test_catalog_change_fails_closed(self):
        key="MATH_UDIV32_32"
        original=dict(selective_linker.MODULES[key])
        try:
            del selective_linker.MODULES[key]["link:zptail"]
            with self.assertRaisesRegex(AssertionError,
                                         "uncertified candidate-set change"):
                audit.audit(per_band=1,maps=audit.MAPS[:1])
        finally:
            selective_linker.MODULES[key]=original


if __name__=="__main__":
    unittest.main()
