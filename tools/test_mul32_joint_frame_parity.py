#!/usr/bin/env python3
"""Both-source multiplication RAM/ZP and same-input busiest-frame proof."""
from __future__ import annotations

import json
import unittest
from mul32_joint_frame_parity import OPTIONS, compare, scenario


class Joint32MulFrameTests(unittest.TestCase):
    def test_four_source_plans_identical_mixed_full64_24_frames(self):
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(code=code):
                report=compare(code,io,zp)
                self.assertEqual(report["paired_calls"],150)
                self.assertEqual(report["frames"],24)
                self.assertEqual(set(report["per_option"]),set(OPTIONS))
                choices=report["per_option"]
                self.assertEqual(choices["fast31-shared"]["linked_source_count"],1)
                self.assertEqual(choices["fast31-independent"]["linked_source_count"],2)
                self.assertEqual(choices["unified375"]["linked_source_count"],1)
                self.assertEqual(choices["compact-pair"]["linked_source_count"],2)
                self.assertLess(choices["fast31-shared"]["main_ram_total_bytes"],
                                choices["fast31-independent"]["main_ram_total_bytes"])
                self.assertEqual(choices["fast31-shared"]["zero_page_bytes"],31)
                self.assertEqual(choices["unified375"]["zero_page_bytes"],0)
                for choice, data in choices.items():
                    self.assertGreater(data["mean_call_cycles"],0)
                    self.assertGreater(data["peak_frame_math_cycles"],0)
                    self.assertEqual(len(data["linked_prg_sha256"]),64)
                print("MUL32_TWO_API_SHARED_VS_SEPARATE",
                      json.dumps(report,sort_keys=True),flush=True)

    def test_scenario_all_caller_states_unique(self):
        cases=scenario()
        self.assertEqual(len(cases),150)
        self.assertEqual(len({q[-1] for q in cases}),150)


if __name__=="__main__":
    unittest.main()
