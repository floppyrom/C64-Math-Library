#!/usr/bin/env python3
"""Canonical UDIV16 V2 low-zero-page donor and qualified 384-input speed choice."""
from __future__ import annotations
import tempfile, unittest, hashlib
from pathlib import Path
import math_builder,selective_linker as linker, selective_speed_udiv16 as speed
ROOT=Path(__file__).resolve().parents[1]

class V2PublicU16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ram=1800,zp=2,objective='speed'):
        return math_builder.create_plan(self.index,['UDIV16'],objective=objective,
            ram_budget=ram,zp_budget=zp)
    def test_canonical_source_and_same_input_cycles(self):
        for base,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(base=base),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={'code_base':base,'math_io':io})
                m=man['cycle_model_benchmark']
                self.assertEqual(m['cases'],384)
                self.assertEqual(m['corpus_sha256'],speed.CORPUS_SHA256)
                self.assertEqual(set(m['mean_cycles']),speed.EXPECTED)
                self.assertTrue(m['cpu_model_only'])
                self.assertLess(m['mean_cycles']['link:biased'],m['mean_cycles']['link:v2-zerozp'])
                self.assertEqual(man['operations'][0]['variant'],'link:biased')
                print('UDIV16 SOURCE SPEED',hex(base),m['mean_cycles'],flush=True)
    def test_new_low_zp_fallback_and_budget(self):
        for ram,zp,want in ((355,2,'link:biased'),(1513,0,'link:v2-zerozp'),
                            (1513,1,'link:v2-zerozp'),(1600,2,'link:biased')):
            with self.subTest(ram=ram,zp=zp),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(ram,zp),Path(td))
                self.assertEqual(man['operations'][0]['variant'],want)
                self.assertLessEqual(man['resource_use']['main_ram_total_bytes'],ram)
                self.assertLessEqual(man['resource_use']['zero_page_bytes'],zp)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(1512,0),Path(td))
    def test_source_pins_relocations_and_fail_closed(self):
        for base,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with tempfile.TemporaryDirectory() as td:
                plan=self.plan(1600,0,objective='size')
                man=linker.build(plan,Path(td),memory={'code_base':base,'math_io':io})
                self.assertEqual(man['operations'][0]['variant'],'link:v2-zerozp')
                self.assertEqual(int(man['operations'][0]['entry'][1:],16),base)
        api='MATH_UDIV16';original=dict(linker.MODULES[api])
        try:
            del linker.MODULES[api]['link:v2-zerozp']
            with tempfile.TemporaryDirectory() as td,self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                linker.build(self.plan(),Path(td))
        finally:linker.MODULES[api]=dict(original)
        try:
            linker.MODULES[api]['link:v2-zerozp']=dict(original['link:v2-zerozp'],zp=1)
            with tempfile.TemporaryDirectory() as td,self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                linker.build(self.plan(),Path(td))
        finally:linker.MODULES[api]=dict(original)

if __name__=='__main__': unittest.main()
