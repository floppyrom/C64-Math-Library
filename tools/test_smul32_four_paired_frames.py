#!/usr/bin/env python3
"""Four historical SMUL32 same-input source-linked math frame comparisons."""
import json
import unittest

from smul32_four_paired_frames import VARIANTS, compare, scenario


class Signed32FourWayFrames(unittest.TestCase):
    def test_four_variants_two_placements_and_full_abi(self):
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(code=code):
                report=compare(code,io,zp)
                self.assertEqual(report["paired_calls"],150)
                self.assertEqual(report["frames"],24)
                self.assertEqual(set(report["per_variant"]),set(VARIANTS))
                self.assertEqual(report["per_variant"]["link:compact-zerozp"]["zero_page_bytes"],0)
                for v,data in report["per_variant"].items():
                    self.assertGreater(data["mean_public_cycles"],0)
                    self.assertGreater(data["peak_frame_math_cycles"],0)
                    self.assertEqual(len(data["source_sha256"]),64)
                    self.assertGreaterEqual(data["main_ram_total_bytes"],
                                            data["code_span_bytes"])
                print("SMUL32_FOUR_SOURCE_PAIRED_FRAME",
                      json.dumps(report,sort_keys=True),flush=True)

    def test_frame_corpus_identity(self):
        self.assertEqual(len(scenario()),150)
        self.assertEqual(len({v[-1] for v in scenario()}),150)


if __name__=="__main__":
    unittest.main()
