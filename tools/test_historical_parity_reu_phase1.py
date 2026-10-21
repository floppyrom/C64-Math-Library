#!/usr/bin/env python3
"""Safety and provenance regressions for the first parity/REU engineering gate."""
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import historical_parity_triage as triage
import reu_selective_contract as reu


class HistoricalParityTriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = triage.report()

    def test_full_public_inventory_is_not_a_false_parity_certificate(self):
        r = self.result
        self.assertEqual(r["public_operation_count"], 56)
        self.assertEqual(len(r["operation_results"]), 56)
        self.assertEqual(r["identical_case_across_five_historical_profiles"], 11)
        self.assertEqual(r["identical_case_across_historical_and_selective"], 0)
        self.assertEqual(r["qualified_full_speed_parity_apis"], 0)
        self.assertEqual(r["status"], "SOURCE_INVENTORY_ONLY_NOT_SPEED_PARITY")
        for op, item in r["operation_results"].items():
            self.assertFalse(item["performance_parity_certified"], op)
            self.assertGreater(len(item["selective_candidates"]), 0)
            self.assertTrue(item["historical_published_leader"]["source_sha256"])

    def test_missing_historical_extrema_stay_explicitly_unknown(self):
        # The published UMUL8 donor has a mean but no min/max observations.
        # Do not substitute 0 or derive extrema from an unrelated corpus.
        prior = self.result["operation_results"]["MATH_UMUL8"]["historical_published_leader"]
        self.assertGreater(prior["mean_cycles"], 0)
        self.assertIsNone(prior["min_cycles"])
        self.assertIsNone(prior["max_cycles"])

    def test_unsigned_five_profile_inputs_are_identical_only_within_legacy(self):
        same = [r for r in self.result["operation_results"].values()
                if r["historical_five_profile_same_input"] is not None]
        self.assertEqual(len(same), 11)
        for item in same:
            common = item["historical_five_profile_same_input"]
            self.assertTrue(common["cross_profile_same_input"])
            self.assertFalse(common["cross_selective_same_input"])
            self.assertGreater(common["cases"], 0)

    def test_generated_report_is_deterministic(self):
        self.assertEqual(json.dumps(triage.report(), sort_keys=True),
                         json.dumps(self.result, sort_keys=True))

    def test_invalid_historical_source_hash_cannot_be_certified(self):
        with patch.object(triage, "source_hash", return_value="f" * 64):
            with self.assertRaisesRegex(triage.ParityTriageError,
                                        "source hash drift"):
                triage.report()


class NativeREUContractsPhaseOneTests(unittest.TestCase):
    def test_all_available_lifecycle_symbols_at_correct_hardware_tiers(self):
        for profile, families in (
            ("v3_reu_512k", ("UMUL16", "UMUL32")),
            ("v4_reu_16m", ("UMUL16", "UMUL32", "QS16"))
        ):
            for family in families:
                with self.subTest(profile=profile, family=family):
                    r = reu.plan(profile, family)
                    self.assertEqual(len(r["lifecycle_reference_entries"]), 3)
                    self.assertEqual(r["zero_page_overlay"]["exclusive_bytes"],
                                     {"UMUL16":122,"UMUL32":135,"QS16":16}[family])
                    self.assertFalse(r["native_reu_backend_available"])
                    self.assertFalse(r["may_link_legacy_resident_into_stock_prg"])
                    self.assertTrue(r["required_proofs"])
        with self.assertRaisesRegex(reu.REUContractError, "unavailable"):
            reu.plan("v3_reu_512k", "QS16")

    def test_overlay_must_not_overwrite_stock_or_reserved_zp(self):
        fake = {
            "target":"c64",
            "resource_use":{"zero_page_bytes":4},
            "memory_map":{
                "zp_start":"$40",
                "user_zp_reserved":[
                    {"name":"music_irq","start":"$0A","end":"$1F"}
                ],
            },
        }
        r16 = reu.plan("v3_reu_512k","UMUL16",stock_manifest=fake)
        self.assertFalse(r16["compatible_with_supplied_zp_placement"])
        self.assertTrue(any(c["owner"]=="installed_stock_math"
                            for c in r16["collision_risks_in_supplied_stock_manifest"]))
        r32 = reu.plan("v3_reu_512k","UMUL32",stock_manifest=fake)
        self.assertFalse(r32["compatible_with_supplied_zp_placement"])
        self.assertTrue(any(c["owner"]=="music_irq"
                            for c in r32["collision_risks_in_supplied_stock_manifest"]))
        safe = copy.deepcopy(fake)
        safe["resource_use"]["zero_page_bytes"] = 0
        safe["memory_map"]["zp_start"] = None
        safe["memory_map"]["user_zp_reserved"] = []
        empty = reu.plan("v3_reu_512k","UMUL16",stock_manifest=safe)
        self.assertTrue(empty["compatible_with_supplied_zp_placement"])
        self.assertFalse(empty["native_reu_backend_available"])
        qs = reu.plan("v4_reu_16m","QS16",stock_manifest=safe)
        self.assertFalse(qs["compatible_with_supplied_zp_placement"])

    def test_bad_zp_locations_fail_without_native_backend(self):
        fake = {
            "target":"c64",
            "resource_use":{"zero_page_bytes":8},
            "memory_map":{"zp_start":"$FC","user_zp_reserved":[]},
        }
        with self.assertRaisesRegex(reu.REUContractError,"outside zero page"):
            reu.plan("v3_reu_512k","UMUL16",stock_manifest=fake)
        fake["target"]="1581"
        with self.assertRaisesRegex(reu.REUContractError,"stock C64"):
            reu.plan("v3_reu_512k","UMUL16",stock_manifest=fake)

    def test_invalid_or_alias_lifecycle_fails_closed(self):
        original = reu.reference_symbols
        def broken(profile, root=reu.ROOT):
            names = original(profile, root)
            names["MATH_REU_UMUL16_END"] = names["MATH_REU_UMUL16"]
            return names
        with patch.object(reu, "reference_symbols", side_effect=broken):
            with self.assertRaisesRegex(reu.REUContractError,
                                        "Invalid BEGIN"):
                reu.plan("v3_reu_512k","UMUL16")

    def test_reu_report_reproducible(self):
        a=reu.plan("v4_reu_16m","UMUL32")
        self.assertEqual(json.dumps(a,sort_keys=True),
                         json.dumps(reu.plan("v4_reu_16m","UMUL32"),
                                    sort_keys=True))


if __name__=="__main__":
    unittest.main()
