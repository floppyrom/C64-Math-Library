#!/usr/bin/env python3
"""Pinned VICE co-load stock operation-first PRG and Turbo16 REU module.

Three scenarios: absent REU must fall back to stock UMUL16; 512KiB and
16MiB hardware must perform 2 guarded REU multiplication batches and then
still execute the stock public UMUL16 with distinct IO/ZP allocations.
No claim of active IRQ/VIC coexistence or DMA timing.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import tempfile

import configure_math as setup
import math_builder as builder
import native_reu_turbo16_standalone as native


def one(exe, parent, label, installed, tier, bank, port):
    folder=parent/label
    folder.mkdir()
    config={
        "target":"c64","operations":["UMUL16"],"objective":"size",
        "constraints":{"max_zp_bytes":200,"max_ram_bytes":25000},
        "hardware":{"reu":{"turbo16":{
            "capacity_kib":tier,"bank":bank,"reserved_banks":[]}}},
    }
    stock=setup.build_checked(config,builder.operation_index(),folder)
    project=json.loads((folder/"math_project_manifest.json").read_text())
    if not project["physical_memory_bound_by_stock_linker"]:
        raise AssertionError("Unbound stock and REU placements")
    inc=(folder/"math_api.inc").read_text()
    match=re.search(r"^MATH_UMUL16\s*=\s*\$([0-9a-fA-F]+)\s*$",inc,re.M)
    if not match:
        raise AssertionError("Missing actual linked normal public MATH_UMUL16")
    io=int(stock["memory_map"]["math_io_start"][1:],16)
    if io!=0xc040:
        raise AssertionError("Unexpected relocated stock I/O")
    return native.native_case(
        exe,folder,label,installed,tier,bank,port,
        stock_prg=(folder/"math_selective.prg").read_bytes(),
        stock_entry=int(match.group(1),16),stock_io=io)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    opts=p.parse_args()
    exe=os.environ.get("VICE_WRAPPER")
    if not exe or not Path(exe).is_file():
        raise RuntimeError("Pinned native VICE_WRAPPER required")
    cases=(("missing_reu_stock_fallback",0,512,4),
           ("mixed_512k",512,512,4),
           ("mixed_16m",16384,16384,200))
    with tempfile.TemporaryDirectory(prefix="native_reu_stock_mixed_") as td:
        rows=[one(exe,Path(td),name,hardware,tier,bank,9760+i)
              for i,(name,hardware,tier,bank) in enumerate(cases)]
    assert all(x["stock_fallback_correct_with_or_without_reu"] for x in rows)
    assert sum(x["two_batches_passed"] for x in rows)==2
    report={
        "schema":"source-qualified-operation-first-stock-reu-native-coexist-v1",
        "status":"PASS_NATIVE_MIXED_STOCK_REU_FALLBACK",
        "native_vice_reu_dma_executed":True,
        "physical_stock_memory_reserved_before_linking":True,
        "stock_operation_survives_reu_cycles":True,
        "absent_reu_stock_fallback":True,
        "active_irq_and_vic_dma_contention_qualified":False,
        "hardware_dma_cycles_measured":False,
        "cases":rows,
    }
    opts.out.parent.mkdir(parents=True,exist_ok=True)
    opts.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(report["status"],flush=True)


if __name__=="__main__":
    main()
