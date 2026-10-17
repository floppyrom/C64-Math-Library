#!/usr/bin/env python3
"""Native VICE of the *builder-linked* canonical V2 12-ZP size-fast 32/16 core."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path

import math_builder
import selective_linker
from native_selective_u3216 import native,N

FAST="link:v2-sizefast-public"
APIS=("UDIV32_16","UMOD32_16")

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER requires native x64sc")
    index=math_builder.operation_index()
    count=0
    with tempfile.TemporaryDirectory(prefix="native_linked_v2fast_u3216_") as td:
        root=Path(td)
        for k,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(index,list(APIS),objective="size",
                zp_budget=12,ram_budget=2400,pins={api:FAST for api in APIS})
            man=selective_linker.build(plan,root,memory={
                "code_base":code,"math_io":io,"zp_base":zp})
            assert len(man["link_order"])==1
            assert man["resource_use"]["main_ram_total_bytes"]==2400
            assert man["resource_use"]["zero_page_bytes"]==12
            entries={r["api"]:int(r["entry"][1:],16) for r in man["operations"]}
            prg=(root/"math_selective.prg").read_bytes()
            ram=bytearray(65536);ram[code:code+len(prg)-2]=prg[2:]
            for j,api in enumerate(("MATH_UDIV32_16","MATH_UMOD32_16")):
                digest=native(vice,bytearray(ram),entries[api],code,io,
                    "linked_v2fast_%s_%04x"%(api.lower(),code),
                    9900+k*2+j,root)
                count+=N
                print("NATIVE LINKED V2FAST U3216",api,hex(code),N,"PASS",digest,flush=True)
    assert count==4*N
    print("NATIVE LINKED V2 FAST U3216 DIV/MOD TWO MAPS PASS",count)

if __name__=="__main__":
    main()
