#!/usr/bin/env python3
"""Pinned native VICE r46284 source and public signed shifted16 ABI test."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import native_selective_sdiv16_shl8 as harness

VARIANT="link:v2-signed-shifted-public"

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must be pinned native x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="v2_sdiv16_shl8_native_") as td:
        folder=Path(td)
        for i,(code,io,zp) in enumerate((
                (0x8000,0xc000,0x50),
                (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(
                index,["SDIV16_SHL8"],objective="size",
                pins={"SDIV16_SHL8":VARIANT},
                zp_budget=12,ram_budget=2656)
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,
                "zp_base":zp,"scratch_base":io+0x40})
            assert man["operations"][0]["variant"]==VARIANT
            assert man["resource_use"]["image_span_bytes"]==2624
            assert man["resource_use"]["zero_page_bytes"]==12
            assert man["resource_use"]["private_ram_scratch_bytes"]==0
            image=(folder/"math_selective.prg").read_bytes()
            entry=int(man["operations"][0]["entry"][1:],16)
            digest=harness.verify(vice,image,entry,code,io,
                "v2_signed_shifted16_%04x"%code,9950+i,folder)
            total+=harness.N
            print("V2 SIGNED SHL16 NATIVE PASS",hex(code),
                  harness.N,digest,flush=True)
    assert total==2*harness.N
    print("V2 SIGNED SHL16 TWO-MAP VICE PASS",total)

if __name__=="__main__":
    main()
