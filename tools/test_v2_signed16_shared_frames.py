#!/usr/bin/env python3
"""Shared signed16 V2 vs compact under 150 identical calls in 24 frames.

Only complete public Q/R/C CPU-model math cycles are scored. This is not
physical PAL/VIC-II badline, IRQ, SID, REU or drive timing.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_sdiv16_shared as speed

FRAMES=24
CALLS=150


def events():
    pairs=speed.corpus()
    out=[]
    for frame in range(FRAMES):
        count=24 if frame%8==0 else 8 if frame%4==0 else 3
        for k in range(count):
            out.append((frame,k,*pairs[(frame*37+k*83)%len(pairs)]))
    assert len(out)==CALLS
    return out


def run(variant,code,io):
    ram,length=(1745,1705) if variant==speed.FAST else (241,206)
    index=math_builder.operation_index()
    plan=math_builder.create_plan(index,["SDIV16","SMOD16"],
        objective="size",pins={"SDIV16":variant,"SMOD16":variant},
        ram_budget=ram,zp_budget=0)
    with tempfile.TemporaryDirectory() as td:
        man=linker.build(plan,Path(td),memory={
            "code_base":code,"math_io":io,"scratch_base":io+0x40})
        if len(man["link_order"])!=1:
            raise ValueError("Signed16 quotient/remainder source unexpectedly duplicated")
        raw=(Path(td)/"math_selective.prg").read_bytes()
        mem=bytearray(65536)
        mem[code:code+length]=raw[2:]
        cpu=CPU(mem)
        sp=cpu.sp
        entry=int(man["operations"][0]["entry"][1:],16)
        costs=[]
        frames=[0]*FRAMES
        for frame,k,n,d in events():
            nb=n.to_bytes(2,"little")+bytes((0x5a,0xa5))
            db=d.to_bytes(2,"little")+bytes((0x7c,0x6b))
            mem[io+16:io+20]=nb
            mem[io+20:io+24]=db
            mem[io+24:io+28]=bytes((0x55,0x44,0x33,0x22))
            mem[io+28:io+32]=bytes((0x99,0x88,0x77,0x66))
            cpu.a=(n+k+frame)&255
            cpu.x=(d^k)&255
            cpu.y=(n^d^frame)&255
            cpu.c=(n+k)&1
            cpu.d=0
            t=cpu.call(entry,40000)
            value=(int.from_bytes(mem[io+24:io+26],"little"),
                   int.from_bytes(mem[io+28:io+30],"little"),cpu.c)
            if (value!=speed.oracle(n,d) or cpu.sp!=sp
                or bytes(mem[io+16:io+20])!=nb
                or bytes(mem[io+20:io+24])!=db
                or bytes(mem[io+26:io+28])!=bytes((0x33,0x22))
                or bytes(mem[io+30:io+32])!=bytes((0x77,0x66))):
                raise AssertionError((variant,frame,n,d,value,speed.oracle(n,d)))
            costs.append(t)
            frames[frame]+=t
        return {"total":sum(costs),"peak":max(frames),
                "per_call":costs,"per_frame":frames}


class Signed16PairedFrame(unittest.TestCase):
    def test_exact_same_inputs_peak_frame(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            old=run(speed.SMALL,code,io)
            new=run(speed.FAST,code,io)
            result={"origin":"$%04X"%code,"calls":CALLS,
                    "frames":FRAMES,"compact_total":old["total"],
                    "v2_total":new["total"],"compact_peak":old["peak"],
                    "v2_peak":new["peak"],
                    "saved_total":old["total"]-new["total"],
                    "saved_peak":old["peak"]-new["peak"],
                    "regressed_calls":sum(a>b for a,b in
                        zip(new["per_call"],old["per_call"])),
                    "regressed_frames":sum(a>b for a,b in
                        zip(new["per_frame"],old["per_frame"]))}
            print("SIGNED16_V2_SHARED_PAIRED_FRAME",
                  json.dumps(result,sort_keys=True),flush=True)
            self.assertLess(new["total"],old["total"])
            self.assertLess(new["peak"],old["peak"])


if __name__=="__main__":
    unittest.main()
