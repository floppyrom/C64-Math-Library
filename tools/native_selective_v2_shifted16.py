#!/usr/bin/env python3
"""Pinned native VICE r46284 public ABI test of historical V2 shifted divider.

The established 96-vector hardware harness checks Q32/R16/C, caller input
sentinels and two origins against an independent Python oracle.
"""
from __future__ import annotations
import os
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import native_selective_udiv16_shl8 as harness

VARIANT = "link:v2-shifted-public"


def main():
    vice = os.environ.get("VICE_WRAPPER", "")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point at native pinned x64sc")
    index = math_builder.operation_index()
    verified = 0
    with tempfile.TemporaryDirectory(prefix="native_v2_shifted16_") as td:
        folder = Path(td)
        for k, (code, io, zp) in enumerate((
                (0x8000, 0xc000, 0x50),
                (0x7123, 0xc040, 0x70))):
            plan = math_builder.create_plan(
                index, ["UDIV16_SHL8"], objective="size",
                pins={"UDIV16_SHL8": VARIANT},
                zp_budget=12, ram_budget=2400)
            man = linker.build(plan, folder, memory={
                "code_base": code, "math_io": io,
                "zp_base": zp, "scratch_base": io+0x40})
            assert man["resource_use"]["zero_page_bytes"] == 12
            assert man["resource_use"]["image_span_bytes"] == 2368
            assert man["resource_use"]["private_ram_scratch_bytes"] == 0
            assert man["operations"][0]["variant"] == VARIANT
            data = (folder / "math_selective.prg").read_bytes()
            entry = int(man["operations"][0]["entry"][1:], 16)
            mem = bytearray(65536)
            mem[code:code+len(data)-2] = data[2:]
            tag = "shifted16_v2_%04x" % code
            digest = harness.native(
                vice, mem, entry, code, io, tag, 9710+k, folder)
            verified += harness.N
            print("V2 SHL8 PINNED VICE", hex(code), harness.N,
                  digest, flush=True)
    assert verified == 2*harness.N
    print("V2 SHL8 SOURCE-LINKED NATIVE PASS", verified)


if __name__ == "__main__":
    main()
