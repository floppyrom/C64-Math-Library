#!/usr/bin/env python3
"""Pinned native x64sc r46284 shared historical V2 signed 16/16 Q/R proof."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker as linker
import native_selective_sdiv16 as harness

FAST="link:v2-signed-shared"


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to native pinned x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="v2_signed16_shared_vice_") as td:
        out=Path(td)
        for k,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                index,["SDIV16","SMOD16"],objective="size",
                pins={"SDIV16":FAST,"SMOD16":FAST},
                zp_budget=0,ram_budget=1745)
            man=linker.build(plan,out,memory={
                "code_base":code,"math_io":io,"scratch_base":io+0x40})
            assert len(man["operations"])==2
            assert len(man["link_order"])==1
            assert {p["variant"] for p in man["operations"]}=={FAST}
            assert len({p["entry"] for p in man["operations"]})==1
            assert man["resource_use"]["image_span_bytes"]==1705
            assert man["resource_use"]["zero_page_bytes"]==0
            assert man["resource_use"]["private_ram_scratch_bytes"]==8
            raw=(out/"math_selective.prg").read_bytes()
            entry=int(man["operations"][0]["entry"][1:],16)
            digest=harness.verify(vice,raw,entry,code,io,
               "v2_signed16_shared_%04x"%code,9300+k,out)
            total+=harness.N
            print("V2 SIGNED16 Q/R SHARED NATIVE PASS",
                  hex(code),harness.N,digest,flush=True)
    assert total==2*harness.N
    print("V2 SIGNED16 Q/R 192 NATIVE CALLS PASS",total)


if __name__=="__main__":
    main()
