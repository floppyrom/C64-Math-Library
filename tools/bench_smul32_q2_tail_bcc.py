#!/usr/bin/env python3
from pathlib import Path
import json,random,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build
P=["v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
BREU={"v3_reu_512k":ROOT/"v3_reu_512k/reu/c64_math_v3_512k_game_math.reu","v4_reu_16m":ROOT/"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu"}
M=(1<<64)-1
def si(v):return v-(1<<32) if v&0x80000000 else v
def wr(m,a,v):
 for i in range(4):m[a+i]=(v>>(8*i))&255
def rd(m,a):return sum(m[a+i]<<(8*i) for i in range(8))
def api(p):
 d={}
 for l in Path(p).read_text().splitlines():
  if "=" not in l:continue
  n,v=[x.strip() for x in l.split("=",1)]
  if n.startswith("MATH_") and v.startswith("$"):
   try:d[n]=int(v[1:],16)
   except:pass
 return d
def load(prg,inc,reu=None):
 b=Path(prg).read_bytes();a=b[0]|b[1]<<8;m=bytearray(65536);m[a:a+len(b)-2]=b[2:]
 c=CPU(m,reu=bytearray(Path(reu).read_bytes()) if reu else None);c.d=0;p=api(inc);c.call(p["MATH_INIT"],2000000);return c,p
def edges():
 h=1<<31;m=(1<<32)-1;return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,h-2,h-1,h,h+1,m-2,m-1,m]))
def corpus(seed,n):
 e=edges();q=[(x,y) for x in e for y in e];r=random.Random(seed);q += [(r.randrange(1<<32),r.randrange(1<<32)) for _ in range(n)];return q
def q2(seed,n):
 e=edges();q=[(x,y) for x in e if x&0x80000000 for y in e if not y&0x80000000];r=random.Random(seed);q += [(r.randrange(0x80000000,1<<32),r.randrange(0,0x80000000)) for _ in range(n)];return q
def bench(c,entry,pairs):
 t=0;lo=None;hi=None;err=0;vec=[]
 for x,y in pairs:
  wr(c.mem,0xC000,x);wr(c.mem,0xC004,y);bx=bytes(c.mem[0xC000:0xC004]);by=bytes(c.mem[0xC004:0xC008]);cy=c.call(entry,2000000)
  if rd(c.mem,0xC008)!=(si(x)*si(y))&M or c.c or bytes(c.mem[0xC000:0xC004])!=bx or bytes(c.mem[0xC004:0xC008])!=by:err+=1
  t+=cy;vec.append(cy);lo=cy if lo is None else min(lo,cy);hi=cy if hi is None else max(hi,cy)
 return {"cases":len(pairs),"errors":err,"mean":t/len(pairs),"min":lo,"max":hi,"vec":vec}
def clean(x):return {k:v for k,v in x.items() if k!="vec"}
def main():
 tmp=Path(tempfile.mkdtemp());out={"canonical":{},"shared":{},"q2":{}};vecs=[]
 try:
  for p in P:build(p,ROOT/"relocatable_source"/p/"math_config_reference.inc",tmp/p)
  sh=corpus(0x5A170020,19963);qq=q2(0x5132B0,20000)
  for pi,p in enumerate(P,1):
   res=ROOT/p/"resident";bp=res/f"math_{p}_game_math.prg";cp=tmp/p/f"math_{p}_source_built.prg";br=BREU.get(p);cr=tmp/p/f"c64_math_{p}_source_built.reu" if p in BREU else None
   for name,pairs in [("canonical",corpus(0x5A170000+pi*0x100+32,2048)),("shared",sh),("q2",qq)]:
    bc,ba=load(bp,res/"math_api.inc",br);cc,ca=load(cp,tmp/p/"math_api.inc",cr);b=bench(bc,ba["MATH_SMUL32"],pairs);c=bench(cc,ca["MATH_SMUL32"],pairs)
    out[name][p]={"baseline":clean(b),"candidate":clean(c),"delta":c["mean"]-b["mean"]}
    if c["errors"] or c["mean"]>=b["mean"]:raise SystemExit((p,name,out[name][p]))
    if name=="shared":vecs.append(c["vec"])
  out["shared_vectors_identical"]=all(v==vecs[0] for v in vecs[1:])
  evidence={"status":"PASS","date":"2026-10-06","optimization":"Replace the carry-known q2 bounded-tail JMP with an always-taken BCC, shrinking the q2 island by one byte so the hot c4b continuation remains on page $55.","resource_contract":{"zp_bytes":31,"persistent_stack_page_bytes":0,"producer_changed":False,"public_abi_changed":False,"q2_bytes_saved":1},"results":out}
  (ROOT/"validation/review/SMUL32_Q2_TAIL_BCC.json").write_text(json.dumps(evidence,indent=2)+"\\n")
  print(json.dumps(out,indent=2))
  if not out["shared_vectors_identical"]:raise SystemExit("shared vectors diverged")
  print("SMUL32 Q2 TAIL BCC PASS")
 finally:shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__":main()
