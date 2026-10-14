#!/usr/bin/env python3
"""Native x64sc correctness for the independent 32x32->48 SHR16 clone.

Clone assembler source is built from an exact shipped V2 source mirror with
labels, absolute self-modifying references and public output retargeted.
The original resident binary stays intact; result ABI and carry are checked.
"""
from __future__ import annotations
import hashlib,json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from issue144_shr16_independent_clone import (
  assemble,ORIGINAL,CLONE,ENTRY_CLONE,LAST,PROFILES,sha)
import native_issue39_fixed_shr16_tail as native
from native_issue39_signed_multiply_family import H,COUNT,STRIDE,FIELDS

OP="MATH_UMUL32_SHR16"
OUT="validation/review/ISSUE144_SHR16_INDEPENDENT_CLONE_NATIVE_VICE.json"
def extended_harness(code_map,regular_generator):
 def new_generator(api,entry,bits):
  tmpapi=dict(api)
  tmpapi[OP]=ENTRY_CLONE
  code,stop=regular_generator(tmpapi,entry,bits)
  assert H+len(code)<CLONE,(hex(H+len(code)),"harness overlaps clone")
  code+=bytes(CLONE-H-len(code))
  for p in range(CLONE,max(code_map)+1):code+=bytes([code_map.get(p,0)])
  assert H+len(code)<0x1000,hex(H+len(code))
  return code,stop
 return new_generator

def verify_output(old,new,profile):
 assert len(old)==len(new)==STRIDE*len(FIELDS)
 for row in list(range(6))+list(range(8,len(FIELDS))):
  if row==16:
   assert all((old[row*STRIDE+i]&1)==(new[row*STRIDE+i]&1)==0
              for i in range(COUNT)),(profile,"carry mismatch")
  else:
   assert old[row*STRIDE:(row+1)*STRIDE]==new[row*STRIDE:(row+1)*STRIDE],(
      profile,row,"native output input or stack mismatch")

def main():
 original,copy,labels,source,changes=assemble()
 assert labels["MATH_UMUL32_SHR16_CLONE"]==ENTRY_CLONE
 release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 report={
  "status":"PASS_NATIVE_VICE_INDEPENDENT_SHR16_CLONE",
  "cloned_core_origin":hex(CLONE),"cloned_entry":hex(ENTRY_CLONE),
  "cloned_code_bytes":len(copy),"source_sha256":sha(source.encode()),
  "native_cycle_timing_measured":False,
  "normal_public_abi_replaced":False,
  "normal_resident_images_modified":False,
  "normal_reu_images_modified":False,
  "native_pairs_total":0,"results":{}}
 exe=os.getenv("VICE_WRAPPER","x64sc")
 with tempfile.TemporaryDirectory(prefix="issue144_indep_native_") as t:
  temp=Path(t)
  for pi,p in enumerate(PROFILES):
   binary=(ROOT/p/"resident"/f"math_{p}_game_math.prg").read_bytes()
   assert sha(binary)==release["reference_prg_sha256"][p]
   base=native.run_native(p,binary,OP,16030+pi*3,temp,exe)
   prev=native.make_harness
   native.make_harness=extended_harness(copy,prev)
   try:
    ext=native.run_native(p,binary,OP,16031+pi*3,temp,exe)
   finally:native.make_harness=prev
   verify_output(base["dump"],ext["dump"],p)
   report["results"][p]={
     "status":"PASS_NATIVE_INDEPENDENT_SHR16_PUBLIC_RESULT",
     "baseline_calls":COUNT,"clone_calls":COUNT,
     "resident_sha256":sha(binary),
     "original_dump_sha256":base["dump_sha256"],
     "clone_dump_sha256":ext["dump_sha256"],
     "correct_result_carry_inputs_and_stack":True,
     "same_primary_ZP_scratch_shared_non_reentrant":True,
     "clone_executed_from_separate_RAM":True
   }
   report["native_pairs_total"]+=COUNT*2
   print("ISSUE144 NATIVE INDEPENDENT CLONE",p,COUNT*2,"PASS",flush=True)
 assert report["native_pairs_total"]==144
 (ROOT/OUT).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 NATIVE INDEPENDENT CLONE QUALIFIED",report["native_pairs_total"])
if __name__=="__main__":main()
