#!/usr/bin/env python3
"""Native VICE signed FAST31 linked by the operation-first compiler, two maps."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker
from native_selective_smul32 import run_native,N

IDENT="link:fast31-v2-signed"
def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must name actual x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="native_smul32_fast31_link_") as d:
        folder=Path(d)
        for i,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(
                index,["SMUL32"],objective="size",zp_budget=31,
                ram_budget=3000,pins={"SMUL32":IDENT})
            man=selective_linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"zp_base":zp})
            assert man["operations"][0]["variant"]==IDENT
            assert man["resource_use"]["zero_page_bytes"]==31
            entry=int(man["operations"][0]["entry"][1:],16)
            digest=run_native(vice,(folder/"math_selective.prg").read_bytes(),
                              entry,code,io,"smul32_fast31_link_%04x"%code,
                              9360+i,folder)
            total+=N
            print("NATIVE LINKED SMUL32 FAST31",hex(code),N,"PASS",digest,flush=True)
    assert total==2*N
    print("NATIVE LINKED SMUL32 FAST31 TWO MAPS PASS",total)

if __name__=="__main__":
    main()
