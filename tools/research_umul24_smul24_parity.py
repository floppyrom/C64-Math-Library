#!/usr/bin/env python3
"""Matched-input UMUL24/SMUL24 donor triage on released V1-V5 resident PRGs.

Research only: different code addresses and table/REU layouts. Historical
resident timings cannot be plugged into automatic builder speed selection.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import tempfile
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
from validate_signed_multiply import PROFILES, REU, load_profile

ROOT=Path(__file__).resolve().parents[1]
OPS=("MATH_UMUL24","MATH_SMUL24")
EDGE=(0,1,2,3,7,15,127,128,255,256,65535,65536,
      0x7ffffe,0x7fffff,0x800000,0x800001,0xfffffe,0xffffff)
CASES=384
SEED=0x246424


def corpus(count=CASES):
    if count<1:
        raise ValueError("Positive corpus size required")
    edges=[(x,y) for x in EDGE for y in EDGE]
    result=edges[:count]
    rng=random.Random(SEED)
    while len(result)<count:
        result.append((rng.getrandbits(24),rng.getrandbits(24)))
    return result


def signed(n):
    return n-(1<<24) if n&0x800000 else n


def expected(api,x,y):
    if api=="MATH_SMUL24":
        return (signed(x)*signed(y))&((1<<48)-1)
    if api=="MATH_UMUL24":
        return (x*y)&((1<<48)-1)
    raise ValueError(api)


def measure(cpu,entry,io,api,pairs):
    sp=cpu.sp
    cycles=[]
    groups={"zero":[],"small":[],"general":[]}
    for i,(x,y) in enumerate(pairs):
        xb=x.to_bytes(3,"little")
        yb=y.to_bytes(3,"little")
        cpu.mem[io:io+3]=xb
        cpu.mem[io+4:io+7]=yb
        cpu.mem[io+8:io+16]=bytes((0xcd,)*8)
        cpu.a=(i*17+7)&255
        cpu.x=(i*13+9)&255
        cpu.y=(i*11+3)&255
        cpu.c=i&1
        cpu.d=0
        ticks=cpu.call(entry,200000)
        got=int.from_bytes(cpu.mem[io+8:io+14],"little")
        if (got!=expected(api,x,y) or cpu.c!=0 or cpu.sp!=sp
                or bytes(cpu.mem[io:io+3])!=xb
                or bytes(cpu.mem[io+4:io+7])!=yb):
            raise AssertionError((api,i,x,y,got,expected(api,x,y),cpu.c))
        group="zero" if not x or not y else (
            "small" if x<256 and y<256 else "general")
        groups[group].append(ticks)
        cycles.append(ticks)
    ordered=sorted(cycles)
    return {"calls":len(cycles),"mean_cycles":round(sum(cycles)/len(cycles),3),
            "max_cycles":max(cycles),
            "p95_cycles":ordered[(95*len(cycles)+99)//100-1],
            "buckets":{k:{"calls":len(vals),
                          "mean_cycles":(round(sum(vals)/len(vals),3)
                                         if vals else None)}
                       for k,vals in groups.items()}}


def collect(count=CASES,profiles=PROFILES,placements=((0x8000,0xc000),
                                                    (0x7123,0xc040))):
    pairs=corpus(count)
    digest=hashlib.sha256(b"".join(
        x.to_bytes(3,"little")+y.to_bytes(3,"little") for x,y in pairs
    )).hexdigest()
    entries=[]
    for profile in profiles:
        cpu,api=load_profile(profile)
        prg=ROOT/profile/"resident"/("math_"+profile+"_game_math.prg")
        for op in OPS:
            entries.append({"api":op,"variant":"resident:"+profile,
                "placement":"historical-physical-resident",
                "resident_sha256":hashlib.sha256(prg.read_bytes()).hexdigest(),
                "reu_sha256":(hashlib.sha256(REU[profile].read_bytes()).hexdigest()
                              if profile in REU else None),
                **measure(cpu,api[op],0xc000,op,pairs)})
    index=math_builder.operation_index()
    plan=math_builder.create_plan(index,["UMUL24","SMUL24"],
        objective="size",zp_budget=0,ram_budget=424)
    for code,io in placements:
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"scratch_base":io+0x40})
            assert len(man["link_order"])==2,man["link_order"]
            assert man["resource_use"]["zero_page_bytes"]==0
            assert man["resource_use"]["main_ram_total_bytes"]==424
            prg=(folder/"math_selective.prg").read_bytes()
            assert prg[:2]==code.to_bytes(2,"little")
            cpu=CPU(bytearray(65536))
            cpu.mem[code:code+len(prg)-2]=prg[2:]
            apis={v["api"]:int(v["entry"][1:],16) for v in man["operations"]}
            assert set(apis)==set(OPS)
            for op in OPS:
                entries.append({"api":op,"variant":"link:compact-zerozp",
                    "placement":"$%04X/$%04X"%(code,io),
                    "linked_sha256":hashlib.sha256(prg).hexdigest(),
                    **measure(cpu,apis[op],io,op,pairs)})
    return {"status":"PASS","purpose":"Donor research only, not speed promotion",
            "corpus_sha256":digest,"cases":count,
            "timing_basis":"Mini6502 full public entry through RTS, without caller JSR",
            "limitations":"Historical residence/REU/init, code placement and lookup table costs differ; exclude VIC/IRQ/hardware timing",
            "results":entries}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--cases",type=int,default=CASES)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    result=collect(args.cases)
    for api in OPS:
        rank=sorted((x for x in result["results"] if x["api"]==api),
                    key=lambda x:x["mean_cycles"])
        print("MUL24_DONOR",api,json.dumps([
            (x["variant"],x["placement"],x["mean_cycles"],x["max_cycles"])
            for x in rank]),flush=True)
    print("MUL24_CORPUS_SHA256",result["corpus_sha256"],flush=True)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2)+"\n",
                            encoding="utf-8")


if __name__=="__main__":
    main()
