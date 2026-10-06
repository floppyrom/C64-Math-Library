#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build
from build_hybrid import build as build_hybrid

IO=0xC000; MASK32=(1<<32)-1

def parse_api(path):
    out={}
    for line in Path(path).read_text().splitlines():
        if "=" not in line: continue
        k,v=[x.strip() for x in line.split("=",1)]
        if k.startswith("MATH_") and v.startswith("$"):
            try: out[k]=int(v[1:],16)
            except ValueError: pass
    return out
def load(prg,inc):
    b=Path(prg).read_bytes(); a=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[a:a+len(b)-2]=b[2:]
    c=CPU(mem); c.d=0; api=parse_api(inc); c.call(api["MATH_INIT"],2_000_000)
    return c,api
def wr(m,a,v,n=2):
    for i in range(n): m[a+i]=(v>>(8*i))&255
def rd(m,a,n=4): return sum(m[a+i]<<(8*i) for i in range(n))
def si(v): return v-(1<<16) if v&0x8000 else v
def edges():
    s=1<<15; m=(1<<16)-1
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def canonical(seed_index):
    e=edges(); pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x5A17_0000+seed_index*0x100+16)
    pairs += [(rng.randrange(1<<16),rng.randrange(1<<16)) for _ in range(4096)]
    return pairs
def focus(kind,n=20000):
    rng=random.Random(0x516100+sum(map(ord,kind)))
    lo=lambda:rng.randrange(0,0x8000); hi=lambda:rng.randrange(0x8000,0x10000)
    fx,fy={"PP":(lo,lo),"PN":(lo,hi),"NP":(hi,lo),"NN":(hi,hi)}[kind]
    return [(fx(),fy()) for _ in range(n)]
def bench(cpu,entry,pairs):
    total=0; mn=None; mx=None; err=0; cs=[]
    for x,y in pairs:
        wr(cpu.mem,IO,x); wr(cpu.mem,IO+4,y)
        bx=bytes(cpu.mem[IO:IO+2]); by=bytes(cpu.mem[IO+4:IO+6])
        cy=cpu.call(entry,2_000_000)
        got=rd(cpu.mem,IO+8); exp=(si(x)*si(y))&MASK32
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+2])!=bx or bytes(cpu.mem[IO+4:IO+6])!=by:
            err+=1
            if err<=5: print("ERROR",hex(x),hex(y),hex(got),hex(exp),cpu.c)
        total+=cy; cs.append(cy); mn=cy if mn is None else min(mn,cy); mx=cy if mx is None else max(mx,cy)
    return {"cases":len(pairs),"errors":err,"mean_cycles":total/len(pairs),"min_cycles":mn,"max_cycles":mx,"cycles":cs}
def comp(base,cand,pairs):
    b=bench(base[0],base[1]["MATH_SMUL16"],pairs); c=bench(cand[0],cand[1]["MATH_SMUL16"],pairs)
    ds=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    b.pop("cycles"); c.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(ds)/len(ds),"delta_min":min(ds),"delta_max":max(ds)}
def main():
    td=Path(tempfile.mkdtemp(prefix="smul16-v1-y0-"))
    try:
        # V1 candidate
        v1out=td/"v1"
        build("v1_balanced",ROOT/"relocatable_source/v1_balanced/math_config_reference.inc",v1out)
        base=load(ROOT/"v1_balanced/resident/math_v1_balanced_game_math.prg",ROOT/"v1_balanced/resident/math_api.inc")
        cand=load(v1out/"math_v1_balanced_source_built.prg",v1out/"math_api.inc")
        out={"v1_balanced":{"canonical":comp(base,cand,canonical(0))}}
        for k in ("PP","PN","NP","NN"):
            base=load(ROOT/"v1_balanced/resident/math_v1_balanced_game_math.prg",ROOT/"v1_balanced/resident/math_api.inc")
            cand=load(v1out/"math_v1_balanced_source_built.prg",v1out/"math_api.inc")
            out["v1_balanced"][k]=comp(base,cand,focus(k))
        # V5 hybrid candidate, rebuilt from changed V1 donor
        hroot=td/"hybrid"
        build_hybrid(ROOT/"relocatable_source/v5_hybrid_lowzp/math_config_reference.inc",hroot)
        hout=hroot/"math_v5_hybrid_lowzp_game_math.prg"
        hinc=hroot/"math_api.inc"
        base=load(ROOT/"v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg",ROOT/"v5_hybrid_lowzp/resident/math_api.inc")
        cand=load(hout,hinc)
        out["v5_hybrid_lowzp"]={"canonical":comp(base,cand,canonical(4))}
        ok=all(v["canonical"]["candidate"]["errors"]==0 and v["canonical"]["delta_mean_cycles"]<0 for v in out.values())
        out["status"]="PASS" if ok else "FAIL"
        print(json.dumps(out,indent=2))
        if not ok: raise SystemExit(1)
    finally:
        shutil.rmtree(td,ignore_errors=True)
if __name__=="__main__": main()
