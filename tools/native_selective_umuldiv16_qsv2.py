#!/usr/bin/env python3
"""Native pinned x64sc public unsigned UMULDIV16 historical QS+V2 fusion."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker as linker
import native_selective_muldiv16 as native

VARIANT="link:qs-v2-fused"

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must resolve pinned x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="umuldiv16_qsv2_native_") as td:
        folder=Path(td)
        for k,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(
                index,["UMULDIV16"],objective="size",
                pins={"UMULDIV16":VARIANT},zp_budget=12,ram_budget=3691)
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"zp_base":zp,
                "scratch_base":io+0x40})
            assert man["operations"][0]["variant"]==VARIANT
            assert man["resource_use"]["image_span_bytes"]==3655
            assert man["resource_use"]["zero_page_bytes"]==12
            assert man["resource_use"]["private_ram_scratch_bytes"]==4
            entry=int(man["operations"][0]["entry"][1:],16)
            prg=(folder/"math_selective.prg").read_bytes()
            digest=native.run_native(
                vice,prg,entry,code,io,False,
                "umuldiv16_qsv2_%04x"%code,9550+k,folder)
            total+=native.N
            print("UMULDIV16 QS V2 NATIVE PASS",hex(code),native.N,digest,flush=True)
    assert total==2*native.N
    print("UMULDIV16 QS V2 TWO-MAP NATIVE VICE PASS",total)

if __name__=="__main__":
    main()
