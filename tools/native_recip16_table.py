#!/usr/bin/env python3
"""Native VICE r46284 exact Q16 table reciprocal in two C64 memory layouts."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import native_selective_urecip16_q16 as harness

VARIANT="link:threshold-tables-zerozp"


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to native x64sc")
    total=0
    index=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix="recip16_table_native_") as td:
        folder=Path(td)
        for i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                index,["URECIP16_Q16"],objective="size",
                pins={"URECIP16_Q16":VARIANT},
                zp_budget=0,ram_budget=1576)
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io})
            assert man["resource_use"]["image_span_bytes"]==1544
            assert man["resource_use"]["main_ram_total_bytes"]==1576
            assert man["resource_use"]["zero_page_bytes"]==0
            entry=int(man["operations"][0]["entry"][1:],16)
            binary=(folder/"math_selective.prg").read_bytes()
            mem=bytearray(65536)
            mem[code:code+len(binary)-2]=binary[2:]
            digest=harness.native(
                vice,mem,entry,code,io,
                "recip16_table_%04x"%code,9870+i,folder)
            total+=harness.N
            print("RECIP16 TABLE NATIVE PASS",hex(code),
                  harness.N,digest,flush=True)
    assert total==2*harness.N
    print("RECIP16 TABLE TWO-MAP NATIVE PASS",total)


if __name__=="__main__":
    main()
