#!/usr/bin/env python3
"""Issue144: full-Q/R zero-divisor-safe guarded pow2 fastpath experiment.

Uses already published Issue39 full-quotient 114-byte power-of-two helper,
not the new 25-byte remainder-only kernel. Guard fallback handles arbitrary
D16 and divide-by-zero. Do NOT promote without deployment workload proof.
"""
from __future__ import annotations
import hashlib,json,random,statistics,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"tools"))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,wr,rd,expected
POW="routines/standalone_lab/library_dependent/div_u32_u16_pow2_optin.asm"
GUARD="optional/issue144_guarded_pow2_divmod/guard.asm"
def stats(v):
 s=sorted(v)
 return {"mean_cycles":sum(v)/len(v),"median_cycles":statistics.median(v),
         "p95_cycles":s[int(.95*(len(s)-1))],"min_cycles":s[0],"max_cycles":s[-1],
         "cycle_vector_sha256":hashlib.sha256(b"".join(int(x).to_bytes(4,"little",signed=True) for x in v)).hexdigest()}
def vectors(mode):
 rng=random.Random(0xF0143216+["uniform","pow2_10pct","pow2_1pct","pow2_50pct","q0q1","small"].index(mode)*0x1001)
 for i in range(1024):
  d=rng.getrandbits(16)
  if mode.startswith("pow2_"):
   rate=int(mode.split("_")[1][:-3])
   if i%(100//rate)==0:d=1<<rng.randrange(16)
  if mode=="q0q1":
   d=rng.randrange(1,65536);n=rng.randrange(d*2)
  elif mode=="small":
   n=rng.getrandbits(32);d=rng.randrange(1,256)
  else:n=rng.getrandbits(32)
  yield n,d
def main():
 helper,l,_=Assembler().assemble((R/POW).read_text())
 guard,g,_=Assembler().assemble((R/GUARD).read_text())
 assert len(helper)==114 and l["U3216_POW2_OPTIN"]==0x800
 assert g["MATH_UMOD32_16_POW2_GUARDED"]==0x900
 assert not set(helper)&set(guard)
 result={"status":"PASS_RESEARCH_COMPLETE_Q_R_GUARDED_DISPATCH",
     "public_api_not_replaced":True,"requires_114_byte_Issue39_helper":True,
     "profiles":{},"native_vice_not_claimed":True,
     "no_normal_ZP":True}
 for p in PROFILES:
  stock,api=load(p);test,_=load(p)
  assert api["MATH_UMOD32_16"]==0x3226
  for addr,b in {**helper,**guard}.items():
   assert test.mem[addr]==0,(p,addr,"caller RAM unavailable")
   test.mem[addr]=b
  row={}
  for mode in ("uniform","pow2_10pct","pow2_1pct","pow2_50pct","q0q1","small"):
   before=[];after=[]
   for n,d in vectors(mode):
    for c in (stock,test):
     wr(c.mem,0xC010,n,4);wr(c.mem,0xC014,d,2)
     wr(c.mem,0xC018,0x45AABBCC,4)
     wr(c.mem,0xC01C,0x77F01234,4)
    a=stock.call(api["MATH_UMOD32_16"],4000000)
    b=test.call(0x900,4000000)
    q,r,flag=expected(n,d,32,16)
    assert (rd(stock.mem,0xC018,4),rd(stock.mem,0xC01C,2),stock.c)==(q,r,flag)
    assert (rd(test.mem,0xC018,4),rd(test.mem,0xC01C,2),test.c)==(q,r,flag)
    assert (rd(test.mem,0xC010,4),rd(test.mem,0xC014,2))==(n,d)
    before.append(a);after.append(b)
   row[mode]={"baseline":stats(before),"candidate":stats(after),
             "paired_savings":stats([x-y for x,y in zip(before,after)])}
  result["profiles"][p]=row
  print("GUARD",p,"uniform",row["uniform"]["paired_savings"]["mean_cycles"],
        "pow2_10pct",row["pow2_10pct"]["paired_savings"]["mean_cycles"],flush=True)
 dest=R/"validation/review/ISSUE144_POW2_QR_GUARD_RESEARCH.json"
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 POWER2 FULL Q/R GUARDED RESEARCH PASS",len(PROFILES)*6*1024)
if __name__=="__main__":main()
