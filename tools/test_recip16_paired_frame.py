#!/usr/bin/env python3
"""Matched 150-call / 24-frame reciprocal latency gate.

Only the math public-call CPU-model cycles are scored; results are *not*
cycle-accurate physical VIC-II badline, IRQ, SID or REU frame timings.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_recip16 as speed

FRAMES=24
COUNT=150
CONFIG={
    speed.SMALL:(132,99),
    speed.FAST:(481,448),
    speed.TABLE:(1576,1544),
}


def events():
    corpus=speed.corpus()
    records=[]
    for frame in range(FRAMES):
        volume=24 if frame%8==0 else (8 if frame%4==0 else 3)
        for k in range(volume):
            records.append((frame,k,corpus[(frame*37+k*83)%len(corpus)]))
    assert len(records)==COUNT
    return records


def run(variant,code,io):
    total_ram,bytes_used=CONFIG[variant]
    index=math_builder.operation_index()
    plan=math_builder.create_plan(
        index,["URECIP16_Q16"],objective="size",
        pins={"URECIP16_Q16":variant},zp_budget=0,ram_budget=total_ram)
    with tempfile.TemporaryDirectory() as td:
        folder=Path(td)
        man=linker.build(plan,folder,memory={
            "code_base":code,"math_io":io,"scratch_base":io+0x40})
        image=(folder/"math_selective.prg").read_bytes()
        cpu=CPU(bytearray(65536))
        mem=cpu.mem
        mem[code:code+bytes_used]=image[2:]
        entry=int(man["operations"][0]["entry"][1:],16)
        sp=cpu.sp
        per_call=[]
        per_frame=[0]*FRAMES
        for frame,i,d in events():
            mem[io+20:io+24]=d.to_bytes(2,"little")+b"\x5a\xa5"
            mem[io+16:io+20]=b"\xde\xad\xbe\xef"
            mem[io+24:io+28]=b"\x55\xaa\x77\xcc"
            mem[io+28:io+32]=b"\x12\x34\x56\x78"
            cpu.a=(d+i+frame)&255
            cpu.x=(d+frame)&255
            cpu.y=(d^i)&255
            cpu.c=(d+i)&1
            cpu.d=0
            cycles=cpu.call(entry,50000)
            out=(int.from_bytes(mem[io+24:io+27],"little"),cpu.c)
            want=(65536//d if d else 0,int(d==0))
            if (out!=want or mem[io+27]!=0xcc or
                mem[io+16:io+20]!=b"\xde\xad\xbe\xef" or
                mem[io+20:io+24]!=d.to_bytes(2,"little")+b"\x5a\xa5" or
                mem[io+28:io+32]!=b"\x12\x34\x56\x78" or
                cpu.sp!=sp):
                raise AssertionError((variant,frame,i,d,out,want))
            per_call.append(cycles)
            per_frame[frame]+=cycles
        return {"total":sum(per_call),"peak_frame":max(per_frame),
                "per_call":per_call,"per_frame":per_frame}


class ReciprocalPairedFrames(unittest.TestCase):
    def test_source_matched_busy_frame_and_call_tail(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            metrics={p:run(p,code,io) for p in CONFIG}
            ref=metrics[speed.SMALL]
            fast=metrics[speed.TABLE]
            gate=metrics[speed.FAST]
            out={
                "origin":"$%04X"%code,
                "calls":COUNT,"frames":FRAMES,
                "compact_total":ref["total"],
                "compact_peak_frame":ref["peak_frame"],
                "threshold_total":gate["total"],
                "threshold_peak_frame":gate["peak_frame"],
                "table_total":fast["total"],
                "table_peak_frame":fast["peak_frame"],
                "table_saved_total":ref["total"]-fast["total"],
                "table_saved_peak":ref["peak_frame"]-fast["peak_frame"],
                "table_regressed_calls":sum(
                    a>b for a,b in zip(fast["per_call"],ref["per_call"])),
                "table_regressed_frames":sum(
                    a>b for a,b in zip(fast["per_frame"],ref["per_frame"])),
                "threshold_regressed_calls":sum(
                    a>b for a,b in zip(gate["per_call"],ref["per_call"])),
            }
            print("RECIP16_PAIRED_FRAME",json.dumps(out,sort_keys=True),
                  flush=True)
            self.assertLess(fast["total"],ref["total"])
            self.assertLess(fast["peak_frame"],ref["peak_frame"])
            self.assertEqual(out["table_regressed_frames"],0)


if __name__=="__main__":
    unittest.main()
