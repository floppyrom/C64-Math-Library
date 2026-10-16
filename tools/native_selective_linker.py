#!/usr/bin/env python3
"""Native VICE correctness qualification of independently linked arithmetic PRGs.

Reuses the existing monitor/harness verifier but passes the *new combined*
selected binary, not the source files from which it originated.
No native cycle-performance claims are made.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "routines/standalone_lab/portable"))
import math_builder
import selective_linker
from native_vice import VICE, check

def main():
    if not os.environ.get("VICE_WRAPPER") or not VICE.is_file():
        raise RuntimeError("VICE_WRAPPER must point to a working native x64sc")
    index = math_builder.operation_index()
    total = 0
    with tempfile.TemporaryDirectory(prefix="math_selective_native_") as td:
        folder = Path(td)
        for layout, code, io, zp in (
            ("ref", 0x8000, 0xC000, 0x50),
            ("alt", 0x7123, 0xC040, 0x60),
        ):
            plan = math_builder.create_plan(
                index, ["UDIV16", "UMOD16"], zp_budget=2, ram_budget=1000)
            man = selective_linker.build(
                plan, folder,
                memory={"code_base": code, "math_io": io, "zp_base": zp})
            prg = (folder / "math_selective.prg").read_bytes()
            mem = bytearray(65536)
            mem[code:code+len(prg)-2] = prg[2:]
            entries = {r["api"]: int(r["entry"][1:], 16) for r in man["operations"]}
            mp = {
                "INPUT_NUM": io + 16, "INPUT_DIV": io + 20,
                "OUTPUT_QUOT": io + 24, "OUTPUT_REM": io + 28,
            }
            for j, api in enumerate(sorted(entries)):
                row = check(mem[:], entries[api], 16, mp,
                            "selective_" + layout + "_" + api.lower(),
                            7450 + total // 96, folder, api == "MATH_UMOD16")
                total += row["cases"]
                print(layout, api, "native VICE PASS", row["cases"], flush=True)

            zero = math_builder.create_plan(
                index, ["UMOD16"], objective="zp", zp_budget=0,
                ram_budget=1100, pins={"UMOD16": "link:direct-zerozp"})
            man = selective_linker.build(
                zero, folder, memory={"code_base": code, "math_io": io})
            prg = (folder / "math_selective.prg").read_bytes()
            mem = bytearray(65536)
            mem[code:code+len(prg)-2] = prg[2:]
            entry = int(man["operations"][0]["entry"][1:], 16)
            row = check(mem, entry, 16, mp,
                        "selective_" + layout + "_umod16_zerozp",
                        7450 + total // 96, folder, True)
            total += row["cases"]
            print(layout, "UMOD16 zero-ZP", "native VICE PASS",
                  row["cases"], flush=True)
    for layout, code, io in (("ref32", 0x8000, 0xC000),
                             ("alt32", 0x7123, 0xC040)):
        mp = {"INPUT_NUM": io + 16, "INPUT_DIV": io + 20,
              "OUTPUT_QUOT": io + 24, "OUTPUT_REM": io + 28}
        with tempfile.TemporaryDirectory(prefix="math_selective_native32_") as td:
            folder = Path(td)
            plan = math_builder.create_plan(
                index, ["UDIV32_32", "UMOD32_32"], zp_budget=4, ram_budget=1200)
            man = selective_linker.build(
                plan, folder, memory={"code_base": code, "math_io": io})
            prg = (folder / "math_selective.prg").read_bytes()
            mem = bytearray(65536)
            mem[code:code+len(prg)-2] = prg[2:]
            for api, entry in ((x["api"], int(x["entry"][1:], 16))
                               for x in man["operations"]):
                row = check(mem[:], entry, 32, mp,
                            "selective_" + layout + "_" + api.lower(),
                            7450 + total // 96, folder,
                            api == "MATH_UMOD32_32")
                total += row["cases"]
                print(layout, api, "native VICE PASS", row["cases"], flush=True)
            zero = math_builder.create_plan(
                index, ["UDIV32_32"], objective="zp", zp_budget=0,
                ram_budget=800,
                pins={"UDIV32_32": "link:aligned-zerozp"})
            man = selective_linker.build(
                zero, folder, memory={"code_base": code, "math_io": io})
            prg = (folder / "math_selective.prg").read_bytes()
            mem = bytearray(65536)
            mem[code:code+len(prg)-2] = prg[2:]
            entry = int(man["operations"][0]["entry"][1:], 16)
            row = check(mem, entry, 32, mp,
                        "selective_" + layout + "_udiv32_zerozp",
                        7450 + total // 96, folder, False)
            total += row["cases"]
            print(layout, "UDIV32 zero-ZP", "native VICE PASS",
                  row["cases"], flush=True)
    assert total == 1152, total
    print("SELECTIVE LINKER NATIVE VICE PASS", total)

if __name__ == "__main__":
    main()
