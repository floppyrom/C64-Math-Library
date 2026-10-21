#!/usr/bin/env python3
"""Source-built Turbo16 REU DMA swap, batch, zero-page and arithmetic tests."""
import unittest
from unittest.mock import patch
import reu_turbo16_swap_experiment as exp

class Turbo16ModularSwapTests(unittest.TestCase):
    def test_default_and_relocated_dma_lifecycle_and_math(self):
        for opts in ({},dict(zp=0x20,io=0xc080,table=0x5000,
                             api=0x4000,ctrl=0x4a00,state=0xc040,bank=6)):
            with self.subTest(opts=opts):
                d=exp.cpu_model_proof(**opts)
                self.assertEqual(d["arithmetic_calls"],224)
                self.assertEqual(d["proof_status"],
                                 "CPU_MODEL_FULL_ARITHMETIC_AND_DMA_SWAP_TWO_BATCHES")
                self.assertFalse(d["native_vice_qualified"])
                self.assertFalse(d["source_linker_reu_variant_available"])
                self.assertFalse(d["independent_quarter_square_tables_implemented"])
                self.assertTrue(d["result_digest_sha256"])
                self.assertEqual(len(d["batch_evidence"]),2)
                for b in d["batch_evidence"]:
                    self.assertEqual(b["calls"],112)
                    self.assertTrue(b["zero_page_exact_restoration"])
                    self.assertTrue(b["reu_overlay_persisted_with_live_smc_operands"])
                    self.assertTrue(b["nested_begin_rejected"])
                    self.assertGreater(b["begin_model_cycles"],0)
                    self.assertGreater(b["end_model_cycles"],0)
                self.assertEqual(
                    d["entrypoints"]["begin"],
                    "$%04X"%opts.get("ctrl",0x3a00))

    def test_guard_invalid_resource_placements_and_missing_reu_tier(self):
        for kwargs in (
            {"zp":0x86},
            {"ctrl":0xc000},
            {"state":0xc004},
            {"table":0xc000},
            {"api":0xd000},
            {"bank":8},
            {"bank":256,"reu_bytes":16777216},
            {"reu_bytes":65536},
            {"ctrl":0x3a01},
            {"state":0xdfff},
        ):
            with self.subTest(kwargs=kwargs),self.assertRaises(
                (exp.SwapError,exp.fragment.FragmentError)):
                exp.assemble(**kwargs)

    def test_tamper_source_blocks_build(self):
        with patch.object(exp.fragment,"locked_source",
                          side_effect=exp.fragment.FragmentError("tampered source")):
            with self.assertRaisesRegex(exp.fragment.FragmentError,
                                        "tampered source"):
                exp.assemble()

    def test_proof_replay_is_deterministic(self):
        left=exp.cpu_model_proof()
        right=exp.cpu_model_proof()
        self.assertEqual(left["result_digest_sha256"],right["result_digest_sha256"])
        self.assertEqual(left["batch_evidence"],right["batch_evidence"])

if __name__=="__main__":
    unittest.main()
