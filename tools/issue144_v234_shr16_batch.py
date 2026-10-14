#!/usr/bin/env python3
"""Issue144 V2/V3/V4 optional unsigned SHR16 batch—exact CPU-model proof.

Every caller's normal UMUL32 shared producer MUST be excluded while active;
this never upgrades the default library, regardless of correctness/timing.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import CORPORA,load
from issue144_shr16_direct_slice_overlay_research import PATCH,run,metrics,sha
P=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
ASM=ROOT/"optional/issue144_v234_umul32_shr16_exclusive/overlay_begin_end.asm"
OP="MATH_UMUL32_SHR16"

def audit_profile(profile,pairs,asm,begin,end):
 normal,api=load(profile);candidate,api2=load(profile)
 assert api==api2 and api[OP]==0x5e12
 for pc,val in asm.items():
  assert candidate.mem[pc]==0,(profile,hex(pc),"occupies patch installer RAM")
  candidate.mem[pc]=val
 sourcebytes={pc:bytes(candidate.mem[pc:pc+len(val)]) for pc,val in PATCH.items()}
 assert sourcebytes[0x586e]==bytes.fromhex("8d09c0")
 assert sourcebytes[0x58c7]==bytes.fromhex("8d08c0")
 assert sourcebytes[0xc4e3]==bytes.fromhex("20")
 for pc,old in sourcebytes.items():
  if len(old)==1 and pc not in (0xc4e3,):
   assert old[0]-2==PATCH[pc][0],(profile,pc,"high-output dest incompatible")
 # Four interspersed stock public calls to ensure valid no-patch baseline.
 for x,y in pairs[:8]:
  run(candidate,api,OP,x,y)
  run(candidate,api,"MATH_UMUL32",x,y)
 setup=candidate.call(begin,200000)
 assert all(candidate.mem[pc:pc+len(value)]==value for pc,value in PATCH.items())
 assert candidate.sp==0xfd
 base=[]; trial=[]
 for x,y in pairs:
  cycles1,out=run(normal,api,OP,x,y)
  cycles2,shifted=run(candidate,api,OP,x,y)
  assert out==shifted
  base.append(cycles1);trial.append(cycles2)
 savings=[a-b for a,b in zip(base,trial)]
 assert min(savings)==max(savings)==53,(profile,min(savings),max(savings))
 endcost=candidate.call(end,200000)
 assert setup==76 and endcost==80,(profile,setup,endcost)
 for pc,old in sourcebytes.items():
  assert candidate.mem[pc:pc+len(old)]==old,(profile,hex(pc),"restoration mismatch")
 # Verify all normal product bytes after restore, including same-operand inputs.
 for x,y in pairs[:min(128,len(pairs))]:
  run(candidate,api,"MATH_UMUL32",x,y)
  run(candidate,api,OP,x,y)
 return {
   "status":"PASS_CPU_MODEL_EXCLUSIVE_ONLY",
   "profile":profile,"cases":len(pairs),
   "baseline":metrics(base),"candidate":metrics(trial),
   "paired_savings":metrics(savings),
   "savings_every_case":53,
   "setup_cycles":setup,"restore_cycles":endcost,
   "strict_break_even_calls_with_both_caller_jsrs":4,
   "ordinary_umul32_revalidated_after_end":True,
   "normal_umul32_safe_during_patch":False,
   "patch_prestate_exact_bytes_verified":True,
   "code_patch_installer_cannot_overlap_game_ram":True,
   "installed_profile_unchanged":True,
   "normal_public_abi_candidate":False
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--limit",type=int,default=2409)
 args=ap.parse_args()
 assert 1<=args.limit<=len(CORPORA[32])
 asm,labels,_=Assembler().assemble(ASM.read_text())
 begin=labels["MUL32_SHR16_BEGIN"];end=labels["MUL32_SHR16_END"]
 assert begin==0x900 and end>begin and max(asm)<0x1000
 pairs=CORPORA[32][:args.limit]
 data=b"".join(a.to_bytes(4,"little")+b.to_bytes(4,"little") for a,b in pairs)
 release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 result={
   "status":"PASS_V234_EXCLUSIVE_RESEARCH","source":str(ASM.relative_to(ROOT)),
   "source_sha256":sha(ASM.read_bytes()),"cases_each":len(pairs),
   "operand_vector_sha256":sha(data),
   "profiles":{},"native_cycle_timing_claimed":False,
   "public_profile_promotion":False,"reu_dma_timing_claimed":False}
 for p in P:
  prg=ROOT/p/"resident"/f"math_{p}_game_math.prg"
  assert sha(prg.read_bytes())==release["reference_prg_sha256"][p]
  result["profiles"][p]=audit_profile(p,pairs,asm,begin,end)
  result["profiles"][p]["released_prg_sha256"]=sha(prg.read_bytes())
  print("V234 EXCLUSIVE",p,"PASS",len(pairs),"53 cycles",flush=True)
 out=ROOT/"validation/review/ISSUE144_V234_SHR16_BATCH_CPU_MODEL.json"
 out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 V2-V4 PUBLIC-ENTRY BATCH RESEARCH PASS",len(pairs)*len(P),"paired calls")
if __name__=="__main__":main()
