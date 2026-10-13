#!/usr/bin/env python3
"""Strict standalone-to-source integration screen for the 16-bit root seed trial.

No shipped PRGs or canonical release metadata modified. Source-assemble stock
V1/V2/V3 on both reference and alternate maps, constrain generated writes to
the original ISQRT16 island and verify mixed public ISQRT16/ISQRT32 results.
An exact public ABI and resource proof, not native VICE certification.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,math,random,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm
import validate_source_build as sourcecheck
from validate_unsigned_division import load as shipped_load,wr,rd
from screen_issue39_isqrt16_seed_square import samples16,samples32,IS16,IS32,N,Z

PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k')
LIMITS={'v1_balanced':(0xC8DB,0xCA24),
        'v2_pareto_fast':(0xC836,0xC966),
        'v3_reu_512k':(0xC841,0xC971)}
def sha(b):return hashlib.sha256(b).hexdigest()
def sample(cpu,entry,n,width):
    count=width//8
    wr(cpu.mem,N,n,count)
    inp=bytes(cpu.mem[N:N+count])
    wr(cpu.mem,Z,0xA6B5D4C3,4)
    cpu.d=0
    sp=cpu.sp
    cyc=cpu.call(entry,2_000_000)
    got=rd(cpu.mem,Z,2)
    assert got==math.isqrt(n),(width,hex(n),'sqrt',got,math.isqrt(n))
    assert bytes(cpu.mem[N:N+count])==inp,(width,hex(n),'N modified')
    assert bytes(cpu.mem[Z+2:Z+4])==bytes((0xB5,0xA6)),(width,hex(n),'Z sentinel')
    assert cpu.c==0 and cpu.sp==sp,(width,hex(n),'carry/stack')
    return cyc,got
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path)
    args=ap.parse_args()
    report={'status':'PASS_RESEARCH_ONLY_SOURCE_NOT_RELEASED',
      'native_vice_calls':0,'resource_growth_outside_isqrt16_island':0,
      'normal_zp_growth':0,'source_built_cases':0,'profiles':{},
      'v5_hybrid_not_yet_integrated':True}
    cases16=samples16(1536)
    cases32=samples32(768)
    with tempfile.TemporaryDirectory(prefix='issue39_root_source_') as d:
        root=Path(d)
        for p in PROFILES:
            base,entries=shipped_load(p)
            ref_manifest=None
            record={}
            for mode in ('reference','alternate'):
                cfg=ROOT/'relocatable_source'/p/('math_config_'+mode+'.inc')
                dest=root/mode/p
                manifest=asm.build(p,cfg,dest)
                assert set(entries).issubset(set(manifest['public_entries'])),(p,'API count')
                import re
                parseaddr=lambda x:int(x[1:],16)
                assert parseaddr(manifest['public_entries']['MATH_ISQRT16'])==(
                    IS16 if mode=='reference' else
                    parseaddr(manifest['public_entries']['MATH_ISQRT16']))
                assert 'relocatable_source/game_math/isqrt16_seed_square_trial.inc' in manifest['included_sources']
                expanded=asm.preprocess(ROOT/'relocatable_source'/p/'math_relocatable.asm',cfg)
                mem,labels,const=asm.Assembler().assemble(expanded)
                lo=labels['IS16_FAST_START']
                hi=labels['IS16_FAST_END']
                lim=const['IS16_FAST_LIMIT']
                assert hi<=lim,(p,mode,'seed out of original space',hex(hi),hex(lim))
                assert hi-lo>=256 and hi-lo<=304,(p,mode,'unacceptable code+table budget',hi-lo)
                if mode=='reference':
                    assert lo==LIMITS[p][0] and lim==LIMITS[p][1],(p,'reference origin',hex(lo),hex(lim))
                    oldprg=ROOT/p/'resident'/('math_'+p+'_game_math.prg')
                    before=oldprg.read_bytes()
                    after=(dest/manifest['output_prg']).read_bytes()
                    assert len(before)==len(after),(p,'resident size drift')
                    start=int.from_bytes(before[:2],'little')
                    assert start==int.from_bytes(after[:2],'little')
                    changed=[start+i for i,(a,b) in enumerate(zip(before[2:],after[2:])) if a!=b]
                    assert changed and all(lo<=addr<lim for addr in changed),(p,'source writes beyond root island',changed[:10])
                    assert sha(before)!=sha(after)
                    record['changed_bytes']=len(changed)
                    record['original_sha256']=sha(before)
                test,API,io,M,_=sourcecheck.load(p,root/mode)
                api16=API['MATH_ISQRT16'];api32=API['MATH_ISQRT32']
                original_cycles=candidate_cycles=[0,0] if mode=='reference' else None
                for width,values,entry in ((16,cases16,api16),(32,cases32,api32)):
                    totals=[0,0]
                    for n in values:
                        a,actual=sample(test,entry,n,width)
                        totals[1]+=a
                        if mode=='reference':
                            b,expected=sample(base,entries['MATH_ISQRT16' if width==16 else 'MATH_ISQRT32'],n,width)
                            assert expected==actual
                            totals[0]+=b
                    record[mode+('_isqrt16' if width==16 else '_isqrt32')]={
                      'cases':len(values),'source_mean_cycles':totals[1]/len(values),
                      'baseline_mean_cycles':totals[0]/len(values) if mode=='reference' else None,
                      'source_minus_baseline':(totals[1]-totals[0])/len(values) if mode=='reference' else None}
                    report['source_built_cases']+=len(values)
                record[mode+'_root_island']=dict(start=hex(lo),end=hex(hi),budget_end=hex(lim),
                                                 candidate_bytes=hi-lo,available_bytes=lim-lo)
                record[mode+'_resident_sha256']=manifest['output_sha256']
                print(p,mode,'CODE+SEED',hi-lo,'AVAILABLE',lim-lo,'16 mean',
                      record[mode+'_isqrt16']['source_mean_cycles'],'32 mean',
                      record[mode+'_isqrt32']['source_mean_cycles'],flush=True)
            report['profiles'][p]=record
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('ISQRT16 SAME-ISLAND SOURCE BUILD VALIDATED',report['source_built_cases'],flush=True)
if __name__=='__main__':main()
