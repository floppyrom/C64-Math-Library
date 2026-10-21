#!/usr/bin/env python3
"""No invented IRQ timings: static source checks and forged-evidence rejection."""
from __future__ import annotations

import copy
import unittest

import mixed_seven_frame_parity as seven
import native_pal_vic_cia_probe as cia
from native_pal_irq_sid_burst import (
    IRQ,IRQ_COUNT,FRAME_SET,LINES,PLANS,irq_handler,
    irq_harness,compare,
)


def fake(plan, frame, display, armed, line, wall=12000):
    return {
        "plan":plan,"frame":frame,"display_enabled":display,
        "raster_irq_enabled":armed,"raster_irq_line":line,
        "raster_irq_serviced":int(armed),
        "measured_cia_phi2_slots":wall+(220 if armed else 0),
        "qualified_prg_sha256":plan+"-"*30,
        "source_frame_inputs_sha256":str(frame)*64,
        "source_linked_calls":24,
        "captured_outputs_sha256":str(frame)*64,
    }


class NativeIRQSIDTests(unittest.TestCase):
    def setUp(self):
        self.entries={api:0x4123+0x20*i for i,api in enumerate(seven.OPS)}

    def test_real_raster_irq_handler_preserves_registers_and_acks_vic(self):
        handler=irq_handler()
        self.assertEqual(handler[:5],bytes((0x48,0x8a,0x48,0x98,0x48)))
        self.assertEqual(handler[-6:],bytes((0x68,0xa8,0x68,0xaa,0x68,0x40)))
        self.assertIn(bytes((0x8d,0x19,0xd0)),handler)
        self.assertIn(bytes((0xee,IRQ_COUNT & 255,IRQ_COUNT >> 8)),handler)
        for addr in (0xd400,0xd401,0xd404,0xd418):
            self.assertIn(bytes((0x8d,addr & 255,addr>>8)),handler)
        self.assertLess(len(handler),128)

    def test_identical_math_burst_and_only_one_byte_diff_for_irq_enable(self):
        for frame in FRAME_SET:
            for display in (False,True):
                with self.subTest(frame=frame,display=display):
                    control,stop0,oracle0,calls0=irq_harness(
                        self.entries,frame=frame,display=display,
                        irq_enabled=False,raster_line=90)
                    armed,stop1,oracle1,calls1=irq_harness(
                        self.entries,frame=frame,display=display,
                        irq_enabled=True,raster_line=90)
                    self.assertEqual((stop0,oracle0,calls0),(stop1,oracle1,calls1))
                    self.assertEqual(calls0,len([x for x in seven.scenario() if x[0]==frame]))
                    self.assertEqual(calls0,24)
                    self.assertEqual(len(control),len(armed))
                    self.assertIn(bytes((0xad,0x0d,0xdc,0xad,0x0d,0xdd,0x58)),armed)
                    diff=[i for i,(x,y) in enumerate(zip(control,armed)) if x!=y]
                    self.assertEqual(len(diff),1)
                    self.assertEqual((control[diff[0]],armed[diff[0]]),(0,1))
                    self.assertEqual(armed[IRQ-cia.HARNESS:],irq_handler())
                    self.assertLess(stop0,IRQ)
                    self.assertTrue(armed[stop0-cia.HARNESS:stop0-cia.HARNESS+3]
                                    == bytes((0x4c,stop0 & 255,stop0>>8)))
                    for api,address in self.entries.items():
                        self.assertIn(bytes((0x20,address & 255,address>>8)),armed)
                    self.assertEqual(
                        oracle1,
                        cia.harness(self.entries,frame=frame,display=display)[2])

    def test_invalid_irq_controls_are_rejected(self):
        for line in (0,256,-1,True,"90"):
            with self.subTest(line=line),self.assertRaises(ValueError):
                irq_harness(self.entries,frame=8,display=True,
                            irq_enabled=True,raster_line=line)
        with self.assertRaises(ValueError):
            irq_harness(self.entries,frame=8,display=True,irq_enabled=1)

    def test_pair_checker_rejects_missing_duplicate_and_corrupted_samples(self):
        plans=("fast31-stock-v2",)
        frames=(8,)
        lines=(90,)
        rows=[fake(plans[0],8,d,a,90) for d in (False,True) for a in (False,True)]
        summary=compare(rows,plans=plans,frames=frames,lines=lines)
        self.assertEqual(summary[plans[0]]["nominal_deadline_misses"],0)
        self.assertEqual(summary[plans[0]]["worst_irq_sid_added_slots"],220)
        with self.assertRaises(ValueError):
            compare(rows[:-1],plans=plans,frames=frames,lines=lines)
        with self.assertRaises(ValueError):
            compare(rows+[rows[0]],plans=plans,frames=frames,lines=lines)
        tampered=copy.deepcopy(rows)
        tampered[1]["captured_outputs_sha256"]="f"*64
        with self.assertRaises(AssertionError):
            compare(tampered,plans=plans,frames=frames,lines=lines)
        tampered=copy.deepcopy(rows)
        tampered[1]["raster_irq_serviced"]=0
        with self.assertRaises(AssertionError):
            compare(tampered,plans=plans,frames=frames,lines=lines)
        tampered=copy.deepcopy(rows)
        tampered[1]["measured_cia_phi2_slots"]=11800
        with self.assertRaises(AssertionError):
            compare(tampered,plans=plans,frames=frames,lines=lines)


if __name__=="__main__":
    unittest.main()
