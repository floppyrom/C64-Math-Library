#!/usr/bin/env python3
"""Native x64sc proof for separately linked 73-byte UMUL8 quarter-square source."""
from __future__ import annotations
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from native_selective_multiply import N, run_native


def main():
    vice=os.environ.get("VICE_WRAPPER")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="native_fast_umul8_") as td:
        directory=Path(td)
        for i,(origin,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                index,["UMUL8"],zp_budget=0,ram_budget=1129,
                pins={"UMUL8":"link:quarter-square"})
            manifest=selective_linker.build(
                plan,directory,memory={"code_base":origin,"math_io":io})
            assert manifest["resource_use"]["image_span_bytes"]==1095
            entry=int(manifest["operations"][0]["entry"][1:],16)
            image=(directory/"math_selective.prg").read_bytes()
            digest=run_native(vice,image,entry,origin,io,
                              "quarter_umul8_%04x"%origin,7510+i,
                              directory,bits=8)
            total+=N
            print("NATIVE QUARTER-SQUARE UMUL8",hex(origin),"PASS",N,digest,flush=True)
    assert total==192
    print("NATIVE QUARTER-SQUARE UMUL8 PASS",total)


if __name__=="__main__":
    main()
