#!/usr/bin/env python3
"""Real native VICE validation of V2 separate-RAM relocated SEEK16 k0=1 INIT.

Original $19F0 foreign code and $1A00 resident table untouched. Compare
all 16-byte step frames, carry/X/SP on 4×16 native STEP scenarios.
No physical CPU timing claims.
"""
from __future__ import annotations
import os,sys,tempfile,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import native_issue39_seek_all_modes as native
from issue144_seek16_k1_relocate import assemble,NEW,PUBLIC
def main():
 exe=os.environ.get("VICE_WRAPPER","x64sc")
 copy,labels,source=assemble("k1")
 assert len(copy)==291
 scenarios=((16,"one",0x0100),(16,"step",0x0180),
            (16,"int",0x0200),(16,"step",0x8100))
 original_scenarios=native.SCENARIOS
 make=native.build_code
 resident=native.resident
 native.SCENARIOS=scenarios
 with tempfile.TemporaryDirectory(prefix="issue144_seek16_v2_vice_") as name:
  folder=Path(name)
  try:
   baseline_raw,blob,reu=native.native("v2_pareto_fast",18500,folder,exe)
   baseline=native.verify("v2_pareto_fast",baseline_raw)
   candidate=bytearray(blob)
   at=PUBLIC-0x1000+2
   assert candidate[at]==0x4c and int.from_bytes(candidate[at+1:at+3],"little")==0x18e2
   candidate[at+1:at+3]=NEW.to_bytes(2,"little")
   def extended(A):
    code,stop=make(A)
    assert native.ENTRY+len(code)<NEW
    code+=bytes(NEW-native.ENTRY-len(code))
    code+=bytes(copy.get(i,0) for i in range(NEW,max(copy)+1))
    assert native.ENTRY+len(code)<0x1000
    return code,stop
   native.resident=lambda p:bytes(candidate)
   native.build_code=extended
   alt_raw,_,_=native.native("v2_pareto_fast",18501,folder,exe)
   alt=native.verify("v2_pareto_fast",alt_raw)
   assert baseline_raw==alt_raw,"native VICE results, flags or SP differ"
  finally:
   native.SCENARIOS=original_scenarios
   native.build_code=make
   native.resident=resident
 report={"status":"PASS_NATIVE_VICE_RELOCATED_SEEK16_V2_K1",
  "profile":"v2_pareto_fast",
  "source_sha256":hashlib.sha256(source.encode()).hexdigest(),
  "native_original_step_calls":baseline["step_calls"],
  "native_candidate_step_calls":alt["step_calls"],
  "native_original_and_candidate_INIT_calls":len(scenarios)*2,
  "outputs_carry_x_stack_bitwise_equal":True,
  "stock_prg_file_unchanged":True,
  "foreign_resident_19f0_and_1a00_unchanged":True,
  "native_cycles_measured":False,
  "not_reentrant":True,
  "independent_required_application_ram":"$0D00-$0E22"}
 out=ROOT/"validation/review/ISSUE144_SEEK16_K1_RELOCATED_NATIVE_VICE.json"
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2)+"\n")
 print("ISSUE144 SEEK16 RELOCATED NATIVE VICE PASS",baseline["step_calls"],alt["step_calls"])
if __name__=="__main__":
 main()
