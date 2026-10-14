#!/usr/bin/env python3
"""Issue #144 B/C domain-specific Pareto candidates: paired public-call CPU model.

These are opt-in specialists, not drop-in general API replacements. In
particular the 32/16 power-of-two remainder routine deliberately DOES NOT
produce a quotient, while MATH_UMOD32_16 currently does.
"""
from __future__ import annotations
import argparse,hashlib,json,math,random,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,wr,rd

POW="optional/issue144_pow2_mod32_16/mod32_16_pow2_remainder_only.asm"
SQRT="optional/issue144_isqrt32_u16/low16_dispatch.asm"
def sha(b):return hashlib.sha256(b).hexdigest()
def metrics(data):
 a=list(data);s=sorted(a)
 return {"mean_cycles":sum(a)/len(a),"median_cycles":statistics.median(a),
  "p95_cycles":s[int(.95*(len(s)-1))],"min_cycles":s[0],"max_cycles":s[-1],
  "cycle_vector_sha256":sha(b"".join(int(x).to_bytes(4,"little",signed=True) for x in a))}
def install(cpu,asm):
 machine,labels,_=Assembler().assemble(asm)
 for addr,byte in machine.items():
  assert cpu.mem[addr]==0,("occupied non-library RAM",hex(addr))
  cpu.mem[addr]=byte
 return labels,len(machine)
def test_mod(profile,limit):
 old,api=load(profile);new,_=load(profile)
 asm=(ROOT/POW).read_text();labels,nbytes=install(new,asm)
 entry=labels["MATH_UMOD32_16_POW2_RONLY"]
 assert entry==0x0C00 and nbytes==25
 rng=random.Random(0x1443216)
 pairs=[]
 for shift in range(16):
  d=1<<shift
  for n in [0,1,d-1,d,d+1,65535,65536,0xFFFFFFFF,0x80000000,0x7FFFFFFF,0x12345678,0xABCDEF01]:
   pairs.append((n&0xFFFFFFFF,d))
  for _ in range(limit):pairs.append((rng.getrandbits(32),d))
 before=[];after=[]
 for n,d in pairs:
  for cpu in (old,new):
   wr(cpu.mem,0xC010,n,4);wr(cpu.mem,0xC014,d,2)
   wr(cpu.mem,0xC018,0xA36F4412,4)
  stack=new.sp;rx=new.x;ry=new.y
  c0=old.call(api["MATH_UMOD32_16"],4000000)
  c1=new.call(entry,4000000)
  assert rd(old.mem,0xC01C,2)==rd(new.mem,0xC01C,2)==n%(d)
  assert (old.c,new.c)==(0,0)
  assert rd(new.mem,0xC018,4)==0xA36F4412
  assert rd(new.mem,0xC010,4)==n and rd(new.mem,0xC014,2)==d
  assert (new.sp,new.x,new.y)==(stack,rx,ry)
  before.append(c0);after.append(c1)
 gain=[a-b for a,b in zip(before,after)]
 assert min(gain)>0 and len(set(after))==1 and after[0]==38
 return {"status":"PASS_RONLY_POW2_CONTRACT","cases":len(pairs),
  "public_alias_produces_quotient_but_specialist_does_not":True,
  "required_d_nonzero_power_two":True,"code_bytes":nbytes,
  "source_sha256":sha(asm.encode()),"stock":metrics(before),
  "specialist":metrics(after),"saved":metrics(gain),
  "operand_sha256":sha(b"".join(n.to_bytes(4,"little")+d.to_bytes(2,"little") for n,d in pairs)),
  "X_Y_stack_and_inputs_preserved":True}
def test_isqrt(profile,limit):
 old,api=load(profile);fast,_=load(profile);auto,_=load(profile)
 asm=(ROOT/SQRT).read_text()
 labels,nbytes=install(fast,asm);install(auto,asm)
 assert labels["MATH_ISQRT32_LOW16_ONLY"]==0xC40
 assert labels["MATH_ISQRT32_AUTO"]==0xC43
 rng=random.Random(0x1441532)
 lows=list(range(256))+[x*x for x in range(256)]+[rng.getrandbits(16) for _ in range(limit)]
 full=[rng.getrandbits(32) for _ in range(limit*2)]
 tests={"low16":lows,"full32":full,
        "mixed_10pct":[rng.getrandbits(16) if i%10==0 else rng.getrandbits(32) for i in range(limit*2)]}
 results={}
 for group,nums in tests.items():
  traces={"baseline":[],"guarded":[]}
  if group=="low16":traces["low16_only"]=[]
  for n in nums:
   todo=[("baseline",old,api["MATH_ISQRT32"]),
         ("guarded",auto,labels["MATH_ISQRT32_AUTO"])]
   if group=="low16":todo.append(("low16_only",fast,labels["MATH_ISQRT32_LOW16_ONLY"]))
   for name,cpu,entry in todo:
    wr(cpu.mem,0xC010,n,4)
    keep=bytes(cpu.mem[0xC010:0xC014])
    cycles=cpu.call(entry,2000000)
    assert rd(cpu.mem,0xC008,2)==math.isqrt(n)
    assert cpu.c==0 and bytes(cpu.mem[0xC010:0xC014])==keep
    traces[name].append(cycles)
  result={"cases":len(nums),"corpus_sha256":sha(b"".join(n.to_bytes(4,"little") for n in nums)),
          "timings":{k:metrics(v) for k,v in traces.items()},
          "guard_savings":metrics([x-y for x,y in zip(traces["baseline"],traces["guarded"])])}
  if "low16_only" in traces:
   result["low16_only_savings"]=metrics([x-y for x,y in zip(traces["baseline"],traces["low16_only"])])
  results[group]=result
 return {"status":"PASS_LOW16_AND_ALL_DOMAIN_GUARDED_CORRECTNESS",
         "precondition_for_low16_only":"upper 16 input bits zero",
         "guard_not_default_recommended":True,
         "source_sha256":sha(asm.encode()),"code_bytes":nbytes,
         "V4_REU_bus_or_DMA_time_measured":False,"workloads":results}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--profile",required=True,choices=PROFILES)
 p.add_argument("--mod-random-per-power",type=int,default=160)
 p.add_argument("--sqrt-random",type=int,default=800)
 args=p.parse_args()
 results={"status":"PASS_CPU_MODEL_DOMAIN_SCREEN_ONLY",
     "profile":args.profile,"mod_pow2":test_mod(args.profile,args.mod_random_per_power),
     "isqrt_low16":test_isqrt(args.profile,args.sqrt_random),
     "published_binaries_altered":False,"zero_page_added":0,
     "native_vice_cycles_measured":False,
     "not_general_promotion":True}
 path=ROOT/"validation/review"/("ISSUE144_BC_DOMAIN_"+args.profile+".json")
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(results,sort_keys=True,indent=2)+"\n")
 print("ISSUE144 BC SCREEN",args.profile,
       "UMOD",round(results["mod_pow2"]["saved"]["mean_cycles"],3),
       "ISQRT",round(results["isqrt_low16"]["workloads"]["low16"]["low16_only_savings"]["mean_cycles"],3),
       "PASS",flush=True)
if __name__=="__main__":main()
