#!/usr/bin/env python3
"""150 identical signed scaled multiply public calls in 24 math frames.

This does not model VIC-II badlines, IRQ scheduling, REU or actual PAL timing.
"""
import json
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smul16_shr8 as speed

FRAMES=24
CALLS=150
CONFIG={speed.SMALL:(222,184),speed.FAST:(1419,1383)}

def events():
    vals=speed.corpus()
    out=[]
    for frame in range(FRAMES):
        n=24 if frame%8==0 else 8 if frame%4==0 else 3
        for k in range(n):
            out.append((frame,k,*vals[(frame*37+k*83)%len(vals)]))
    assert len(out)==CALLS
    return out

def run(variant,code,io):
    ram,size=CONFIG[variant]
    plan=math_builder.create_plan(
        math_builder.operation_index(),["SMUL16_SHR8"],objective="size",
        pins={"SMUL16_SHR8":variant},zp_budget=0,ram_budget=ram)
    with tempfile.TemporaryDirectory() as td:
        man=linker.build(plan,Path(td),memory={
             "code_base":code,"math_io":io,"scratch_base":io+0x40})
        prg=(Path(td)/"math_selective.prg").read_bytes()
        mem=bytearray(65536)
        mem[code:code+size]=prg[2:]
        cpu=CPU(mem)
        sp=cpu.sp
        entry=int(man["operations"][0]["entry"][1:],16)
        calls=[]
        frames=[0]*FRAMES
        for frame,k,x,y in events():
            xb=x.to_bytes(2,"little")+bytes((0xa5,0x5a))
            yb=y.to_bytes(2,"little")+bytes((0x6b,0x7c))
            mem[io:io+4]=xb
            mem[io+4:io+8]=yb
            mem[io+8:io+16]=bytes((0x99,0x88,0x77,0x66,0xdd,0xdd,0xdd,0xdd))
            cpu.a=(x+frame+k)&255
            cpu.x=(y+frame+k)&255
            cpu.y=(x^y^k)&255
            cpu.c=(x+y+k)&1
            cpu.d=0
            cycles=cpu.call(entry,60000)
            value=int.from_bytes(mem[io+8:io+11],"little")
            if (value!=speed.oracle(x,y) or cpu.c!=0 or cpu.sp!=sp
                or bytes(mem[io:io+4])!=xb
                or bytes(mem[io+4:io+8])!=yb
                or bytes(mem[io+12:io+16])!=bytes((0xdd,))*4):
                raise AssertionError((variant,frame,k,x,y,value))
            calls.append(cycles)
            frames[frame]+=cycles
        return {"total":sum(calls),"peak":max(frames),
                "per_call":calls,"per_frame":frames}

class SameInputFrames(unittest.TestCase):
    def test_signed_scaled_peak_math_frame(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            portable=run(speed.SMALL,code,io)
            table=run(speed.FAST,code,io)
            report={"origin":"$%04X"%code,"frames":FRAMES,"calls":CALLS,
                "portable_total":portable["total"],"quarter_total":table["total"],
                "portable_peak":portable["peak"],"quarter_peak":table["peak"],
                "saved_total":portable["total"]-table["total"],
                "saved_peak":portable["peak"]-table["peak"],
                "regressed_calls":sum(a>b for a,b in zip(table["per_call"],portable["per_call"])),
                "regressed_frames":sum(a>b for a,b in zip(table["per_frame"],portable["per_frame"]))}
            print("SMUL16_SHR8_QS_PAIRED",json.dumps(report,sort_keys=True),flush=True)
            self.assertLess(table["total"],portable["total"])
            self.assertLess(table["peak"],portable["peak"])

if __name__=="__main__":
    unittest.main()
