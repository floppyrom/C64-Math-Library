#!/usr/bin/env python3
"""Paired 150-call / 24-frame public compound-math busy-frame latency gate.

Synthetic math-only CPU model, not physical VIC/IRQ/REU/PAL frame timing.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smuldiv16_qsv2 as speed

FRAMES=24
COUNT=150
CONFIG={speed.SMALL:(477,439,0),speed.FAST:(4299,4263,12)}

def events():
    c=speed.corpus()
    out=[]
    for frame in range(FRAMES):
        n=24 if frame%8==0 else 8 if frame%4==0 else 3
        for k in range(n):
            out.append((frame,k,*c[(frame*37+k*83)%len(c)]))
    assert len(out)==COUNT
    return out

def run(variant,code,io,zp):
    budget,length,zp_budget=CONFIG[variant]
    plan=math_builder.create_plan(
        math_builder.operation_index(),["SMULDIV16"],objective="size",
        pins={"SMULDIV16":variant},ram_budget=budget,zp_budget=zp_budget)
    with tempfile.TemporaryDirectory() as td:
        folder=Path(td)
        man=linker.build(plan,folder,memory={
            "code_base":code,"math_io":io,
            "zp_base":zp,"scratch_base":io+0x40})
        image=(folder/"math_selective.prg").read_bytes()
        mem=bytearray(65536)
        mem[code:code+length]=image[2:]
        cpu=CPU(mem)
        sp=cpu.sp
        entry=int(man["operations"][0]["entry"][1:],16)
        calls=[]
        frames=[0]*FRAMES
        for frame,k,x,y,d in events():
            xb=x.to_bytes(2,"little")+bytes((0xa5,0x5a))
            yb=y.to_bytes(2,"little")+bytes((0x6b,0x7c))
            db=d.to_bytes(2,"little")+bytes((0xe1,0xe2))
            mem[io:io+4]=xb
            mem[io+4:io+8]=yb
            mem[io+8:io+12]=bytes((0x88,))*4
            mem[io+16:io+20]=bytes((0x77,))*4
            mem[io+20:io+24]=db
            mem[io+24:io+28]=bytes((0x99,))*4
            mem[io+28:io+32]=bytes((0x21,0x43,0x65,0x87))
            cpu.a=(x+k+frame)&255
            cpu.x=(y+k+frame)&255
            cpu.y=(d+k)&255
            cpu.c=(x+y+d+k)&1
            cpu.d=0
            ticks=cpu.call(entry,100000)
            product,q,rem,carry=speed.oracle(x,y,d)
            got=(int.from_bytes(mem[io+8:io+12],"little"),
                 int.from_bytes(mem[io+16:io+20],"little"),
                 int.from_bytes(mem[io+24:io+28],"little"),
                 int.from_bytes(mem[io+28:io+30],"little"),cpu.c)
            if (got!=(product,product,q,rem,carry) or cpu.sp!=sp
                or bytes(mem[io:io+4])!=xb
                or bytes(mem[io+4:io+8])!=yb
                or bytes(mem[io+20:io+24])!=db
                or bytes(mem[io+30:io+32])!=bytes((0x65,0x87))):
                raise AssertionError((variant,frame,k,x,y,d,got))
            calls.append(ticks)
            frames[frame]+=ticks
        return {"total":sum(calls),"peak":max(frames),
                "per_call":calls,"per_frame":frames}

class CompoundBusyFrames(unittest.TestCase):
    def test_same_input_busiest_math_frame(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            reference=run(speed.SMALL,code,io,zp)
            historic=run(speed.FAST,code,io,zp)
            result={"origin":"$%04X"%code,"calls":COUNT,"frames":FRAMES,
                    "portable_total":reference["total"],
                    "qsv2_total":historic["total"],
                    "portable_peak":reference["peak"],
                    "qsv2_peak":historic["peak"],
                    "saved_total":reference["total"]-historic["total"],
                    "saved_peak":reference["peak"]-historic["peak"],
                    "regressed_calls":sum(x>y for x,y in
                        zip(historic["per_call"],reference["per_call"])),
                    "regressed_frames":sum(x>y for x,y in
                        zip(historic["per_frame"],reference["per_frame"]))}
            print("SMULDIV16_QS_V2_PAIRED_FRAME",
                  json.dumps(result,sort_keys=True),flush=True)
            self.assertLess(historic["total"],reference["total"])
            self.assertLess(historic["peak"],reference["peak"])

if __name__=="__main__":
    unittest.main()
