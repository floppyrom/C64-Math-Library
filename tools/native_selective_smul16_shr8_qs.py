#!/usr/bin/env python3
"""Pinned VICE r46284 signed Q8.8 quarter-square public PRG two-map gate."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker as linker
import native_selective_smul16_shr8 as native

VARIANT="link:qs-signed-shr8-public"

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must resolve pinned native x64sc")
    index=math_builder.operation_index()
    count=0
    with tempfile.TemporaryDirectory(prefix="smul16_shr8_qs_native_") as td:
        out=Path(td)
        for i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                index,["SMUL16_SHR8"],objective="size",
                pins={"SMUL16_SHR8":VARIANT},zp_budget=0,ram_budget=1419)
            man=linker.build(plan,out,memory={
                "code_base":code,"math_io":io,"scratch_base":io+0x40})
            assert man["operations"][0]["variant"]==VARIANT
            assert man["resource_use"]["image_span_bytes"]==1383
            assert man["resource_use"]["zero_page_bytes"]==0
            assert man["resource_use"]["private_ram_scratch_bytes"]==4
            entry=int(man["operations"][0]["entry"][1:],16)
            image=(out/"math_selective.prg").read_bytes()
            digest=native.run_native(
                vice,image,entry,code,io,
                "qs_smul16_shr8_%04x"%code,9150+i,out)
            print("SMUL16 SHR8 QS NATIVE PASS",hex(code),native.N,digest,flush=True)
            count+=native.N
    assert count==2*native.N
    print("SMUL16 SHR8 QS TWO-MAP PINNED VICE PASS",count)

if __name__=="__main__":
    main()
