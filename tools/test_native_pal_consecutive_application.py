#!/usr/bin/env python3
"""Static/fail-closed coverage for experimental varied PAL music/render harness."""
from __future__ import annotations

import hashlib
import unittest

import mixed_seven_frame_parity as seven
import native_pal_consecutive_application as application
import native_pal_consecutive_busiest as repeated


class ApplicationPALTests(unittest.TestCase):
    def setUp(self):
        self.exports={api:0x4123+0x20*i for i,api in enumerate(seven.OPS)}

    def test_exact_original_150_call_bodies_and_independent_frame_oracles(self):
        for display in (False,True):
            raw,halt,expected,geo=application.build_harness(
                self.exports,display=display)
            self.assertEqual(geo["source_frames"],24)
            self.assertEqual(geo["source_public_calls"],150)
            self.assertEqual(geo["calls_by_frame"],
                             [24 if i%8==0 else 8 if i%4==0 else 3
                              for i in range(24)])
            self.assertEqual(len(expected),48)
            self.assertLess(halt,application.EXPECT)
            self.assertLess(application.SUB+geo["source_body_bytes"],0xc000)
            self.assertEqual(geo["sid_irq_bytes"],
                             len(application.sequencer_irq()))
            self.assertEqual(geo["renderer_bytes"],
                             len(application.renderer()))
            self.assertEqual(geo["rendered_character_cells_per_frame"],64)
            self.assertEqual(geo["rendered_color_cells_per_frame"],16)
            expected_table=bytearray()
            carried=bytearray(48)
            for frame,addr in enumerate(geo["body_addresses"]):
                *_,math,oracle,count=application.extract_frame(
                    self.exports,frame,display)
                offset=addr-application.MAIN
                self.assertEqual(raw[offset:offset+len(math)],math)
                self.assertEqual(hashlib.sha256(math).hexdigest(),
                                 geo["body_sha256_by_frame"][frame])
                self.assertEqual(len(oracle),2*count)
                expected_table.extend(oracle)
                carried[:len(oracle)]=oracle
            self.assertEqual(expected,bytes(carried))
            expect_pos=application.EXPECT-application.MAIN
            self.assertEqual(raw[expect_pos:expect_pos+300],expected_table)
            self.assertEqual(geo["oracle_sha256"],
                             hashlib.sha256(expected_table).hexdigest())
            self.assertEqual(len(set(geo["body_addresses"])),24)

    def test_real_sid_register_and_vic_screen_writes_are_encoded(self):
        irq=application.sequencer_irq()
        self.assertTrue(irq.startswith(bytes((0x48,0x8a,0x48,0x98,0x48))))
        self.assertTrue(irq.endswith(bytes((0x68,0xa8,0x68,0xaa,0x68,0x40)))
                        or irq.count(bytes((0x68,0xa8,0x68,0xaa,0x68,0x40)))==1)
        for address in (0xd400,0xd401,0xd407,0xd408,0xd40e,0xd40f):
            self.assertIn(bytes((0x8d,))+application.word(address),irq)
        painter=application.renderer()
        for address in (0x0400,0x0428,0x0450,0x0478,0xd800):
            self.assertIn(bytes((0x9d,))+application.word(address),painter)
        self.assertIn(bytes((0xee,0x01,0x3a)),painter)

    def test_light_final_frame_can_finish_before_line90(self):
        self.assertEqual(application.varied_irq_events(23),0)
        self.assertEqual(application.varied_irq_events(24),0)
        self.assertEqual(application.varied_irq_events(25),1)
        for invalid in (-1,0,22,255,256,True,23.0,"23"):
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                application.varied_irq_events(invalid)
        for invalid_jobs in (0,23,25,True):
            with self.assertRaises(ValueError):
                application.varied_irq_events(23,invalid_jobs)

    def test_shared_monitor_reserve_parameter_rejects_synthetic_nops(self):
        for display in (False, True):
            raw, halt, oracle, layout = application.build_harness(
                self.exports, display=display)
            same = application.build_harness(
                self.exports, display=display, reserve_cpu_cycles=0)
            self.assertEqual((raw, halt, oracle, layout), same)
        for bad in (-2, 1, 256, True, False, 0.0, "0", None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                application.build_harness(
                    self.exports, display=True, reserve_cpu_cycles=bad)

    def test_invalid_source_set_or_display_rejected(self):
        for bad in ({},dict(list(self.exports.items())[:-1])):
            with self.assertRaises(ValueError):
                application.build_harness(bad,display=True)
        for bad_display in (1,0,None,"yes"):
            with self.assertRaises(ValueError):
                application.build_harness(self.exports,display=bad_display)

    def test_synthetic_control_is_not_silently_changed(self):
        for display in (False,True):
            baseline,halt,expected,geo=repeated.build_harness(
                self.exports,display=display)
            self.assertEqual(geo["body_bytes"],len(baseline)-(repeated.SUB-repeated.MAIN))
            self.assertEqual(len(expected),48)
            self.assertNotEqual(
                hashlib.sha256(baseline).digest(),
                hashlib.sha256(application.build_harness(
                    self.exports,display=display)[0]).digest())


if __name__=="__main__":
    unittest.main()
