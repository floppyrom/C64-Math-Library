#!/usr/bin/env python3
"""Native VICE proof of both operation-first *linked* hybrid public entries."""
from __future__ import annotations
import os
import sys
import tempfile
from pathlib import Path
import math_builder
import selective_linker

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"routines/standalone_lab/portable"))
from native_vice import VICE,check

ID="link:v2-lowdivisor-hybrid"
APIS=("UDIV32_32","UMOD32_32")

def main():
    if not os.environ.get("VICE_WRAPPER") or not VICE.is_file():
        raise RuntimeError("Real native x64sc required in VICE_WRAPPER")
    idx=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="native_v2hybrid_builder_") as td:
        root=Path(td)
        for k,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(
                idx,list(APIS),objective="size",ram_budget=3232,
                zp_budget=12,pins={api:ID for api in APIS})
            man=selective_linker.build(plan,root,memory={
                "code_base":code,"math_io":io,"zp_base":zp})
            assert len(man["link_order"])==1
            assert man["resource_use"]["zero_page_bytes"]==12
            entries={x["api"]:int(x["entry"][1:],16) for x in man["operations"]}
            prg=(root/"math_selective.prg").read_bytes()
            memory=bytearray(65536)
            memory[code:code+len(prg)-2]=prg[2:]
            mapping={"INPUT_NUM":io+16,"INPUT_DIV":io+20,
                     "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28}
            for j,api in enumerate(("MATH_UDIV32_32","MATH_UMOD32_32")):
                r=check(bytearray(memory),entries[api],32,mapping,
                        "linked_hybrid_%s_%04x"%(api.lower(),code),
                        9780+2*k+j,root,False)
                total+=r["cases"]
                print("NATIVE LINKED HYBRID U3232",api,hex(code),
                      r["cases"],"PASS",flush=True)
    assert total==384,total
    print("NATIVE LINKED V2 LOW-DIVISOR U3232 Q/R TWO-MAP PASS",total)

if __name__=="__main__":
    main()
