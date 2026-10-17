#!/usr/bin/env python3
"""Six real public entrypoints from one *operation-first-linked* FAST31 PRG."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker
from native_selective_umul32 import run_native as run_u,N
from native_selective_smul32 import run_native as run_s
from native_selective_umul32_shr16 import run_native as run_ushr
from native_selective_smul32_shr16 import run_native as run_sshr
from test_selective_fast31_six_source import OPS

ID="link:fast31-shared-full64"
def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to real headless x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="native_fast31_six_linked_") as td:
        root=Path(td)
        for k,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(index,list(OPS),objective="size",
                zp_budget=31,ram_budget=3000,pins={name:ID for name in OPS})
            man=selective_linker.build(plan,root,memory={
                "code_base":code,"math_io":io,"zp_base":zp})
            assert len(man["link_order"])==1
            assert man["resource_use"]["zero_page_bytes"]==31
            entries={x["api"].removeprefix("MATH_"):int(x["entry"][1:],16)
                     for x in man["operations"]}
            binary=(root/"math_selective.prg").read_bytes()
            for i,op in enumerate(OPS):
                run=run_s if op.startswith("SMUL") else run_u
                if op.endswith("SHR16"):
                    run=run_sshr if op.startswith("SMUL") else run_ushr
                digest=run(vice,binary,entries[op],code,io,
                           "sixbuilder_%s_%04x"%(op.lower(),code),
                           9660+k*len(OPS)+i,root)
                total+=N
                print("NATIVE LINKED FAST31 SIX",op,hex(code),N,"PASS",digest,flush=True)
    assert total==12*N
    print("NATIVE LINKED FAST31 SIX ENTRIES TWO MAPS PASS",total)

if __name__=="__main__":
    main()
