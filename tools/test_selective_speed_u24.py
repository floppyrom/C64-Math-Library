#!/usr/bin/env python3
"""384 matched complete Q24/R24 public calls, and budget-aware speed choice."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import math_builder
import selective_linker as linker
import selective_speed_u24 as speed

DIV='UDIV24'
MOD='UMOD24'

class U24SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,operations,ram=1493,zp=3):
        calls={key:100 for key in operations} if len(operations)>1 else None
        return math_builder.create_plan(self.index,
            list(operations),objective='speed',ram_budget=ram,zp_budget=zp,
            workload_calls=calls)

    def test_two_map_matched_public_cycle_proofs(self):
        for code,io,scratch,zp in ((0x8000,0xc000,0xc020,0x50),
                                   (0x7123,0xc040,0xc060,0x70)):
            mem={'code_base':code,'math_io':io,
                 'scratch_base':scratch,'zp_base':zp}
            for op in (DIV,MOD):
                with self.subTest(code=code,op=op),tempfile.TemporaryDirectory() as td:
                    manifest=linker.build(self.plan((op,)),Path(td),memory=mem)
                    model=manifest['cycle_model_benchmark']
                    self.assertEqual(model['cases'],speed.COUNT)
                    self.assertEqual(model['corpus_sha256'],speed.CORPUS_SHA256)
                    self.assertTrue(model['cpu_model_only'])
                    self.assertEqual(set(model['mean_cycles']),speed.EXPECTED)
                    self.assertLess(model['mean_cycles']['link:v2-repose-fast'],
                                    model['mean_cycles']['link:portable-restoring'])
                    self.assertEqual(set(model['donor_sha256']),speed.EXPECTED)
                    self.assertEqual(manifest['operations'][0]['variant'],
                                     'link:v2-repose-fast')
                    print('U24 FULL PUBLIC SPEED',hex(code),op,model['mean_cycles'],flush=True)

    def test_no_zp_and_tight_ram_select_portable(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            for name,budget,zp in ((DIV,226,0),(MOD,226,0),(DIV,300,3),(MOD,1493,0)):
                man=linker.build(self.plan((name,),ram=budget,zp=zp),folder/name)
                self.assertEqual(man['operations'][0]['variant'],'link:portable-restoring')
                self.assertEqual(man['resource_use']['zero_page_bytes'],0)
            mixed=linker.build(self.plan((DIV,MOD),ram=1493,zp=3),folder/'mixed')
            self.assertEqual(len(mixed['link_order']),1)
            self.assertEqual({q['variant'] for q in mixed['operations']},{'link:v2-repose-fast'})
            self.assertEqual(mixed['resource_use']['main_ram_total_bytes'],1493)
            self.assertEqual(set(mixed['cycle_model_benchmark']['operations']),
                             {'MATH_'+DIV,'MATH_'+MOD})

    def test_source_and_resources_fail_closed(self):
        api='MATH_UDIV24'
        original=dict(linker.MODULES[api])
        with tempfile.TemporaryDirectory() as td:
            try:
                del linker.MODULES[api]['link:v2-repose-fast']
                with self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                    linker.build(self.plan((DIV,)),Path(td)/'missing')
            finally:
                linker.MODULES[api]=dict(original)
            try:
                linker.MODULES[api]['link:v2-repose-fast']=dict(
                    original['link:v2-repose-fast'],requires_writable_code=False)
                with self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                    linker.build(self.plan((DIV,)),Path(td)/'provenance')
            finally:
                linker.MODULES[api]=dict(original)

if __name__=='__main__':
    unittest.main()
