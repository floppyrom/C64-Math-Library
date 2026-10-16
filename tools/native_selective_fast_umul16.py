#!/usr/bin/env python3
"""Native x64sc qualification of source-linked UMUL16 quarter-square PRGs."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from native_selective_multiply import run_native, N

def main():
    vice=os.environ.get("VICE_WRAPPER")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to native x64sc")
    index=math_builder.operation_index()
    total=0
    for i,(origin,io,scratch) in enumerate(((0x8000,0xc000,0xc020),
                                            (0x7123,0xc040,0xc080))):
        with tempfile.TemporaryDirectory(prefix="selective_fast_umul16_") as d:
            folder=Path(d)
            plan=math_builder.create_plan(
                index,["UMUL16"],objective="size",zp_budget=0,
                ram_budget=1291,pins={"UMUL16":"link:quarter-square"})
            man=selective_linker.build(
                plan,folder,memory={"code_base":origin,"math_io":io,
                                     "scratch_base":scratch})
            assert man["resource_use"]["image_span_bytes"]==1255
            entry=int(man["operations"][0]["entry"][1:],16)
            digest=run_native(vice,(folder/"math_selective.prg").read_bytes(),
                              entry,origin,io,"umul16_qs_%04x"%origin,
                              7500+i,folder,bits=16)
            total+=N
            print("NATIVE LINKED UMUL16 QUARTER-SQUARE",hex(origin),
                  N,"PASS",digest,flush=True)
    assert total==2*N
    print("NATIVE LINKED UMUL16 QUARTER-SQUARE PASS",total)

if __name__=="__main__":
    main()
