#!/usr/bin/env python3
"""Issue #39: V2-V4 UMUL24 no-carry CLC removal, exact resident-byte paired proof.

Only modifies transient CPU memory; no published PRG or source is changed.
Source geometry: after BCS R24_final, STA z4 / STX z5 leave C=0;
old CLC/RTS ($18 $60) -> RTS/NOP ($60 $EA), length and branch targets stable.
"""
from pathlib import Path
from collections import Counter
import hashlib, json, random, sys, tempfile
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from validate_umul24_directout import corpus
from validate_unsigned_division import load as resident
from validate_source_build import load as source_cpu
import assemble_sources
P=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')
ADDRESS={'reference':0x5747,'alternate':0x3747}
OLD=bytes.fromhex('18 60')
NEW=bytes.fromhex('60 ea')
MASK=(1<<48)-1

def sha(b): return hashlib.sha256(b).hexdigest()
def rd(m,a,n):return sum(m[a+j]<<(8*j) for j in range(n))
def wr(m,a,x,n):
    for j in range(n):m[a+j]=(x>>(8*j))&255

def check(cpu,api,io,x,y,signed=False):
    name='MATH_SMUL24' if signed else 'MATH_UMUL24'
    a=api[name]
    wr(cpu.mem,io,x,3);wr(cpu.mem,io+4,y,3)
    before=bytes(cpu.mem[io:io+3]+cpu.mem[io+4:io+7])
    cpu.mem[io+8:io+14]=b'\\x91'*6
    cpu.mem[io+0x30]=0xa6
    sp=cpu.sp
    cpu.d=0
    cyc=cpu.call(a,20000)
    sx=lambda t:t-(1<<24) if t & (1<<23) else t
    expected=((sx(x)*sx(y)) if signed else x*y)&MASK
    got=rd(cpu.mem,io+8,6)
    state=(got,cpu.c,cpu.sp,bytes(cpu.mem[io:io+3]+cpu.mem[io+4:io+7]),cpu.mem[io+0x30])
    assert state==(expected,0,sp,before,0xa6),(name,hex(x),hex(y),state,hex(expected))
    return cyc,state

def run_profile(profile,mode,pairs):
    if mode=='reference':
        original=R/profile/'resident'/f'math_{profile}_game_math.prg'
        old_blob=original.read_bytes()
        old,api=resident(profile);new,api2=resident(profile)
        io=0xc000
    else:
        raise AssertionError('only using build layout')
    assert api==api2
    adr=ADDRESS[mode]
    lo=int.from_bytes(old_blob[:2],'little')
    off=2+adr-lo
    assert old_blob[off:off+2]==OLD,(profile,mode,hex(adr),old_blob[off:off+2].hex())
    new.mem[adr:adr+2]=NEW
    candidate=old_blob[:off]+NEW+old_blob[off+2:]
    changed=[lo+j for j,(a,b) in enumerate(zip(old_blob[2:],candidate[2:])) if a!=b]
    assert changed==[adr,adr+1],(profile,mode,changed)
    hist=Counter();signed_calls=0
    for i,(x,y) in enumerate(pairs):
        old_cycles,a=check(old,api,io,x,y)
        new_cycles,b=check(new,api2,io,x,y)
        assert a==b
        hist[new_cycles-old_cycles]+=1
        if i%23==0:
            old_cycles,a=check(old,api,io,x,y,signed=True)
            new_cycles,b=check(new,api2,io,x,y,signed=True)
            assert a==b and old_cycles==new_cycles,(profile,mode,'signed',x,y)
            signed_calls+=1
    assert not (set(hist)-{-2,0}),(profile,mode,hist)
    assert hist[-2]>0 and hist[0]>0
    if mode=='reference':
        assert hist==Counter({-2:7789,0:2535}),(profile,hist)
    return dict(cases=len(pairs),cycle_delta_histogram={str(k):v for k,v in sorted(hist.items())},
       mean_saving_cycles=-sum(k*v for k,v in hist.items())/len(pairs),
       signed_mixed_cases=signed_calls,changed_addresses=[hex(v) for v in changed],
       original_sha256=sha(old_blob),candidate_sha256=sha(candidate))

def source_alt(profile,folder):
    cfg=R/'relocatable_source'/profile/'math_config_alternate.inc'
    manifest=assemble_sources.build(profile,cfg,folder)
    obj=folder/manifest['output_prg']
    return obj.read_bytes()

def run_alternate(profile,folder,pairs):
    old_blob=source_alt(profile,folder)
    a,api,io,manifest,_=source_cpu(profile,folder.parent)
    b,api2,io2,_,_=source_cpu(profile,folder.parent)
    assert api==api2 and io==io2
    adr=ADDRESS['alternate']
    lo=int.from_bytes(old_blob[:2],'little')
    off=2+adr-lo
    assert old_blob[off:off+2]==OLD,(profile,hex(adr),old_blob[off:off+2].hex())
    b.mem[adr:adr+2]=NEW
    patched=old_blob[:off]+NEW+old_blob[off+2:]
    changed=[lo+j for j,(x,y) in enumerate(zip(old_blob[2:],patched[2:])) if x!=y]
    assert changed==[adr,adr+1]
    hist=Counter();signed_calls=0
    for i,(x,y) in enumerate(pairs):
        former,oa=check(a,api,io,x,y)
        current,na=check(b,api2,io,x,y)
        assert oa==na
        hist[current-former]+=1
        if i%23==0:
            cy1,oa=check(a,api,io,x,y,True)
            cy2,na=check(b,api2,io,x,y,True)
            assert oa==na and cy1==cy2
            signed_calls+=1
    assert not (set(hist)-{-2,0}) and hist[-2]>0
    return dict(cases=len(pairs),cycle_delta_histogram={str(k):v for k,v in sorted(hist.items())},
                mean_saving_cycles=-sum(k*v for k,v in hist.items())/len(pairs),
                signed_mixed_cases=signed_calls,changed_addresses=[hex(v) for v in changed],
                original_sha256=sha(old_blob),candidate_sha256=sha(patched))

def main():
    pairs=corpus()
    assert len(pairs)==10324
    rng=random.Random(0xC63924CC)
    sub=pairs[:256]+[pairs[i] for i in rng.sample(range(len(pairs)),512)]
    report={'status':'PASS_RESEARCH_NO_RELEASE_CHANGE','native_vice_calls':0,
            'modified_tracked_prgs':False,'source_changed':False,
            'scope':'V2/V3/V4 UMUL24 direct no-carry return',
            'paired_unsigned_calls':0,'paired_signed_calls':0,'profiles':{}}
    with tempfile.TemporaryDirectory(prefix='issue39_umul24_clc_') as tmp:
        base=Path(tmp)
        for p in P:
            d=base/'alternate'/p;d.mkdir(parents=True)
            ref=run_profile(p,'reference',pairs)
            alt=run_alternate(p,d,sub)
            report['profiles'][p]={'reference':ref,'alternate':alt}
            for e in (ref,alt):
                report['paired_unsigned_calls']+=e['cases']
                report['paired_signed_calls']+=e['signed_mixed_cases']
            print('UMUL24 CLC',p,'reference',ref['cycle_delta_histogram'],'alternate',alt['cycle_delta_histogram'],flush=True)
    assert report['paired_unsigned_calls']==3*(10324+768)
    assert report['paired_signed_calls']>1200
    if '--output' in sys.argv:
        path=Path(sys.argv[sys.argv.index('--output')+1])
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\\n')
    print('ISSUE39 UMUL24 NONCARRY CLC SCREEN PASS',report['paired_unsigned_calls'],report['paired_signed_calls'])
if __name__=='__main__':main()
