#!/usr/bin/env python3
"""Paired 24-frame UMUL24 compact versus source-linked biased V2 producer.

Deterministic full public X24/Y24/Z48/C calls, same 150 operands, call slots,
input registers and physical load origins. Cycle totals are Mini6502 math
execution only; they are NOT real PAL/VIC-II/IRQ/REU frame measurements.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_umul24 as speed

FRAMES=24
CALLS=150
API="MATH_UMUL24"


def scenario():
    pairs=speed.corpus()
    result=[]
    for frame in range(FRAMES):
        volume=24 if frame%8==0 else (8 if frame%4==0 else 3)
        for ordinal in range(volume):
            x,y=pairs[(frame*37+ordinal*83)%len(pairs)]
            result.append((frame,ordinal,x,y))
    assert len(result)==CALLS
    return result


def measure(variant,code,io,zp):
    if variant not in (speed.FAST,speed.COMPACT):
        raise ValueError("Invalid UMUL24 source identifier")
    fast=variant==speed.FAST
    index=math_builder.operation_index()
    plan=math_builder.create_plan(index,["UMUL24"],objective="size",
        zp_budget=24 if fast else 0,ram_budget=3000 if fast else 256,
        pins={"UMUL24":variant})
    with tempfile.TemporaryDirectory(prefix="umul24_frame_") as td:
        output=Path(td)
        man=linker.build(plan,output,memory={
            "code_base":code,"math_io":io,
            "scratch_base":io+0x40,"zp_base":zp})
        assert man["operations"][0]["variant"]==variant
        assert man["resource_use"]["zero_page_bytes"]==(24 if fast else 0)
        image=(output/"math_selective.prg").read_bytes()
        assert image[:2]==code.to_bytes(2,"little")
        mem=bytearray(65536)
        mem[code:code+len(image)-2]=image[2:]
        entry=int(man["operations"][0]["entry"][1:],16)
        cpu=CPU(mem)
        sp=cpu.sp
        frames=[0]*FRAMES
        calls=[]
        for frame,ordinal,x,y in scenario():
            xb=x.to_bytes(3,"little")
            yb=y.to_bytes(3,"little")
            mem[io:io+4]=xb+bytes([0x6a])
            mem[io+4:io+8]=yb+bytes([0xa5])
            mem[io+8:io+16]=bytes([0xcc]*6+[0x49,0x59])
            cpu.a=(frame*17+ordinal*29)&255
            cpu.x=(frame*31+ordinal*7)&255
            cpu.y=(frame*13+ordinal*23)&255
            cpu.c=(frame+ordinal)&1
            cpu.d=0
            ticks=cpu.call(entry,100000)
            got=int.from_bytes(mem[io+8:io+14],"little")
            if (got!=(x*y)&((1<<48)-1) or cpu.c!=0 or cpu.sp!=sp
                    or bytes(mem[io:io+4])!=xb+bytes([0x6a])
                    or bytes(mem[io+4:io+8])!=yb+bytes([0xa5])
                    or bytes(mem[io+14:io+16])!=bytes([0x49,0x59])):
                raise AssertionError(("UMUL24 ABI",variant,frame,ordinal,x,y,got))
            frames[frame]+=ticks
            calls.append(ticks)
        return {"frame_math_cycles":frames,"total":sum(calls),
                "peak":max(frames),"calls":calls}


def compare(code,io,zp):
    compact=measure(speed.COMPACT,code,io,zp)
    v2=measure(speed.FAST,code,io,zp)
    delta=[n-o for o,n in zip(compact["calls"],v2["calls"])]
    frames=[n-o for o,n in zip(compact["frame_math_cycles"],
                                v2["frame_math_cycles"])]
    summary={
        "code_origin":"$%04X"%code,"io":"$%04X"%io,
        "calls":CALLS,"frames":FRAMES,
        "portable_total":compact["total"],"v2_total":v2["total"],
        "portable_peak":compact["peak"],"v2_peak":v2["peak"],
        "peak_savings":compact["peak"]-v2["peak"],
        "total_savings":compact["total"]-v2["total"],
        "regressed_calls":sum(x>0 for x in delta),
        "worst_call_regression":max([0]+delta),
        "regressed_frames":sum(x>0 for x in frames),
        "worst_frame_regression":max([0]+frames),
    }
    if not summary["peak_savings"]>0 or not summary["total_savings"]>0:
        raise AssertionError(("V2 UMUL24 speed regression",summary))
    return summary


class UMUL24PairedFrameTests(unittest.TestCase):
    def test_same_150_public_calls_across_24_frames_and_both_placements(self):
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(code=code):
                result=compare(code,io,zp)
                self.assertEqual(result["calls"],150)
                self.assertEqual(result["frames"],24)
                print("UMUL24_BIASED_PAIRED_FRAME",
                      json.dumps(result,sort_keys=True),flush=True)


if __name__=="__main__":
    unittest.main()
