#!/usr/bin/env python3
"""True native VICE trial of source-backed V2 BEGIN/CALL/END exclusive batch.

The stand-alone BEGIN/END source is assembled at $0E00 only in the temporary
native test harness. No installed resident PRG is modified.
"""
from __future__ import annotations
import hashlib,json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
import native_issue39_fixed_shr16_tail as native
from native_issue39_signed_multiply_family import H,COUNT,STRIDE,FIELDS
from issue144_shr16_direct_slice_overlay_research import sha

PROFILE="v2_pareto_fast"
ENTRY="MATH_UMUL32_SHR16"
ORIGIN=0x0e00
SOURCE=ROOT/"optional/issue144_v2_umul32_shr16_exclusive/overlay_begin_end.asm"

def wrap_generator(original):
 def wrapped(api,entry,bits):
  source=SOURCE.read_text()
  assert source.count("* = $0900")==1
  assembled,labels,_=Assembler().assemble(
      source.replace("* = $0900","* = $0e00"))
  start=labels["MUL32_SHR16_BEGIN"]
  end=labels["MUL32_SHR16_END"]
  assert start==ORIGIN and end>start
  original_code,original_stop=original(api,entry,bits)
  assert original_code[:6]==b"\x78\xd8\xa9\x34\x85\x01"
  assert original_code[6]==0x20
  assert original_code[9:11]==b"\xa2\x00"
  loop=H+11
  original_jmp=bytes((0x4c,loop&255,loop>>8))
  assert original_code.count(original_jmp)==1
  assert original_code[-3:]==bytes((0x4c,original_stop&255,original_stop>>8))
  def jsr(addr):return bytes((0x20,addr&255,addr>>8))
  new_stop=original_stop+6
  code=(original_code[:9]+jsr(start)+original_code[9:-3]+jsr(end)+
        bytes((0x4c,new_stop&255,new_stop>>8)))
  relocated_loop=loop+3
  assert code.count(original_jmp)==1
  code=code.replace(original_jmp,
                    bytes((0x4c,relocated_loop&255,relocated_loop>>8)))
  assert H+len(code)==new_stop+3
  assert H+len(code)<ORIGIN
  code+=bytes(ORIGIN-(H+len(code)))
  for pc in range(ORIGIN,max(assembled)+1):
   code+=bytes((assembled.get(pc,0),))
  assert H+len(code)<0x1000
  return code,new_stop
 return wrapped

def main():
    released=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    original=(ROOT/PROFILE/"resident"/("math_"+PROFILE+"_game_math.prg")).read_bytes()
    assert sha(original)==released["reference_prg_sha256"][PROFILE]
    output={"status":"PASS_NATIVE_EXCLUSIVE_BEGIN_CALL_END","profile":PROFILE,
            "published_prg_sha256":sha(original),
            "source_sha256":sha(SOURCE.read_bytes()),
            "entry":ENTRY,"calls":COUNT*2,
            "native_cycle_timing_measured":False,
            "default_prg_changed":False,
            "regular_mixed_call_qualified":False,
            "true_source_assembled_in_harness":True}
    with tempfile.TemporaryDirectory(prefix="issue144_beginend_native_") as t:
      temp=Path(t)
      baseline=native.run_native(PROFILE,original,ENTRY,15820,temp,
                                os.getenv("VICE_WRAPPER","x64sc"))
      previous=native.make_harness
      native.make_harness=wrap_generator(previous)
      try:
       specialist=native.run_native(PROFILE,original,ENTRY,15821,temp,
                                   os.getenv("VICE_WRAPPER","x64sc"))
      finally:
       native.make_harness=previous
    old,new=baseline["dump"],specialist["dump"]
    assert len(old)==len(new)==len(FIELDS)*STRIDE
    for row in list(range(6))+list(range(8,len(FIELDS))):
      if row==16:
       assert all((old[row*STRIDE+i]&1)==(new[row*STRIDE+i]&1)==0
                  for i in range(COUNT))
      else:
       assert old[row*STRIDE:(row+1)*STRIDE]==new[row*STRIDE:(row+1)*STRIDE],(
             "native ABI divergence",row)
    output.update({
      "baseline_dump_sha256":baseline["dump_sha256"],
      "batch_dump_sha256":specialist["dump_sha256"],
      "outputs_6_bytes_exact":True,
      "carry_zero_and_inputs_stack_match":True,
      "volatile_status_flags_may_differ":True,
      "begin_and_end_executed_native":True,
      "ordinary_umul32_while_active_illegal":True})
    dest=ROOT/"validation/review/ISSUE144_V2_SHR16_BEGIN_END_NATIVE_VICE.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("ISSUE144 NATIVE VICE SOURCE-BACKED BEGIN/CALL/END PASS",
          output["calls"],flush=True)
if __name__=="__main__":main()
