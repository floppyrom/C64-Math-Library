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
    def test_issue285_pinned_table_full56_at_both_origins(self):
        # Exercise the exact (not 55-source-pinned) optimizer under the
        # issue's actual 18 KB/4-ZP budget. Performance is logged, not
        # asserted as a flaky shared-runner wall-clock threshold.
        names = tuple(sorted(L.MODULES))
        self.assertEqual(len(names), 56)
        for origin in (0x2000, 0x4321):
            for objective in ('size', 'balanced', 'zp'):
                for pinned in (False, True):
                    pins = ({'MATH_ISQRT16': 'link:square-table'}
                            if pinned else {})
                    with self.subTest(origin=hex(origin), objective=objective,
                                      pinned=pinned):
                        start = time.perf_counter()
                        selected = L.choose(names, pins, objective, 4, 18000,
                                            code_base=origin,
                                            scratch_base=0xc020)
                        duration = time.perf_counter() - start
                        self.assertEqual(set(selected), set(names))
                        if pinned:
                            self.assertEqual(selected['MATH_ISQRT16'][0],
                                             'link:square-table')
                        chosen = [(api, *selected[api]) for api in names]
                        zp = max(spec['zp'] for _, _, spec in chosen)
                        scratch = max(spec['scratch'] for _, _, spec in chosen)
                        code = (L.projected_end(origin, L.place_modules(
                            L.unique_code_modules(chosen), origin)) - origin)
                        _, persistent = L.place_state(
                            L.state_requirements(spec for _, _, spec in chosen),
                            0xc020, scratch)
                        ram = code + 32 + scratch + persistent
                        self.assertLessEqual(ram, 18000)
                        self.assertLessEqual(zp, 4)
                        print('ISSUE285 EXACT56', hex(origin), objective,
                              'pinned', pinned, 'RAM', ram, 'ZP', zp,
                              'elapsed_s', round(duration, 4), flush=True)

    def test_all_56_complete_without_cartesian_expansion(self):
        all_names=tuple(sorted(L.MODULES))
        product=1
        for api in all_names:
            product*=len(L.pareto_resource_variants(L.MODULES[api]))
        self.assertGreater(product,100_000_000)
        begin=time.monotonic()
        chosen=L.choose(all_names,{},'size',None,None)
        self.assertEqual(set(chosen),set(all_names))
        # Bound search duration while tolerating shared CI runner variance.
        # A verified full-catalog solve took 90.95s against the old 90s cutoff.
        self.assertLess(time.monotonic()-begin,120)
        physical=L.unique_code_modules([(api,*chosen[api]) for api in all_names])
        self.assertLess(len(physical),len(all_names))

if __name__=='__main__': unittest.main()
