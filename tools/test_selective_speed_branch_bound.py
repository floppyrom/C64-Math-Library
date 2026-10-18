#!/usr/bin/env python3
"""Exact speed search versus original Cartesian oracle; shared-code/budget tests."""
import itertools
import random
import unittest
from unittest.mock import patch
import selective_linker as L

OPS=('MATH_UMUL32','MATH_SMUL32','MATH_UDIV32_32','MATH_UMOD32_32','MATH_ISQRT32')
SIXTEEN=tuple('MATH_'+x for x in ('UMUL8 UMUL16 UMUL16_SHR8 UMOD8 UDIV8 ISQRT32 '
    'UMUL32 SMUL32 UMUL32_READY SMUL32_READY UMUL32_SHR16 SMUL32_SHR16 '
    'UDIV32_16 UMOD32_16 UDIV32_32 UMOD32_32').split())

def metric(names,seed):
    rng=random.Random(seed)
    return {api:{key:rng.randint(40,2000)/4 for key in L.MODULES[api]} for api in names}

def exhaustive(names,cycles,calls,ram,zp,base):
    best=None
    for items in itertools.product(*[[(api,k,v) for k,v in sorted(L.MODULES[api].items())]
                                     for api in names]):
        z=max(v['zp'] for _,_,v in items)
        scratch=max(v['scratch'] for _,_,v in items)
        code=L.projected_end(base,L.place_modules(L.unique_code_modules(items),base))-base
        _,state=L.place_state(L.state_requirements(v for _,_,v in items),0xc060,scratch)
        size=code+32+scratch+state
        if (zp is not None and z>zp) or (ram is not None and size>ram):continue
        fingerprint=tuple(k for _,k,_ in items)
        score=(sum(calls[api]*cycles[api][k] for api,k,_ in items),size,z,fingerprint)
        if best is None or score<best[0]:best=(score,dict(zip(names,fingerprint)))
    return best[1] if best else None

class BranchBoundTests(unittest.TestCase):
    def test_exhaustive_equivalence(self):
        for seed,ram,zp,base in ((1,None,None,0x8000),(2,2800,31,0x7123),
                                 (3,2100,4,0x8000),(4,3300,31,0x7123),
                                 (5,4000,12,0x8000),(6,8000,0,0x7123),
                                 (7,2500,12,0x7123)):
            with self.subTest(seed=seed):
                cycles=metric(OPS,seed)
                calls={api:seed*(i+1) for i,api in enumerate(OPS)}
                reference=exhaustive(OPS,cycles,calls,ram,zp,base)
                if reference is None:
                    with self.assertRaises(L.LinkError):
                        L.choose(OPS,{},'speed',zp,ram,code_base=base,
                                 scratch_base=0xc060,cycle_metrics=cycles,workload_calls=calls)
                else:
                    chosen=L.choose(OPS,{},'speed',zp,ram,code_base=base,
                                 scratch_base=0xc060,cycle_metrics=cycles,workload_calls=calls)
                    self.assertEqual({api:k for api,(k,_) in chosen.items()},reference)

    def test_shared_images_and_pins(self):
        for ops,key,ram,zp in ((('MATH_UDIV32_32','MATH_UMOD32_32'),
                                'link:v2-lowdivisor-hybrid',2528,12),
                               (('MATH_UMUL32','MATH_SMUL32'),
                                'link:fast31-shared-full64',2592,31)):
            cycles={api:{k:(1.0 if k==key else 1000.0)
                         for k in L.MODULES[api]} for api in ops}
            choice=L.choose(ops,{api:key for api in ops},'speed',zp,ram,
                            cycle_metrics=cycles,workload_calls={api:1 for api in ops})
            self.assertEqual({k for k,_ in choice.values()},{key})
            self.assertEqual(len(L.unique_code_modules([(api,*choice[api]) for api in ops])),1)

    def test_fail_closed(self):
        api='MATH_UMUL32'
        cycles=metric((api,),10)
        for value in (float('nan'),float('inf'),0,-1,True,'100'):
            with self.assertRaisesRegex(L.LinkError,'invalid comparable'):
                altered={api:dict(cycles[api])}
                altered[api][next(iter(altered[api]))]=value
                L.choose((api,),{},'speed',31,cycle_metrics=altered,
                         workload_calls={api:1})
        with self.assertRaisesRegex(L.LinkError,'incomplete comparable'):
            L.choose((api,),{},'speed',31,cycle_metrics={api:{}},workload_calls={api:1})

    def test_sixteen_operation_scaling(self):
        names=SIXTEEN
        product=1
        for api in names:product*=len(L.MODULES[api])
        self.assertGreater(product,1_000_000)
        cycles={api:{k:2200-0.1*max(0,sum(n for _,n in v['segments'])-150)
                     +0.33*v['zp'] for k,v in L.MODULES[api].items()} for api in names}
        with patch.object(L,'projected_end',wraps=L.projected_end) as count:
            got=L.choose(names,{},'speed',12,4500,cycle_metrics=cycles,
                         workload_calls={api:10 for api in names})
        self.assertEqual(set(got),set(names))
        self.assertLess(count.call_count,10_000)
        physical=L.place_modules(L.unique_code_modules([(api,*got[api]) for api in names]),0x8000)
        self.assertLessEqual(L.projected_end(0x8000,physical)-0x8000+32+
                             max(v['scratch'] for _,v in got.values()),4500)

if __name__=='__main__':unittest.main()
