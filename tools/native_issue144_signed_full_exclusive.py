#!/usr/bin/env python3
"""Issue144 native x64sc correctness: unrestricted signed SHR16 exclusive overlay.

Applies the exact verified source-generated instruction patch in a disposable
copy of each original resident PRG; the shipped PRGs are untouched. This
overlay is *not* safe for mixed SMUL32 producer use while enabled.
"""
from __future__ import annotations
import json,os,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"tools"))
from issue144_signed_full_exclusive import PROFILES,patch_map,sha
from native_issue144_shr16_independent_clone import verify_output
from native_issue39_signed_multiply_family import COUNT
import native_issue39_fixed_shr16_tail as native
OUT="validation/review/ISSUE144_SIGNED_SHR16_FULL_EXCLUSIVE_NATIVE_VICE.json"
def patch_prg(blob,patch):
 result=bytearray(blob)
 assert int.from_bytes(blob[:2],"little")==0x1000
 for addr,value in patch.items():
  off=addr-0x1000+2
  before=bytes(result[off:off+len(value)])
  if len(value)==3:assert before[0]==0x8D
  elif addr in (0xC50C,0xC575):assert before==b"\x20"
  else:assert result[off-1]==0x8D and result[off+1]==0xC0
  result[off:off+len(value)]=value
 return bytes(result)
def main():
 release=json.loads((R/"RELEASE_STATUS.json").read_text())
 report={"status":"PASS_NATIVE_ALL_SIGNED_DOMAIN_EXCLUSIVE_ONLY","profiles":{},
  "baseline_and_candidate_calls":0,"native_cycles_measured":False,
  "normal_prgs_unchanged":True,"ordinary_SMUL32_during_overlay_valid":False}
 exe=os.getenv("VICE_WRAPPER","x64sc")
 with tempfile.TemporaryDirectory(prefix="issue144_signed_exclusive_") as folder:
  temp=Path(folder)
  for i,p in enumerate(PROFILES):
   raw=(R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()
   assert sha(raw)==release["reference_prg_sha256"][p]
   modified=patch_prg(raw,patch_map(p))
   baseline=native.run_native(p,raw,"MATH_SMUL32_SHR16",19430+i*3,temp,exe)
   optin=native.run_native(p,modified,"MATH_SMUL32_SHR16",19431+i*3,temp,exe)
   verify_output(baseline["dump"],optin["dump"],p)
   report["profiles"][p]={"status":"PASS_NATIVE_SIX_OUTPUT_BYTES_CARRY_INPUTS_SP",
     "paired_vectors":COUNT,"original_resident_sha256":sha(raw),
     "disposable_overlay_sha256":sha(modified),
     "original_resident_disk_file_unchanged":True}
   report["baseline_and_candidate_calls"]+=COUNT*2
   print("NATIVE SIGNED SHR16 EXCLUSIVE",p,COUNT*2,"PASS",flush=True)
 assert report["baseline_and_candidate_calls"]==240
 path=R/OUT;path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("NATIVE SIGNED SHR16 EXCLUSIVE PASS",240)
if __name__=="__main__":main()
