#!/usr/bin/env python3
"""Pinned native VICE r46284 proof for the weighted-speed shared trig linker."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker as linker
import native_selective_trig8 as native

OPS=("SIN8","COS8","SINCOS8")

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to working pinned x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="speed_trig8_native_") as td:
        output=Path(td)
        for serial,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                index,list(OPS),objective="speed",zp_budget=0,
                ram_budget=600,workload_calls={op:100 for op in OPS})
            man=linker.build(plan,output,memory={
                "code_base":code,"math_io":io})
            assert man["resource_use"]["shared_table_bytes"]==256
            assert man["resource_use"]["zero_page_bytes"]==0
            assert len(man["shared_tables"])==1
            entries={x["api"]:int(x["entry"][1:],16)
                     for x in man["operations"]}
            image=(output/"math_selective.prg").read_bytes()
            for k,api in enumerate(OPS):
                digest=native.verify(
                    vice,image,entries["MATH_"+api],code,io,
                    "trig8_speed_%s_%04x"%(api.lower(),code),
                    9320+3*serial+k,output,api)
                print("TRIG8 SPEED NATIVE PASS",api,hex(code),
                      native.N,digest,flush=True)
                total+=native.N
    assert total==6*native.N
    print("TRIG8 SPEED NATIVE VICE PASS",total)

if __name__=="__main__":
    main()
