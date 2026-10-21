#!/usr/bin/env python3
"""Turbo16 source-backed four-plane lookup payload + real REU SWAP CPU proof."""
import hashlib
import json
import unittest
from unittest.mock import patch

import reu_turbo16_source_tables as tables
import reu_turbo16_swap_experiment as swap


class Turbo16SourceIntegratedSwapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = swap.cpu_model_proof()

    def test_no_frozen_prg_build_dependency_and_same_real_math(self):
        p = self.record
        self.assertIsNone(p["test_only_table_fixture"])
        self.assertIn("no resident PRG required", p["lookup_table_provenance"])
        self.assertEqual(p["arithmetic_calls"], 224)
        self.assertEqual(p["test_only_table_bytes"], 2048)
        self.assertEqual(p["test_only_table_planes"], 4)
        self.assertFalse(p["native_vice_qualified"])
        self.assertFalse(p["source_linker_reu_variant_available"])
        self.assertFalse(p["independent_quarter_square_tables_implemented"])
        self.assertEqual(len(p["batch_evidence"]),2)
        self.assertTrue(all(x["zero_page_exact_restoration"]
                            for x in p["batch_evidence"]))
        self.assertTrue(all(x["reu_overlay_persisted_with_live_smc_operands"]
                            for x in p["batch_evidence"]))
        _, chunks = tables.materialize()
        for name, sha in p["source_table_hashes"].items():
            self.assertEqual(sha, hashlib.sha256(chunks[name]).hexdigest())

    def test_source_provenance_tamper_fails_closed(self):
        with patch.object(tables,"materialize",
                          side_effect=tables.TableError("SHA source changed")):
            with self.assertRaisesRegex(tables.TableError,"source changed"):
                swap.cpu_model_proof()

    def test_second_physical_map_uses_identical_lookup_bytes(self):
        p=swap.cpu_model_proof(zp=0x20,io=0xc080,table=0x5000,
                               api=0x4000,ctrl=0x4a00,state=0xc040,bank=6)
        self.assertEqual(p["arithmetic_calls"], 224)
        self.assertEqual(p["source_table_hashes"],self.record["source_table_hashes"])
        self.assertEqual(p["result_digest_sha256"],self.record["result_digest_sha256"])

    def test_source_reports_are_deterministic(self):
        self.assertEqual(json.dumps(self.record["source_table_hashes"],sort_keys=True),
                         json.dumps(swap.cpu_model_proof()["source_table_hashes"],sort_keys=True))


if __name__=="__main__":
    unittest.main()
