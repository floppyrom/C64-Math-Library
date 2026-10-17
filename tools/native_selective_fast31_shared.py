#!/usr/bin/env python3
"""Native VICE: one linked FAST31 image, both signed/unsigned public exports."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker
from native_selective_umul32 import run_native as run_unsigned, N
from native_selective_smul32 import run_native as run_signed

SHARED="link:fast31-shared-full64"
def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must name actual x64sc emulator")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="native_fast31_shared_") as d:
        root=Path(d)
        for i,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(
                index,["SMUL32","UMUL32"],objective="size",
                zp_budget=31,ram_budget=3000,
                pins={"SMUL32":SHARED,"UMUL32":SHARED})
            manifest=selective_linker.build(plan,root,memory={
                "code_base":code,"math_io":io,"zp_base":zp})
            assert len(manifest["link_order"])==1
            assert manifest["resource_use"]["zero_page_bytes"]==31
            e={v["api"]:int(v["entry"][1:],16) for v in manifest["operations"]}
            prg=(root/"math_selective.prg").read_bytes()
            for signed in (False,True):
                api="MATH_SMUL32" if signed else "MATH_UMUL32"
                proof=run_signed if signed else run_unsigned
                digest=proof(vice,prg,e[api],code,io,
                    "fast31_shared_%s_%04x"%("signed" if signed else "unsigned",code),
                    9440+i*2+int(signed),root)
                total+=N
                print("NATIVE SHARED FAST31",api,hex(code),N,"PASS",digest,flush=True)
    assert total==4*N
    print("NATIVE FAST31 BOTH EXPORTS TWO MAPS PASS",total)

if __name__=="__main__":
    main()
