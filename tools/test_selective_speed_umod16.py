#!/usr/bin/env python3
"""Public UMOD16 speed selection and comparable-cycle source regression."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import math_builder
import selective_linker as linker
import selective_speed_umod16 as speed

class UMOD16SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, ram=1100, zp=2):
        return math_builder.create_plan(self.index,
            ['UMOD16'], objective='speed', zp_budget=zp, ram_budget=ram)

    def test_two_map_exact_public_cycle_benchmark(self):
        for code, io, zp in ((0x8000, 0xc000, 0x50),
                             (0x7123, 0xc040, 0x70)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as td:
                man = linker.build(self.plan(), Path(td), memory={
                    'code_base': code, 'math_io': io, 'zp_base': zp,
                    'scratch_base': io+32})
                measure = man['cycle_model_benchmark']
                self.assertEqual(measure['cases'], 384)
                self.assertEqual(measure['corpus_sha256'], speed.CORPUS_SHA256)
                self.assertEqual(set(measure['mean_cycles']), speed.EXPECTED)
                self.assertTrue(measure['cpu_model_only'])
                self.assertEqual(set(measure['donor_sha256']), speed.EXPECTED)
                self.assertLess(measure['mean_cycles']['link:direct-zerozp'],
                                measure['mean_cycles']['link:biased'])
                self.assertEqual(man['operations'][0]['variant'], 'link:direct-zerozp')
                print('UMOD16 PUBLIC SPEED', hex(code), measure['mean_cycles'], flush=True)

    def test_budget_fallback_and_unfeasible(self):
        with tempfile.TemporaryDirectory() as td:
            for size, zp, expected in ((294, 2, 'link:biased'),
                                       (600, 2, 'link:biased'),
                                       (1010, 0, 'link:direct-zerozp'),
                                       (1010, 2, 'link:direct-zerozp')):
                man = linker.build(self.plan(size, zp), Path(td)/('m%d_%d' % (size,zp)))
                self.assertEqual(man['operations'][0]['variant'], expected)
                self.assertLessEqual(man['resource_use']['main_ram_total_bytes'], size)
                self.assertLessEqual(man['resource_use']['zero_page_bytes'], zp)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(294, 0), Path(td)/'infeasible')

    def test_fail_closed_on_variant_set_and_resources(self):
        api = 'MATH_UMOD16'
        original = dict(linker.MODULES[api])
        with tempfile.TemporaryDirectory() as td:
            try:
                del linker.MODULES[api]['link:biased']
                with self.assertRaisesRegex(linker.LinkError, 'cycle-model measurement failed'):
                    linker.build(self.plan(), Path(td)/'missing')
            finally:
                linker.MODULES[api] = dict(original)
            try:
                linker.MODULES[api]['link:direct-zerozp'] = dict(
                    original['link:direct-zerozp'], scratch=0)
                with self.assertRaisesRegex(linker.LinkError, 'cycle-model measurement failed'):
                    linker.build(self.plan(), Path(td)/'wrong-contract')
            finally:
                linker.MODULES[api] = dict(original)

if __name__ == '__main__':
    unittest.main()
