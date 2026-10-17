#!/usr/bin/env python3
"""Native VICE x64sc quarter-square UMUL32 at two independent relocations."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker
from native_selective_umul32 import run_native, N


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to an installed native x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="umul32_qs_native_") as td:
        folder=Path(td)
        for k,(code,io,scratch) in enumerate(
                ((0x8000,0xc000,0xc020),(0x7123,0xc040,0xc080))):
            plan=math_builder.create_plan(
                index,["UMUL32"],objective="speed",zp_budget=0,ram_budget=2086,
                pins={"UMUL32":"link:quarter-square-32"})
            man=selective_linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"scratch_base":scratch})
            assert man["operations"][0]["variant"]=="link:quarter-square-32"
            assert man["resource_use"]["image_span_bytes"]==2050
            entry=int(man["operations"][0]["entry"][1:],16)
            digest=run_native(vice,(folder/"math_selective.prg").read_bytes(),
                              entry,code,io,"umul32_qs_%04x"%code,
                              8990+k,folder)
            total+=N
            print("NATIVE UMUL32 QUARTER-SQUARE",hex(code),N,"PASS",digest,
                  flush=True)
    assert total==2*N
    print("NATIVE UMUL32 QUARTER-SQUARE TWO MAPS PASS",total)


if __name__=="__main__":
    main()
