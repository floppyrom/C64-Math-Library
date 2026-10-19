#!/usr/bin/env python3
"""Signed shifted16 V2 vs portable: matched 150 calls in 24 math frames.

This is a stock CPU-model arithmetic budget, NOT a VIC-II/IRQ/PAL physical
cycle-frame guarantee. Validate signed Q24/R16/C for every call and compare
the busiest frame in both relocated public-ABI images.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_sdiv16_shl8 as speed

COUNT=150
FRAMES=24
CHOICES={speed.FAST:(2656,12,2624),speed.SMALL:(272,0,237)}


def events():
    pairs=speed.corpus()
    rows=[]
    for frame in range(FRAMES):
        volume=24 if frame%8==0 else (8 if frame%4==0 else 3)
        for ordinal in range(volume):
            n,d=pairs[(frame*37+ordinal*83)%len(pairs)]
            rows.append((frame,ordinal,n,d))
    assert len(rows)==COUNT
    return rows


def exercise(variant,code,io,zp):
    ram,zbudget,imagesize=CHOICES[variant]
    index=math_builder.operation_index()
    plan=math_builder.create_plan(
        index,["SDIV16_SHL8"],objective="size",
        pins={"SDIV16_SHL8":variant},
        zp_budget=zbudget,ram_budget=ram)
    with tempfile.TemporaryDirectory() as td:
        folder=Path(td)
        man=linker.build(plan,folder,memory={
            "code_base":code,"math_io":io,
            "zp_base":zp,"scratch_base":io+0x40})
        assert man["operations"][0]["variant"]==variant
        prg=(folder/"math_selective.prg").read_bytes()
        assert len(prg)==imagesize+2
        mem=bytearray(65536)
        mem[code:code+imagesize]=prg[2:]
        cpu=CPU(mem)
        sp=cpu.sp
        entry=int(man["operations"][0]["entry"][1:],16)
        calls=[]
        frames=[0]*FRAMES
        for frame,ordinal,n,d in events():
            nb=n.to_bytes(2,"little")+bytes((0xa5,0x5a))
            db=d.to_bytes(2,"little")+bytes((0x6b,0x7c))
            mem[io+16:io+20]=nb
            mem[io+20:io+24]=db
            mem[io+24:io+28]=bytes((0x42,0x43,0x44,0x45))
            mem[io+28:io+32]=bytes((0x51,0x52,0x53,0x54))
            cpu.a=(n+ordinal+frame)&255
            cpu.x=(d+frame)&255
            cpu.y=(n^d^ordinal)&255
            cpu.c=(n+d+ordinal)&1
            cpu.d=0
            ticks=cpu.call(entry,65000)
            got=(int.from_bytes(mem[io+24:io+27],"little"),
                 int.from_bytes(mem[io+28:io+30],"little"),cpu.c)
            if (got!=speed.oracle(n,d) or
                bytes(mem[io+16:io+20])!=nb or
                bytes(mem[io+20:io+24])!=db or
                mem[io+27]!=0x45 or
                bytes(mem[io+30:io+32])!=bytes((0x53,0x54)) or
                cpu.sp!=sp):
                raise AssertionError((variant,frame,ordinal,n,d,got,
                                      speed.oracle(n,d)))
            calls.append(ticks)
            frames[frame]+=ticks
        return {"calls":calls,"frames":frames,
                "total":sum(calls),"peak":max(frames)}


class SignedShiftedPairedFrames(unittest.TestCase):
    def test_matched_frame_speed_two_origins(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            with self.subTest(code=code):
                compact=exercise(speed.SMALL,code,io,zp)
                historical=exercise(speed.FAST,code,io,zp)
                report={
                    "origin":"$%04X"%code,"calls":COUNT,"frames":FRAMES,
                    "portable_total":compact["total"],
                    "v2_total":historical["total"],
                    "portable_peak":compact["peak"],
                    "v2_peak":historical["peak"],
                    "saved_total":compact["total"]-historical["total"],
                    "saved_peak":compact["peak"]-historical["peak"],
                    "regressed_calls":sum(x>y for x,y in zip(
                        historical["calls"],compact["calls"])),
                    "regressed_frames":sum(x>y for x,y in zip(
                        historical["frames"],compact["frames"]))}
                print("V2_SIGNED_SHL16_PAIRED_FRAMES",
                      json.dumps(report,sort_keys=True),flush=True)
                self.assertLess(historical["total"],compact["total"])
                self.assertLess(historical["peak"],compact["peak"])

if __name__=="__main__":
    unittest.main()
