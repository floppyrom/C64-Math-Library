#!/usr/bin/env python3
"""Issue144: executable two-byte public JMP installer/restore source proof."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import CORPORA,load
from issue144_shr16_independent_clone import assemble,installed_mem,PROFILES,ENTRY_CLONE,sha
from issue144_shr16_direct_slice_overlay_research import run
SOURCE=ROOT/"optional/issue144_v234_umul32_shr16_independent/public_entry_redirect.asm"
ENTRY=0x5e12;OP="MATH_UMUL32_SHR16"

def main():
 code,labels,_=Assembler().assemble(SOURCE.read_text())
 assert min(code)==0x0c80 and max(code)<0x0d05
 enable=labels["MATH_UMUL32_SHR16_FAST_ENABLE"]
 disable=labels["MATH_UMUL32_SHR16_FAST_DISABLE"]
 old,clone,_,_,_=assemble()
 report={"status":"PASS_SOURCE_INSTALL_RESTORE_MODEL",
  "source_sha256":sha(SOURCE.read_bytes()),"results":{},
  "normal_production_prgs_unchanged":True,
  "native_vice_cycle_timing_measured":False}
 for p in PROFILES:
  cpu,api=load(p)
  installed_mem(cpu,clone)
  for address,val in code.items():
   assert cpu.mem[address]==0,p
   cpu.mem[address]=val
  assert api[OP]==ENTRY
  assert bytes(cpu.mem[ENTRY:ENTRY+3])==b"\x4c\xe3\xc4"
  failed_return=cpu.call(disable,50000)
  assert cpu.c==1 and bytes(cpu.mem[ENTRY:ENTRY+3])==b"\x4c\xe3\xc4",(
      "disable must reject normal state without changes")
  before=cpu.call(enable,50000)
  assert cpu.c==0 and bytes(cpu.mem[ENTRY:ENTRY+3])==b"\x4c\x03\x0e"
  for x,y in CORPORA[32][:256]:
   run(cpu,api,OP,x,y)
   run(cpu,api,"MATH_UMUL32",x,y)
   if (x^y)&0xff==0:run(cpu,api,"MATH_SMUL32",x,y)
  restored=cpu.call(disable,50000)
  assert cpu.c==0 and bytes(cpu.mem[ENTRY:ENTRY+3])==b"\x4c\xe3\xc4"
  for x,y in CORPORA[32][:256]:
   run(cpu,api,OP,x,y)
  report["results"][p]={
   "status":"PASS_CORRECT_PUBLIC_JMP_RESTORATION",
   "installed_clone_entry":hex(ENTRY_CLONE),
   "setup_cycles_excl_jsr":before,"restore_cycles_excl_jsr":restored,
   "source_installer_bytes":len(code),
   "fast_math_calls":256,"restored_math_calls":256,
   "normal_full_UMUL32_mixed_calls":256,
   "all_public_results_correct":True,
   "public_entry_opcode_preserved":True,
   "original_unsigned_producer_unpatched":True}
  print("ISSUE144 ENABLE/DISABLE",p,"PASS",before,restored,flush=True)
 out=ROOT/"validation/review/ISSUE144_SHR16_PUBLIC_ENTRY_INSTALLER_CPU_MODEL.json"
 out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 PUBLIC ENTRY SOURCE-BASED PATCH-RESTORE PASS")
if __name__=="__main__":main()
