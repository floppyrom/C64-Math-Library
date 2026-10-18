#!/usr/bin/env python3
"""Two-layout pinned native VICE qualification of signed V2 hybrid DIV/MOD."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker as linker
import native_selective_sdiv32_32 as harness

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must be a native x64sc binary")
    index=math_builder.operation_index()
    count=0
    with tempfile.TemporaryDirectory(prefix="v2signed3232_") as td:
        folder=Path(td)
        for i,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(index,
                ["SDIV32_32","SMOD32_32"],objective="size",
                zp_budget=12,ram_budget=2912,
                pins={"SDIV32_32":"link:v2-hybrid-signed",
                      "SMOD32_32":"link:v2-hybrid-signed"})
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"zp_base":zp,
                "scratch_base":io+0x40})
            assert len(man["link_order"])==1
            assert man["resource_use"]["main_ram_total_bytes"]==2912
            assert man["resource_use"]["zero_page_bytes"]==12
            data=(folder/"math_selective.prg").read_bytes()
            entries={v["api"]:int(v["entry"][1:],16)
                     for v in man["operations"]}
            for j,api in enumerate(("MATH_SDIV32_32","MATH_SMOD32_32")):
                tag="linked_signed_v2hybrid_%04x_%s"%(code,api.lower())
                digest=harness.verify(vice,data,entries[api],code,io,
                                     tag,8310+i*2+j,folder)
                count+=harness.N
                print("SIGNED V2 HYBRID NATIVE",hex(code),api,
                      harness.N,digest,flush=True)
    assert count==4*harness.N
    print("SIGNED V2 HYBRID NATIVE 2-LAYOUT PASS",count)

if __name__=="__main__":
    main()
