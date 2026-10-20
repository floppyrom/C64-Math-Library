#!/usr/bin/env python3
"""Static source provenance and boundary-case setup for native r46284 tests."""
from __future__ import annotations
import hashlib
import unittest

import native_research_d65536 as native
import research_d65536_hybrid as research


class NativeD65536ResearchTests(unittest.TestCase):
    def test_native_cases_include_exact_worst_frame8_operand(self):
        for signed_mode in (False,True):
            with self.subTest(signed=signed_mode):
                cases=native.inputs(signed_mode)
                self.assertEqual(len(cases),96)
                self.assertEqual(cases[0],(0x80000001,0x10000))
                self.assertIn((0x80000001,0),cases)
                self.assertIn((0x80000001,0xffff0000),cases)
                self.assertEqual(native.exact_target()[0][3:5],cases[0])

    def test_four_native_source_images_do_not_overlap_monitor_harness(self):
        rows=native.source_images()
        self.assertEqual(len(rows),4)
        signatures=[]
        for mode,variant,binary,entry in rows:
            self.assertEqual(int.from_bytes(binary[:2],"little"),native.CODE)
            self.assertLess(native.CODE+len(binary)-2,native.native_probe.HARNESS)
            self.assertTrue(native.CODE<=entry<native.CODE+len(binary)-2)
            signatures.append((mode,variant,hashlib.sha256(binary).hexdigest()))
        self.assertEqual(len({sha for _,_,sha in signatures}),4)
        self.assertEqual(rows[1][3],rows[0][3])
        self.assertEqual(rows[3][3],rows[2][3]+96)
        self.assertEqual(len(rows[1][2])-len(rows[0][2]),96)
        self.assertEqual(len(rows[3][2])-len(rows[2][2]),96)


if __name__=="__main__":
    unittest.main()
