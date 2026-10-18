#!/usr/bin/env python3
"""Native VICE r46284: signed historical V2 producer linked by the builder."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import native_selective_sdiv32_16 as native

def main():
    vice = os.environ.get("VICE_WRAPPER", "")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must identify pinned native x64sc")
    index = math_builder.operation_index()
    count = 0
    with tempfile.TemporaryDirectory(prefix="builder_signed_v2_3216_") as temp:
        folder = Path(temp)
        for i,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                          (0x7123,0xc040,0x70))):
            plan = math_builder.create_plan(index,["SDIV32_16","SMOD32_16"],
                objective="size",zp_budget=12,ram_budget=2912,
                pins={"SDIV32_16":"link:v2-signed-magnitude",
                      "SMOD32_16":"link:v2-signed-magnitude"})
            man = linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"zp_base":zp})
            assert len(man["link_order"]) == 1
            assert man["resource_use"]["main_ram_total_bytes"] == 2912
            assert man["resource_use"]["zero_page_bytes"] == 12
            prg=(folder/"math_selective.prg").read_bytes()
            entries={op["api"]:int(op["entry"][1:],16) for op in man["operations"]}
            for j,api in enumerate(("MATH_SDIV32_16","MATH_SMOD32_16")):
                tag="linked_v2mag_%04x_%s"%(code,api.lower())
                digest=native.verify(vice,prg,entries[api],code,io,tag,
                                     8900+2*i+j,folder)
                count+=native.N
                print("BUILDER SIGNED V2 MAG NATIVE",hex(code),api,
                      native.N,digest,flush=True)
    assert count==2*2*native.N
    print("BUILDER SIGNED V2 MAG SHARED-PRODUCER VICE PASS",count)

if __name__=="__main__":
    main()
