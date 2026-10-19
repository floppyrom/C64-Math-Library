#!/usr/bin/env python3
"""Same-input 150-call signed 16x16 math workload over 24 frames.

CPU model only, not physical VIC/IRQ/PAL timing.
"""
import json
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smul16 as speed

FRAMES=24
CALLS=150
CONFIG={speed.SMALL:(199,161),speed.FAST:(1387,1351)}

def events():
    values=speed.corpus()
    result=[]
    for frame in range(FRAMES):
        count=24 if frame%8==0 else 8 if frame%4==0 else 3
        for i in range(count):
            result.append((frame,i,*values[(frame*37+i*83)%len(values)]))
    assert len(result)==CALLS
    return result

def run(variant,code,io):
    ram,size=CONFIG[variant]
    plan=math_builder.create_plan(
       math_builder.operation_index(),["SMUL16"],objective="size",
       pins={"SMUL16":variant},zp_budget=0,ram_budget=ram)
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
        for frame,i,x,y in events():
            xb=x.to_bytes(2,"little")+bytes((0xa5,0x5a))
            yb=y.to_bytes(2,"little")+bytes((0x6b,0x7c))
            mem[io:io+4]=xb
            mem[io+4:io+8]=yb
            mem[io+8:io+16]=bytes((0x99,0x88,0x77,0x66,0xdd,0xdd,0xdd,0xdd))
            cpu.a=(x+frame+i)&255
            cpu.x=(y+frame+i)&255
            cpu.y=(x^y^i)&255
            cpu.c=(x+y+i)&1
            cpu.d=0
            cycles=cpu.call(entry,60000)
            actual=int.from_bytes(mem[io+8:io+12],"little")
            expected=(speed.signed(x)*speed.signed(y))&0xffffffff
            if (actual!=expected or cpu.c!=0 or cpu.sp!=sp
                or bytes(mem[io:io+4])!=xb
                or bytes(mem[io+4:io+8])!=yb
                or bytes(mem[io+12:io+16])!=bytes((0xdd,))*4):
                raise AssertionError((variant,frame,i,x,y,actual,expected))
            calls.append(cycles)
            frames[frame]+=cycles
        return {"total":sum(calls),"peak":max(frames),
                "per_call":calls,"per_frame":frames}

class QSFrames(unittest.TestCase):
    def test_same_calls_and_peak(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            small=run(speed.SMALL,code,io)
            fast=run(speed.FAST,code,io)
            report={"origin":"$%04X"%code,
                    "calls":CALLS,"frames":FRAMES,
                    "compact_total":small["total"],
                    "qs_total":fast["total"],
                    "compact_peak":small["peak"],
                    "qs_peak":fast["peak"],
                    "saved_total":small["total"]-fast["total"],
                    "saved_peak":small["peak"]-fast["peak"],
                    "regressed_calls":sum(a>b for a,b in zip(fast["per_call"],small["per_call"])),
                    "regressed_frames":sum(a>b for a,b in zip(fast["per_frame"],small["per_frame"]))}
            print("SMUL16_QS_PAIRED_FRAME",json.dumps(report,sort_keys=True),flush=True)
            self.assertLess(fast["total"],small["total"])
            self.assertLess(fast["peak"],small["peak"])
if __name__=="__main__":
    unittest.main()
