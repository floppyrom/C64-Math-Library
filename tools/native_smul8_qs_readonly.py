#!/usr/bin/env python3
"""Pinned native VICE r46284 proof of immutable signed8 quarter-square source."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker as linker
import native_selective_smul8 as old

VARIANT="link:qs-readonly"

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must resolve native pinned x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="read_only_smul8_vice_") as td:
        folder=Path(td)
        for k,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                index,["SMUL8"],objective="size",
                pins={"SMUL8":VARIANT},zp_budget=0,ram_budget=1193)
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"scratch_base":io+0x40})
            assert man["operations"][0]["variant"]==VARIANT
            assert man["resource_use"]["image_span_bytes"]==1159
            assert man["resource_use"]["zero_page_bytes"]==0
            assert man["resource_use"]["private_ram_scratch_bytes"]==2
            binary=(folder/"math_selective.prg").read_bytes()
            entry=int(man["operations"][0]["entry"][1:],16)
            digest=old.verify(vice,binary,entry,code,io,
                "smul8_qs_readonly_%04x"%code,9260+k,folder,"SMUL8")
            print("SMUL8 QS READONLY VICE PASS",hex(code),old.N,digest,flush=True)
            total+=old.N
    assert total==2*old.N
    print("SMUL8 QS READONLY BOTH NATIVE MAPS PASS",total)

if __name__=="__main__":
    main()
