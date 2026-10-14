#!/usr/bin/env python3
"""Real x64sc correctness for signed SHR16 two opt-in public-entry variants.

24 native operand pairs per variant/profile. No CPU cycle timings attributed
to VICE. Stock 32-bit signed/unsigned producers and PRGs remain unchanged.
"""
from __future__ import annotations
import json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from issue144_shr16_independent_clone import assemble,CLONE,PROFILES,sha
from issue144_signed_shr16_hybrid_research import SOURCE,VARIANTS,ENTRY,DEFAULT_JMP
from native_issue144_shr16_independent_clone import verify_output
import native_issue39_fixed_shr16_tail as native
from native_issue39_signed_multiply_family import H, COUNT

OP="MATH_SMUL32_SHR16"
OUT="validation/review/ISSUE144_SIGNED_SHR16_HYBRID_NATIVE_VICE.json"

def source_harness(code_map,original):
    def extend(api,entry,bits):
        code,stop=original(api,entry,bits)
        assert H+len(code)<CLONE,(hex(H+len(code)),"harness overlaps optional code")
        code+=bytes(CLONE-H-len(code))
        code+=bytes(code_map.get(p,0) for p in range(CLONE,max(code_map)+1))
        assert H+len(code)<0x1000,hex(H+len(code))
        return code,stop
    return extend

def main():
    _, clone, _, unsigned_source, _=assemble()
    asm=(ROOT/SOURCE).read_text()
    signed_code, labels, _=Assembler().assemble(asm)
    assert not set(clone).intersection(signed_code)
    code_map=dict(clone)
    code_map.update(signed_code)
    state=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    result={
        "status":"PASS_NATIVE_SIGNED_SHR16_OPTIONAL_SOURCE_CORRECTNESS",
        "native_cpu_cycles_measured":False,
        "source_sha256":sha(asm.encode()),
        "unsigned_clone_sha256":sha(unsigned_source.encode()),
        "results":{},"native_calls_total":0,
        "resident_prgs_changed":False,"resident_reu_changed":False,
        "default_library_abi_changed":False,
        "extra_code_RAM_and_shared_ZP":True,
        "interrupt_reentrant_safe":False,
    }
    exe=os.getenv("VICE_WRAPPER","x64sc")
    with tempfile.TemporaryDirectory(prefix="issue144_signed_vice_") as tmp:
        temp=Path(tmp)
        for pi,p in enumerate(PROFILES):
            binary=(ROOT/p/"resident"/f"math_{p}_game_math.prg").read_bytes()
            assert sha(binary)==state["reference_prg_sha256"][p]
            at=ENTRY-0x1000+2
            assert binary[at:at+3]==DEFAULT_JMP
            baseline=native.run_native(p,binary,OP,16600+pi*10,temp,exe)
            result["native_calls_total"]+=COUNT
            row={"baseline":baseline["dump_sha256"],"variants":{}}
            for vi,(kind,labelname) in enumerate(VARIANTS.items()):
                entry=labels[labelname]
                patched=bytearray(binary)
                patched[at+1:at+3]=bytes((entry & 255,entry >> 8))
                assert patched[at]==0x4C
                prev=native.make_harness
                native.make_harness=source_harness(code_map,prev)
                try:
                    tested=native.run_native(
                      p,bytes(patched),OP,16601+pi*10+vi,temp,exe)
                finally:
                    native.make_harness=prev
                verify_output(baseline["dump"],tested["dump"],p)
                row["variants"][kind]={
                    "native_signed_pairs":COUNT,
                    "status":"PASS_SIX_BYTES_FLAGS_INPUT_AND_STACK",
                    "public_entry_retained":"$5E15",
                    "redirected_target":hex(entry),
                    "original_signed_producer_bytes_patched":False,
                    "only_two_public_jmp_operands_patched_in_disposable_copy":True,
                    "native_cycles_measured":False}
                result["native_calls_total"]+=COUNT
                print("NATIVE SIGNED",p,kind,COUNT,"PASS",flush=True)
            result["results"][p]=row
    assert result["native_calls_total"]==len(PROFILES)*(1+len(VARIANTS))*COUNT
    output=ROOT/OUT
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("ISSUE144 SIGNED HYBRID NATIVE VICE PASS",result["native_calls_total"])

if __name__=="__main__":
    main()
