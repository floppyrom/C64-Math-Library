#!/usr/bin/env python3
"""Legacy source validation: matched frame/ABI corpus across all five donors."""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from export_legacy_signed_frame_trace import PROFILES, WIDE_OPS, export
from frame_cycle_budget import load_trace, score

class HistoricalWideFrameTests(unittest.TestCase):
    def test_all_five_initialized_resident_public_calls_are_matched(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            datasets=[]
            for profile in PROFILES:
                file=root/(profile+".csv")
                result=export(profile,file,frames=8)
                rows, metadata=load_trace(file)
                self.assertEqual(result["calls"],50)
                self.assertEqual(result["peak_frame_math_cycles"],
                                 score(rows,metadata,frame_count=8)["peak_frame_math_cycles"])
                self.assertEqual({row.operation for row in rows},
                                 {"MATH_"+op for op in WIDE_OPS})
                self.assertEqual({row.variant for row in rows},{"resident:"+profile})
                info=json.loads(file.with_suffix(".manifest.json").read_text())
                self.assertTrue(info["initialized_by_math_init"])
                self.assertTrue(info["synthetic_not_real_game"])
                self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),
                                 info["trace_sha256"])
                self.assertEqual(info["calls"],50)
                self.assertTrue(info["resident_prg_sha256"])
                if profile.startswith("v3_") or profile.startswith("v4_"):
                    self.assertTrue(info["reu"]["sha256"])
                else:
                    self.assertIsNone(info["reu"])
                datasets.append((profile,rows,metadata))
            reference=datasets[0][1]
            for profile,rows,metadata in datasets[1:]:
                # Actual per-call physical placement can differ between
                # historical profiles. Preserve it as provenance; compare
                # only sequence/input identities and score each separately.
                self.assertEqual([c.key for c in reference],
                                 [c.key for c in rows], profile)
                self.assertGreater(score(rows,metadata,frame_count=8)
                                   ["peak_frame_math_cycles"],0)

    def test_reject_invalid_profile_or_frame_count(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"bad.csv"
            with self.assertRaisesRegex(ValueError,"Unknown historical profile"):
                export("unknown",out,frames=2)
            with self.assertRaisesRegex(ValueError,"frames must be"):
                export(PROFILES[0],out,frames=0)

if __name__=="__main__":
    unittest.main()
