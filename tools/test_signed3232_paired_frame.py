#!/usr/bin/env python3
"""Same-placement paired 24-frame signed32/32 public-call workload proof.

Measured CPU-model public JSR cycle totals. No IRQ, VIC, SID, real PAL
raster timing or hardware cycle claim. Both producer choices are linked
independently under identical addresses and preserve full public Q/R/C.
"""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_s3232 as speed
from frame_cycle_budget import Call, score

OPS = ("MATH_SDIV32_32","MATH_SMOD32_32")
VARIANTS=(speed.PORTABLE,speed.FAST)
FRAMES=24
CALLS=150


def scenario():
    pairs=speed.corpus()
    calls=[]
    for frame in range(FRAMES):
        volume=24 if frame%8==0 else (8 if frame%4==0 else 3)
        for ordinal in range(volume):
            n,d=pairs[(frame*37+ordinal*83)%len(pairs)]
            api=OPS[(frame+ordinal)%2]
            identity=hashlib.sha256(("%s|%08x|%08x|%d|%d" %
                (api,n,d,frame,ordinal)).encode()).hexdigest()
            calls.append((frame,ordinal,api,n,d,identity))
    assert len(calls)==CALLS
    return calls


def evaluate(variant,code,io,zp=0x50):
    if variant not in VARIANTS:
        raise ValueError("Candidate must be source-qualified")
    index=math_builder.operation_index()
    plan=math_builder.create_plan(index,[s[5:] for s in OPS],
        objective="size",zp_budget=12 if variant==speed.FAST else 0,
        ram_budget=2912 if variant==speed.FAST else 453,
        pins={a:variant for a in OPS})
    with tempfile.TemporaryDirectory(prefix="signed3232_trace_") as temp:
        path=Path(temp)
        man=linker.build(plan,path,memory={
            "code_base":code,"math_io":io,"zp_base":zp,
            "scratch_base":io+0x40})
        entries={x["api"]:int(x["entry"][1:],16)
                 for x in man["operations"]}
        assert set(entries)==set(OPS)
        assert len(man["link_order"])==1
        image=(path/"math_selective.prg").read_bytes()
        assert image[:2]==code.to_bytes(2,"little")
        mem=bytearray(65536)
        mem[code:code+len(image)-2]=image[2:]
        immutable=bytes(mem[code:code+len(image)-2])
        cpu=CPU(mem)
        sp=cpu.sp
        observations=[]
        for frame,ordinal,api,n,d,identity in scenario():
            nb=n.to_bytes(4,"little")
            db=d.to_bytes(4,"little")
            mem[io+16:io+20]=nb
            mem[io+20:io+24]=db
            mem[io+24:io+32]=bytes((0xbb,)*8)
            cpu.a=(frame*17+ordinal*29)&255
            cpu.x=(frame*31+ordinal*7)&255
            cpu.y=(frame*13+ordinal*23)&255
            cpu.c=(frame+ordinal)&1
            cpu.d=0
            ticks=cpu.call(entries[api],150000)
            got=(int.from_bytes(mem[io+24:io+28],"little"),
                 int.from_bytes(mem[io+28:io+32],"little"),cpu.c)
            want=speed.reference(n,d)
            if (got!=want or bytes(mem[io+16:io+20])!=nb
                    or bytes(mem[io+20:io+24])!=db or cpu.sp!=sp):
                raise AssertionError((variant,frame,ordinal,api,n,d,got,want))
            observations.append(Call(frame,ordinal,api,identity,ticks,variant))
        if bytes(mem[code:code+len(image)-2])!=immutable:
            raise AssertionError("Signed32/32 modified executable image")
        info={"measurement_basis":"cpu-model-public-entry-through-rts",
              "placement":"%04x/%04x"%(code,io),
              "variants":{api:variant for api in OPS}}
        return observations,score(observations,info,frame_count=FRAMES)


def compare(code,io):
    old,before=evaluate(speed.PORTABLE,code,io)
    new,after=evaluate(speed.FAST,code,io)
    a={(v.frame,v.ordinal,v.operation,v.input_id):v.cycles for v in old}
    b={(v.frame,v.ordinal,v.operation,v.input_id):v.cycles for v in new}
    if len(a)!=CALLS or set(a)!=set(b):
        raise AssertionError("Signed32/32 public frame input corpus drifted")
    regressions=[b[k]-a[k] for k in a if b[k]>a[k]]
    old_frames=before["frame_math_cycles"]
    new_frames=after["frame_math_cycles"]
    per_frame=[n-o for o,n in zip(old_frames,new_frames)]
    result={"code":"$%04X"%code,"io":"$%04X"%io,
            "calls":CALLS,"frames":FRAMES,
            "portable_total":before["total_math_cycles"],
            "v2_total":after["total_math_cycles"],
            "portable_peak":before["peak_frame_math_cycles"],
            "v2_peak":after["peak_frame_math_cycles"],
            "peak_savings":before["peak_frame_math_cycles"]-
                           after["peak_frame_math_cycles"],
            "regressed_frames":sum(n>0 for n in per_frame),
            "worst_frame_regression":max([0]+per_frame),
            "regressed_calls":len(regressions),
            "worst_call_regression":max([0]+regressions)}
    if not result["v2_total"]<result["portable_total"]:
        raise AssertionError("Hybrid regressed aggregate mixed frame workload")
    if not result["v2_peak"]<result["portable_peak"]:
        raise AssertionError("Hybrid regressed peak synthetic frame workload")
    return result


class Signed3232PairedFrameTests(unittest.TestCase):
    def test_24_frame_both_source_variants_two_origins(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(code=code):
                result=compare(code,io)
                self.assertEqual((result["calls"],result["frames"]),(150,24))
                print("SIGNED3232_V2_PAIRED_FRAME",
                      json.dumps(result,sort_keys=True),flush=True)


if __name__=="__main__":
    unittest.main()
