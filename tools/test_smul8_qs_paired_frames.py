#!/usr/bin/env python3
"""SMUL8 source-linked 150-call/24-frame synthetic math latency comparison.

This test intentionally does *not* demand that the read-only QS source
outperform the original V1 SMC source. ROM-safety and main RAM footprint
are different Pareto attributes, and speed mode must select on actual
matched public-call CPU-model means and within the resource budget.

No physical PAL frame, VIC-II badline, IRQ or REU timing is inferred.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smul8 as speed

FRAMES=24
CALLS=150
SIZES={speed.OLD:2336,speed.NEW:1193}


def events():
    corpus=speed.corpus()
    out=[]
    for frame in range(FRAMES):
        count=24 if frame%8==0 else 8 if frame%4==0 else 3
        for i in range(count):
            x,y=corpus[(frame*37+i*83)%len(corpus)]
            out.append((frame,i,x,y))
    assert len(out)==CALLS
    return out


def run(variant,code,io):
    index=math_builder.operation_index()
    plan=math_builder.create_plan(
        index,["SMUL8"],objective="size",
        pins={"SMUL8":variant},
        zp_budget=0,ram_budget=SIZES[variant])
    with tempfile.TemporaryDirectory() as td:
        folder=Path(td)
        man=linker.build(plan,folder,memory={
            "code_base":code,"math_io":io,"scratch_base":io+0x40})
        self_image=(folder/"math_selective.prg").read_bytes()
        start=int.from_bytes(self_image[:2],"little")
        if start!=code: raise AssertionError("SMUL8 unexpected load origin")
        memory=bytearray(65536)
        memory[start:start+len(self_image)-2]=self_image[2:]
        cpu=CPU(memory)
        stack=cpu.sp
        entry=int(man["operations"][0]["entry"][1:],16)
        original=bytes(memory[code:code+1159]) if variant==speed.NEW else None
        calls=[]
        frame_ticks=[0]*FRAMES
        for frame,i,x,y in events():
            memory[io:io+2]=bytes((x,0xa5))
            memory[io+4:io+6]=bytes((y,0x5a))
            memory[io+8:io+12]=bytes((0xcc,0xdd,0x42,0x43))
            cpu.a=(x+frame+i)&255
            cpu.x=(y^frame^i)&255
            cpu.y=(x^y^i)&255
            cpu.c=(x+i)&1
            cpu.d=0
            cycles=cpu.call(entry,5000)
            signed_x=x-(256 if x&128 else 0)
            signed_y=y-(256 if y&128 else 0)
            actual=int.from_bytes(memory[io+8:io+10],"little")
            expected=(signed_x*signed_y)&65535
            if (actual!=expected or cpu.c!=0 or cpu.sp!=stack
                or bytes(memory[io:io+2])!=bytes((x,0xa5))
                or bytes(memory[io+4:io+6])!=bytes((y,0x5a))
                or bytes(memory[io+10:io+12])!=bytes((0x42,0x43))):
                raise AssertionError((variant,frame,i,x,y,actual,expected))
            calls.append(cycles)
            frame_ticks[frame]+=cycles
        if original is not None:
            assert bytes(memory[code:code+1159])==original, "Read-only QS code/tables changed"
        return {"total":sum(calls),"mean":sum(calls)/len(calls),
                "maximum":max(calls),"peak_frame":max(frame_ticks),
                "per_call":calls,"per_frame":frame_ticks,
                "main_ram":man["resource_use"]["main_ram_total_bytes"]}


class Signed8QSPairedFrames(unittest.TestCase):
    def test_busiest_frame_with_exact_same_public_calls(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            old=run(speed.OLD,code,io)
            new=run(speed.NEW,code,io)
            report={
              "origin":"$%04X"%code,
              "frames":FRAMES,"calls":CALLS,
              "v1_smc_mean":old["mean"],
              "readonly_qs_mean":new["mean"],
              "v1_smc_max":old["maximum"],
              "readonly_qs_max":new["maximum"],
              "v1_smc_peak_math_frame":old["peak_frame"],
              "readonly_qs_peak_math_frame":new["peak_frame"],
              "readonly_qs_main_ram_saved":old["main_ram"]-new["main_ram"],
              "readonly_qs_regressed_calls":sum(
                a>b for a,b in zip(new["per_call"],old["per_call"])),
              "readonly_qs_regressed_frames":sum(
                a>b for a,b in zip(new["per_frame"],old["per_frame"])),
            }
            print("SMUL8_READONLY_QS_PAIRED_FRAME",
                  json.dumps(report,sort_keys=True),flush=True)
            # Historical SMC table alignment depends on code origin.
            # Preserve both genuinely measured RAM footprints rather than
            # assuming the $8000 alignment at a non-page origin.
            self.assertEqual(old["main_ram"],2336 if code==0x8000 else 2301)
            self.assertEqual(new["main_ram"],1193)
            self.assertEqual(report["readonly_qs_main_ram_saved"],
                             old["main_ram"]-new["main_ram"])
            self.assertGreaterEqual(report["readonly_qs_main_ram_saved"],1100)
            self.assertEqual(len(old["per_frame"]),FRAMES)
            self.assertEqual(len(new["per_frame"]),FRAMES)


if __name__=="__main__":
    unittest.main()
