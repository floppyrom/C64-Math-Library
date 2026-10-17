#!/usr/bin/env python3
"""Native VICE: one shared six-entry 375-byte signed/unsigned 32-bit producer."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker
from native_selective_umul32_shr16 import run_native as unsigned_native, N as N1
from native_selective_smul32_shr16 import run_native as signed_native, N as N2


def main():
    vice = os.environ.get("VICE_WRAPPER", "")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must name native x64sc")
    index = math_builder.operation_index()
    ops = ("UMUL32", "UMUL32_READY", "UMUL32_SHR16",
           "SMUL32", "SMUL32_READY", "SMUL32_SHR16")
    total = 0
    with tempfile.TemporaryDirectory(prefix="unified32_native_") as tmp:
        folder = Path(tmp)
        for i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan = math_builder.create_plan(index,ops,objective="size",zp_budget=0,
                                            ram_budget=419)
            man = selective_linker.build(plan,folder,memory={
                "code_base":code,"math_io":io})
            assert man["resource_use"]["image_span_bytes"] == 375
            assert man["resource_use"]["main_ram_total_bytes"] == 419
            assert man["resource_use"]["zero_page_bytes"] == 0
            assert len(man["link_order"]) == 1
            ep = {v["api"]:int(v["entry"][1:],16) for v in man["operations"]}
            prg = (folder/"math_selective.prg").read_bytes()
            for k,name in enumerate(("UMUL32_SHR16","SMUL32_SHR16")):
                run = signed_native if name.startswith("SMUL") else unsigned_native
                digest = run(vice,prg,ep["MATH_"+name],code,io,
                             "unified_"+name.lower()+"_%04x"%code,
                             8540+i*2+k,folder)
                total += N2 if name.startswith("SMUL") else N1
                print("NATIVE",name,hex(code),"PASS",digest,flush=True)
    assert total == 2*(N1+N2)
    print("NATIVE UNIFIED32 SHR16 2-MAP PASS",total)

if __name__ == "__main__":
    main()
