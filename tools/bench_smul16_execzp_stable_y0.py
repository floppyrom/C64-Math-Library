#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILE="v2_pareto_fast"; IO=0xC000; MASK32=(1<<32)-1

def parse_api(path):
    out={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        k,v=[x.strip() for x in line.split("=",1)]
        if k.startswith("MATH_") and v.startswith("$"):
            try: out[k]=int(v[1:],16)
            except ValueError: pass
    return out
def load(prg,inc):
    b=prg.read_bytes(); a=b[0]|b[1]<<8
    mem=bytearray(65536); mem[a:a+len(b)-2]=b[2:]
    c=CPU(mem); c.d=0; api=parse_api(inc); c.call(api["MATH_INIT"],2_000_000)
    return c,api
def wr(m,a,v,n=2):
    for i in range(n): m[a+i]=(v>>(8*i))&255
def rd(m,a,n): return sum(m[a+i]<<(8*i) for i in range(n))
def si(v): return v-(1<<16) if v&0x8000 else v
def edges():
    s=1<<15; m=(1<<16)-1
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def canonical():
    e=edges(); pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x5A17_0110)
    pairs += [(rng.randrange(1<<16),rng.randrange(1<<16)) for _ in range(20000)]
    return pairs
def xneg():
    e=edges(); xs=[x for x in e if x&0x8000]; ys=e
    pairs=[(x,y) for x in xs for y in ys]
    rng=random.Random(0x5162)
    pairs += [(rng.randrange(0x8000,1<<16),rng.randrange(1<<16)) for _ in range(20000)]
    return pairs
def bench(cpu,entry,pairs,shr=False):
    total=0; lo=None; hi=None; errs=0; cyc=[]
    for x,y in pairs:
        wr(cpu.mem,IO,x); wr(cpu.mem,IO+4,y)
        bx=bytes(cpu.mem[IO:IO+2]); by=bytes(cpu.mem[IO+4:IO+6])
        c=cpu.call(entry,2_000_000)
        prod=(si(x)*si(y))&MASK32
        if shr:
            exp=(prod>>8)&0xFFFFFF; got=rd(cpu.mem,IO+8,3)
        else:
            exp=prod; got=rd(cpu.mem,IO+8,4)
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+2])!=bx or bytes(cpu.mem[IO+4:IO+6])!=by:
            errs+=1
            if errs<=8: print("ERROR",hex(x),hex(y),hex(got),hex(exp),cpu.c)
        total+=c; cyc.append(c); lo=c if lo is None else min(lo,c); hi=c if hi is None else max(hi,c)
    return {"cases":len(pairs),"errors":errs,"mean_cycles":total/len(pairs),"min_cycles":lo,"max_cycles":hi,"cycles":cyc}
def compare(base,cand,name,pairs,shr=False):
    b=bench(base[0],base[1][name],pairs,shr); c=bench(cand[0],cand[1][name],pairs,shr)
    ds=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    b.pop("cycles"); c.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(ds)/len(ds),"delta_min":min(ds),"delta_max":max(ds)}
def main():
    tmp=Path(tempfile.mkdtemp(prefix="smul16-execzp-"))
    try:
        build(PROFILE,ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc",tmp)
        def pair():
            return (
              load(ROOT/PROFILE/"resident"/f"math_{PROFILE}_game_math.prg",ROOT/PROFILE/"resident"/"math_api.inc"),
              load(tmp/f"math_{PROFILE}_source_built.prg",tmp/"math_api.inc")
            )
        base,cand=pair(); out={"canonical":compare(base,cand,"MATH_SMUL16",canonical())}
        base,cand=pair(); out["xneg_focus"]=compare(base,cand,"MATH_SMUL16",xneg())
        base,cand=pair(); out["shr8"]=compare(base,cand,"MATH_SMUL16_SHR8",canonical(),True)
        out["status"]="PASS" if all(v["candidate"]["errors"]==0 for v in out.values() if isinstance(v,dict) and "candidate" in v) else "FAIL"
        print(json.dumps(out,indent=2))
        if out["status"]!="PASS" or out["canonical"]["delta_mean_cycles"]>=0: raise SystemExit(1)
    finally:
        shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__": main()
