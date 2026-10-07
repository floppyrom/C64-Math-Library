#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILE="v2_pareto_fast"; IO=0xC000; MASK48=(1<<48)-1

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
    b=Path(prg).read_bytes(); a=b[0]|b[1]<<8
    mem=bytearray(65536); mem[a:a+len(b)-2]=b[2:]
    c=CPU(mem); c.d=0; api=parse_api(Path(inc)); c.call(api["MATH_INIT"],2_000_000)
    return c,api

def wr(m,a,v,n=3):
    for i in range(n):m[a+i]=(v>>(8*i))&255
def rd(m,a,n=6):return sum(m[a+i]<<(8*i) for i in range(n))
def si(v):return v-(1<<24) if v&0x800000 else v

def edges():
    s=1<<23;m=(1<<24)-1
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))

def canonical():
    e=edges();p=[(x,y) for x in e for y in e]
    r=random.Random(0x5A170118);p += [(r.randrange(1<<24),r.randrange(1<<24)) for _ in range(10000)]
    return p

def quadrant(kind,n=10000):
    r=random.Random(0x524000+sum(map(ord,kind)))
    lo=lambda:r.randrange(0,0x800000); hi=lambda:r.randrange(0x800000,1<<24)
    fs={"PP":(lo,lo),"PN":(lo,hi),"NP":(hi,lo),"NN":(hi,hi)}
    fx,fy=fs[kind]; return [(fx(),fy()) for _ in range(n)]

def bench(cpu,entry,pairs):
    total=0;lo=None;hi=None;errs=0;cyc=[]
    for x,y in pairs:
        wr(cpu.mem,IO,x);wr(cpu.mem,IO+4,y)
        bx=bytes(cpu.mem[IO:IO+3]);by=bytes(cpu.mem[IO+4:IO+7])
        c=cpu.call(entry,2_000_000); got=rd(cpu.mem,IO+8); exp=(si(x)*si(y))&MASK48
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+3])!=bx or bytes(cpu.mem[IO+4:IO+7])!=by:
            errs+=1
            if errs<=8: print("ERROR",hex(x),hex(y),hex(got),hex(exp),cpu.c)
        total+=c;cyc.append(c);lo=c if lo is None else min(lo,c);hi=c if hi is None else max(hi,c)
    return {"cases":len(pairs),"errors":errs,"mean_cycles":total/len(pairs),"min_cycles":lo,"max_cycles":hi,"cycles":cyc}

def compare(base,cand,pairs):
    b=bench(base[0],base[1]["MATH_SMUL24"],pairs); c=bench(cand[0],cand[1]["MATH_SMUL24"],pairs)
    ds=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    b.pop("cycles");c.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(ds)/len(ds),"delta_min":min(ds),"delta_max":max(ds)}

def main():
    td=Path(tempfile.mkdtemp(prefix="smul24-inline-"))
    try:
        man=build(PROFILE,ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc",td)
        baseprg=ROOT/PROFILE/"resident"/f"math_{PROFILE}_game_math.prg"
        baseinc=ROOT/PROFILE/"resident"/"math_api.inc"
        candprg=td/man["output_prg"];candinc=td/"math_api.inc"
        def pair(): return load(baseprg,baseinc),load(candprg,candinc)
        b,c=pair();out={"canonical":compare(b,c,canonical())}
        for q in ("PP","PN","NP","NN"):
            b,c=pair();out[q]=compare(b,c,quadrant(q))
        out["status"]="PASS" if all(v["candidate"]["errors"]==0 for v in out.values() if isinstance(v,dict) and "candidate" in v) else "FAIL"
        print(json.dumps(out,indent=2))
        if out["status"]!="PASS" or out["canonical"]["delta_mean_cycles"]>=0: raise SystemExit(1)
    finally:
        shutil.rmtree(td,ignore_errors=True)

if __name__=="__main__":main()
