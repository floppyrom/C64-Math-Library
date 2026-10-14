#!/usr/bin/env python3
"""Real VICE nonnegative signed SHR16 public-entry alias proof.

The 24 native vectors are filtered to sign-bit-clear signed operands;
this specialization must not be used for arbitrary signed inputs.
"""
from __future__ import annotations
import json,os,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from issue144_shr16_independent_clone import assemble,ENTRY_CLONE,PROFILES,sha
from issue144_signed_shr16_hybrid_research import ENTRY,DEFAULT_JMP
from native_issue144_shr16_independent_clone import verify_output
from native_issue144_shr16_public_entry_optin import patched_harness
import native_issue39_fixed_shr16_tail as native
from native_issue39_signed_multiply_family import COUNT
OP="MATH_SMUL32_SHR16"
OUT="validation/review/ISSUE144_SIGNED_NONNEGATIVE_SHR16_NATIVE_VICE.json"

def main():
    _,copy,_,source,_=assemble()
    state=json.loads((R/"RELEASE_STATUS.json").read_text())
    report={"status":"PASS_NATIVE_NONNEGATIVE_SIGNED_SHR16_OPTIN",
            "precondition":"x>=0 and y>=0 as signed 32-bit integers",
            "profiles":{},"native_calls":0,
            "native_cpu_cycles_measured":False,
            "signed_public_address":"$5E15",
            "alias_unsigned_clone":hex(ENTRY_CLONE),
            "ordinary_signed_producer_unchanged":True,
            "default_prgs_reu_unchanged":True,
            "unsigned_clone_source_sha256":sha(source.encode())}
    exe=os.getenv("VICE_WRAPPER","x64sc")
    saved=native.pairs
    def nonnegative_pairs(bits):
        return [(x&((1<<(bits-1))-1),y&((1<<(bits-1))-1))
                 for x,y in saved(bits)]
    native.pairs=nonnegative_pairs
    try:
        with tempfile.TemporaryDirectory(prefix="issue144_signed_nonnegative_") as tmp:
            work=Path(tmp)
            for i,p in enumerate(PROFILES):
                prg=(R/p/"resident"/f"math_{p}_game_math.prg").read_bytes()
                assert sha(prg)==state["reference_prg_sha256"][p]
                at=ENTRY-0x1000+2
                assert prg[at:at+3]==DEFAULT_JMP
                after=bytearray(prg)
                after[at+1:at+3]=bytes((ENTRY_CLONE&255,ENTRY_CLONE>>8))
                old=native.run_native(p,prg,OP,17100+i*3,work,exe)
                prev=native.make_harness
                native.make_harness=patched_harness(copy,prev)
                try:
                    new=native.run_native(p,bytes(after),OP,17101+i*3,work,exe)
                finally:native.make_harness=prev
                verify_output(old["dump"],new["dump"],p)
                report["native_calls"]+=COUNT*2
                report["profiles"][p]={
                  "status":"PASS_NATIVE_PRECONDITIONED_PUBLIC_ENTRY",
                  "nonnegative_pairs":COUNT,
                  "baseline_calls":COUNT,"optimized_calls":COUNT,
                  "signed_six_output_bytes_equal":True,
                  "inputs_carry_and_stack_preserved":True}
                print("NATIVE NONNEGATIVE SIGNED",p,COUNT*2,"PASS",flush=True)
    finally:native.pairs=saved
    assert report["native_calls"]==len(PROFILES)*COUNT*2
    path=R/OUT
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE144 SIGNED NONNEGATIVE VICE PASS",report["native_calls"])

if __name__=="__main__":
    main()
