#!/usr/bin/env python3
"""Native x64sc proof of relocated original V1 UMUL8 at two code/ZP origins."""
from __future__ import annotations
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
from native_selective_multiply import N, run_native


def main():
    vice = os.environ.get("VICE_WRAPPER")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to a native x64sc executable")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="native_umul8_v1_") as folder:
        base=Path(folder)
        for i,(origin,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                             (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(index,["UMUL8"],
                pins={"UMUL8":"link:v1-resident-fast"},
                zp_budget=4,ram_budget=1311)
            man=selective_linker.build(plan,base,memory={
                "code_base":origin,"math_io":io,"zp_base":zp})
            assert man["resource_use"]["zero_page_bytes"]==4
            assert man["resource_use"]["code_and_tables_bytes"]==1073
            entry=int(man["operations"][0]["entry"][1:],16)
            data=(base/"math_selective.prg").read_bytes()
            digest=run_native(vice,data,entry,origin,io,
                "original_umul8_%04x"%origin,7530+i,base,bits=8)
            total+=N
            print("NATIVE ORIGINAL V1 UMUL8",hex(origin),"PASS",N,digest,flush=True)
    assert total==192
    print("NATIVE ORIGINAL V1 UMUL8 PASS",total)


if __name__=="__main__":
    main()
