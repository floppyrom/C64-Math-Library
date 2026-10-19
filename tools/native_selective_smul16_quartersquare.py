#!/usr/bin/env python3
"""Pinned native VICE r46284 proof of signed16 quarter-square public calls."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import native_selective_smul16 as harness

VARIANT="link:qs-signed-public"


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to pinned native x64sc")
    index=math_builder.operation_index()
    count=0
    with tempfile.TemporaryDirectory(prefix="smul16_qs_native_") as td:
        folder=Path(td)
        for i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(index,["SMUL16"],objective="size",
                pins={"SMUL16":VARIANT},
                zp_budget=0,ram_budget=1387)
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"scratch_base":io+0x40})
            assert man["operations"][0]["variant"]==VARIANT
            assert man["resource_use"]["image_span_bytes"]==1351
            assert man["resource_use"]["zero_page_bytes"]==0
            assert man["resource_use"]["private_ram_scratch_bytes"]==4
            entry=int(man["operations"][0]["entry"][1:],16)
            binary=(folder/"math_selective.prg").read_bytes()
            digest=harness.run_native(
                vice,binary,entry,code,io,
                "smul16_signed_qs_%04x"%code,9050+i,folder)
            count+=harness.N
            print("SMUL16 SIGNED QS VICE PASS",hex(code),
                  harness.N,digest,flush=True)
    assert count==2*harness.N
    print("SMUL16 SIGNED QS TWO-MAP VICE PASS",count)


if __name__=="__main__":
    main()
