#!/usr/bin/env python3
"""Pinned headless VICE r46284 proof of threshold-fast stock reciprocal."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import native_selective_urecip16_q16 as harness

VARIANT="link:threshold-zerozp"


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must resolve native x64sc")
    count=0
    index=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix="recip16_threshold_native_") as td:
        folder=Path(td)
        for i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                index,["URECIP16_Q16"],objective="size",
                pins={"URECIP16_Q16":VARIANT},
                zp_budget=0,ram_budget=481)
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,
                "scratch_base":io+0x40})
            assert man["resource_use"]["image_span_bytes"]==448
            assert man["resource_use"]["zero_page_bytes"]==0
            assert man["resource_use"]["private_ram_scratch_bytes"]==1
            entry=int(man["operations"][0]["entry"][1:],16)
            binary=(folder/"math_selective.prg").read_bytes()
            mem=bytearray(65536)
            mem[code:code+len(binary)-2]=binary[2:]
            digest=harness.native(
                vice,mem,entry,code,io,
                "recip16_threshold_%04x"%code,9820+i,folder)
            count+=harness.N
            print("RECIP16 THRESHOLD NATIVE PASS",hex(code),
                  harness.N,digest,flush=True)
    assert count==2*harness.N
    print("RECIP16 THRESHOLD BOTH VICE MAPS PASS",count)


if __name__=="__main__":
    main()
