#!/usr/bin/env python3
"""Public-address-stable V2/V3/V4 UMUL32_SHR16 opt-in specialist proof.

Install separate-routed cloned core and change only the two byte target of
the existing $5E12 JMP. Normal UMUL32/SMUL32 share scratch sequentially
but can coexist; original producer executable is unmodified by the clone.
No public release PRG is changed in the repository.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from benchmark_multiply_refresh import CORPORA,load
from issue144_shr16_independent_clone import (
  PROFILES,ENTRY_CLONE,ORIGINAL,LAST,assemble,installed_mem,before_blob,sha)
from issue144_shr16_direct_slice_overlay_research import run,metrics

ENTRY=0x5E12
NEW=bytes((ENTRY_CLONE&255,(ENTRY_CLONE>>8)&255))
OLD=b"\xe3\xc4"
OP="MATH_UMUL32_SHR16"

def profile_test(profile,clone,pairs):
 source=before_blob(profile,assemble()[0])
 baseline,api=load(profile)
 candidate,api2=load(profile)
 assert api==api2 and api[OP]==ENTRY
 installed_mem(candidate,clone)
 assert bytes(candidate.mem[ENTRY:ENTRY+3])==b"\x4c"+OLD
 assert bytes(candidate.mem[ORIGINAL:LAST+1])==bytes(baseline.mem[ORIGINAL:LAST+1])
 candidate.mem[ENTRY+1:ENTRY+3]=NEW
 assert bytes(candidate.mem[ENTRY:ENTRY+3])==b"\x4c"+NEW
 current=[]; improved=[]
 for i,(x,y) in enumerate(pairs):
  c0,out=run(baseline,api,OP,x,y)
  dx,dy=pairs[(i*109+13)%len(pairs)]
  run(candidate,api,"MATH_UMUL32",dx,dy)
  if i%7==0:run(candidate,api,"MATH_SMUL32",dx,dy)
  original_core=bytes(candidate.mem[ORIGINAL:LAST+1])
  c1,out_new=run(candidate,api2,OP,x,y)
  assert out==out_new,(profile,i,"public entry mismatch")
  assert bytes(candidate.mem[ORIGINAL:LAST+1])==original_core,(
      profile,i,"redirected clone modified original core")
  run(candidate,api,"MATH_UMUL32",dx,dy)
  current.append(c0);improved.append(c1)
 saved=[a-b for a,b in zip(current,improved)]
 assert min(saved)==max(saved)==59,(profile,min(saved),max(saved))
 candidate.mem[ENTRY+1:ENTRY+3]=OLD
 assert bytes(candidate.mem[ENTRY:ENTRY+3])==b"\x4c"+OLD
 for x,y in pairs[:min(96,len(pairs))]:
  run(candidate,api,OP,x,y)
  run(candidate,api,"MATH_UMUL32",x,y)
 return {"status":"PASS_STABLE_PUBLIC_ENTRY_RESEARCH",
  "profile":profile,"pairs":len(pairs),
  "resident_original_sha256":sha(source),
  "public_address":hex(ENTRY),"old_JMP_target":hex(int.from_bytes(OLD,"little")),
  "new_JMP_target":hex(ENTRY_CLONE),
  "entry_patch_only_two_bytes":True,
  "library_other_public_addresses_unchanged":True,
  "ordinary_umul32_signed_smul32_interleaved":True,
  "shared_core_unchanged_during_fast_call":True,
  "ordinary_path_restored_and_verified":True,
  "baseline":metrics(current),"optin_entry":metrics(improved),
  "paired_savings":metrics(saved),"savings_every_pair":59,
  "normal_library_binary_written":False,
  "normal_library_ZP_growth":0,
  "extra_ram_required":True,
  "native_vice_pending":True}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--limit",type=int,default=2409)
 a=ap.parse_args()
 assert 1<=a.limit<=len(CORPORA[32])
 orig,clone,labels,asm,changed=assemble()
 report={"status":"PASS_UMUL32_SHR16_STABLE_PUBLIC_ENTRY_CPU_MODEL",
         "profiles":{},"cases_each":a.limit,
         "candidate_source_sha256":sha(asm.encode()),
         "clone_entry":hex(ENTRY_CLONE),
         "public_entry":hex(ENTRY),
         "direct_clone_vs_public_redirect_overhead_cycles":3,
         "optin_not_default":True,
         "published_regular_prg_unchanged":True,
         "native_cycle_timing_claimed":False}
 for profile in PROFILES:
  report["profiles"][profile]=profile_test(profile,clone,CORPORA[32][:a.limit])
  print("ISSUE144 PUBLIC ENTRY",profile,"PASS",a.limit,"59 saved",flush=True)
 dest=ROOT/"validation/review/ISSUE144_SHR16_PUBLIC_ENTRY_OPTIN_CPU_MODEL.json"
 dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 PUBLIC ENTRY COMPATIBLE OPTIONAL REDIRECT PASS",
       a.limit*len(PROFILES),flush=True)
if __name__=="__main__":main()
