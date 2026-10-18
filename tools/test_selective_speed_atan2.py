#!/usr/bin/env python3
"""ATAN2_8 speed-selection correctness, source and page-alignment regression."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import math_builder, selective_linker as linker, selective_speed_atan2 as speed

class SpeedATAN2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ram=1500):
        return math_builder.create_plan(self.index,['ATAN2_8'],objective='speed',
              zp_budget=0,ram_budget=ram)

    def test_same_corpus_and_two_code_maps(self):
        for base,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(base=base),tempfile.TemporaryDirectory() as d:
                man=linker.build(self.plan(),Path(d),memory={'code_base':base,'math_io':io,
                    'scratch_base':io+32})
                measurement=man['cycle_model_benchmark']
                self.assertEqual(measurement['cases'],speed.COUNT)
                self.assertEqual(measurement['corpus_sha256'],speed.CORPUS_SHA256)
                self.assertEqual(measurement['output_sha256'],speed.OUTPUT_SHA256)
                self.assertEqual(set(measurement['mean_cycles']),speed.EXPECTED)
                self.assertTrue(measurement['cpu_model_only'])
                self.assertLess(measurement['mean_cycles']['link:sum-fast'],
                    measurement['mean_cycles']['link:compact'])
                self.assertEqual(man['operations'][0]['variant'],'link:sum-fast')
                self.assertEqual(man['resource_use']['zero_page_bytes'],0)
                print('ATAN2 speed',hex(base),measurement['mean_cycles'],flush=True)

    def test_ram_budget_selects_compact(self):
        for ram,want in ((800,'link:compact'),(1000,'link:compact'),
                         (1312,'link:sum-fast'),(1500,'link:sum-fast')):
            with self.subTest(ram=ram),tempfile.TemporaryDirectory() as d:
                man=linker.build(self.plan(ram),Path(d))
                self.assertEqual(man['operations'][0]['variant'],want)
                self.assertLessEqual(man['resource_use']['main_ram_total_bytes'],ram)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(linker.LinkError):
            linker.build(self.plan(799),Path(d))

    def test_missing_and_changed_source_contract_fail_closed(self):
        api='MATH_ATAN2_8';original=dict(linker.MODULES[api])
        with tempfile.TemporaryDirectory() as d:
            try:
                del linker.MODULES[api]['link:sum-fast']
                with self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                    linker.build(self.plan(),Path(d)/'missing')
            finally:linker.MODULES[api]=dict(original)
            try:
                linker.MODULES[api]['link:sum-fast']=dict(original['link:sum-fast'],zp=2)
                with self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                    linker.build(self.plan(),Path(d)/'bad-resource')
            finally:linker.MODULES[api]=dict(original)

if __name__=='__main__': unittest.main()
