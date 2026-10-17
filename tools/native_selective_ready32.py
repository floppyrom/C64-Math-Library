#!/usr/bin/env python3
"""Native VICE comparison of operation-first READY32 and safe ordinary aliases."""
from __future__ import annotations
import os
from pathlib import Path
import tempfile
import math_builder
import selective_linker
from native_selective_umul32 import run_native as run_unsigned, N as UN
from native_selective_smul32 import run_native as run_signed, N as SN

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must name native x64sc")
    index=math_builder.operation_index()
    ops=("UMUL32","UMUL32_READY","SMUL32","SMUL32_READY")
    count=0
    with tempfile.TemporaryDirectory(prefix="ready32_native_") as td:
        folder=Path(td)
        for map_i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(index,list(ops),objective="size",
                zp_budget=0,ram_budget=541)
            man=selective_linker.build(plan,folder,
                memory={"code_base":code,"math_io":io})
            assert man["resource_use"]["image_span_bytes"]==497
            assert man["resource_use"]["main_ram_total_bytes"]==541
            assert man["resource_use"]["zero_page_bytes"]==0
            ep={v["api"]:int(v["entry"][1:],16) for v in man["operations"]}
            assert ep["MATH_UMUL32"]==ep["MATH_UMUL32_READY"]
            assert ep["MATH_SMUL32"]==ep["MATH_SMUL32_READY"]
            prg=(folder/"math_selective.prg").read_bytes()
            for k,name in enumerate(ops):
                entry=ep["MATH_"+name]
                run=run_signed if name.startswith("SMUL") else run_unsigned
                digest=run(vice,prg,entry,code,io,name.lower()+"_%04x"%code,
                           8370+4*map_i+k,folder)
                count+=SN if name.startswith("SMUL") else UN
                print("NATIVE",name,hex(code),"PASS",digest,flush=True)
    assert count==8*UN
    print("NATIVE READY32 ALIAS 2-MAP PASS",count)

if __name__=="__main__":
    main()
