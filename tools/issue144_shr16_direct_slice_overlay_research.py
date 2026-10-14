#!/usr/bin/env python3
"""Issue144, common-input 32x32 multiplication and noncomposable SHR16 overlay.

The original resident PRGs are never modified. A disposable emulator instance
tests a V2-only output-slice adaptation that shares its core with UMUL32;
therefore this is research, not a default or mixed-call-safe optimization.
"""
from __future__ import annotations
import argparse,hashlib,json,statistics,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from benchmark_multiply_refresh import CORPORA,PROFILES,load,wr,rd,si
MASK48=(1<<48)-1
OPS=("MATH_UMUL32","MATH_UMUL32_SHR16","MATH_SMUL32","MATH_SMUL32_SHR16")
SITES=((0x587E,0xC00A),(0x5893,0xC00B),(0x58A7,0xC00C),
       (0x58B4,0xC00D),(0x58BB,0xC00E),(0x58C2,0xC00F))
PATCH={0x586E:b"\xea\xea\xea",0x58C7:b"\x18\xea\xea",0xC4E3:b"\x4c"}
PATCH.update({pc+1:bytes([(addr-2)&255]) for pc,addr in SITES})

def sha(data):return hashlib.sha256(data).hexdigest()
def metrics(a):
 s=sorted(a)
 return dict(mean_cycles=sum(a)/len(a),median_cycles=statistics.median(a),
             p95_cycles=s[int(.95*(len(s)-1))],
             min_cycles=s[0],max_cycles=s[-1],
             cycle_vector_sha256=sha(b"".join(v.to_bytes(4,"little") for v in a)))
def run(c,api,op,x,y):
 wr(c.mem,0xC000,x,4);wr(c.mem,0xC004,y,4)
 original=bytes(c.mem[0xC000:0xC008]);stack=c.sp
 c.c=(x^y)&1
 cy=c.call(api[op],2_000_000)
 signed="SMUL" in op
 prod=(si(x,32)*si(y,32)) if signed else (x*y)
 if "SHR16" in op:
  expected=(prod>>16)&MASK48;n=6
 else:expected=prod&((1<<64)-1);n=8
 got=rd(c.mem,0xC008,n)
 assert got==expected,(op,hex(x),hex(y),hex(got),hex(expected))
 assert bytes(c.mem[0xC000:0xC008])==original,(op,"input overwritten")
 assert c.sp==stack,(op,"stack mismatch")
 assert c.c==0,(op,"carry mismatch")
 return cy,bytes(c.mem[0xC008:0xC008+n])

def install(cpu):
 original={pc:bytes(cpu.mem[pc:pc+len(new)]) for pc,new in PATCH.items()}
 assert original[0x586E]==b"\x8d\x09\xc0"
 assert original[0x58C7]==b"\x8d\x08\xc0"
 assert original[0xC4E3]==b"\x20"
 for pc,addr in SITES:
  assert cpu.mem[pc]==0x8D and cpu.mem[pc+1]==(addr&255) and cpu.mem[pc+2]==0xC0,(pc,addr)
 for pc,new in PATCH.items():cpu.mem[pc:pc+len(new)]=new
 return original

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--limit",type=int,default=512);args=ap.parse_args()
 assert 1<=args.limit<=len(CORPORA[32])
 pairs=CORPORA[32][:args.limit]
 pbytes=b"".join(x.to_bytes(4,"little")+y.to_bytes(4,"little") for x,y in pairs)
 report=dict(status="PASS",kind="CPU-model public-call corpus and exclusive overlay experiment",
             convention="public entry through RTS excluding caller JSR and input setup",
             pairs_per_profile=len(pairs),operand_vector_sha256=sha(pbytes),
             profile_means={},overlay={},
             resident_prg_modified=False,public_abi_replacement=False,
             native_vice_candidate_qualified=False,private_optisearch_published=False)
 for profile in PROFILES:
  cpu,api=load(profile)
  timings={name:[] for name in OPS}
  for x,y in pairs:
   for name in OPS:
    cycles,_=run(cpu,api,name,x,y)
    timings[name].append(cycles)
  report["profile_means"][profile]={name:metrics(timings[name]) for name in OPS}
  for prefix in ("MATH_UMUL32","MATH_SMUL32"):
   diff=[shift-full for shift,full in zip(timings[prefix+"_SHR16"],timings[prefix])]
   report["profile_means"][profile][prefix+"_SHR16"]["same_operand_overhead_vs_full"]={
    "mean":sum(diff)/len(diff),"min":min(diff),"max":max(diff),
    "histogram":dict(Counter(diff))}
  print("PUBLIC",profile,[(n,round(metrics(timings[n])["mean_cycles"],3)) for n in OPS],flush=True)
 profile="v2_pareto_fast"
 old,api=load(profile);new,api2=load(profile)
 assert api==api2
 saved=install(new)
 base=[];trial=[]
 for x,y in pairs:
  a,out=run(old,api,"MATH_UMUL32_SHR16",x,y)
  b,other=run(new,api,"MATH_UMUL32_SHR16",x,y)
  assert out==other
  base.append(a);trial.append(b)
 delta=[a-b for a,b in zip(base,trial)]
 assert min(delta)>0,(min(delta),max(delta))
 report["overlay"]={
  "status":"PASS_EXCLUSIVE_OVERLAY_ONLY",
  "baseline":metrics(base),"candidate":metrics(trial),
  "per_call_savings":metrics(delta),
  "savings_histogram":dict(Counter(delta)),
  "live_patch_bytes":sum(map(len,PATCH.values())),
  "patches":{format(pc,"04X"):{"old":saved[pc].hex(),"new":new.hex()}
             for pc,new in PATCH.items()},
  "warning":"Shared UMUL32 producer is altered. Mixed normal UMUL32 calls are not valid while the overlay is active; this is NOT a drop-in library routine. Setup/restore cycles excluded.",
  "native_vice_candidate_qualified":False,
  "regular_mixed_call_abi_qualified":False}
 for pc,b in saved.items():new.mem[pc:pc+len(b)]=b
 fresh,entry=load(profile)
 for x,y in pairs[:min(len(pairs),80)]:
  run(fresh,entry,"MATH_UMUL32",x,y)
  run(fresh,entry,"MATH_UMUL32_SHR16",x,y)
 report["overlay"]["clean_unmodified_normal_path_rechecked"]=True
 path=ROOT/"validation/review/ISSUE144_SHR16_DIRECT_SLICE_OVERLAY_RESEARCH.json"
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 DIRECT-SLICE RESEARCH PASS",len(pairs),"paired",
       "savings",metrics(delta)["mean_cycles"],flush=True)

if __name__=="__main__":main()
