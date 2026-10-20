#!/usr/bin/env python3
"""Fail-closed static probes; actual CIA readings require native pinned x64sc."""
from __future__ import annotations

import unittest

import mixed_seven_frame_parity as seven
from native_pal_vic_cia_probe import (FRAME, HARNESS, PAL_SLOTS, RESULT,
                                       busiest_calls, decode_elapsed,
                                       expected_byte, harness)


class NativePalVICCIATests(unittest.TestCase):
    def setUp(self):
        self.entries = {api: 0x4123 + i for i, api in enumerate(seven.OPS)}

    def test_real_synthetic_source_trace_is_encoded_unchanged(self):
        self.assertEqual(PAL_SLOTS, 19656)
        for frame in (0, 8, 16):
            with self.subTest(frame=frame):
                source = busiest_calls(frame)
                code, halt, expected, count = harness(self.entries, frame=frame)
                self.assertEqual(count, 24)
                self.assertEqual(count, len(source))
                self.assertEqual(len(expected), 2 * count)
                self.assertEqual(halt, HARNESS + len(code) - 3)
                self.assertLess(halt, 0x8000)
                self.assertTrue(code.endswith(bytes((0x4c, halt & 255, halt >> 8))))
                self.assertEqual(expected, bytes(
                    bit for _, _, api, x, y, n, *_ in source
                    for bit in expected_byte(api, x, y, n)))
                self.assertEqual(len([x for x in source if x[2] in seven.OPS]), count)
        self.assertEqual(RESULT, 0x3b00)

    def test_vic_on_and_off_change_only_display_control(self):
        on, h_on, out_on, count = harness(self.entries, frame=FRAME, display=True)
        off, h_off, out_off, count_off = harness(self.entries, frame=FRAME, display=False)
        self.assertEqual((h_on, out_on, count), (h_off, out_off, count_off))
        diff = [i for i, (a, b) in enumerate(zip(on, off)) if a != b]
        self.assertEqual(len(diff), 1)
        self.assertEqual((on[diff[0]], off[diff[0]]), (0x1b, 0x0b))
        for api, address in self.entries.items():
            jsr = bytes((0x20, address & 255, address >> 8))
            self.assertGreaterEqual(on.count(jsr), 1, api)

    def test_cia_32bit_decode_across_full_16bit_rollovers(self):
        for ticks in (0, 1, 100, 65534, 65535, 65536, 65537,
                      70000, 131072, 19656, 200000, 0xfffffffe):
            with self.subTest(ticks=ticks):
                a = (0xffff - (ticks & 0xffff)).to_bytes(2, 'little')
                b = (0xffff - (ticks >> 16)).to_bytes(2, 'little')
                self.assertEqual(decode_elapsed(a + b), ticks)
        with self.assertRaises(ValueError):
            decode_elapsed(b'\xff\xff')

    def test_reject_unqualified_frames_or_missing_exports(self):
        for frame in (-1, 24, '0', True):
            with self.subTest(frame=frame), self.assertRaises(ValueError):
                busiest_calls(frame)
        with self.assertRaises(ValueError):
            harness({**self.entries, 'MATH_INVALID': 0x5555})


if __name__ == '__main__':
    unittest.main()
