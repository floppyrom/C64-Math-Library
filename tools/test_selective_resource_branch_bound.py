#!/usr/bin/env python3
"""Exhaustive reference proof of exact 56-operation resource frontier search."""
import itertools
import time
import unittest
import selective_linker as L

OPS = ('MATH_UMUL32', 'MATH_SMUL32', 'MATH_UDIV32_32',
       'MATH_UMOD32_32', 'MATH_ISQRT32')
SHARED = ('MATH_UMUL32', 'MATH_SMUL32', 'MATH_UMUL32_READY',
          'MATH_SMUL32_READY', 'MATH_UDIV32_32', 'MATH_UMOD32_32')
ALIGNED = ('MATH_UMUL8', 'MATH_ATAN2_8', 'MATH_ISQRT32',
           'MATH_UMUL32', 'MATH_SMUL32')

def reference(names, objective, ram_budget, zp_budget, base, pins=None):
    choices = []
    pins = pins or {}
    for api in names:
        items = L.MODULES[api]
        if api in pins:
            items = {pins[api]: items[pins[api]]}
        else:
            items = L.pareto_resource_variants(items)
        choices.append([(api, name, spec) for name, spec in sorted(items.items())])
    best = None
    winner = None
    for combo in itertools.product(*choices):
        zp = max(spec['zp'] for _, _, spec in combo)
        scratch = max(spec['scratch'] for _, _, spec in combo)
        code = (L.projected_end(base, L.place_modules(L.unique_code_modules(combo), base)) - base)
        _, state = L.place_state(L.state_requirements(s for _, _, s in combo), 0xc060, scratch)
        ram = code + 32 + scratch + state
        if ram_budget is not None and ram > ram_budget:
            continue
        if zp_budget is not None and zp > zp_budget:
            continue
        if objective == 'size':
            score = (ram, zp, code)
        elif objective == 'balanced':
            score = (ram + 8*zp, ram, zp)
        elif objective == 'zp':
            score = (zp, ram, code)
        else:
            raise AssertionError(objective)
        score += (tuple(name for _, name, _ in combo),)
        if best is None or score < best:
            best = score
            winner = {api:name for api,name,_ in combo}
    return winner

class ResourceBranchBoundTests(unittest.TestCase):
    def test_matches_full_exhaustive_oracle(self):
        for names in (OPS, ALIGNED, SHARED):
            for objective in ('size','balanced','zp'):
                for ram, zp, base in ((None,None,0x8000),
                                      (2700,12,0x7123),
                                      (3600,31,0x8000),
                                      (1700,4,0x7123)):
                    with self.subTest(names=names, objective=objective, ram=ram,zp=zp,base=base):
                        exp = reference(names,objective,ram,zp,base)
                        if exp is None:
                            with self.assertRaises(L.LinkError):
                                L.choose(names,{},objective,zp,ram,code_base=base,
                                         scratch_base=0xc060)
                        else:
                            selected = L.choose(names,{},objective,zp,ram,
                                                code_base=base,scratch_base=0xc060)
                            self.assertEqual({api:name for api,(name,_) in selected.items()}, exp)
    def test_pinned_shared_producer_and_limits(self):
        names=('MATH_UDIV32_32','MATH_UMOD32_32')
        pins={api:'link:v2-lowdivisor-hybrid' for api in names}
        for objective in ('size','balanced','zp'):
            for base in (0x8000,0x7123):
                exp=reference(names,objective,2528,12,base,pins)
                selected=L.choose(names,pins,objective,12,2528,code_base=base)
                self.assertEqual({api:name for api,(name,_) in selected.items()},exp)
                self.assertEqual(len(L.unique_code_modules([(api,*selected[api]) for api in names])),1)
            with self.assertRaises(L.LinkError):
                L.choose(names,pins,objective,11,2528)
    def test_all_56_complete_without_cartesian_expansion(self):
        all_names=tuple(sorted(L.MODULES))
        product=1
        for api in all_names:
            product*=len(L.pareto_resource_variants(L.MODULES[api]))
        self.assertGreater(product,100_000_000)
        begin=time.monotonic()
        chosen=L.choose(all_names,{},'size',None,None)
        self.assertEqual(set(chosen),set(all_names))
        # Liberal ceiling for busy CI; millions of combinations cannot meet it.
        self.assertLess(time.monotonic()-begin,90)
        physical=L.unique_code_modules([(api,*chosen[api]) for api in all_names])
        self.assertLess(len(physical),len(all_names))

if __name__=='__main__': unittest.main()
