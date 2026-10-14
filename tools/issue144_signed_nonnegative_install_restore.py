#!/usr/bin/env python3
"""Assembly and CPU-state qualification of signed nonnegative alias installer."""
from __future__ import annotations
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import CORPORA,load
from issue144_shr16_independent_clone import PROFILES,assemble,installed_mem,sha
from issue144_shr16_direct_slice_overlay_research import run
from issue144_signed_shr16_hybrid_research import ENTRY,DEFAULT_JMP

SOURCE="optional/issue144_signed_shr16_hybrid/nonnegative_enable_disable.asm"
OUT="validation/review/ISSUE144_SIGNED_NONNEGATIVE_INSTALLER_MODEL.json"
def main():
    program=(R/SOURCE).read_text()
    code,labels,_=Assembler().assemble(program)
    assert min(code)==0x0C00 and max(code)<0x0C80
    _,clone,_,_,_=assemble()
    result={"status":"PASS_SIGNED_NONNEGATIVE_INSTALL_RESTORE_MODEL",
       "assembly_sha256":sha(program.encode()),
       "compiler_emitted_bytes":len(code),
       "code_range":[hex(min(code)),hex(max(code))],
       "profiles":{},"production_images_written":False,
       "only_signed_public_entry_target_touched":True,
       "guaranteed_nonnegative_operands_required":True}
    pairs=[(x,y) for x,y in CORPORA[32]
       if x<0x80000000 and y<0x80000000][:80]
    for p in PROFILES:
        c,api=load(p)
        installed_mem(c,clone)
        for pc,b in code.items():
            assert c.mem[pc]==0,("installer RAM occupied",p,hex(pc))
            c.mem[pc]=b
        assert bytes(c.mem[ENTRY:ENTRY+3])==DEFAULT_JMP
        before=bytes(c.mem[ENTRY:ENTRY+3])
        c.call(labels["SMUL32_SHR16_NONNEG_ENABLE"],200000)
        assert c.c==0
        assert bytes(c.mem[ENTRY:ENTRY+3])==bytes((0x4C,0x03,0x0E))
        for x,y in pairs:
            run(c,api,"MATH_SMUL32_SHR16",x,y)
            run(c,api,"MATH_UMUL32",x,y)
            run(c,api,"MATH_SMUL32",x,y)
        c.call(labels["SMUL32_SHR16_NONNEG_DISABLE"],200000)
        assert c.c==0
        assert bytes(c.mem[ENTRY:ENTRY+3])==before
        for x,y in pairs:
            run(c,api,"MATH_SMUL32_SHR16",x,y)
        result["profiles"][p]={"status":"PASS",
          "enabled_public_entry":"$5E15 -> $0E03",
          "restored_public_entry":"$5E15 -> $C50C",
          "enable_disable_source_executed":True,
          "signed_and_unsigned_calls_while_enabled":True,
          "nonnegative_calls_each_phase":len(pairs)}
        print("SIGN-QUALIFIED PUBLIC ENTRY INSTALL/RESTORE",p,"PASS",flush=True)
    path=R/OUT
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":
    main()
