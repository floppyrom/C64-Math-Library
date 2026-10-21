#!/usr/bin/env python3
"""Static tests must not mislabel timed native samples as source-model proof."""
from __future__ import annotations

import unittest

import mixed_seven_frame_parity as seven
import native_pal_irq_sid_burst as irq
import native_pal_consecutive_busiest as burst
import native_pal_vic_cia_probe as cia


class ConsecutivePALTests(unittest.TestCase):
    def setUp(self):
        self.entries={api:0x4123+0x20*i for i,api in enumerate(seven.OPS)}

    def test_24_frame_bursts_have_exact_original_public_math_source(self):
        for display in (False,True):
            with self.subTest(display=display):
                code,halt,expected,geometry=burst.build_harness(
                    self.entries,display=display)
                original,_,first_expected,calls=irq.irq_harness(
                    self.entries,frame=8,display=display,
                    irq_enabled=True,raster_line=90)
                start=original.index(irq.START,original.index(irq.SYNCH))
                stop=original.rfind(bytes((0xa9,0,0x8d,0x0e,0xdc)))
                original_body=original[start+10:stop]+b'\x60'
                self.assertEqual(code[burst.SUB-burst.MAIN:],original_body)
                self.assertEqual(expected,first_expected)
                self.assertEqual(calls,24)
                self.assertEqual(len(expected),48)
                self.assertEqual(geometry["body_start"],burst.SUB)
                self.assertEqual(geometry["body_bytes"],len(original_body))
                self.assertEqual(code[burst.HANDLER-burst.MAIN:
                                      burst.HANDLER-burst.MAIN+len(irq.irq_handler())],
                                 irq.irq_handler())
                self.assertLess(halt,burst.HANDLER)
                self.assertEqual(code[halt-burst.MAIN:halt-burst.MAIN+3],
                                 bytes((0x4c,halt&255,halt>>8)))
                self.assertEqual(code[geometry["main_loop"]-burst.MAIN:
                                      geometry["main_loop"]-burst.MAIN+2],
                                 bytes((0x2c,0x11)))
                for op,address in self.entries.items():
                    self.assertIn(bytes((0x20,address&255,address>>8)),original_body,op)
                self.assertIn(bytes((0xad,0x04,0xdc,0x9d,0x00,0x3c)),code)
                self.assertEqual(burst.PAL,19656)
                self.assertEqual(burst.RUNS,24)
                self.assertEqual(burst.FRAME,8)

    def test_display_control_changes_only_one_vic_immediate_byte(self):
        on,halt0,expected0,geometry0=burst.build_harness(
            self.entries,display=True)
        off,halt1,expected1,geometry1=burst.build_harness(
            self.entries,display=False)
        self.assertEqual((halt0,expected0,geometry0),(halt1,expected1,geometry1))
        self.assertEqual(len(on),len(off))
        differences=[i for i,(a,b) in enumerate(zip(on,off)) if a!=b]
        self.assertEqual(len(differences),1)
        self.assertEqual((on[differences[0]],off[differences[0]]),(0x1b,0x0b))

    def test_single_timer_start_and_per_frame_chained_samples(self):
        program,halt,expected,geometry=burst.build_harness(
            self.entries,display=True)
        init=program[:burst.HANDLER-burst.MAIN]
        # No software reload in the repeated math-body execution;
        # only a guarded first-iteration start of CIA1 A/B.
        self.assertEqual(init.count(irq.START),1)
        self.assertEqual(init.count(bytes((0xa9,0x11,0x8d,0x0e,0xdc))),1)
        for i in range(4):
            self.assertIn(bytes((0xad,0x04+i,0xdc,
                                 0x9d,(burst.DATA+i)&255,(burst.DATA+i)>>8)),init)
        self.assertIn(bytes((0xbd,burst.OUTPUT&255,burst.OUTPUT>>8)),init)
        self.assertIn(bytes((0xdd,burst.EXPECT&255,burst.EXPECT>>8)),init)
        self.assertIn(bytes((0xee,burst.ERROR_COUNTER&255,burst.ERROR_COUNTER>>8)),init)
        # Consecutive full 32-bit counter decode must survive A rollover.
        ticks=(19656,65536,65537,24*19656)
        for t in ticks:
            with self.subTest(t=t):
                counter=(0xffffffff-t).to_bytes(4,'little')
                self.assertEqual(cia.decode_elapsed(counter),t)

    def test_overloaded_bursts_report_skipped_raster_events_instead_of_failing(self):
        self.assertEqual(burst.extra_irq_events(24),0)
        self.assertEqual(burst.extra_irq_events(47),23)
        self.assertEqual(burst.extra_irq_events(48),24)
        for bad in (0,23,255,True,24.0,"47"):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                burst.extra_irq_events(bad)

    def test_reject_invalid_source_entries_and_display_controls(self):
        for bad in (0,1,None,"True"):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                burst.build_harness(self.entries,display=bad)
        with self.assertRaises(ValueError):
            burst.build_harness({"MATH_UMUL32":0x4123},display=True)
        with self.assertRaises(ValueError):
            burst.read_monitor("",b"",self.entries,__import__("pathlib").Path("."),"x",
                               19001,display=True)


if __name__=="__main__":
    unittest.main()
