#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILES=["v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m"]; IO=0xC000; MASK48=(1<<48)-1

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
def wr(m,a,v,n=3):
    for i in range(n): m[a+i]=(v>>(8*i))&255
def rd(m,a,n=6): return sum(m[a+i]<<(8*i) for i in range(n))
def si(v): return v-(1<<24) if v&0x800000 else v
def edges():
    s=1<<23; m=(1<<24)-1
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def canonical(pi):
    e=edges(); pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x5A17_0000+pi*0x100+24)
    pairs += [(rng.randrange(1<<24),rng.randrange(1<<24)) for _ in range(2048)]
    return pairs
def q2():
    e=edges(); xs=[x for x in e if x&0x800000]; ys=[y for y in e if not y&0x800000]
    pairs=[(x,y) for x in xs for y in ys]
    rng=random.Random(0x52424)
    pairs += [(rng.randrange(0x800000,1<<24),rng.randrange(0,0x800000)) for _ in range(20000)]
    return pairs
def bench(cpu,entry,pairs):
    total=0; lo=None; hi=None; errs=0; cyc=[]
    for x,y in pairs:
        wr(cpu.mem,IO,x); wr(cpu.mem,IO+4,y)
        bx=bytes(cpu.mem[IO:IO+3]); by=bytes(cpu.mem[IO+4:IO+7])
        c=cpu.call(entry,2_000_000); got=rd(cpu.mem,IO+8)
        exp=(si(x)*si(y))&MASK48
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+3])!=bx or bytes(cpu.mem[IO+4:IO+7])!=by:
            errs+=1
            if errs<=8: print("ERROR",hex(x),hex(y),hex(got),hex(exp),cpu.c)
        total+=c; cyc.append(c); lo=c if lo is None else min(lo,c); hi=c if hi is None else max(hi,c)
    return {"cases":len(pairs),"errors":errs,"mean_cycles":total/len(pairs),"min_cycles":lo,"max_cycles":hi,"cycles":cyc}
def comp(base,cand,pairs):
    b=bench(base[0],base[1]["MATH_SMUL24"],pairs)
    c=bench(cand[0],cand[1]["MATH_SMUL24"],pairs)
    ds=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    b.pop("cycles"); c.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(ds)/len(ds),"delta_min":min(ds),"delta_max":max(ds)}
def main():
    results={}
    for pi,profile in enumerate(PROFILES):
        tmp=Path(tempfile.mkdtemp(prefix="smul24-q2-"+profile+"-"))
        try:
            build(profile,ROOT/"relocatable_source"/profile/"math_config_reference.inc",tmp)
            base=load(ROOT/profile/"resident"/f"math_{profile}_game_math.prg",ROOT/profile/"resident"/"math_api.inc")
            cand=load(tmp/f"math_{profile}_source_built.prg",tmp/"math_api.inc")
            out={"canonical":comp(base,cand,canonical(pi))}
            base=load(ROOT/profile/"resident"/f"math_{profile}_game_math.prg",ROOT/profile/"resident"/"math_api.inc")
            cand=load(tmp/f"math_{profile}_source_built.prg",tmp/"math_api.inc")
            out["q2_focus"]=comp(base,cand,q2())
            out["status"]="PASS" if not out["canonical"]["candidate"]["errors"] and not out["q2_focus"]["candidate"]["errors"] else "FAIL"
            results[profile]=out
            if out["status"]!="PASS" or out["canonical"]["delta_mean_cycles"]>=0: raise SystemExit(1)
        finally:
            shutil.rmtree(tmp,ignore_errors=True)
    print(json.dumps({"status":"PASS","profiles":results},indent=2))
if __name__=="__main__": main()
