#!/usr/bin/env python3
"""Native VICE original public MATH_UMUL32_SHR16 address with optional redirect.

Checks baseline $5E12 JMP $C4E3 versus identical JMP opcode redirected to
separate clone entry $0E03 in a disposable in-memory PRG image. Production
PRGs are unchanged, and ordinary MATH_UMUL32 core is not patched.
"""
from __future__ import annotations
import json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from issue144_shr16_independent_clone import assemble,CLONE,ENTRY_CLONE,PROFILES,sha
from native_issue144_shr16_independent_clone import verify_output
import native_issue39_fixed_shr16_tail as native
from native_issue39_signed_multiply_family import H,COUNT
PUBLIC=0x5E12
OP="MATH_UMUL32_SHR16"
EVID="validation/review/ISSUE144_SHR16_PUBLIC_ENTRY_OPTIN_NATIVE_VICE.json"

def patched_harness(copy,make_harness):
 def new(api,entry,bits):
  # Use genuine original MATH_UMUL32_SHR16 entry, not clone alias.
  code,stop=make_harness(api,entry,bits)
  assert H+len(code)<CLONE
  code+=bytes(CLONE-H-len(code))
  for pc in range(CLONE,max(copy)+1):code+=bytes([copy.get(pc,0)])
  assert H+len(code)<0x1000
  return code,stop
 return new

def main():
 old,copy,labels,source,changes=assemble()
 assert labels["MATH_UMUL32_SHR16_CLONE"]==ENTRY_CLONE
 report={"status":"PASS_NATIVE_OPTIN_STABLE_PUBLIC_ENTRY_32_SHR16",
         "results":{},"native_calls_total":0,"source_sha256":sha(source.encode()),
         "entry_address":hex(PUBLIC),"redirected_destination":hex(ENTRY_CLONE),
         "native_cycle_timing_measured":False,
         "published_prgs_unchanged":True,"normal_UMUL32_core_unchanged":True,
         "regular_default_profile_promoted":False}
 release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 exe=os.getenv("VICE_WRAPPER","x64sc")
 with tempfile.TemporaryDirectory(prefix="issue144_public_optin_vice_") as t:
  tmp=Path(t)
  for pi,p in enumerate(PROFILES):
   raw=(ROOT/p/"resident"/f"math_{p}_game_math.prg").read_bytes()
   assert sha(raw)==release["reference_prg_sha256"][p]
   assert int.from_bytes(raw[:2],"little")==0x1000
   at=PUBLIC-0x1000+2
   assert raw[at:at+3]==b"\x4c\xe3\xc4",p
   trial=bytearray(raw)
   trial[at+1:at+3]=bytes((ENTRY_CLONE&255,ENTRY_CLONE>>8))
   assert trial[at]==0x4c and trial!=raw
   before=native.run_native(p,raw,OP,16110+pi*3,tmp,exe)
   original_harness=native.make_harness
   native.make_harness=patched_harness(copy,original_harness)
   try:
    after=native.run_native(p,bytes(trial),OP,16111+pi*3,tmp,exe)
   finally:native.make_harness=original_harness
   verify_output(before["dump"],after["dump"],p)
   report["results"][p]={
     "status":"PASS_NATIVE_PUBLIC_ADDRESS_UNCHANGED",
     "baseline_calls":COUNT,"optin_calls":COUNT,
     "entry_preserved":hex(PUBLIC),
     "only_stock_prg_byte_changes_in_disposable_candidate":[at+1,at+2],
     "baseline_original_sha256":sha(raw),
     "temporary_candidate_sha256":sha(bytes(trial)),
     "native_six_bytes_carry_inputs_and_stack_equal":True,
     "native_cycle_timing_measured":False,
     "extra_ram_clone_required":True,
     "ordinary_core_not_patched":True}
   report["native_calls_total"]+=COUNT*2
   print("ISSUE144 PUBLIC ENTRY NATIVE VICE",p,COUNT*2,"PASS",flush=True)
 assert report["native_calls_total"]==144
 (ROOT/EVID).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 NATIVE ORIGINAL PUBLIC ADDRESS OPTIONAL FAST CLONE PASS",144)
if __name__=="__main__":main()
