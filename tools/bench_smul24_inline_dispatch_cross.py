#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILES=["v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
IO=0xC000; MASK48=(1<<48)-1
REU={
 "v3_reu_512k":ROOT/"v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
 "v4_reu_16m":ROOT/"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu",
}

def api(path):
    out={}
    for line in Path(path).read_text().splitlines():
        if "=" not in line: continue
        k,v=[x.strip() for x in line.split("=",1)]
        if k.startswith("MATH_") and v.startswith("$"):
            try:out[k]=int(v[1:],16)
            except ValueError:pass
    return out

def load(prg,inc,reu=None):
    b=Path(prg).read_bytes();a=b[0]|b[1]<<8
    m=bytearray(65536);m[a:a+len(b)-2]=b[2:]
    rb=bytearray(Path(reu).read_bytes()) if reu else None
    c=CPU(m,reu=rb);c.d=0;ap=api(inc);c.call(ap["MATH_INIT"],2_000_000)
    return c,ap
def wr(m,a,v):
    for i in range(3):m[a+i]=(v>>(8*i))&255
def rd(m,a):return sum(m[a+i]<<(8*i) for i in range(6))
def si(v):return v-(1<<24) if v&0x800000 else v
def edges():
    s=1<<23;m=(1<<24)-1
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def canonical(pi):
    e=edges();p=[(x,y) for x in e for y in e]
    r=random.Random(0x5A17_0000+pi*0x100+24)
    p += [(r.randrange(1<<24),r.randrange(1<<24)) for _ in range(2048)]
    return p
def quadrant(kind,n=6000):
    r=random.Random(0x524100+sum(map(ord,kind)))
    lo=lambda:r.randrange(0,0x800000);hi=lambda:r.randrange(0x800000,1<<24)
    fx,fy={"PP":(lo,lo),"PN":(lo,hi),"NP":(hi,lo),"NN":(hi,hi)}[kind]
    return [(fx(),fy()) for _ in range(n)]
def bench(cpu,entry,pairs):
    total=0;mn=None;mx=None;err=0;cy=[]
    for x,y in pairs:
        wr(cpu.mem,IO,x);wr(cpu.mem,IO+4,y);bx=bytes(cpu.mem[IO:IO+3]);by=bytes(cpu.mem[IO+4:IO+7])
        c=cpu.call(entry,2_000_000);got=rd(cpu.mem,IO+8);exp=(si(x)*si(y))&MASK48
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+3])!=bx or bytes(cpu.mem[IO+4:IO+7])!=by:
            err+=1
            if err<=5:print("ERROR",hex(x),hex(y),hex(got),hex(exp),cpu.c)
        total+=c;cy.append(c);mn=c if mn is None else min(mn,c);mx=c if mx is None else max(mx,c)
    return {"cases":len(pairs),"errors":err,"mean_cycles":total/len(pairs),"min_cycles":mn,"max_cycles":mx,"cycles":cy}
def comp(b,c,pairs):
    x=bench(b[0],b[1]["MATH_SMUL24"],pairs);y=bench(c[0],c[1]["MATH_SMUL24"],pairs)
    d=[q-p for p,q in zip(x["cycles"],y["cycles"])]
    x.pop("cycles");y.pop("cycles")
    return {"baseline":x,"candidate":y,"delta_mean_cycles":sum(d)/len(d),"delta_min":min(d),"delta_max":max(d)}
def main():
    res={}
    for pi,p in enumerate(PROFILES):
        td=Path(tempfile.mkdtemp(prefix="s24inline-"+p+"-"))
        try:
            man=build(p,ROOT/"relocatable_source"/p/"math_config_reference.inc",td)
            bp=ROOT/p/"resident"/f"math_{p}_game_math.prg";bi=ROOT/p/"resident"/"math_api.inc"
            cp=td/man["output_prg"];ci=td/"math_api.inc"; cr=(td/man["output_reu"]) if man.get("output_reu") else None
            def pair():return load(bp,bi,REU.get(p)),load(cp,ci,cr)
            b,c=pair();r={"canonical":comp(b,c,canonical(pi))}
            for q in ("PP","PN","NP","NN"):
                b,c=pair();r[q]=comp(b,c,quadrant(q))
            r["status"]="PASS" if all(v["candidate"]["errors"]==0 for v in r.values() if isinstance(v,dict) and "candidate" in v) else "FAIL"
            if r["status"]!="PASS" or r["canonical"]["delta_mean_cycles"]>=0:raise SystemExit((p,r))
            res[p]=r
        finally:shutil.rmtree(td,ignore_errors=True)
    print(json.dumps({"status":"PASS","profiles":res},indent=2))
if __name__=="__main__":main()
