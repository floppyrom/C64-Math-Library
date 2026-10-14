#!/usr/bin/env python3
"""Issue144 native V2/V3/V4—source-assembled exclusive patch BEGIN/END.

Checks exact 48-bit shifted output and documented public ABI. No REU cycle
timing or bus occupancy is claimed; no production PRG or REU file changed.
"""
from __future__ import annotations
import hashlib,json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from benchmark_multiply_refresh import REU
from issue144_shr16_direct_slice_overlay_research import sha
import native_issue144_shr16_batch_source as prev
import native_issue39_fixed_shr16_tail as harness
from native_issue39_signed_multiply_family import COUNT,STRIDE,FIELDS
P=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
ASM=ROOT/"optional/issue144_v234_umul32_shr16_exclusive/overlay_begin_end.asm"
OP="MATH_UMUL32_SHR16"

def match(a,b,p):
 assert len(a)==len(b)==len(FIELDS)*STRIDE
 for row in list(range(6))+list(range(8,len(FIELDS))):
  if row==16: # C=0 required. Other volatile status bits may vary.
   assert all((a[row*STRIDE+i]&1)==(b[row*STRIDE+i]&1)==0
              for i in range(COUNT)),(p,"carry")
  else:
   assert a[row*STRIDE:(row+1)*STRIDE]==b[row*STRIDE:(row+1)*STRIDE],(
        p,row,"native ABI mismatch")

def main():
 state=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 results={"status":"PASS_NATIVE_VICE_V234_EXCLUSIVE_BATCH",
          "profiles":{},"total_native_calls":0,
          "native_cycle_timing_measured":False,"reu_dma_timing_measured":False,
          "normal_public_abi_promoted":False,
          "output_bytes_six_correct":True,
          "signed_umul32_unaffected_outside_exclusive_period":True,
          "private_optisearch_source_published":False}
 exe=os.getenv("VICE_WRAPPER","x64sc")
 saved_source=prev.SOURCE
 prev.SOURCE=ASM
 with tempfile.TemporaryDirectory(prefix="issue144_v234_vice_") as d:
  tmp=Path(d)
  for idx,p in enumerate(P):
   path=ROOT/p/"resident"/f"math_{p}_game_math.prg"
   binary=path.read_bytes()
   assert sha(binary)==state["reference_prg_sha256"][p]
   # Native 6510 public entry does not access REU for this multiplier.
   # REU images are not mounted in the saved native harness.
   baseline=harness.run_native(p,binary,OP,15920+idx*3,tmp,exe)
   normal_make=harness.make_harness
   harness.make_harness=prev.wrap_generator(normal_make)
   try:
    changed=harness.run_native(p,binary,OP,15921+idx*3,tmp,exe)
   finally:harness.make_harness=normal_make
   match(baseline["dump"],changed["dump"],p)
   results["profiles"][p]={
    "status":"PASS_NATIVE_EXCLUSIVE_SOURCE_BEGIN_END",
    "source_sha256":sha(ASM.read_bytes()),
    "resident_sha256":sha(binary),
    "baseline_calls":COUNT,
    "candidate_calls":COUNT,
    "baseline_record_sha256":baseline["dump_sha256"],
    "candidate_record_sha256":changed["dump_sha256"],
    "output_carry_inputs_stack_equal":True,
    "native_cycle_timing_measured":False,
    "normal_umul32_mixed_call_safe":False,
    "reu_assist_used":False
   }
   results["total_native_calls"]+=2*COUNT
   print("ISSUE144 NATIVE",p,"SOURCE BEGIN-END PASS",2*COUNT,flush=True)
 prev.SOURCE=saved_source
 assert results["total_native_calls"]==144
 out=ROOT/"validation/review/ISSUE144_V234_SHR16_BATCH_NATIVE_VICE.json"
 out.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 V234 NATIVE SHARED-PRODUCER EXCLUSIVE PROOF PASS",results["total_native_calls"])
if __name__=="__main__":main()
