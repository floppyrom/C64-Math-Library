#!/usr/bin/env python3
"""Issue144 A: common-input four-way 32-bit multiply upper16-zero specialist.

This does not optimize arbitrary 32-bit inputs: x,y must lie in [0,65535]
as 32-bit bit-patterns. The signed 32-bit cases are consequently positive.
Preserves original operands, result ABI and carry, no added ordinary ZP.
"""
from __future__ import annotations
import argparse,hashlib,json,random,statistics,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import load,wr,rd
from validate_unsigned_division import PROFILES
SRC="optional/issue144_four_mul_narrow16/four_u32_narrow16.asm"
OPS={
 "MATH_UMUL32":"MATH_UMUL32_U16DOMAIN",
 "MATH_SMUL32":"MATH_SMUL32_U16DOMAIN",
 "MATH_UMUL32_SHR16":"MATH_UMUL32_SHR16_U16DOMAIN",
 "MATH_SMUL32_SHR16":"MATH_SMUL32_SHR16_U16DOMAIN"}
def sha(data):return hashlib.sha256(data).hexdigest()
def summary(a):
 v=sorted(a)
 return {"mean_cycles":sum(a)/len(a),"median_cycles":statistics.median(a),
  "p95_cycles":v[int(.95*(len(v)-1))],"min_cycles":v[0],"max_cycles":v[-1],
  "vector_sha256":sha(b"".join(int(x).to_bytes(4,"little",signed=True) for x in a))}
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--profile",choices=PROFILES,required=True)
 args=parser.parse_args()
 raw=(R/SRC).read_text()
 code,labels,_=Assembler().assemble(raw)
 assert labels["MATH_UMUL32_U16DOMAIN"]==0x0E60 and max(code)<0x1000
 edges=[0,1,2,3,7,255,256,32767,32768,65534,65535]
 rng=random.Random(0x14416)
 pairs=[(x,y) for x in edges for y in edges]
 pairs += [(rng.randrange(65536),rng.randrange(65536)) for _ in range(1024)]
 operand_sha=sha(b"".join(x.to_bytes(4,"little")+y.to_bytes(4,"little") for x,y in pairs))
 stock,api=load(args.profile);candidate,api2=load(args.profile)
 assert api==api2
 for where,byte in code.items():
  assert candidate.mem[where]==0,("occupied caller-owned RAM",hex(where))
  candidate.mem[where]=byte
 entries={}
 for name,alt in OPS.items():
  before=[];after=[]
  for x,y in pairs:
   for cpu in (stock,candidate):
    wr(cpu.mem,0xC000,x,4);wr(cpu.mem,0xC004,y,4)
   stack=candidate.sp
   a=stock.call(api[name],2000000)
   b=candidate.call(labels[alt],2000000)
   expected=((x*y)>>16) if "SHR16" in name else x*y
   size=6 if "SHR16" in name else 8
   assert rd(stock.mem,0xC008,size)==rd(candidate.mem,0xC008,size)==expected
   assert (stock.c,candidate.c)==(0,0)
   assert rd(candidate.mem,0xC000,4)==x and rd(candidate.mem,0xC004,4)==y
   assert candidate.sp==stack
   before.append(a);after.append(b)
  gains=[a-b for a,b in zip(before,after)]
  assert min(gains)>0
  entries[name]={"cases":len(pairs),"stock":summary(before),
       "optin":summary(after),"paired_savings":summary(gains),
       "low16_sign_bit_can_be_set":True,"full_32bit_operand_inputs_preserved":True}
 report={"status":"PASS_FOUR_NARROW16_PUBLIC_ABI_SHAPED_OPTINS",
         "profile":args.profile,"cases_per_operation":len(pairs),
         "source_sha256":sha(raw.encode()),"code_bytes":len(code),
         "operand_vector_sha256":operand_sha,"entries":entries,
         "precondition":"both 32-bit operand upper 16-bit words zero",
         "normal_ZP_extra":0,"regular_resident_prg_changed":False,
         "native_VICE_cycles_measured":False}
 out=R/"validation/review"/("ISSUE144_FOUR_MUL_NARROW16_"+args.profile+".json")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 NARROW16",args.profile,
   [(k,round(v["paired_savings"]["mean_cycles"],3)) for k,v in entries.items()],
   "PASS",flush=True)
if __name__=="__main__":main()
