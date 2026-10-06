#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILES=["v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
REU={
 "v3_reu_512k": ROOT/"v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
 "v4_reu_16m": ROOT/"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu",
}
MASK=lambda n:(1<<n)-1

def signed(v,b): return v-(1<<b) if v&(1<<(b-1)) else v
def wr(mem,a,v,n=4):
    for i in range(n): mem[a+i]=(v>>(8*i))&255
def rd(mem,a,n): return sum(mem[a+i]<<(8*i) for i in range(n))
def api(path):
    out={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        n,v=[x.strip() for x in line.split("=",1)]
        if n.startswith("MATH_") and v.startswith("$"):
            try: out[n]=int(v[1:],16)
            except ValueError: pass
    return out
def edge(bits):
    m=MASK(bits); h=1<<(bits-1)
    vals=[0,1,2,3,7,15,16,31,63,127,128,255,h-2,h-1,h,h+1,m-2,m-1,m]
    return list(dict.fromkeys(v&m for v in vals))
def load(prg,api_path,reu_path=None):
    b=prg.read_bytes(); base=b[0]|b[1]<<8
    mem=bytearray(65536); mem[base:base+len(b)-2]=b[2:]
    reu=bytearray(reu_path.read_bytes()) if reu_path else None
    c=CPU(mem,reu=reu); c.d=0
    a=api(api_path); c.call(a["MATH_INIT"],2_000_000)
    return c,a
def bench(c,entry,pairs,shift16=False):
    io=0xC000; tot=0; lo=None; hi=None; errs=0; vec=[]
    for x,y in pairs:
        wr(c.mem,io,x); wr(c.mem,io+4,y)
        bx=bytes(c.mem[io:io+4]); by=bytes(c.mem[io+4:io+8])
        cy=c.call(entry,2_000_000); vec.append(cy)
        prod=(signed(x,32)*signed(y,32)) & MASK(64)
        if shift16:
            exp=(prod>>16)&MASK(48); got=rd(c.mem,io+8,6)
        else:
            exp=prod; got=rd(c.mem,io+8,8)
        if got!=exp or c.c!=0 or bytes(c.mem[io:io+4])!=bx or bytes(c.mem[io+4:io+8])!=by:
            errs+=1
            if errs<=5: print("ERROR",hex(x),hex(y),hex(got),hex(exp),c.c)
        tot+=cy; lo=cy if lo is None else min(lo,cy); hi=cy if hi is None else max(hi,cy)
    return {"cases":len(pairs),"errors":errs,"mean_cycles":tot/len(pairs),"min_cycles":lo,"max_cycles":hi},vec

def resident(profile):
    return load(ROOT/profile/"resident"/f"math_{profile}_game_math.prg",
                ROOT/profile/"resident"/"math_api.inc",REU.get(profile))

def candidate(profile,tmp):
    od=tmp/profile
    build(profile,ROOT/"relocatable_source"/profile/"math_config_reference.inc",od)
    rp=od/f"c64_math_{profile}_source_built.reu"
    return load(od/f"math_{profile}_source_built.prg",od/"math_api.inc",rp if rp.exists() else None)

def main():
    e=edge(32)
    canonical={}
    shared={}
    shared_pairs=[(x,y) for x in e for y in e]
    rngs=random.Random(0x51A32B0)
    shared_pairs += [(rngs.randrange(1<<32),rngs.randrange(1<<32)) for _ in range(19963)]
    shift_pairs=[(x,y) for x in e for y in e]
    rngd=random.Random(0x51632)
    shift_pairs += [(rngd.randrange(1<<32),rngd.randrange(1<<32)) for _ in range(4000)]
    tmp=Path(tempfile.mkdtemp(prefix="smul32-q1-all-"))
    try:
        shared_vecs={}
        for pi,p in enumerate(["v1_balanced"]+PROFILES+["v5_hybrid_lowzp"]):
            if p not in PROFILES: continue
            pairs=[(x,y) for x in e for y in e]
            rng=random.Random(0x5A17_0000+pi*0x100+32)
            pairs += [(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(2048)]
            b,ba=resident(p); c,ca=candidate(p,tmp)
            br,_=bench(b,ba["MATH_SMUL32"],pairs)
            cr,_=bench(c,ca["MATH_SMUL32"],pairs)
            canonical[p]={"baseline":br,"candidate":cr,"delta":cr["mean_cycles"]-br["mean_cycles"]}

            c2,ca2=candidate(p,tmp)
            sr,sv=bench(c2,ca2["MATH_SMUL32"],shared_pairs)
            shared[p]=sr; shared_vecs[p]=sv

            c3,ca3=candidate(p,tmp)
            dr,_=bench(c3,ca3["MATH_SMUL32_SHR16"],shift_pairs,True)
            canonical[p]["shr16_candidate"]=dr

        ref=shared_vecs[PROFILES[0]]
        identical=all(shared_vecs[p]==ref for p in PROFILES[1:])
        out={"canonical":canonical,"shared":{"profiles":shared,
             "cycle_vectors_identical":identical},"shared_cases":len(shared_pairs)}
        print(json.dumps(out,indent=2))
        if any(canonical[p]["candidate"]["errors"] or canonical[p]["shr16_candidate"]["errors"] for p in PROFILES):
            raise SystemExit("candidate correctness failure")
        if any(shared[p]["errors"] for p in PROFILES): raise SystemExit("shared correctness failure")
        if not identical: raise SystemExit("shared cycle vectors differ")
        if any(canonical[p]["delta"]>=0 for p in PROFILES): raise SystemExit("not faster in every profile")
        print("SMUL32 Q1 BOUNDED ALL-PROFILE PASS")
    finally:
        shutil.rmtree(tmp,ignore_errors=True)

if __name__=="__main__": main()
