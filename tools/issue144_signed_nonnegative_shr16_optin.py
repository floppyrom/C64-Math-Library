#!/usr/bin/env python3
"""Issue144 signed SHR16: qualified-operand NONNEGATIVE specialist screen.

If the application proves both signed 32-bit operands are >=0, their signed
product equals the unsigned product exactly; the established independent
unsigned SHR16 producer is then directly usable from the signed public JMP.
That precondition is essential. This is an opt-in source study, not a default.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from benchmark_multiply_refresh import CORPORA,load
from issue144_shr16_direct_slice_overlay_research import run,metrics
from issue144_shr16_independent_clone import (
    PROFILES, ENTRY_CLONE,assemble,installed_mem,sha)
from issue144_signed_shr16_hybrid_research import ENTRY,DEFAULT_JMP,stats_signed

OUT="validation/review/ISSUE144_SIGNED_NONNEGATIVE_SHR16_OPTIN_MODEL.json"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--limit",type=int,default=2409)
    a=ap.parse_args()
    assert 1<=a.limit<=len(CORPORA[32])
    q=[(x,y) for x,y in CORPORA[32][:a.limit]
         if x<0x80000000 and y<0x80000000]
    assert q
    _,clone,_,source,_=assemble()
    rec={"status":"PASS_NONNEGATIVE_SIGNED_SHR16_RESEARCH_MODEL",
      "signed_input_precondition":"both input sign bits clear",
      "input_pairs":len(q),"profiles":{},
      "only_original_signed_public_JMP_two_operands_redirected":True,
      "clone_entry":hex(ENTRY_CLONE),
      "native_vice_not_timed":True,
      "unsigned_clone_source_sha256":sha(source.encode()),
      "not_safe_when_either_input_is_negative":True,
      "default_production_unchanged":True}
    for p in PROFILES:
        old,api=load(p);new,copy_api=load(p)
        assert api==copy_api
        installed_mem(new,clone)
        assert bytes(new.mem[ENTRY:ENTRY+3])==DEFAULT_JMP
        new.mem[ENTRY+1:ENTRY+3]=bytes((ENTRY_CLONE&255,ENTRY_CLONE>>8))
        left=[];right=[]
        for i,(x,y) in enumerate(q):
            assert (x|y)&0x80000000==0
            if i%29==0:
                xx,yy=q[(i*23+17)%len(q)]
                for machine in (old,new):
                    run(machine,api,"MATH_SMUL32",xx,yy)
                    run(machine,api,"MATH_UMUL32",xx,yy)
            c0,o0=run(old,api,"MATH_SMUL32_SHR16",x,y)
            c1,o1=run(new,copy_api,"MATH_SMUL32_SHR16",x,y)
            assert o0==o1
            left.append(c0);right.append(c1)
        diff=[u-v for u,v in zip(left,right)]
        assert min(diff)>0,(p,min(diff))
        new.mem[ENTRY+1:ENTRY+3]=DEFAULT_JMP[1:]
        for x,y in q[:min(64,len(q))]:
            run(new,api,"MATH_SMUL32_SHR16",x,y)
        rec["profiles"][p]={
          "status":"PASS_PRECONDITIONED_PUBLIC_ENTRY",
          "cases":len(q),"baseline":metrics(left),
          "optin":metrics(right),
          "paired_savings":stats_signed(diff),
          "min_savings_positive":True,
          "ordinary_calls_interleaved":True,
          "signed_public_entry_restored_and_retested":True,
        }
        print("NONNEGATIVE SIGNED",p,"cases",len(q),"mean saved",
              rec["profiles"][p]["paired_savings"]["mean_cycles"],flush=True)
    dest=ROOT/OUT
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
    print("ISSUE144 NONNEGATIVE SIGNED SHR16 SPECIALIST PASS",len(q)*len(PROFILES))
if __name__=="__main__":
    main()
