#!/usr/bin/env python3
"""Issue144: exact V2 ASM patch-install/remove cost and batch break-even.

The opt-in patch kit is for the *one-routine exclusive* resource class;
normal UMUL32 and any transitive shared-producer users are unavailable in
the active interval. No public/default profile bytes are changed.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import CORPORA,load
from issue144_shr16_direct_slice_overlay_research import PATCH,run,metrics,sha

ASM=ROOT/"optional/issue144_v2_umul32_shr16_exclusive/overlay_begin_end.asm"
P="v2_pareto_fast"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--limit",type=int,default=1024);a=ap.parse_args()
 assert 1<=a.limit<=len(CORPORA[32])
 asm,labels,_=Assembler().assemble(ASM.read_text())
 begin=labels["MUL32_SHR16_BEGIN"];end=labels["MUL32_SHR16_END"]
 assert begin==0x0900 and begin<end and end+90<0x1000
 cpu,api=load(P)
 for pc,val in asm.items():
  assert cpu.mem[pc]==0,(hex(pc),"patch setup region already occupied")
  cpu.mem[pc]=val
 original={pc:bytes(cpu.mem[pc:pc+len(b)]) for pc,b in PATCH.items()}
 assert original[0x586E]==b"\x8d\x09\xc0"
 assert original[0x58C7]==b"\x8d\x08\xc0"
 assert original[0xC4E3]==b"\x20"
 for x,y in CORPORA[32][:min(a.limit,16)]:
  run(cpu,api,"MATH_UMUL32",x,y)
  run(cpu,api,"MATH_UMUL32_SHR16",x,y)
 cost_setup=cpu.call(begin,100000)
 assert all(bytes(cpu.mem[pc:pc+len(new)])==new for pc,new in PATCH.items())
 assert cpu.sp==0xfd
 ref,api_ref=load(P)
 ordinary=[];special=[]
 for x,y in CORPORA[32][:a.limit]:
  baseline,_=run(ref,api_ref,"MATH_UMUL32_SHR16",x,y)
  candidate,_=run(cpu,api,"MATH_UMUL32_SHR16",x,y)
  ordinary.append(baseline);special.append(candidate)
 delta=[x-y for x,y in zip(ordinary,special)]
 assert set(delta)=={53},dict((x,delta.count(x)) for x in set(delta))
 cost_restore=cpu.call(end,100000)
 for pc,old in original.items():
  assert bytes(cpu.mem[pc:pc+len(old)])==old,(hex(pc),"failed restore")
 for x,y in CORPORA[32][:min(a.limit,128)]:
  run(cpu,api,"MATH_UMUL32",x,y)
  run(cpu,api,"MATH_UMUL32_SHR16",x,y)
 # The caller JSR for BEGIN/END is excluded from CPU.call by definition;
 # break-even must account for it on both ends if counting complete program time.
 overhead=cost_setup+cost_restore
 breakeven=overhead//53+1
 record={
   "status":"PASS_EXCLUSIVE_BATCH_CPU_MODEL",
   "profile":P,
   "basis":"CPU.call entry through RTS; no caller JSR included",
   "source_path":str(ASM.relative_to(ROOT)),
   "source_sha256":sha(ASM.read_bytes()),
   "asm_origin":begin,
   "asm_bytes":end+len(asm)-max(asm)-begin if False else len(asm),
   "entry_begin":begin,"entry_end":end,
   "patched_existing_bytes":sum(len(v) for v in PATCH.values()),
   "precondition":"exact stock V2 profile, MATH_INIT, RAM visible, exclusive core ownership",
   "ordinary_UMUL32_legal_while_active":False,
   "resident_prgs_changed":False,
   "abi_default_profile_changed":False,
   "setup_cpu_cycles_excl_caller_jsr":cost_setup,
   "restore_cpu_cycles_excl_caller_jsr":cost_restore,
   "batch_patch_overhead_cpu_cycles_excl_caller_jsr":overhead,
   "per_call_steady_state_savings_cpu_cycles":53,
   "first_call_count_with_positive_net_savings_excl_caller_jsrs":breakeven,
   "tested_pairs":a.limit,
   "baseline":metrics(ordinary),
   "batch_candidate":metrics(special),
   "savings":metrics(delta),
   "original_core_correct_after_restore":True,
   "native_begin_end_qualified":False,
   "native_cycle_timing_measured":False,
 }
 out=ROOT/"validation/review/ISSUE144_V2_SHR16_BATCH_BREAK_EVEN.json"
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 V2 BATCH ASM PASS",a.limit,"BEGIN",cost_setup,
       "END",cost_restore,"BREAKEVEN",breakeven,flush=True)
if __name__=="__main__":main()
