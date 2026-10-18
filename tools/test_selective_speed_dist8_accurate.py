#!/usr/bin/env python3
"""Comparable 384-pair DIST8_ACCURATE cycle selection, budgets and provenance."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import math_builder
import selective_linker as linker
import selective_speed_dist8_accurate as speed

class AccurateDist8SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ram=1600,zp=2):
        return math_builder.create_plan(self.index,['DIST8_ACCURATE'],
                  objective='speed',ram_budget=ram,zp_budget=zp)

    def test_identical_public_cycles_two_maps(self):
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as temp:
                man=linker.build(self.plan(),Path(temp),memory={
                  'code_base':code,'math_io':io,'zp_base':zp,'scratch_base':io+32})
                model=man['cycle_model_benchmark']
                self.assertEqual(model['cases'],384)
                self.assertEqual(model['corpus_sha256'],speed.CORPUS_SHA256)
                self.assertTrue(model['cpu_model_only'])
                self.assertEqual(set(model['mean_cycles']),speed.EXPECTED)
                self.assertEqual(set(model['source_sha256']),speed.EXPECTED)
                self.assertLess(model['mean_cycles']['link:v2-zp-tables'],
                                model['mean_cycles']['link:v1-ram-tables'])
                self.assertEqual(man['operations'][0]['variant'],'link:v2-zp-tables')
                print('DIST8_ACCURATE SPEED',hex(code),model['mean_cycles'],flush=True)

    def test_budget_selects_correct_implementation(self):
        with tempfile.TemporaryDirectory() as temp:
            for ram,zp,want in ((802,0,'link:v1-ram-tables'),
                                (1600,0,'link:v1-ram-tables'),
                                (800,2,'link:v2-zp-tables'),
                                (1600,2,'link:v2-zp-tables')):
                man=linker.build(self.plan(ram,zp),Path(temp)/f'{ram}_{zp}')
                self.assertEqual(man['operations'][0]['variant'],want)
                self.assertLessEqual(man['resource_use']['main_ram_total_bytes'],ram)
                self.assertLessEqual(man['resource_use']['zero_page_bytes'],zp)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(799,2),Path(temp)/'impossible')

    def test_changed_source_contract_fails_closed(self):
        key='MATH_DIST8_ACCURATE'
        original=dict(linker.MODULES[key])
        with tempfile.TemporaryDirectory() as temp:
            try:
                del linker.MODULES[key]['link:v2-zp-tables']
                with self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                    linker.build(self.plan(),Path(temp)/'missing')
            finally:
                linker.MODULES[key]=dict(original)
            try:
                linker.MODULES[key]['link:v2-zp-tables']=dict(
                    original['link:v2-zp-tables'],zp=0)
                with self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                    linker.build(self.plan(),Path(temp)/'bad_resource')
            finally:
                linker.MODULES[key]=dict(original)

if __name__=='__main__':unittest.main()
