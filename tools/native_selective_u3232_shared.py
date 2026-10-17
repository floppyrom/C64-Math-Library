#!/usr/bin/env python3
"""Native VICE proof: one builder-compiled Q32/R32 kernel serves DIV and MOD."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import math_builder
import selective_linker
from native_vice import VICE,check

FAST="link:shared-aligned-zerozp"
OPS=("UDIV32_32","UMOD32_32")

def main():
    if not os.environ.get("VICE_WRAPPER") or not VICE.is_file():
        raise RuntimeError("VICE_WRAPPER must point to a working native x64sc")
    catalog=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="native_u3232_shared_") as td:
        root=Path(td)
        for i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                catalog,list(OPS),objective="size",zp_budget=0,
                ram_budget=612,pins={op:FAST for op in OPS})
            manifest=selective_linker.build(
                plan,root,memory={"code_base":code,"math_io":io})
            assert len(manifest["link_order"])==1
            assert manifest["resource_use"]["main_ram_total_bytes"]==612
            entries={x["api"]:int(x["entry"][1:],16) for x in manifest["operations"]}
            assert len(set(entries.values()))==1
            prg=(root/"math_selective.prg").read_bytes()
            mem=bytearray(65536)
            mem[code:code+len(prg)-2]=prg[2:]
            mapping={"INPUT_NUM":io+16,"INPUT_DIV":io+20,
                     "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28}
            for j,op in enumerate(OPS):
                api="MATH_"+op
                result=check(bytearray(mem),entries[api],32,mapping,
                             "u3232_shared_%s_%04x"%(op.lower(),code),
                             9900+i*2+j,root,op=="UMOD32_32")
                total+=result["cases"]
                print("NATIVE SHARED U3232",api,hex(code),result["cases"],
                      "PASS",flush=True)
    assert total==384,total
    print("NATIVE SHARED U3232 TWO MAPS AND APIs PASS",total)

if __name__=="__main__":
    main()
