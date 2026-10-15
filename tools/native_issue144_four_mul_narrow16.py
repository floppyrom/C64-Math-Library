#!/usr/bin/env python3
"""Real x64sc proof: four full/SHR16 32-bit public-call-shaped opt-ins V1-V5.

Signed and unsigned operands are strictly 0..65535 in their full 32-bit
representations. A/X/Y ordinary clobber is allowed; result/carry/input/SP
must be correct. VICE is NOT a CPU cycle benchmark.
"""
from __future__ import annotations
import hashlib,json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES
from native_issue144_shr16_independent_clone import verify_output
import native_issue39_fixed_shr16_tail as fixed
import native_issue39_signed_multiply_family as signed

SOURCE="optional/issue144_four_mul_narrow16/four_u32_narrow16.asm"
OPS={
 "MATH_UMUL32":"MATH_UMUL32_U16DOMAIN",
 "MATH_SMUL32":"MATH_SMUL32_U16DOMAIN",
 "MATH_UMUL32_SHR16":"MATH_UMUL32_SHR16_U16DOMAIN",
 "MATH_SMUL32_SHR16":"MATH_SMUL32_SHR16_U16DOMAIN"}

def short_pairs(bits):
 edge=[0,1,2,3,7,15,255,256,32767,32768,65534,65535]
 v=list(zip(edge,edge))+list(zip(edge,reversed(edge)))
 assert len(v)==signed.COUNT
 return v
def inject_program(source,existing_generator):
 def generator(api,entry,bits):
  code,stop=existing_generator(api,entry,bits)
  lo=min(source)
  assert signed.H+len(code)<lo
  code+=bytes(lo-signed.H-len(code))
  code+=bytes(source.get(i,0) for i in range(lo,max(source)+1))
  assert signed.H+len(code)<0x1000
  return code,stop
 return generator
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
 asm=(ROOT/SOURCE).read_text()
 bytes_by_addr,labels,_=Assembler().assemble(asm)
 assert max(bytes_by_addr)<0x1000
 orig_signed_pairs=signed.pairs;orig_fixed_pairs=fixed.pairs
 orig_signed_make=signed.make_harness;orig_fixed_make=fixed.make_harness
 signed.pairs=short_pairs;fixed.pairs=short_pairs
 release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 result={"status":"PASS_NATIVE_VICE_FOUR_NARROW16_U32_MUL",
         "source_sha256":sha(asm.encode()),
         "native_cpu_cycles_measured":False,
         "precondition":"both full-width 32-bit input upper words zero",
         "stock_PRGs_changed":False,"profiles":{},"total_native_calls":0}
 try:
  exe=os.getenv("VICE_WRAPPER","x64sc")
  with tempfile.TemporaryDirectory(prefix="issue144_fourmul_native_") as td:
   tmp=Path(td)
   for pi,p in enumerate(PROFILES):
    raw=(ROOT/p/"resident"/f"math_{p}_game_math.prg").read_bytes()
    assert sha(raw)==release["reference_prg_sha256"][p]
    row={}
    for i,(name,symbol) in enumerate(OPS.items()):
     at=signed.api(p)[name]-0x1000+2
     assert at>=2
     candidate=bytearray(raw)
     where=labels[symbol]
     candidate[at:at+3]=bytes((0x4C,where&255,where>>8))
     if "SHR16" in name:
      stock=fixed.run_native(p,raw,name,19200+pi*10+i*2,tmp,exe)
      fixed.make_harness=inject_program(bytes_by_addr,orig_fixed_make)
      try:alt=fixed.run_native(p,bytes(candidate),name,19201+pi*10+i*2,tmp,exe)
      finally:fixed.make_harness=orig_fixed_make
      verify_output(stock["dump"],alt["dump"],p)
     else:
      stock=signed.native(p,raw,name,32,19200+pi*10+i*2,tmp,exe)
      signed.make_harness=inject_program(bytes_by_addr,orig_signed_make)
      try:alt=signed.native(p,bytes(candidate),name,32,19201+pi*10+i*2,tmp,exe)
      finally:signed.make_harness=orig_signed_make
      assert stock["pairs"]==alt["pairs"]==signed.COUNT
     row[name]={"native_original_calls":signed.COUNT,
       "native_candidate_calls":signed.COUNT,
       "correct_inputs_outputs_carry_stack":True,
       "public_target_patch_in_disposable_image_only":True}
     result["total_native_calls"]+=signed.COUNT*2
     print("NATIVE FOUR NARROW16",p,name,signed.COUNT*2,"PASS",flush=True)
    result["profiles"][p]=row
 finally:
  signed.pairs=orig_signed_pairs;fixed.pairs=orig_fixed_pairs
  signed.make_harness=orig_signed_make;fixed.make_harness=orig_fixed_make
 assert result["total_native_calls"]==5*4*24*2
 dest=ROOT/"validation/review/ISSUE144_FOUR_MUL_NARROW16_NATIVE_VICE.json"
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 FOUR MATH NARROW16 NATIVE PASS",result["total_native_calls"])
if __name__=="__main__":main()
