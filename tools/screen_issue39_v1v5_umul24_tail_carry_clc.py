#!/usr/bin/env python3
"""Bounded V1/V5 FAST24 public tail carry-clear specialization, research only.

Carry=0 at the no-overflow BCS fallthrough. Move shared public-tail CLC
into the rare carry branch (after INX), keeping caller carry=0 in both cases.
Proof runs original and mutated canonical sources on reference/alternate maps;
never changes the repository's released PRGs.
"""
from pathlib import Path
import collections, hashlib, json, random, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm
import build_hybrid
import validate_source_build as source_check
from validate_umul24_directout import corpus

PROFILES=('v1_balanced','v5_hybrid_lowzp')
MAPS=('reference','alternate')
SOURCE=ROOT/'relocatable_source/v1_balanced/umul24_fast24_shared.inc'
OLD_RARE="""U24_final:
        inx
        jmp U24_FAST24_public_tail"""
NEW_RARE="""U24_final:
        inx
        clc
        jmp U24_FAST24_public_tail"""
OLD_TAIL="""U24_FAST24_public_tail:
        sta MATH_IO+$0C
        stx MATH_IO+$0D
        clc
        rts"""
NEW_TAIL="""U24_FAST24_public_tail:
        sta MATH_IO+$0C
        stx MATH_IO+$0D
        rts"""
MASK=(1<<48)-1

def sha(b):return hashlib.sha256(b).hexdigest()
def wr(m,at,x):
    for i in range(3):m[at+i]=(x>>(8*i))&255
def rd(m,at):
    return sum(m[at+i]<<(8*i) for i in range(6))
def sign(x):return x-(1<<24) if x&(1<<23) else x

def call(cpu,api,io,x,y,signed=False):
    label='MATH_SMUL24' if signed else 'MATH_UMUL24'
    wr(cpu.mem,io,x);wr(cpu.mem,io+4,y)
    before=bytes(cpu.mem[io:io+3]+cpu.mem[io+4:io+7])
    cpu.mem[io+0x30]=0xa6
    sp=cpu.sp;cpu.d=0
    cy=cpu.call(api[label],20_000)
    want=((sign(x)*sign(y)) if signed else (x*y))&MASK
    value=rd(cpu.mem,io+8)
    assert value==want and cpu.c==0 and cpu.sp==sp,(label,hex(x),hex(y),hex(value),hex(want),cpu.c)
    assert bytes(cpu.mem[io:io+3]+cpu.mem[io+4:io+7])==before
    assert cpu.mem[io+0x30]==0xa6
    return cy,value

def build_all(base,version):
    for mode in MAPS:
        for p in PROFILES:
            conf=ROOT/'relocatable_source'/p/('math_config_'+mode+'.inc')
            dest=base/version/mode/p
            dest.mkdir(parents=True)
            if p=='v1_balanced':asm.build(p,conf,dest)
            else:build_hybrid.build(conf,dest)

def main():
    cases=corpus();assert len(cases)==10324
    rnd=random.Random(0x39002488)
    sampled=[cases[i] for i in rnd.sample(range(len(cases)),1024)]
    original=SOURCE.read_text()
    assert original.count(OLD_RARE)==original.count(OLD_TAIL)==1
    mutated=original.replace(OLD_RARE,NEW_RARE).replace(OLD_TAIL,NEW_TAIL)
    status=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    report={'status':'RESEARCH_NO_RELEASE_CHANGE',
            'modified_production_binaries':False,
            'source_restored_after_screen':True,
            'native_vice_calls':0,
            'unsigned_paired_cases':0,'signed_mixed_paired_cases':0,
            'profiles':{},'source_sha256_before':sha(original.encode()),
            'source_sha256_candidate':sha(mutated.encode())}
    with tempfile.TemporaryDirectory(prefix='issue39_v1v5_tail_clc_') as temporary:
        base=Path(temporary)
        try:
            build_all(base,'old')
            SOURCE.write_text(mutated)
            build_all(base,'new')
        finally:
            SOURCE.write_text(original)
        assert SOURCE.read_text()==original
        for profile in PROFILES:
            report['profiles'][profile]={}
            original_prg=(ROOT/profile/'resident'/f'math_{profile}_game_math.prg').read_bytes()
            assert sha(original_prg)==status['reference_prg_sha256'][profile]
            for mode in MAPS:
                old,oldapi,oldio,oldman,_=source_check.load(profile,base/'old'/mode)
                new,newapi,newio,newman,_=source_check.load(profile,base/'new'/mode)
                assert oldapi==newapi and oldio==newio
                folder=base/'old'/mode/profile
                oldblob=(folder/oldman['output_prg']).read_bytes()
                folder=base/'new'/mode/profile
                newblob=(folder/newman['output_prg']).read_bytes()
                assert len(oldblob)==len(newblob),(profile,mode,'resident size growth')
                if mode=='reference':
                    assert oldblob==original_prg,(profile,'current source does not rebuild resident')
                    ld=int.from_bytes(oldblob[:2],'little')
                    changed=[ld+i for i,(x,y) in enumerate(zip(oldblob[2:],newblob[2:])) if x!=y]
                    assert changed and all(0x2700<=x<0x3000 for x in changed),(
                        profile,'modified outside FAST24 owned source islands',list(map(hex,changed[:25])))
                pairs=cases if mode=='reference' else sampled
                distribution=collections.Counter()
                signed_pairs=0
                for i,(x,y) in enumerate(pairs):
                    before,product=call(old,oldapi,oldio,x,y)
                    after,newproduct=call(new,newapi,newio,x,y)
                    assert product==newproduct
                    distribution[after-before]+=1
                    if i%37==0:
                        b,product=call(old,oldapi,oldio,x,y,True)
                        a,newproduct=call(new,newapi,newio,x,y,True)
                        assert (a,newproduct)==(b,product),(profile,mode,'signed path changes',x,y)
                        signed_pairs+=1
                delta=sum(c*n for c,n in distribution.items())/len(pairs)
                report['unsigned_paired_cases']+=len(pairs)
                report['signed_mixed_paired_cases']+=signed_pairs
                report['profiles'][profile][mode]={
                    'cases':len(pairs),'delta_mean_cycles':delta,
                    'delta_histogram':{str(k):v for k,v in sorted(distribution.items())},
                    'old_prg_sha256':sha(oldblob),'candidate_prg_sha256':sha(newblob),
                    'signed_mixed_cases':signed_pairs}
                print('V1V5 FAST24 CLC',profile,mode,len(pairs),
                      'DELTA',delta,'DISTRIBUTION',dict(distribution),flush=True)
    report['total_negative_cycle_cells']=sum(
       sum(n for c,n in ((int(x),y) for x,y in m['delta_histogram'].items()) if c<0)
       for profile in report['profiles'].values() for m in profile.values())
    report['total_positive_cycle_cells']=sum(
       sum(n for c,n in ((int(x),y) for x,y in m['delta_histogram'].items()) if c>0)
       for profile in report['profiles'].values() for m in profile.values())
    report['status']=('PASS_STRICT_NO_REGRESSION_RESEARCH' if report['total_positive_cycle_cells']==0
                      else 'PASS_ARITHMETIC_WITH_TIMING_REGRESSIONS')
    assert report['total_negative_cycle_cells']>0
    if '--output' in sys.argv:
        p=Path(sys.argv[sys.argv.index('--output')+1])
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('V1V5 FAST24 RARE CARRY MOVED CLC SCREEN',report['status'],
          'PAIRED',report['unsigned_paired_cases'],flush=True)
if __name__=='__main__':main()
