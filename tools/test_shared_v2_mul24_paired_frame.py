#!/usr/bin/env python3
"""Paired 24-frame interleaved unsigned/signed 24-bit public multiplications.

Same code origins, 150 operand pairs, call order and register inputs for both
compiler-selected variants. Arithmetic CPU-model only, NOT PAL frame timing.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smul24 as speed

FRAMES=24
CALLS=150
OPS=("MATH_UMUL24","MATH_SMUL24")


def scenario():
    pairs=speed.corpus()
    out=[]
    for frame in range(FRAMES):
        volume=24 if frame%8==0 else (8 if frame%4==0 else 3)
        for ordinal in range(volume):
            x,y=pairs[(frame*37+ordinal*83)%len(pairs)]
            out.append((frame,ordinal,OPS[(frame+ordinal)&1],x,y))
    assert len(out)==CALLS
    return out


def measure(variant,code,io,zp):
    index=math_builder.operation_index()
    fast=variant==speed.FAST
    plan=math_builder.create_plan(index,["UMUL24","SMUL24"],
        objective="size",zp_budget=24 if fast else 0,
        ram_budget=3000 if fast else 1000,
        pins={name[5:]:variant for name in OPS})
    with tempfile.TemporaryDirectory() as td:
        folder=Path(td)
        man=linker.build(plan,folder,memory={
            "code_base":code,"math_io":io,"zp_base":zp,
            "scratch_base":io+0x40})
        assert len(man["link_order"])==(1 if fast else 2)
        image=(folder/"math_selective.prg").read_bytes()
        assert image[:2]==code.to_bytes(2,"little")
        mem=bytearray(65536)
        mem[code:code+len(image)-2]=image[2:]
        entries={e["api"]:int(e["entry"][1:],16)
                 for e in man["operations"]}
        cpu=CPU(mem);sp=cpu.sp
        frames=[0]*FRAMES
        calls=[]
        for frame,ordinal,api,x,y in scenario():
            xb=x.to_bytes(3,"little")
            yb=y.to_bytes(3,"little")
            mem[io:io+4]=xb+bytes([0x6a])
            mem[io+4:io+8]=yb+bytes([0xa5])
            mem[io+8:io+16]=bytes([0xcc]*6+[0x49,0x59])
            cpu.a=(frame*17+ordinal*29)&255
            cpu.x=(frame*31+ordinal*7)&255
            cpu.y=(frame*13+ordinal*23)&255
            cpu.c=(frame+ordinal)&1;cpu.d=0
            ticks=cpu.call(entries[api],100000)
            a=speed.signed(x) if api=="MATH_SMUL24" else x
            b=speed.signed(y) if api=="MATH_SMUL24" else y
            actual=int.from_bytes(mem[io+8:io+14],"little")
            if (actual!=(a*b)&speed.MASK48 or cpu.c!=0 or
                    cpu.sp!=sp or
                    bytes(mem[io:io+4])!=xb+bytes([0x6a]) or
                    bytes(mem[io+4:io+8])!=yb+bytes([0xa5]) or
                    bytes(mem[io+14:io+16])!=bytes([0x49,0x59])):
                raise AssertionError((variant,frame,ordinal,api,x,y,actual))
            frames[frame]+=ticks;calls.append(ticks)
        return {"frame_math_cycles":frames,"total":sum(calls),
                "peak":max(frames),"calls":calls}


def compare(code,io,zp):
    compact=measure(speed.COMPACT,code,io,zp)
    fast=measure(speed.FAST,code,io,zp)
    delta=[x-y for x,y in zip(fast["calls"],compact["calls"])]
    frame_delta=[x-y for x,y in zip(fast["frame_math_cycles"],
                                    compact["frame_math_cycles"])]
    result={"code":"$%04X"%code,"frames":FRAMES,"calls":CALLS,
            "portable_total":compact["total"],"v2_total":fast["total"],
            "portable_peak":compact["peak"],"v2_peak":fast["peak"],
            "peak_savings":compact["peak"]-fast["peak"],
            "total_savings":compact["total"]-fast["total"],
            "regressed_calls":sum(x>0 for x in delta),
            "worst_call_regression":max([0]+delta),
            "regressed_frames":sum(x>0 for x in frame_delta),
            "worst_frame_regression":max([0]+frame_delta)}
    if result["peak_savings"]<=0 or result["total_savings"]<=0:
        raise AssertionError(("Biased signed/unsigned frame regression",result))
    return result


class SharedBiasedMul24Frames(unittest.TestCase):
    def test_paired_150_calls_two_origins(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            with self.subTest(code=code):
                summary=compare(code,io,zp)
                print("SHARED_V2_BIASED_MUL24_FRAME",
                      json.dumps(summary,sort_keys=True),flush=True)


if __name__=="__main__":
    unittest.main()
