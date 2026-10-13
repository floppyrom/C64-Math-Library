#!/usr/bin/env python3
"""Paired public UMUL24 tail-fallthrough 6502 source-build feasibility screen.

Never modify released PRGs. Exact current main resident is the pinned baseline.
Three stock fast profiles × reference+alternate relocated sources; source
diffs confined to previous UMUL24 core. Same-input cycles/ABI/product, plus
SMUL24 mixed-call and repeated-input retention checks.
"""
from pathlib import Path
import collections,hashlib,json,random,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm
import validate_source_build as testmod
from validate_unsigned_division import load as load_resident
from validate_umul24_directout import corpus as all_cases
PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
MASK=(1<<48)-1
def h(b):return hashlib.sha256(b).hexdigest()
def wr(mem,a,x,count):
    for j in range(count):mem[a+j]=(x>>(8*j))&255
def rd(mem,a,n):return sum(mem[a+j]<<(j*8) for j in range(n))
def call(cpu,api,io,x,y,signed=False):
    for address,num in ((io,x),(io+4,y)):wr(cpu.mem,address,num,3)
    prior=bytes(cpu.mem[io:io+3]+cpu.mem[io+4:io+7])
    cpu.d=0
    sp=cpu.sp
    n="MATH_SMUL24" if signed else "MATH_UMUL24"
    cyc=cpu.call(api[n],20000)
    product=rd(cpu.mem,io+8,6)
    a=(x-(1<<24) if x&(1<<23) else x) if signed else x
    b=(y-(1<<24) if y&(1<<23) else y) if signed else y
    assert product == (a*b)&MASK,(n,hex(x),hex(y),product,(a*b)&MASK)
    assert cpu.c==0 and cpu.sp==sp
    assert bytes(cpu.mem[io:io+3]+cpu.mem[io+4:io+7])==prior,(n,"input changed")
    return cyc,product
def main():
    original=ROOT/"RELEASE_STATUS.json"
    sha=json.loads(original.read_text())["reference_prg_sha256"]
    cases=all_cases()
    assert len(cases)==10324,len(cases)
    rng=random.Random(0xC6392400)
    mixed=cases[:256]+[cases[i] for i in rng.sample(range(len(cases)),512)]
    report={"status":"PASS_RESEARCH_NO_RELEASE_CHANGE","main_pins":{},
       "paired_calls":0,"signed_mixed_calls":0,"native_vice_calls":0,
       "scope":"UMUL24 in V2/V3/V4 only, unchanged V1/V5 donor",
       "profiles":{}}
    with tempfile.TemporaryDirectory(prefix="issue39_umul24_tail_") as tmp:
      base=Path(tmp)
      for profile in PROFILES:
        original_bytes=(ROOT/profile/"resident"/f"math_{profile}_game_math.prg").read_bytes()
        assert h(original_bytes)==sha[profile],(profile,"baseline pin")
        report["main_pins"][profile]=h(original_bytes)
        previous,old_api=load_resident(profile)
        results={}
        for mode in ("reference","alternate"):
            folder=base/mode/profile
            cfg=ROOT/"relocatable_source"/profile/f"math_config_{mode}.inc"
            man=asm.build(profile,cfg,folder)
            prg=(folder/man["output_prg"]).read_bytes()
            if mode=="reference":
                assert len(prg)==len(original_bytes),(profile,mode,"unexpected resident length")
            else:
                assert len(prg)>1024,(profile,mode,"truncated relocated resident")
            if mode=="reference":
                ld=int.from_bytes(prg[:2],"little")
                assert ld==int.from_bytes(original_bytes[:2],"little")==0x1000
                changed=[ld+i for i,(a,b) in enumerate(zip(original_bytes[2:],prg[2:])) if a!=b]
                assert changed and all(0x5600<=a<0x5900 for a in changed),(
                      profile,mode,"unowned code modification",list(map(hex,changed[:20])))
                report.setdefault("changed_bytes",{})[profile]={"count":len(changed),
                  "first":hex(min(changed)),"last":hex(max(changed))}
            new,api,io,man,_=testmod.load(profile,base/mode)
            assert man["output_sha256"]==h(prg)
            compare=cases if mode=="reference" else mixed
            hist=collections.Counter()
            for x,y in compare:
                former,oldp=call(previous,old_api,0xC000,x,y)
                current,newp=call(new,api,io,x,y)
                assert newp==oldp
                hist[current-former]+=1
            assert min(hist)<0 and max(hist)<=0,(profile,mode,"no strictly dominating hot improvement",hist)
            results[mode]={"cases":len(compare),"cycle_deltas":dict(sorted(hist.items())),
                 "mean_delta":sum(d*n for d,n in hist.items())/len(compare),
                 "output_prg_sha256":h(prg)}
            report["paired_calls"]+=2*len(compare)
            # Interleave SMUL24 with UMUL24; both share square tables but
            # not executable code, and their ZP lifetime may overlap.
            for x,y in mixed[:512]:
                a,b=call(new,api,io,x,y,True)
                c,d=call(new,api,io,x,y,False)
                # the signed private producer is out of change scope:
                aa,bb=call(previous,old_api,0xC000,x,y,True)
                assert a==aa and b==bb,(profile,mode,"signed producer changed")
                report["signed_mixed_calls"]+=3
            print("UMUL24 TAIL",profile,mode,"PAIRED",len(compare),
                  "MEAN_DELTA",results[mode]["mean_delta"],
                  "DIST",results[mode]["cycle_deltas"],flush=True)
        report["profiles"][profile]=results
    assert report["paired_calls"]==2*len(PROFILES)*(len(cases)+len(mixed))
    print("UMUL24 TAIL RESEARCH SOURCE ABI AND TIMING PASS",
           report["paired_calls"],"paired calls",flush=True)
    out=ROOT/"validation/review/ISSUE39_UMUL24_TAIL_FALLTHROUGH_SCREEN.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
