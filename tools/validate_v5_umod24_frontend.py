#!/usr/bin/env python3
"""V5 UMOD24 imported remainder-only frontend: 1553-case exact V2/V5 cycle ABI gate."""
from pathlib import Path
import hashlib, json, sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from benchmark_unsigned_common_corpus import corpus
from validate_unsigned_division import load,wr,rd,expected
N,D,RADDR=0xC010,0xC014,0xC01C
v2,api2=load('v2_pareto_fast')
v5,api5=load('v5_hybrid_lowzp')
seed,pairs=corpus('MATH_UMOD24',24,24,0,1024)
assert len(pairs)==1553
report=json.loads((R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
datum=report['routines']['MATH_UMOD24']
assert datum['cases_per_profile']==len(pairs)
assert datum['same_cases_sha256']==hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()
total=[0,0]
for n,d,_ in pairs:
    target_r=0 if d==0 else n%d
    target_c=1 if d==0 else 0
    for idx,(cpu,api) in enumerate(((v2,api2),(v5,api5))):
        wr(cpu.mem,N,n,3);wr(cpu.mem,D,d,3)
        cycles=cpu.call(api['MATH_UMOD24'],4_000_000)
        got=(rd(cpu.mem,RADDR,3),cpu.c,rd(cpu.mem,N,3),rd(cpu.mem,D,3))
        assert got==(target_r,target_c,n,d),(idx,hex(n),hex(d),got,target_r,target_c)
        if idx==0:ref_cycles=cycles
        else:assert cycles==ref_cycles,(hex(n),hex(d),ref_cycles,cycles)
        total[idx]+=cycles
assert report['status']=='PASS'
assert report['sources']['v2_pareto_fast']['resident_sha256']==hashlib.sha256((R/'v2_pareto_fast/resident/math_v2_pareto_fast_game_math.prg').read_bytes()).hexdigest()
assert report['sources']['v5_hybrid_lowzp']['resident_sha256']==hashlib.sha256((R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg').read_bytes()).hexdigest()
assert total[0]==total[1],('V2/V5 exact per-operand cycle parity',total)
for profile,total_cycles in (('v2_pareto_fast',total[0]),('v5_hybrid_lowzp',total[1])):
    published=datum['metrics'][profile]['mean_cycles']
    assert abs(total_cycles/len(pairs)-published)<1e-9,(profile,total_cycles,published)
print('V5 UMOD24 SOURCE TRANSPLANT PASS: 1553 identical operands; zero mismatches, exact V2/V5 cycle parity')
