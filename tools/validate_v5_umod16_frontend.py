#!/usr/bin/env python3
"""Permanent V5/V2 UMOD16 shared-input 1705-case exact output/cycle regression."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from benchmark_unsigned_common_corpus import corpus
from validate_unsigned_division import load,wr,rd
A,B=load('v2_pareto_fast'),load('v5_hybrid_lowzp')
seed,pairs=corpus('MATH_UMOD16',16,16,0,1024)
assert len(pairs)==1705
report=json.loads((R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
x=report['routines']['MATH_UMOD16']
assert x['cases_per_profile']==len(pairs)
assert x['same_cases_sha256']==hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()
total=[0,0]
for n,d,_ in pairs:
    expected=(0 if d==0 else n%d,1 if d==0 else 0,n,d)
    last=None
    for i,(cpu,api) in enumerate((A,B)):
        wr(cpu.mem,0xc010,n,2);wr(cpu.mem,0xc014,d,2)
        cyc=cpu.call(api['MATH_UMOD16'],4_000_000)
        result=(rd(cpu.mem,0xc01c,2),cpu.c,rd(cpu.mem,0xc010,2),rd(cpu.mem,0xc014,2))
        assert result==expected,(i,hex(n),hex(d),result,expected)
        if i:assert cyc==last,(hex(n),hex(d),cyc,last)
        last=cyc;total[i]+=cyc
assert total[0]==total[1]
for profile in ('v2_pareto_fast','v5_hybrid_lowzp'):
    image=R/profile/'resident'/f'math_{profile}_game_math.prg'
    assert hashlib.sha256(image.read_bytes()).hexdigest()==report['sources'][profile]['resident_sha256'],profile
assert abs(total[0]/len(pairs)-x['metrics']['v2_pareto_fast']['mean_cycles'])<1e-9
assert abs(total[1]/len(pairs)-x['metrics']['v5_hybrid_lowzp']['mean_cycles'])<1e-9
print('V5 UMOD16 REMAINDER FRONTEND PASS: 1705 identical V2/V5 cases, exact cycle parity, no errors')
