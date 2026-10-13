#!/usr/bin/env python3
"""Issue39 V2 UMUL8 same-size in-place source-built direct-output screen.

The public wrapper plus the shifted ($52FE..$5322) 37-byte private arithmetic
kernel replace the original public wrapper and original ($5300..$5322) kernel.
The 2-byte prefix must be exact zero padding in the published resident.
Tests both relocation maps, full 56-entry mixed API validator and exhaustive
all-input 8x8 arithmetic/ABI. No published binary or release status is changed.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,random,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm,validate_source_build as check
from validate_unsigned_division import load as shipped_load, wr, rd

P='v2_pareto_fast'
N=65536
SEED=0x3916
def sha(b):return hashlib.sha256(b).hexdigest()

def corpus(seed=SEED,n=4096):
    g=random.Random(seed)
    edge=[0,1,2,3,7,15,16,31,63,127,128,254,255]
    samples=[(x,y) for x in edge for y in edge]
    samples.extend((g.randrange(256),g.randrange(256)) for _ in range(n))
    return samples

def public_one(cpu,entry,io,x,y):
    wr(cpu.mem,io,x+0x5500,2)
    wr(cpu.mem,io+4,y+0xAA00,2)
    cpu.mem[io+8:io+12]=bytes([0xAB,0xCD,0x93,0x71])
    cpu.d=0
    cpu.c=(x^y)&1
    sp=cpu.sp
    cycles=cpu.call(entry,3000)
    got=rd(cpu.mem,io+8,2)
    assert got==x*y,(hex(entry),x,y,got,x*y)
    assert rd(cpu.mem,io,2)==x+0x5500
    assert rd(cpu.mem,io+4,2)==y+0xAA00
    assert cpu.c==0 and cpu.sp==sp
    assert bytes(cpu.mem[io+10:io+12])==bytes([0x93,0x71])
    return cycles

def trial():
    status=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    oldprg=(ROOT/P/'resident'/f'math_{P}_game_math.prg').read_bytes()
    assert sha(oldprg)==status['reference_prg_sha256'][P]
    assert oldprg[2+0x52FE-0x1000:2+0x5300-0x1000]==b'\x00\x00',(
       'only valid if prior 2 bytes are zero padding')
    original,oldapi=shipped_load(P)
    report={'status':'PASS_SOURCE_RESEARCH_NO_RELEASE',
      'current_v2_resident_sha256':sha(oldprg),
      'reference':{},'alternate':{},
      'native_vice_calls':0,'extra_normal_zp_bytes':0,
      'extra_resident_prg_bytes':0,'V2_only':True,
      'production_source_regeneration_pending':True}
    with tempfile.TemporaryDirectory(prefix='issue39_umul8_source_') as root:
        root=Path(root)
        for kind in ('reference','alternate'):
            cfg=ROOT/'relocatable_source'/P/('math_config_'+kind+'.inc')
            dest=root/kind/P
            man=asm.build(P,cfg,dest)
            prg=(dest/man['output_prg']).read_bytes()
            assert len(prg)==len(oldprg),('resident grew',kind,len(prg),len(oldprg))
            expanded=asm.preprocess(ROOT/'relocatable_source'/P/'math_relocatable.asm',cfg)
            _,lab,const=asm.Assembler().assemble(expanded)
            assert lab['UMUL8_DIRECT_PRIVATE_END']-lab['UMUL8_DIRECT_PRIVATE']==37
            assert lab['UMUL8_DIRECT_PRIVATE']==const['REG_KERNEL']+0x12FE
            assert lab['UMUL8_DIRECT_PRIVATE_END']==const['REG_KERNEL']+0x1323
            assert lab['UMUL8_DIRECT_PUBLIC_ENTRY']==const['MATH_UMUL8']
            if kind=='reference':
                delta=[0x1000+i for i,(a,b) in enumerate(zip(oldprg[2:],prg[2:])) if a!=b]
                assert delta and all(
                    (0x3000<=a<0x3013) or (0x52FE<=a<0x5323)
                    for a in delta),('out-of-island modifications',list(map(hex,delta[:30])))
                report['reference']['changed_bytes']=len(delta)
            c,api,io,_,_=check.load(P,root/kind)
            destentry=api['MATH_UMUL8']
            assert destentry==const['MATH_UMUL8']
            # Exhaustive source-built on reference; representative edge/random
            # operands on alternate relocated map.
            vals=((n&255,n>>8) for n in range(N)) if kind=='reference' else iter(corpus())
            calls=0;cy=0;diffs={}
            for x,y in vals:
                newcycles=public_one(c,destentry,io,x,y)
                if kind=='reference':
                    oldcycles=public_one(original,oldapi['MATH_UMUL8'],0xC000,x,y)
                    d=newcycles-oldcycles
                    diffs[d]=diffs.get(d,0)+1
                cy+=newcycles;calls+=1
            if kind=='reference':
                assert diffs=={-6:65536},('unexpected time distribution',diffs)
            report[kind].update(public_pairs=calls,
              mean_candidate_cycles=cy/calls,
              candidate_sha256=sha(prg),
              delta_histogram={str(k):v for k,v in sorted(diffs.items())},
              same_resident_size=True,code_bytes=37)
            print(P,kind,'SOURCE-OWNED UMUL8 PASS',calls,
                  'means',round(cy/calls,6),'diffs',diffs,flush=True)
            # Mixed API suite discovers any hidden callers into the original
            # $5300 native kernel or resource collisions with other families.
            v=check.validate(P,root/kind)
            assert v['status']=='PASS' and v['public_entries_executed']>=56
            report[kind]['full_abi_calls']=v['machine_calls']
            report[kind]['public_entries_executed']=v['public_entries_executed']
            print(P,kind,'ALL PUBLIC APIs PASS',v['machine_calls'],flush=True)
    assert report['reference']['mean_candidate_cycles']<78.5
    return report

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path)
    args=ap.parse_args()
    out=trial()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('ISQ39 V2 UMUL8 SOURCE-COMPACT PUBLIC DIRECT OUTPUT VALIDATED',flush=True)

if __name__=='__main__':main()
