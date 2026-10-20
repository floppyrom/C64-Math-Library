#!/usr/bin/env python3
"""Fail-closed nominal PAL headroom arithmetic, not a real app-timing claim."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import unittest
import native_pal_reserved_workload as gate


def fixture():
    sources=[]; by={}
    for i,label in enumerate(gate.LABELS):
        peak=(19883,17618,17580)[i]
        sha=str(i+1)*64
        sources.append({'label':label,'linked_prg_sha256':sha,
                        'linked_ram_bytes':(8957,9213,8957)[i],
                        'zero_page_bytes':31,
                        'variants':{api:label for api in gate.OPS}})
        frames=[]
        for frame in range(24):
            slots=peak if frame==8 else 2000
            n=24 if frame in (0,8) else 8 if frame in (4,12,16,20) else 3
            if frame==23: n+=16
            frames.append({'frame':frame,'display_on_slots':slots,
                           'display_off_slots':slots-100,
                           'visible_vic_overhead_slots':100,
                           'nominal_frame_headroom_slots':gate.PAL-slots,
                           'source_linked_calls':n,'output_sha256':str(frame%10)*64})
        calls=sum(f['source_linked_calls'] for f in frames)
        assert calls==150,calls
        by[label]={'prg_sha256':sha,'per_frame':frames,
                   'total_public_calls_per_display':150,
                   'peak_visible_slots':peak,'peak_frame_index':8,
                   'worst_nominal_headroom_slots':gate.PAL-peak,
                   'nominal_deadline_overruns':int(peak>gate.PAL)}
    return {'schema':gate.EXPECTED_SCHEMA,
            'source_report_basis':gate.EXPECTED_BASIS,
            'native_emulator':'pinned-x64sc-r46284',
            'nominal_pal_slots':gate.PAL,
            'native_public_calls_per_display':450,
            'real_application_frame_certified':False,
            'consecutive_50hz_frames_measured':False,
            'sid_irq_reu_application_work_measured':False,
            'sources':sources,'by_plan':by}


class ReservedPALWorkloadTests(unittest.TestCase):
    def test_select_exact_peak_and_memory(self):
        r=fixture()
        x=gate.select(r,reserve_nonmath_slots=2050,max_ram=8957,max_zp=31,require_headroom=True)
        self.assertEqual(x['selected_plan'],'fast31-uv2-s65536')
        self.assertEqual(x['eligible_plan_count'],1)
        self.assertEqual([p for p in x['plans'] if p['plan']=='fast31-uv2-s65536'][0]
                         ['estimated_remaining_slots_after_reservation'],26)
        self.assertFalse(x['continuous_50hz_application_certified'])
        with self.assertRaises(ValueError):
            gate.select(r,reserve_nonmath_slots=2077,max_ram=10000,max_zp=31,require_headroom=True)
        self.assertIsNone(gate.select(r,reserve_nonmath_slots=0,max_ram=8957,max_zp=0)['selected_plan'])

    def test_reject_incomplete_corrupted_source_and_timing_evidence(self):
        r=fixture()
        changes=(
            lambda c:c['by_plan'].pop('fast31-stock-v2'),
            lambda c:c['sources'][0].__setitem__('linked_prg_sha256','f'*64),
            lambda c:c['by_plan']['fast31-uv2-s65536']['per_frame'][8].__setitem__('display_on_slots',17000),
            lambda c:c['by_plan']['fast31-uv2-s65536']['per_frame'][8].__setitem__('output_sha256','f'*64),
            lambda c:c['by_plan']['fast31-u65536-s65536']['per_frame'].pop(),
            lambda c:c.__setitem__('consecutive_50hz_frames_measured',True),
        )
        for mutation in changes:
            c=copy.deepcopy(r);mutation(c)
            with self.subTest(mutation=repr(mutation)),self.assertRaises(ValueError):
                gate.verified_plans(c)

    def test_refuse_negative_or_boolean_budgets(self):
        r=fixture()
        for kwargs in ({'reserve_nonmath_slots':-1,'max_ram':20000,'max_zp':31},
                       {'reserve_nonmath_slots':True,'max_ram':20000,'max_zp':31},
                       {'reserve_nonmath_slots':0,'max_ram':-1,'max_zp':31}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                gate.select(r,**kwargs)

    def test_real_ci_native_report_when_explicitly_supplied(self):
        import os
        file=os.environ.get('D65536_NATIVE_REPORT')
        if not file:
            self.skipTest('Optional actual pinned x64sc JSON artifact not supplied')
        r=json.loads(Path(file).read_text(encoding='utf-8'))
        self.assertEqual(gate.select(r,reserve_nonmath_slots=2050,max_ram=8957,
                                     max_zp=31,require_headroom=True)['selected_plan'],
                         'fast31-uv2-s65536')


if __name__ == '__main__':
    unittest.main()
