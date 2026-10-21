#!/usr/bin/env python3
"""Static regression and fail-closed summaries of native extra-work experiments."""
from __future__ import annotations

import copy
import unittest

import mixed_seven_frame_parity as seven
import native_pal_consecutive_busiest as baseline
import native_pal_consecutive_reserve as reserve


class ReservePALTests(unittest.TestCase):
    def setUp(self):
        self.entries={api:0x4123+0x20*i for i,api in enumerate(seven.OPS)}

    def test_exact_original_call_body_plus_two_cycle_nops(self):
        for display in (False,True):
            original,halt,oracle,old=baseline.build_harness(
                self.entries,display=display)
            modified,halt2,oracle2,new=baseline.build_harness(
                self.entries,display=display,reserve_cpu_cycles=512)
            offset=baseline.SUB-baseline.MAIN
            self.assertEqual(halt,halt2)
            self.assertEqual(oracle,oracle2)
            self.assertEqual(original[:offset],modified[:offset])
            self.assertEqual(
                modified[offset:offset+old["body_bytes"]-1],
                original[offset:-1])
            self.assertEqual(
                modified[offset+old["body_bytes"]-1:
                         offset+old["body_bytes"]-1+256],
                b"\xea"*256)
            self.assertEqual(modified[-1],0x60)
            self.assertEqual(new["body_bytes"]-old["body_bytes"],256)
            self.assertEqual(old["injected_nonmath_nop_cpu_cycles"],0)
            self.assertEqual(new["injected_nonmath_nop_cpu_cycles"],512)

    def test_budget_rejects_odd_and_oversized_nominal_instruction_cycles(self):
        for value in (-2,1,3,2049,2050,0.5,True,"512"):
            with self.subTest(value=value),self.assertRaises(ValueError):
                baseline.build_harness(self.entries,display=True,
                                       reserve_cpu_cycles=value)
        for value in ("","256","512,0","0,0","0,256,256","0,1",
                      "0,2050","0, 256","0,0x100"):
            with self.subTest(value=value),self.assertRaises(ValueError):
                reserve.parse_reserves(value)
        self.assertEqual(reserve.parse_reserves("0,256,512"),
                         (0,256,512))
        self.assertEqual(reserve.parse_reserves("0"),(0,))

    @staticmethod
    def fake(cycles,late=False):
        step=19656
        elapsed=step*24- (1200 if not late else -200)
        records=[{"deadline_margin_slots":1200,
                  "nominal_deadline_missed":False} for _ in range(24)]
        if late:
            records[-1]={"deadline_margin_slots":-200,
                         "nominal_deadline_missed":True}
        return {
            "plan":"fast31-uv2-s65536",
            "display_enabled":True,
            "injected_nonmath_nop_cpu_cycles":cycles,
            "qualified_prg_sha256":"a"*64,
            "source_frame_inputs_sha256":"b"*64,
            "public_output_sha256":"c"*64,
            "total_public_calls":576,
            "frame_count":24,
            "public_output_error_count":0,
            "observed_raster_irq_events":24+(1 if late else 0),
            "extra_raster_irq_events_vs_completed_work_items":int(late),
            "nominal_deadline_misses":int(late),
            "last_completed_elapsed_slots":elapsed,
            "geometry":{"injected_nonmath_nop_cpu_cycles":cycles},
            "records":records
        }

    def test_capture_genuinely_timed_margin_and_first_failed_reserve(self):
        rows=[self.fake(0),self.fake(512),self.fake(1024,True)]
        summary=reserve.rank(rows,(0,512,1024),
                             "fast31-uv2-s65536",True)
        self.assertEqual(summary["largest_tested_passing_nonmath_nop_cpu_reserve"],
                         512)
        self.assertEqual(summary["first_tested_failing_nonmath_nop_cpu_reserve"],
                         1024)
        self.assertEqual(summary["level_results"][0]["last_deadline_margin_slots"],
                         1200)
        with self.assertRaises(AssertionError):
            reserve.rank(rows[:-1],(0,512,1024),
                         "fast31-uv2-s65536",True)
        forged=copy.deepcopy(rows)
        forged[1]["public_output_sha256"]="0"*64
        with self.assertRaises(AssertionError):
            reserve.rank(forged,(0,512,1024),
                         "fast31-uv2-s65536",True)
        forged=copy.deepcopy(rows)
        forged[1]["geometry"]["injected_nonmath_nop_cpu_cycles"]=0
        with self.assertRaises(AssertionError):
            reserve.rank(forged,(0,512,1024),
                         "fast31-uv2-s65536",True)


if __name__=="__main__":
    unittest.main()
