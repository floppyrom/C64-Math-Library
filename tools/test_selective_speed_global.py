#!/usr/bin/env python3
"""Certified per-API speed corpora with explicit mixed-project call frequencies."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import math_builder as mb
import selective_linker as linker


class GlobalSpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = mb.operation_index()

    def plan(self, calls, budget=4096, zp=4, pins=None):
        return mb.create_plan(self.index, ['UMUL8', 'UMUL16'],
                              objective='speed', workload_calls=calls,
                              zp_budget=zp, ram_budget=budget, pins=pins)

    def test_weighted_selection_and_reproducible_provenance(self):
        plan = self.plan({'umul8': 100, 'umul16': 20})
        with tempfile.TemporaryDirectory() as td:
            m1 = linker.build(plan, Path(td), memory={
                'code_base': 0x7123, 'math_io': 0xc040, 'zp_base': 0x70})
            m2 = linker.build(plan, Path(td), memory={
                'code_base': 0x7123, 'math_io': 0xc040, 'zp_base': 0x70})
            self.assertEqual(m1['prg_sha256'], m2['prg_sha256'])
            self.assertEqual(m1['cycle_model_benchmark'], m2['cycle_model_benchmark'])
            self.assertEqual(m1['workload_calls'], {'MATH_UMUL8':100, 'MATH_UMUL16':20})
            self.assertEqual(m1['cycle_model_benchmark']['workload_calls'], m1['workload_calls'])
            self.assertIn('workload-weighted', m1['selection_basis'])
            self.assertTrue(m1['cycle_model_benchmark']['cpu_model_only'])
            details = m1['cycle_model_benchmark']['operations']
            self.assertEqual(set(details), set(m1['workload_calls']))
            for model in details.values():
                self.assertTrue(model['corpus_sha256'])
                self.assertTrue(model['cpu_model_only'])
            selected = {entry['api']:entry['variant'] for entry in m1['operations']}
            calculated = sum(m1['workload_calls'][api] * details[api]['mean_cycles'][variant]
                             for api,variant in selected.items())
            self.assertAlmostEqual(m1['estimated_weighted_cycles'], calculated)
            saved = json.loads((Path(td)/'selective_manifest.json').read_text())
            self.assertEqual(saved['estimated_weighted_cycles'], calculated)

    def test_ram_budget_can_force_compact_and_pins_work(self):
        plan = self.plan({'UMUL8': 3, 'UMUL16': 70}, budget=209, zp=0)
        with tempfile.TemporaryDirectory() as td:
            result = linker.build(plan, Path(td))
            self.assertEqual(result['resource_use']['zero_page_bytes'], 0)
            self.assertLessEqual(result['resource_use']['main_ram_total_bytes'], 209)
            self.assertEqual({e['variant'] for e in result['operations']},
                             {'link:compact-zerozp'})
            pinned = self.plan({'UMUL8':1, 'UMUL16':1}, pins={'UMUL8':'link:compact-zerozp'})
            chosen = linker.build(pinned, Path(td))
            self.assertEqual(next(x for x in chosen['operations']
                                  if x['api']=='MATH_UMUL8')['variant'], 'link:compact-zerozp')

    def test_workload_tradeoff_changes_global_choice_under_ram_cap(self):
        # At 1400 bytes, only one quarter-square source fits. Prioritize
        # whichever operation is actually called frequently, with the other
        # operation retaining its compact source (same ABI, 0 ZP).
        with tempfile.TemporaryDirectory() as td:
            a = linker.build(self.plan({'UMUL8':1000,'UMUL16':1},budget=1400),
                             Path(td)/'many8')
            b = linker.build(self.plan({'UMUL8':1,'UMUL16':1000},budget=1400),
                             Path(td)/'many16')
            choice_a={x['api']:x['variant'] for x in a['operations']}
            choice_b={x['api']:x['variant'] for x in b['operations']}
            self.assertEqual(choice_a,{'MATH_UMUL8':'link:quarter-square',
                                       'MATH_UMUL16':'link:compact-zerozp'})
            self.assertEqual(choice_b,{'MATH_UMUL8':'link:compact-zerozp',
                                       'MATH_UMUL16':'link:quarter-square'})
            self.assertLessEqual(a['resource_use']['main_ram_total_bytes'],1400)
            self.assertLessEqual(b['resource_use']['main_ram_total_bytes'],1400)

    def test_missing_invalid_or_unqualified_models_rejected(self):
        for workload in (None, {}, {'UMUL8':2}, {'UMUL8':0, 'UMUL16':1},
                         {'UMUL8':True,'UMUL16':1}, {'UMUL8':1.5,'UMUL16':1},
                         {'UMUL8':1,'UMUL16':1,'ISQRT32':1},
                         {'UMUL8':1,'MATH_UMUL8':2,'UMUL16':1}):
            with self.subTest(workload=workload), self.assertRaises(mb.SelectionError):
                self.plan(workload)
        with self.assertRaises(mb.SelectionError):
            mb.create_plan(self.index,['UMUL8'],objective='balanced',
                           workload_calls={'UMUL8':1})
        unknown = mb.create_plan(self.index,['SDIV16'],objective='speed')
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(linker.LinkError,'No authenticated'):
                linker.build(unknown,Path(td))
            plan=self.plan({'UMUL8':1,'UMUL16':1})
            plan['workload_calls']['MATH_UMUL16'] = 0
            with self.assertRaisesRegex(linker.LinkError,'positive workload calls'):
                linker.build(plan,Path(td))

    def test_cli_config_and_workload_override(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)
            cfg=path/'workload.json'
            cfg.write_text(json.dumps({'operations':['UMUL8','UMUL16'],
                        'objective':'speed','constraints':{'max_ram_bytes':4000,'max_zp_bytes':4},
                        'workload_calls':{'UMUL8':120,'UMUL16':20}}))
            args=[sys.executable,str(ROOT/'tools/math_builder.py'),
                  '--config',str(cfg),'--out',str(path/'result.json'),'--build']
            ok=subprocess.run(args,capture_output=True,text=True,cwd=ROOT)
            self.assertEqual(ok.returncode,0,ok.stderr)
            data=json.loads((path/'selective_manifest.json').read_text())
            self.assertEqual(data['workload_calls'],{'MATH_UMUL8':120,'MATH_UMUL16':20})
            bad=subprocess.run(args+['--calls','UMUL8=2'],capture_output=True,text=True,cwd=ROOT)
            self.assertNotEqual(bad.returncode,0)
            self.assertIn('Duplicate workload',bad.stderr)
            no_weights=subprocess.run([sys.executable,str(ROOT/'tools/math_builder.py'),
                '--operation','UMUL8','--operation','UMUL16','--objective','speed','--preview'],
                capture_output=True,text=True,cwd=ROOT)
            self.assertNotEqual(no_weights.returncode,0)
            self.assertIn('requires workload calls',no_weights.stderr)

if __name__=='__main__':
    unittest.main()
