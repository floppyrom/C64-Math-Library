#!/usr/bin/env python3
"""Native VICE proof of linked unrolled public Q32/R16 shared producer."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker
from native_selective_u3216 import native,N

FAST="link:accum-unrolled-32"
APIS=("UDIV32_16","UMOD32_16")

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must name native x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="native_u3216_unrolled_linked_") as td:
        root=Path(td)
        for k,(code,io,scratch) in enumerate(((0x8000,0xc000,0xc020),
                                            (0x7123,0xc040,0xc080))):
            plan=math_builder.create_plan(
                index,list(APIS),objective="size",zp_budget=0,
                ram_budget=1804,pins={api:FAST for api in APIS})
            man=selective_linker.build(plan,root,memory={
                "code_base":code,"math_io":io,"scratch_base":scratch})
            assert len(man["link_order"])==1
            assert man["resource_use"]["main_ram_total_bytes"]==1804
            entries={x["api"]:int(x["entry"][1:],16) for x in man["operations"]}
            prg=(root/"math_selective.prg").read_bytes()
            image=bytearray(65536)
            image[code:code+len(prg)-2]=prg[2:]
            for j,api in enumerate(("MATH_UDIV32_16","MATH_UMOD32_16")):
                digest=native(vice,bytearray(image),entries[api],code,io,
                              "unrolled_linked_%s_%04x"%(api.lower(),code),
                              9820+k*2+j,root)
                total+=N
                print("NATIVE LINKED UNROLLED U3216",api,hex(code),N,
                      "PASS",digest,flush=True)
    assert total==4*N
    print("NATIVE LINKED UNROLLED ZERO-ZP U3216 BOTH APIS PASS",total)

if __name__=="__main__":
    main()
