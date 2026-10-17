#!/usr/bin/env python3
"""Native VICE qualification of FAST31 selected through the operation-first builder."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker
from native_selective_umul32 import run_native,N

IDENT="link:fast31-v2-public"

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to native x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="umul32_fast31_link_") as td:
        folder=Path(td)
        for k,(base,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(
                index,["UMUL32"],objective="size",zp_budget=31,
                ram_budget=3000,pins={"UMUL32":IDENT})
            man=selective_linker.build(plan,folder,memory={
                "code_base":base,"math_io":io,"zp_base":zp})
            assert man["operations"][0]["variant"]==IDENT
            assert man["resource_use"]["zero_page_bytes"]==31
            entry=int(man["operations"][0]["entry"][1:],16)
            digest=run_native(vice,(folder/"math_selective.prg").read_bytes(),
                              entry,base,io,"umul32_fast31_link_%04x"%base,
                              9180+k,folder)
            total+=N
            print("NATIVE LINKED FAST31 UMUL32",hex(base),N,"PASS",digest,flush=True)
    assert total==2*N
    print("NATIVE LINKED FAST31 UMUL32 TWO MAPS PASS",total)

if __name__=="__main__":
    main()
