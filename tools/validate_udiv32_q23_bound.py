#!/usr/bin/env python3
"""V1/V5 32/32 bounded quotient-2/3 source and deterministic ABI/cycle check."""
from pathlib import Path
import random,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from common_corpus_ranking import load_common
from validate_unsigned_division import load,wr,rd,expected
j=load_common(R)
target={'MATH_UDIV32_32':(358.00916086478566,2729),
        'MATH_UMOD32_32':(435.22463343108507,1705)}
v5_means={'MATH_UDIV32_32':275.01319164529133,
          'MATH_UMOD32_32':302.35307917888565}
for name,(mean,cases) in target.items():
    r=j['routines'][name]
    assert r['cases_per_profile']==cases
    assert abs(r['metrics']['v1_balanced']['mean_cycles']-mean)<1e-10
    assert abs(r['metrics']['v5_hybrid_lowzp']['mean_cycles']-v5_means[name])<1e-10
rng=random.Random(0x132323)
cases=[(0xffffffff,0x50000000),(0xfffffffd,0x7fffffff),
       (0x87a174cb,0x43f94b3c),(0xe0123456,0x43f94b3c),
       (0xffffffff,0x40000000),(0x80000000,0x40000000),
       (0xffffffff,1),(0,0),(0xffffffff,0xffffffff)]
for _ in range(150):
    d=rng.randrange(0x40000000,0x80000000)
    n=rng.getrandbits(32)
    cases.append((n,d))
for p in ('v1_balanced','v5_hybrid_lowzp'):
    cpu,api=load(p)
    assert bytes(cpu.mem[0x6860:0x6866])==b'\xad\x17\xc0\xc9\x40\x90',p
    for n,d in cases:
        d3=(d>>24)&255;n3=(n>>24)&255
        if 0x40<=d3<0x80 and n3>2*d3+1:
            assert 2<=n//d<=3,(hex(n),hex(d))
        for name in target:
            wr(cpu.mem,0xc010,n,4);wr(cpu.mem,0xc014,d,4)
            cpu.call(api[name],4_000_000)
            q,r,c=expected(n,d,32,32)
            assert (rd(cpu.mem,0xc01c,4),cpu.c)==(r,c)
            if name=='MATH_UDIV32_32':assert rd(cpu.mem,0xc018,4)==q
            assert rd(cpu.mem,0xc010,4)==n and rd(cpu.mem,0xc014,4)==d
print('V1/V5 32/32 q2/q3 bound PASS: verified source, operands, carry, output and 2 common cycle means')
