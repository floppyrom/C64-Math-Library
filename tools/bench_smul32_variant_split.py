#!/usr/bin/env python3
"""Compare V2 SMUL32 bounded-summation variants without modifying the branch."""
from pathlib import Path
import json, random, shutil, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILE="v2_pareto_fast"
SRC=ROOT/"relocatable_source"/PROFILE/"smul32_fast31_v29.inc"
MASK=(1<<64)-1

def section(s,a,b):
    i=s.index(a+":"); j=s.index(b+":",i)
    return s[i:j+len(b)+1]

def replace(s,a,b,v):
    i=s.index(a+":"); j=s.index(b+":",i)
    return s[:i]+v+s[j+len(b)+1:]

def edge_values():
    m=(1<<32)-1; h=1<<31
    vals=[0,1,2,3,7,15,16,31,63,127,128,255,h-2,h-1,h,h+1,m-2,m-1,m]
    return list(dict.fromkeys(x&m for x in vals))

def corpus(seed,count):
    e=edge_values(); p=[(x,y) for x in e for y in e]; r=random.Random(seed)
    p += [(r.randrange(1<<32),r.randrange(1<<32)) for _ in range(count)]
    return p

def api(path):
    d={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        a,b=[x.strip() for x in line.split("=",1)]
        if a.startswith("MATH_") and b.startswith("$"):
            try:d[a]=int(b[1:],16)
            except ValueError:pass
    return d

def load(prg,inc):
    b=prg.read_bytes(); a=b[0]|b[1]<<8; mem=bytearray(65536); mem[a:a+len(b)-2]=b[2:]
    c=CPU(mem); c.d=0; p=api(inc); c.call(p["MATH_INIT"],2_000_000); return c,p

def wr(mem,a,v,n=4):
    for i in range(n):mem[a+i]=(v>>(8*i))&255

def rd(mem,a,n=8):
    return sum(mem[a+i]<<(8*i) for i in range(n))

def si(v):
    return v-(1<<32) if v&(1<<31) else v

def bench(cpu,entry,pairs):
    total=0; err=0; mn=None; mx=None
    q={"q0":[0,0],"q1":[0,0],"q2":[0,0],"nn":[0,0]}
    for x,y in pairs:
        wr(cpu.mem,0xC000,x);wr(cpu.mem,0xC004,y)
        cy=cpu.call(entry,2_000_000)
        got=rd(cpu.mem,0xC008); exp=(si(x)*si(y))&MASK
        if got!=exp or cpu.c: err+=1
        total+=cy;mn=cy if mn is None else min(mn,cy);mx=cy if mx is None else max(mx,cy)
        k=("nn" if x&(1<<31) and y&(1<<31) else
           "q2" if x&(1<<31) else "q1" if y&(1<<31) else "q0")
        q[k][0]+=cy;q[k][1]+=1
    return {"cases":len(pairs),"errors":err,"mean":total/len(pairs),"min":mn,"max":mx,
            "quadrants":{k:v[0]/v[1] for k,v in q.items() if v[1]}}

def main():
    candidate=SRC.read_text()
    baseline=subprocess.check_output(["git","show","origin/main:"+str(SRC.relative_to(ROOT))],text=True)
    q1=section(candidate,"S32V28_q1_summation","S32V28_q1_cg_code_end")
    q2=section(candidate,"S32V28_q2_summation","S32V28_q2_cg_code_end")
    variants={
      "baseline":baseline,
      "q1_only":replace(baseline,"S32V28_q1_summation","S32V28_q1_cg_code_end",q1),
      "q2_only":replace(baseline,"S32V28_q2_summation","S32V28_q2_cg_code_end",q2),
      "both":candidate,
    }
    p1=corpus(0x5A170120,2048)
    p2=corpus(0x5A170020,19963)
    original=SRC.read_text(); tmp=Path(tempfile.mkdtemp(prefix="smul32-split-")); out={}
    try:
      for name,text in variants.items():
        SRC.write_text(text)
        od=tmp/name
        build(PROFILE,ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc",od)
        c,p=load(od/f"math_{PROFILE}_source_built.prg",od/"math_api.inc")
        a=bench(c,p["MATH_SMUL32"],p1)
        c,p=load(od/f"math_{PROFILE}_source_built.prg",od/"math_api.inc")
        b=bench(c,p["MATH_SMUL32"],p2)
        out[name]={"canonical":a,"shared":b}
      print(json.dumps(out,indent=2))
      if out["both"]["canonical"]["errors"] or out["both"]["shared"]["errors"]:
        raise SystemExit("both candidate failed correctness")
    finally:
      SRC.write_text(original);shutil.rmtree(tmp,ignore_errors=True)

if __name__=="__main__":main()
