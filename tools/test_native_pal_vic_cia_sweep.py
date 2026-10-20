#!/usr/bin/env python3
"""No hardware time is asserted by these sweep summarization unit tests."""
from __future__ import annotations

import copy
import unittest

from native_pal_vic_cia_sweep import (PAL_SLOTS, parse_frames,
                                      percentile95, summarize)


class NativePALSweepTests(unittest.TestCase):
    def test_explicit_frame_selector_preserves_exact_frame_order(self):
        self.assertEqual(parse_frames('all'), tuple(range(24)))
        self.assertEqual(parse_frames('0,4,8,12,16,20'), (0,4,8,12,16,20))
        self.assertEqual(parse_frames('23'), (23,))
        for bad in ('', '0,', ' 0', '0, 1', '00,0', '3,2', '0,0',
                    '24', '-1', '0.5', '2-5', 'all,0', '1,,2'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_frames(bad)

    def test_p95_nearest_rank_and_pal_bound(self):
        self.assertEqual(PAL_SLOTS, 19656)
        self.assertEqual(percentile95(list(range(1,25))), 23)
        self.assertEqual(percentile95([42]), 42)
        for x in ([],[-1],[1.0],[True]):
            with self.subTest(x=x), self.assertRaises(ValueError):
                percentile95(x)

    @staticmethod
    def sample(frame, display, cycles, *, sha='a'*64):
        return {'frame':frame, 'display_enabled':display,
                'measured_cia_phi2_slots':cycles,
                'captured_outputs_sha256':str(frame)*64,
                'source_frame_inputs_sha256':str(frame+1)*64,
                'qualified_prg_sha256':sha,
                'source_linked_calls':24 if frame%8==0 else 3}

    def test_misses_and_headroom_report_actual_native_bursts(self):
        rows=[self.sample(0,False,16174),self.sample(0,True,17244),
              self.sample(1,False,19350),self.sample(1,True,19700)]
        result=summarize(rows,frames=(0,1),profile='fast31')
        self.assertEqual(result['frames_measured'],2)
        self.assertEqual(result['native_calls_measured_per_display'],27)
        self.assertEqual(result['peak_display_on_frame'],1)
        self.assertEqual(result['peak_display_on_native_slots'],19700)
        self.assertEqual(result['nominal_pal_deadline_misses'],1)
        self.assertEqual(result['worst_nominal_headroom_slots'],-44)
        self.assertEqual(result['p95_display_on_native_slots'],19700)
        self.assertEqual(result['per_frame'][0]['display_vic_overhead_slots'],1070)
        self.assertFalse(result['per_frame'][0]['nominal_deadline_missed'])

    def test_refuse_forged_pairs_and_incomplete_evidence(self):
        rows=[self.sample(0,False,16174),self.sample(0,True,17244)]
        with self.assertRaises(ValueError):
            summarize(rows[:1],frames=(0,),profile='fast31')
        with self.assertRaises(ValueError):
            summarize(rows+[rows[0]],frames=(0,),profile='fast31')
        with self.assertRaises(ValueError):
            summarize(rows,frames=(0,),profile='unknown')
        forged=copy.deepcopy(rows)
        forged[1]['captured_outputs_sha256']='f'*64
        with self.assertRaises(AssertionError):
            summarize(forged,frames=(0,),profile='fast31')
        forged=copy.deepcopy(rows)
        forged[1]['qualified_prg_sha256']='f'*64
        with self.assertRaises(AssertionError):
            summarize(forged,frames=(0,),profile='fast31')
        forged=copy.deepcopy(rows)
        forged[1]['measured_cia_phi2_slots']=16000
        with self.assertRaises(AssertionError):
            summarize(forged,frames=(0,),profile='fast31')
        forged=copy.deepcopy(rows)
        forged[1]['measured_cia_phi2_slots']=True
        with self.assertRaises(ValueError):
            summarize(forged,frames=(0,),profile='fast31')


if __name__=='__main__':
    unittest.main()
