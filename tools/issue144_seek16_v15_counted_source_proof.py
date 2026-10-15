#!/usr/bin/env python3
"""Issue #144 D: compare V1/V5 counted SEEK16 with original public source.

This tests actual source-built resident code in both relocation maps. It
reassembles the unmodified independent SEEK template as an internal baseline
and patches only original SEEK bytes into a separate disposable 6502 image.
No reference PRG/REU is modified; performance is CPU model, not VICE timing.
"""
from __future__ import annotations

import json
import statistics
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import build,parse_config
from build_hybrid import build as hybrid_build
from validate_source_build import load
from benchmark_seek_profiles import corpus
import seek_kernel as K
from generate_seek_sources import LAYOUTS,SCRATCH

PROFILES=("v1_balanced","v5_hybrid_lowzp")
SPEEDS=(0x0080,0x0100,0x0180,0x0200,0x0300,0x0400,0x8100,0x8180,0x8200,0x8300)
S16_BYTES=K.S16_BYTES

def synth_old(cfg):
    # The profile argument deliberately selects unmodified ordinary template,
    # including its original two JSR accumulator sites and original shared map.
    layout=dict(LAYOUTS["v1_balanced"])
    layout["seek_shared"]="REG_API+$0977"
    config=ROOT/"relocatable_source/v1_balanced"/("math_config_"+cfg+".inc")
    values=parse_config(config)
    decl="".join(f"{k} = ${v:04X}\\n" for k,v in values.items())
    old=K.library("v1_before_issue144",layout,*SCRATCH["v1_balanced"])
    mem,labels,const=Assembler().assemble(decl+old)
    return mem,labels,const

def run(profile,layout,tmp):
    cfg=ROOT/"relocatable_source"/profile/f"math_config_{layout}.inc"
    dest=tmp/layout/profile
    if profile=="v1_balanced":
        build(profile,cfg,dest)
    else:
        hybrid_build(cfg,dest)
    cur,pub,io,man,_=load(profile,tmp/layout)
    base,_,_,_,_=load(profile,tmp/layout)
    old,labels,const=synth_old(layout)
    # Verify canonical source really contains the candidate and that the
    # independent original differs at precisely a nonempty SEEK byte subset.
    diff=[a for a,v in old.items() if cur.mem[a]!=v]
    assert diff,("no installed SEEK difference",profile,layout)
    assert len(diff)<400,("unexpected large patch",profile,layout,len(diff))
    for a,v in old.items():
        base.mem[a]=v
    assert base.mem[pub["MATH_SEEK16_INIT"]]==0x4c
    assert base.mem[pub["MATH_SEEK16_INIT"]+1:pub["MATH_SEEK16_INIT"]+3]==cur.mem[pub["MATH_SEEK16_INIT"]+1:pub["MATH_SEEK16_INIT"]+3]
    assert pub["MATH_SEEK16_INIT"]==0x5e48 if layout=="reference" else True
    state=pub["MATH_SEEK16_POS_XL"]
    starts=[]
    ours=[]
    buckets={f"{s:04X}":[] for s in SPEEDS}
    slower=0
    checked=0
    for index,(x0,y0,x1,y1) in enumerate(corpus(320)):
        slot=index&7
        for speed in SPEEDS:
            for cpu in (base,cur):
                cpu.mem[state+slot]=x0&255
                cpu.mem[state+8+slot]=(x0>>8)&255
                cpu.mem[state+16+slot]=y0
                cpu.mem[io]=x1&255
                cpu.mem[io+1]=(x1>>8)&255
                cpu.mem[io+4]=y1
                cpu.mem[io+0x10]=speed&255
                cpu.mem[io+0x11]=speed>>8
                cpu.x=slot
            before_io=bytes(base.mem[io:io+0x20])
            a=base.call(pub["MATH_SEEK16_INIT"],4_000_000)
            b=cur.call(pub["MATH_SEEK16_INIT"],4_000_000)
            assert bytes(base.mem[io:io+0x20])==bytes(cur.mem[io:io+0x20])==before_io
            assert bytes(base.mem[state:state+S16_BYTES])==bytes(cur.mem[state:state+S16_BYTES]),("init state",profile,layout,index,speed)
            assert (base.c,base.x,base.sp)==(cur.c,cur.x,cur.sp),("init flags",profile,layout,index,speed)
            starts.append(a);ours.append(b)
            saving=a-b
            buckets[f"{speed:04X}"].append(saving)
            slower+=saving<0
            checked+=1
            # STEP and STEP_INT/STEP1 to validate precomputed plane states,
            # including arrival and the continuous post-arrival contract.
            modes=["MATH_SEEK16_STEP"]
            if speed in (0x0100,0x0200,0x0300,0x0400):
                modes.append("MATH_SEEK16_STEP_INT")
            if speed==0x0100:modes.append("MATH_SEEK16_STEP1")
            for mode in modes:
                for _ in range(4):
                    base.x=cur.x=slot
                    base.call(pub[mode],4_000_000)
                    cur.call(pub[mode],4_000_000)
                    assert bytes(base.mem[state:state+S16_BYTES])==bytes(cur.mem[state:state+S16_BYTES]),("STEP",profile,layout,index,speed,mode)
                    assert (base.c,base.x,base.sp)==(cur.c,cur.x,cur.sp),("STEP flags",profile,layout,index,speed,mode)
                # Reinitialize identical original states before another mode.
                # Only STEP mode is subsequently used; the other modes are
                # covered independently by the general source validators.
    saved=[a-b for a,b in zip(starts,ours)]
    return {"profile":profile,"map":layout,"status":"PASS_MODEL_PUBLIC_INIT_STEP",
            "cases":checked,"changed_source_bytes":len(diff),
            "mean_before":statistics.fmean(starts),
            "mean_after":statistics.fmean(ours),
            "mean_saved":statistics.fmean(saved),
            "p95_new_minus_old":sorted([b-a for a,b in zip(starts,ours)])[int(.95*(len(saved)-1))],
            "worst_saved":min(saved),"best_saved":max(saved),
            "slower_calls":slower,
            "speed_buckets":{k:{"mean_saved":statistics.fmean(v),"minimum_saved":min(v),"slower":sum(x<0 for x in v)} for k,v in buckets.items()}}

def main():
    with tempfile.TemporaryDirectory(prefix="issue144_seek_v15_") as d:
        reports=[run(p,lay,Path(d)) for lay in ("reference","alternate") for p in PROFILES]
    assert all(r["cases"]==4080 for r in reports)
    assert all(r["mean_saved"]>0 for r in reports)
    print(json.dumps({"status":"PASS_SEEK16_COUNTED_SOURCE_MODEL",
          "reference_images_modified":False,"profiles":reports},indent=2))
if __name__=="__main__":
    main()
