#!/usr/bin/env python3
"""Issue #39: eight live SEEK objects, every public stepper, both source maps.

Proves the public INIT + STEP/STEP_INT/STEP1 trajectory against the independent
seek_model reference, with eight interleaved objects in distinct slots.
Checks all 20/31 byte planes' slot isolation, X register, carry, repeated
arrival, and stack balance. CPU-model cycles only; no native VICE timing.
"""
from __future__ import annotations
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"routines/movement"))
import validate_source_build as vsb
from seek_model import expected_frames

PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")
MAPS=("reference","alternate")
SEEK8=((0,0,255,199),(255,199,0,0),(0,10,250,10),
       (30,0,30,199),(50,50,50,50),(200,50,10,190),
       (200,170,1,10),(128,80,129,81))
SEEK16=((0,0,319,199),(319,199,0,0),(0,100,1024,100),
        (30000,199,30000,0),(12345,55,12345,55),
        (60000,0,59900,190),(65535,80,65000,80),
        (255,40,256,42))
SPEEDS={
    "step":(0x0080,0x0100,0x0180,0x0200,0x8100,0x8200,0x8400,0x8180),
    "int":(0x0100,0x0200,0x0300,0x0400,0x0500,0x0600,0x0700,0x0800),
    "one":(0x0100,)*8,
}
STATE={"8":("MATH_SEEK8_POS_X",160),"16":("MATH_SEEK16_POS_XL",248)}

def shot(c,base,n,slot):
    assert n%8==0 and slot in range(8)
    return bytes(c.mem[base + k*8 + slot] for k in range(n//8))

def position(c,symbols,width,slot):
    if width==8:
        return (c.mem[symbols["MATH_SEEK8_POS_X"]+slot],
                c.mem[symbols["MATH_SEEK8_POS_Y"]+slot])
    return (c.mem[symbols["MATH_SEEK16_POS_XL"]+slot]|
            c.mem[symbols["MATH_SEEK16_POS_XH"]+slot]<<8,
            c.mem[symbols["MATH_SEEK16_POS_Y"]+slot])

def place(c,symbols,io,width,slot,move,speed):
    x0,y0,x1,y1=move
    if width==8:
        c.mem[symbols["MATH_SEEK8_POS_X"]+slot]=x0
        c.mem[symbols["MATH_SEEK8_POS_Y"]+slot]=y0
    else:
        c.mem[symbols["MATH_SEEK16_POS_XL"]+slot]=x0 & 255
        c.mem[symbols["MATH_SEEK16_POS_XH"]+slot]=x0 >> 8
        c.mem[symbols["MATH_SEEK16_POS_Y"]+slot]=y0
    c.mem[io]=x1 & 255
    c.mem[io+1]=(x1 >> 8) & 255
    c.mem[io+4]=y1
    c.mem[io+0x10]=speed & 255
    c.mem[io+0x11]=(speed >> 8)&255

def scenario(c,api,symbols,io,width,mode):
    prefix=f"MATH_SEEK{width}_"
    moves=SEEK8 if width==8 else SEEK16
    speeds=SPEEDS[mode]
    base,size=STATE[str(width)]
    statebase=symbols[base]
    initial_sp=c.sp
    frames=[expected_frames(*move,speed,mode)
            for move,speed in zip(moves,speeds)]
    assert all(len(f)<5000 for f in frames),(width,mode,"unbounded model")
    timing_init=[]
    timing_step=[]
    # All 8 objects initialized *before* any object advances. Each
    # initialization must leave the other seven stored objects untouched.
    for slot,(move,speed,expected) in enumerate(zip(moves,speeds,frames)):
        place(c,symbols,io,width,slot,move,speed)
        peers={j:shot(c,statebase,size,j) for j in range(8) if j!=slot}
        c.x=slot
        cycles=c.call(api[prefix+"INIT"],200000)
        timing_init.append(cycles)
        assert c.sp==initial_sp and c.x==slot,(width,mode,slot,"INIT ABI")
        assert c.c==int(not expected),(width,mode,slot,"INIT carry")
        assert position(c,symbols,width,slot)==move[:2]
        assert all(shot(c,statebase,size,j)==data for j,data in peers.items()),(
            width,mode,slot,"INIT overwrote another slot")
    # Interleave one public call per live object per logical frame, and
    # include two more calls *after* arrival to test permanent stability.
    limit=max(map(len,frames))+2
    for frame in range(limit):
        for slot,move in enumerate(moves):
            name={"step":"STEP","int":"STEP_INT","one":"STEP1"}[mode]
            expected=frames[slot][frame] if frame<len(frames[slot]) else (
                (move[2],move[3]),True)
            peers={j:shot(c,statebase,size,j) for j in range(8) if j!=slot}
            c.x=slot
            n=c.call(api[prefix+name],200000)
            timing_step.append(n)
            actual=(position(c,symbols,width,slot),bool(c.c))
            assert actual==expected,(width,mode,frame,slot,"trajectory",actual,expected)
            assert c.x==slot and c.sp==initial_sp,(width,mode,frame,slot,"STEP ABI")
            assert all(shot(c,statebase,size,j)==data for j,data in peers.items()),(
                width,mode,frame,slot,"STEP corrupted another object slot")
    return {
      "init_calls":len(timing_init),"step_calls":len(timing_step),
      "model_frames":sum(map(len,frames)),
      "init_mean_cpu_cycles":statistics.fmean(timing_init),
      "step_mean_cpu_cycles":statistics.fmean(timing_step),
      "step_min_cpu_cycles":min(timing_step),
      "step_max_cpu_cycles":max(timing_step),
      "eight_simultaneous_slots":True,
      "post_arrival_calls_per_slot":2,
      "max_frame_length":max(map(len,frames))
    }

def qualify(profile,kind):
    root=ROOT/("build_hybrid" if profile==PROFILES[-1] else "build_source")/kind
    c,api,io,manifest,_=vsb.load(profile,root)
    symbols=vsb.seek_symbols(root/profile)
    original_api=dict(api)
    api.update(symbols)
    data={}
    for width in (8,16):
        for mode in ("step","int","one"):
            data[f"SEEK{width}_{mode.upper()}"]=scenario(
                c,api,symbols,io,width,mode)
    return {"status":"PASS","scenarios":data,
            "public_api_addresses":{k:original_api[k] for k in original_api if
                                    k.startswith(("MATH_SEEK8_","MATH_SEEK16_"))},
            "source_prg_sha256":manifest["output_sha256"]}

def main():
    import seek_kernel
    assert seek_kernel.S8_BYTES==160 and seek_kernel.S16_BYTES==248
    report={"status":"PASS_SEEK_ALL_EIGHT_SLOTS",
            "basis":"full public CPU-model entry, both relocation maps; not native VICE timing",
            "profiles":{},"totals":{"init_calls":0,"step_calls":0,"model_frames":0}}
    for p in PROFILES:
        report["profiles"][p]={}
        for kind in MAPS:
            result=qualify(p,kind)
            report["profiles"][p][kind]=result
            for scenario in result["scenarios"].values():
                for key in report["totals"]:
                    report["totals"][key]+=scenario[key]
            print("SEEK ALL SLOTS",p,kind,"PASS",
                  {k:(v["init_calls"],v["step_calls"])
                   for k,v in result["scenarios"].items()},flush=True)
    assert report["totals"]["init_calls"]==5*2*2*3*8
    out=ROOT/"validation/review/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 ALL EIGHT SLOT PROOF PASS",report["totals"],flush=True)

if __name__=="__main__":main()
