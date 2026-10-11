#!/usr/bin/env python3
"""Paired public 6502 timing/ABI certification of the three-byte Issue39 bypass."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from benchmark_unsigned_common_corpus import SPECS,corpus
from validate_unsigned_division import wr,rd,expected,api
BEFORE={0x6814:0x41,0x6859:0,0x685B:0}
AFTER={0x6814:0x44,0x6859:0x4c,0x685B:0xc1}
j={'status':'PASS','profiles':{},'matched_calls':0,'matched_errors':0}
for profile in ('v1_balanced','v5_hybrid_lowzp'):
    path=ROOT/profile/'resident'/f'math_{profile}_game_math.prg'
    blob=path.read_bytes();lo=blob[0]|blob[1]<<8
    mem=bytearray(65536);mem[lo:lo+len(blob)-2]=blob[2:]
    assert all(mem[a]==v for a,v in AFTER.items()),profile
    parent=mem.copy()
    for a,v in BEFORE.items():parent[a]=v
    results={}
    for name in ('MATH_UDIV32_32','MATH_UMOD32_32'):
        spec=next(s for s in SPECS if s[0]==name)
        _,pairs=corpus(name,spec[1],spec[2],spec[5],spec[7])
        cpus=[CPU(x.copy()) for x in (parent,mem)]
        for cpu in cpus:
            cpu.d=0;cpu.call(0x3280,2_000_000)
        d={'count':len(pairs),'faster':0,'same':0,'slower':0,'d3_zero_qualified':0,'min_delta':99999,'max_delta':-99999,'before_cycles':0,'after_cycles':0}
        for n,div,_ in pairs:
            obs=[]
            for cpu in cpus:
                wr(cpu.mem,0xc010,n,4);wr(cpu.mem,0xc014,div,4)
                cy=cpu.call(api(profile)[name],4_000_000)
                assert rd(cpu.mem,0xc010,4)==n and rd(cpu.mem,0xc014,4)==div
                obs.append((cy,(rd(cpu.mem,0xc018,4),rd(cpu.mem,0xc01c,4),cpu.c)))
            exp=expected(n,div,32,32)
            assert obs[0][1]==obs[1][1],(profile,name,hex(n),hex(div),obs)
            actual=obs[1][1]
            assert (actual==exp if name=='MATH_UDIV32_32' else actual[1:]==exp[1:])
            delta=obs[1][0]-obs[0][0]
            assert delta in (-12,0), (profile,name,hex(n),hex(div),delta)
            if div and div>>24==0 and n>div:
                assert delta==-12
                d['d3_zero_qualified']+=1
            else:
                assert delta==0
            d['faster' if delta<0 else 'slower' if delta>0 else 'same']+=1
            d['min_delta']=min(d['min_delta'],delta);d['max_delta']=max(d['max_delta'],delta)
            d['before_cycles']+=obs[0][0];d['after_cycles']+=obs[1][0]
        d['mean_before']=d['before_cycles']/len(pairs)
        d['mean_after']=d['after_cycles']/len(pairs)
        d['mean_delta']=d['mean_after']-d['mean_before']
        assert d['slower']==0
        results[name]=d;j['matched_calls']+=len(pairs)
    j['profiles'][profile]={'sha256_candidate':hashlib.sha256(blob).hexdigest(),'routines':results}
assert j['matched_calls']==8868
out=ROOT/'validation/review/UDIV32_ZERO_HIGH_BYPASS_PAIRED.json'
out.write_text(json.dumps(j,indent=2)+'\n')
print('ZERO HIGH BYTE BYPASS: PASS',j['matched_calls'],'paired machine-code calls')
