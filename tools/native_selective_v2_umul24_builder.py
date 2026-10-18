#!/usr/bin/env python3
"""Pinned native VICE r46284 public UMUL24 biased V2 builder qualification."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker as linker
import native_selective_umul24 as native

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("Set VICE_WRAPPER to pinned native x64sc")
    index=math_builder.operation_index()
    count=0
    with tempfile.TemporaryDirectory(prefix="public_v2_umul24_") as td:
        folder=Path(td)
        for i,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(index,["UMUL24"],objective="size",
                zp_budget=24,ram_budget=3000,
                pins={"UMUL24":"link:v2-quarter-square"})
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"zp_base":zp,
                "scratch_base":io+0x40})
            assert man["resource_use"]["zero_page_bytes"]==24
            assert man["operations"][0]["variant"]=="link:v2-quarter-square"
            entry=int(man["operations"][0]["entry"][1:],16)
            img=(folder/"math_selective.prg").read_bytes()
            digest=native.run_native(vice,img,entry,code,io,
                "linked_biased_v2_umul24_%04x"%code,9280+i,folder)
            print("BIAS-CARRY V2 UMUL24 NATIVE",hex(code),native.N,
                  digest,flush=True)
            count+=native.N
    assert count==native.N*2
    print("NATIVE BIASED V2 UMUL24 2-LAYOUT PASS",count)

if __name__=="__main__":
    main()
