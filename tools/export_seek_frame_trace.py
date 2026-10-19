#!/usr/bin/env python3
"""Deterministic 50Hz-style mixed SEEK8/SEEK16 frame trace (source CPU model).

Measure complete calls against the final shared-source linked image, including
state transitions, arrival, post-arrival and renewed waypoints. Not actual PAL
VIC bus, music IRQ, sprite fetch or REU timing. Generates frame_cycle_budget
CSV and a source-linked manifest, without touching V1-V5 distributions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
from frame_cycle_budget import COLUMNS, load_trace, score

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ("SEEK8", "SEEK16")
OPS = tuple(family + "_" + suffix for family in FAMILIES
            for suffix in ("INIT", "STEP", "STEP_INT", "STEP1"))
METHODS = ("STEP", "STEP_INT", "STEP1")


def state_positions(mem, state, family, slot):
    if family == "SEEK8":
        return mem[state + slot], mem[state + 8 + slot]
    return (mem[state + slot] | mem[state + 8 + slot] << 8,
            mem[state + 16 + slot])


def set_positions(mem, state, family, slot, x, y):
    mem[state + slot] = x & 255
    if family == "SEEK8":
        mem[state + 8 + slot] = y
    else:
        mem[state + 8 + slot] = x >> 8
        mem[state + 16 + slot] = y


def export(out: Path, frames=24, code=0x8000, io=0xc000):
    if not (1 <= frames <= 200):
        raise ValueError("frame count must be in 1..200")
    if not (0x2000 <= code < 0xa000 and 0xb000 <= io <= 0xd000):
        raise ValueError("Code/I/O relocation exceeds qualified test ranges")
    scratch = io + 0x40
    plan = math_builder.create_plan(math_builder.operation_index(),
                                    list(OPS), objective="size",
                                    ram_budget=2400, zp_budget=0)
    with tempfile.TemporaryDirectory(prefix="seek_trace_linked_") as tmp:
        work = Path(tmp)
        man = linker.build(plan, work, memory={
            "code_base": code, "math_io": io,
            "scratch_base": scratch, "zp_base": 0x50})
        entries = {x["api"]: int(x["entry"][1:], 16)
                   for x in man["operations"]}
        variants = {x["api"]: x["variant"] for x in man["operations"]}
        if (set(entries) != {"MATH_" + s for s in OPS}
            or len(man["link_order"]) != 2
            or man["resource_use"]["zero_page_bytes"] != 0
            or man["resource_use"]["code_and_tables_bytes"] != 1549
            or man["resource_use"]["persistent_state_bytes"] != 408):
            raise ValueError("SEEK8/SEEK16 shared producer geometry drift")
        states = {
            family: int(man["memory_map"]["persistent_state"][family.lower()][1:],16)
            for family in FAMILIES}
        image = (work / "math_selective.prg").read_bytes()
        if image[:2] != code.to_bytes(2, "little"):
            raise ValueError("Linked PRG load base changed")
        mem = bytearray(65536)
        mem[code:code+len(image)-2] = image[2:]
        source_before = bytes(mem[code:code+len(image)-2])
        cpu = CPU(mem)
        sp = cpu.sp
        targets = {}
        observations = []
        for family in FAMILIES:
            state = states[family]
            for slot in range(8):
                sx = (30 + slot*17 if family == "SEEK8"
                      else 150 + slot*37)
                sy = 25 + slot*12
                set_positions(mem, state, family, slot, sx, sy)
        for frame in range(frames):
            call = 0
            for family in FAMILIES:
                state = states[family]
                width = 160 if family == "SEEK8" else 248
                for slot in range(8):
                    mode = METHODS[slot % 3]
                    x, y = state_positions(mem, state, family, slot)
                    if frame % 9 == 0:
                        # Retarget each slot to a bounded, reproducible waypoint;
                        # zero-distance, axis, diagonal and nonarrival cases.
                        dx = (0, 17, -11, 25, -18, 23, -21, 9)[slot]
                        dy = (0, -9, 13, 0, 21, -17, 0, 12)[slot]
                        limit = 255 if family == "SEEK8" else 650
                        tx = max(1, min(limit, x+dx))
                        ty = max(1, min(230, y+dy))
                        targets[family,slot] = (tx, ty)
                        mem[io:io+2] = tx.to_bytes(2,"little")
                        mem[io+4] = ty
                        mem[io+16:io+18] = {
                            "STEP": bytes((128,129)),
                            "STEP_INT": bytes((0,2)),
                            "STEP1": bytes((0,1))}[mode]
                        call = _measure(cpu, mem, observations, man, entries,
                                        variants, frame, call, "MATH_"+family+"_INIT",
                                        family, slot, state, width, targets[family,slot],
                                        io, sp, code)
                    if (family,slot) not in targets:
                        raise ValueError("Missing initialized movement")
                    call = _measure(cpu, mem, observations, man, entries,
                                    variants, frame, call, "MATH_"+family+"_"+mode,
                                    family, slot, state, width, targets[family,slot],
                                    io, sp, code)
        if bytes(mem[code:code+len(image)-2]) != source_before:
            raise ValueError("Linked SEEK source mutated code during frame tracing")
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w",newline="",encoding="utf-8") as stream:
            writer = csv.DictWriter(stream,fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(observations)
        out.with_suffix(".manifest.json").write_text(json.dumps({
            "synthetic_not_real_game": True,
            "not_pal_bus_or_irq_timing": True,
            "frames": frames,
            "manifest": man,
            "trace_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        }, indent=2,sort_keys=True)+"\n",encoding="utf-8")
    calls, meta = load_trace(out)
    result = score(calls, meta, frame_count=frames)
    return {key: result[key] for key in (
        "calls", "peak_frame", "peak_frame_math_cycles",
        "p95_frame_math_cycles", "peak_hotspots")}


def _measure(cpu, mem, observations, manifest, entries, variants,
             frame, ordinal, operation, family, slot, state, width,
             target, io, sp, code):
    io_before = bytes(mem[io:io+32])
    state_before = bytes(mem[state:state+width])
    cpu.a = (frame*17+ordinal*3)&255
    cpu.x = slot
    cpu.y = (frame*11+ordinal*7)&255
    cpu.c = (frame+ordinal)&1
    cpu.d = 0
    caller = (cpu.a,cpu.x,cpu.y,cpu.c)
    input_id = hashlib.sha256(
        operation.encode()+bytes(caller)+io_before+state_before).hexdigest()
    ticks = cpu.call(entries[operation], 160000)
    if (cpu.sp != sp or cpu.x != slot or bytes(mem[io:io+32]) != io_before
        or (cpu.c and state_positions(mem,state,family,slot) != target)):
        raise ValueError("SEEK linked public input/C/X/SP/arrival drift "+
                         repr((operation,frame,slot)))
    if any(mem[state+j] != old for j,old in enumerate(state_before)
           if j%8 != slot):
        raise ValueError("SEEK linked state isolation drift "+
                         repr((operation,frame,slot)))
    observations.append({
        "frame":frame,"call":ordinal,"operation":operation,
        "input_id":input_id,"cycles":ticks,"variant":variants[operation],
        "measurement_basis":"cpu-model-public-entry-through-rts",
        "placement":"$%04X/$%04X"%(code,io)})
    return ordinal+1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--frames",type=int,default=24)
    parser.add_argument("--code-base",type=lambda s:int(s,0),default=0x8000)
    parser.add_argument("--io-base",type=lambda s:int(s,0),default=0xc000)
    args=parser.parse_args()
    print(json.dumps(export(args.out,args.frames,args.code_base,args.io_base),
                     indent=2))
