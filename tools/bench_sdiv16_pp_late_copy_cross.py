#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILES=["v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
REU={
 "v3_reu_512k":ROOT/"v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
 "v4_reu_16m":ROOT/"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu",
}
N=0xC010;D=0xC014;Q=0xC018;R=0xC01C

def parse_api(path):
 out={}
 for line in path.read_text().splitlines():
  if "=" not in line: continue
  k,v=[x.strip() for x in line.split("=",1)]
  if k.startswith("MATH_") and v.startswith("$"):
   try: out[k]=int(v[1:],16)
   except ValueError: pass
 return out
def load(prg,inc,profile):
 b=prg.read_bytes();a=b[0]|b[1]<<8
 mem=bytearray(65536);mem[a:a+len(b)-2]=b[2:]
 reu=bytearray(REU[profile].read_bytes()) if profile in REU else None
 c=CPU(mem,reu=reu);c.d=0;api=parse_api(inc);c.call(api["MATH_INIT"],2_000_000)
 return c,api
def wr(m,a,v):m[a]=v&255;m[a+1]=(v>>8)&255
def rd(m,a):return m[a]|m[a+1]<<8
def si(v):return v-65536 if v&0x8000 else v
def expected(n,d):
 ns,ds=si(n),si(d)
 if ds==0:return 0,0,1
 q=abs(ns)//abs(ds)
 if (ns<0)^(ds<0):q=-q
 r=ns-q*ds
 return q&0xffff,r&0xffff,0
def edge():
 return [0,1,2,3,7,15,16,31,63,127,128,255,0x7ffe,0x7fff,0x8000,0x8001,0xfffd,0xfffe,0xffff]
def corpus():
 e=edge();p=[(n,d) for n in e for d in e]
 rng=random.Random(0xD16C2026)
 p += [(rng.randrange(65536),rng.randrange(65536)) for _ in range(20000)]
 p += [(rng.randrange(65536),0) for _ in range(256)]
 return p
def pp():
 e=[v for v in edge() if not v&0x8000];p=[(n,d) for n in e for d in e]
 rng=random.Random(0xD16F2026)
 p += [(rng.randrange(0x8000),rng.randrange(1,0x8000)) for _ in range(20000)]
 return p
def bench(cpu,entry,pairs):
 total=0;mi=None;ma=None;errs=0;cy=[]
 for n,d in pairs:
  wr(cpu.mem,N,n);wr(cpu.mem,D,d);bn=bytes(cpu.mem[N:N+2]);bd=bytes(cpu.mem[D:D+2])
  c=cpu.call(entry,4_000_000);eq,er,ec=expected(n,d);gq=rd(cpu.mem,Q);gr=rd(cpu.mem,R)
  if (gq,gr,cpu.c)!=(eq,er,ec) or bytes(cpu.mem[N:N+2])!=bn or bytes(cpu.mem[D:D+2])!=bd:
   errs+=1
   if errs<=4:print("ERROR",hex(n),hex(d),hex(gq),hex(gr),cpu.c,hex(eq),hex(er),ec)
  total+=c;cy.append(c);mi=c if mi is None else min(mi,c);ma=c if ma is None else max(ma,c)
 return {"cases":len(pairs),"errors":errs,"mean_cycles":total/len(pairs),"min_cycles":mi,"max_cycles":ma,"cycles":cy}
def comp(base,cand,pairs):
 b=bench(base[0],base[1]["MATH_SDIV16"],pairs);c=bench(cand[0],cand[1]["MATH_SDIV16"],pairs)
 ds=[y-x for x,y in zip(b["cycles"],c["cycles"])]
 b.pop("cycles");c.pop("cycles")
 return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(ds)/len(ds),"delta_min":min(ds),"delta_max":max(ds)}
def main():
 shared=corpus();focus=pp();res={}
 for profile in PROFILES:
  tmp=Path(tempfile.mkdtemp(prefix="sdiv16-cross-"+profile+"-"))
  try:
   build(profile,ROOT/"relocatable_source"/profile/"math_config_reference.inc",tmp)
   def pair():
    return (
     load(ROOT/profile/"resident"/f"math_{profile}_game_math.prg",ROOT/profile/"resident"/"math_api.inc",profile),
     load(tmp/f"math_{profile}_source_built.prg",tmp/"math_api.inc",profile))
   b,c=pair();canon=comp(b,c,shared)
   b,c=pair();ppres=comp(b,c,focus)
   if canon["candidate"]["errors"] or ppres["candidate"]["errors"] or canon["delta_mean_cycles"]>=0:raise SystemExit((profile,canon,ppres))
   res[profile]={"shared":canon,"pp_focus":ppres}
  finally:shutil.rmtree(tmp,ignore_errors=True)
 print(json.dumps({"status":"PASS","profiles":res},indent=2))
if __name__=="__main__":main()
