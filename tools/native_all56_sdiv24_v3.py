#!/usr/bin/env python3
"""V3 signed24 historical producer linked alongside all 56 operations, native VICE.

This checks 2x2x96 signed24 public calls in full 56-operation images. All other
55/54 operations are resident but not executed by this particular native gate.
"""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker as linker
import native_selective_sdiv24 as native

MAPS=(0x2000,0x4321)
DONOR="link:v3-signed-magnitude"
OPS=("SDIV24","SMOD24")


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must identify native x64sc")
    index=math_builder.operation_index()
    assert len(index)==56
    native.H,native.INPUT,native.OUTPUT=0x1000,0x9000,0x9800
    checked=0
    with tempfile.TemporaryDirectory(prefix="full56_v3_signed24_") as t:
        home=Path(t)
        for k,code in enumerate(MAPS):
            address={"code_base":code,"math_io":0xc000,
                     "zp_base":0x40,"scratch_base":0xc020}
            baseline=math_builder.create_plan(index,sorted(index),objective="size",
                                              zp_budget=13,ram_budget=24000)
            original=linker.build(baseline,home,memory=address)
            pins={r["api"].removeprefix("MATH_"):r["variant"]
                  for r in original["operations"]}
            for op in OPS:
                pins[op]=DONOR
            transplanted=math_builder.create_plan(index,sorted(index),
                objective="size",zp_budget=13,ram_budget=24000,pins=pins)
            manifest=linker.build(transplanted,home,memory=address)
            assert len(manifest["operations"])==56
            assert manifest["resource_use"]["zero_page_bytes"]<=13
            assert manifest["resource_use"]["main_ram_total_bytes"]<=24000
            roots={r["api"]:r for r in manifest["operations"] if r["api"] in
                   {"MATH_"+op for op in OPS}}
            assert len(roots)==2 and all(r["variant"]==DONOR for r in roots.values())
            assert len({r["entry"] for r in roots.values()})==2
            prg=(home/"math_selective.prg").read_bytes()
            assert prg[:2]==code.to_bytes(2,"little")
            assert 0x1300<=code and code+len(prg)-2 <= native.INPUT
            for i,op in enumerate(OPS):
                entry=int(roots["MATH_"+op]["entry"][1:],16)
                tag="all56_v3signed24_%04x_%s"%(code,op)
                digest=native.verify(vice,prg,entry,code,0xc000,
                                     tag,8410+4*k+i,home)
                checked+=native.N
                print("ALL56 V3 SIGNED24",hex(code),op,native.N,
                      "PASS",digest,flush=True)
    assert checked==len(MAPS)*len(OPS)*native.N
    print("ALL56 V3 SIGNED24 TWO-MAP TWO-ENTRY NATIVE PASS",checked,flush=True)

if __name__=="__main__":
    main()
