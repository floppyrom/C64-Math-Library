#!/usr/bin/env python3
"""Native VICE r46284: both V2 signed/unsigned public entries, one builder PRG."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker as linker
import native_selective_umul24 as unsigned
import native_selective_smul24 as signed
import selective_v2_fast_umul24 as donor


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must be pinned native x64sc")
    index=math_builder.operation_index()
    verified=0
    with tempfile.TemporaryDirectory(prefix="v2_biased_mul24_shared_") as td:
        folder=Path(td)
        for k,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            plan=math_builder.create_plan(index,["UMUL24","SMUL24"],
                objective="size",zp_budget=24,ram_budget=3000,
                pins={"UMUL24":"link:v2-quarter-square",
                      "SMUL24":"link:v2-quarter-square"})
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,
                "zp_base":zp,"scratch_base":io+0x40})
            assert len(man["link_order"])==1
            assert man["resource_use"]["zero_page_bytes"]==24
            assert man["resource_use"]["private_ram_scratch_bytes"]==0
            _,end=donor.layout(code)
            assert man["resource_use"]["main_ram_total_bytes"]==end-code+32
            entries={e["api"]:int(e["entry"][1:],16)
                     for e in man["operations"]}
            assert len(set(entries.values()))==2
            data=(folder/"math_selective.prg").read_bytes()
            assert len(data)==end-code+2
            for j,(api,harness) in enumerate((
                ("MATH_UMUL24",unsigned),
                ("MATH_SMUL24",signed),
            )):
                tag="mul24_dual_%04x_%s"%(code,api.lower())
                digest=harness.run_native(
                    vice,data,entries[api],code,io,tag,
                    9250+2*k+j,folder)
                verified+=harness.N
                print("V2 BIASED MUL24 DUAL NATIVE",
                      hex(code),api,harness.N,digest,flush=True)
    assert verified==2*2*unsigned.N
    print("V2 BIASED MUL24 SHARED PRODUCER NATIVE PASS",verified)


if __name__=="__main__":
    main()
