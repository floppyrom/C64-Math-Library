#!/usr/bin/env python3
"""150-call / 24-frame same-input shifted-16 divider workload comparison.

CPU-model *math calls only*: no VIC/IRQ/REU/PAL physical frame timing.
Track per-call regressions and whole-frame regressions at two code origins.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_udiv16_shl8 as speed

FRAMES = 24
COUNT = 150


def scenario():
    base = speed.corpus()
    calls = []
    for frame in range(FRAMES):
        volume = 24 if frame % 8 == 0 else (8 if frame % 4 == 0 else 3)
        for ordinal in range(volume):
            n, d = base[(frame * 37 + ordinal * 83) % len(base)]
            calls.append((frame, ordinal, n, d))
    assert len(calls) == COUNT
    return calls


def measure(variant, code, io, zp):
    fast = variant == speed.FAST
    index = math_builder.operation_index()
    plan = math_builder.create_plan(
        index, ["UDIV16_SHL8"], objective="size",
        pins={"UDIV16_SHL8": variant},
        zp_budget=12 if fast else 0, ram_budget=2400 if fast else 162)
    with tempfile.TemporaryDirectory() as td:
        folder = Path(td)
        man = linker.build(plan, folder, memory={
            "code_base": code, "math_io": io,
            "zp_base": zp, "scratch_base": io + 0x40})
        data = (folder / "math_selective.prg").read_bytes()
        assert data[:2] == code.to_bytes(2, "little")
        mem = bytearray(65536)
        mem[code:code+len(data)-2] = data[2:]
        cpu = CPU(mem)
        entry = int(man["operations"][0]["entry"][1:], 16)
        sp = cpu.sp
        frames, calls = [0]*FRAMES, []
        for frame, ordinal, n, d in scenario():
            nb = n.to_bytes(2, "little") + bytes([0x5a, 0xa5])
            db = d.to_bytes(2, "little") + bytes([0x69, 0xab])
            mem[io+16:io+20] = nb
            mem[io+20:io+24] = db
            mem[io+24:io+32] = bytes([0xcc]*4+[0xdd,0xdd,0x49,0x59])
            cpu.a = (frame*17+ordinal*29)&255
            cpu.x = (frame*31+ordinal*7)&255
            cpu.y = (frame*13+ordinal*23)&255
            cpu.c = (frame+ordinal)&1
            cpu.d = 0
            ticks = cpu.call(entry,50000)
            actual = (int.from_bytes(mem[io+24:io+28],"little"),
                      int.from_bytes(mem[io+28:io+30],"little"),cpu.c)
            expected = ((n<<8)//d if d else 0,
                        (n<<8)%d if d else 0,int(d==0))
            if (actual != expected or cpu.sp != sp
                    or bytes(mem[io+16:io+20]) != nb
                    or bytes(mem[io+20:io+24]) != db
                    or bytes(mem[io+30:io+32]) != bytes([0x49,0x59])):
                raise AssertionError((variant,frame,ordinal,n,d,actual,expected))
            calls.append(ticks)
            frames[frame] += ticks
        return {"calls":calls,"frames":frames,"total":sum(calls),
                "peak":max(frames)}


def compare(code,io,zp):
    compact = measure(speed.SMALL,code,io,zp)
    fast = measure(speed.FAST,code,io,zp)
    call_delta = [a-b for a,b in zip(fast["calls"],compact["calls"])]
    frame_delta = [a-b for a,b in zip(fast["frames"],compact["frames"])]
    result = {"origin":"$%04X"%code, "calls":COUNT,"frames":FRAMES,
              "portable_total":compact["total"],"v2_total":fast["total"],
              "portable_peak":compact["peak"],"v2_peak":fast["peak"],
              "saved_total":compact["total"]-fast["total"],
              "saved_peak":compact["peak"]-fast["peak"],
              "regressed_calls":sum(x>0 for x in call_delta),
              "regressed_frames":sum(x>0 for x in frame_delta),
              "worst_call_regression":max([0]+call_delta),
              "worst_frame_regression":max([0]+frame_delta)}
    if result["saved_total"] <= 0 or result["saved_peak"] <= 0:
        raise AssertionError("Historical V2 shifted workload loses: "+repr(result))
    return result


class Shifted16PairedFrames(unittest.TestCase):
    def test_two_origins_150_calls_24_frames(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            with self.subTest(code=code):
                print("V2_SHIFTED16_PAIRED_FRAME",
                      json.dumps(compare(code,io,zp),sort_keys=True),
                      flush=True)


if __name__=="__main__":
    unittest.main()
