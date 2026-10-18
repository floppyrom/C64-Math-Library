#!/usr/bin/env python3
"""Same-input public-call benchmark for five historical UMUL24/SMUL24 donors.

Research only: resident placement means do not qualify speed selection in
the independently linked operation-first installer.
"""
from __future__ import annotations
import argparse,hashlib,json,random,tempfile
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
from benchmark_multiply_refresh import PROFILES,REU,load,edge

ROOT=Path(__file__).resolve().parents[1]
MASK48=(1<<48)-1
OPS=("MATH_UMUL24","MATH_SMUL24")
CASES=512


def corpus():
    e=edge(24)
    rng=random.Random(0x5A246820)
    pairs=[(x,y) for x in e for y in e]
    pairs.extend((rng.getrandbits(24),rng.getrandbits(24))
                 for _ in range(CASES-len(pairs)))
    assert len(pairs)==CASES
    return pairs


def signed(v):
    return v-(1<<24) if v&0x800000 else v


def expected(x,y,api):
    if api=="MATH_SMUL24":
        x,y=signed(x),signed(y)
    return (x*y)&MASK48


def measure(cpu,entry,io,pairs,api):
    sp=cpu.sp
    clocks=[]
    quads={"pp":[],"pn":[],"np":[],"nn":[]}
    for i,(x,y) in enumerate(pairs):
        xb=x.to_bytes(3,"little");yb=y.to_bytes(3,"little")
        cpu.mem[io:io+3]=xb
        cpu.mem[io+4:io+7]=yb
        cpu.mem[io+8:io+16]=bytes((0xcc,)*6+(0x49,0x59))
        cpu.c=i&1;cpu.d=0
        cpu.a=(i*17+3)&255;cpu.x=(i*31+5)&255;cpu.y=(i*13+7)&255
        ticks=cpu.call(entry,150000)
        actual=int.from_bytes(cpu.mem[io+8:io+14],"little")
        if (actual!=expected(x,y,api) or cpu.c!=0 or cpu.sp!=sp
                or bytes(cpu.mem[io:io+3])!=xb
                or bytes(cpu.mem[io+4:io+7])!=yb
                or bytes(cpu.mem[io+14:io+16])!=bytes((0x49,0x59))):
            raise AssertionError((api,i,hex(x),hex(y),
                                  hex(actual),hex(expected(x,y,api))))
        quad=("n" if x&0x800000 else "p")+("n" if y&0x800000 else "p")
        quads[quad].append(ticks)
        clocks.append(ticks)
    ordered=sorted(clocks)
    return {"calls":len(clocks),
            "mean_cycles":round(sum(clocks)/len(clocks),3),
            "p95_cycles":ordered[(len(clocks)*95+99)//100-1],
            "max_cycles":max(clocks),
            "quadrants":{k:{"calls":len(v),
                             "mean_cycles":round(sum(v)/len(v),3) if v else None}
                         for k,v in quads.items()}}


def collect(profiles=PROFILES,placements=((0x8000,0xc000),
                                         (0x7123,0xc040))):
    pairs=corpus()
    digest=hashlib.sha256(b"".join(x.to_bytes(3,"little")+
        y.to_bytes(3,"little") for x,y in pairs)).hexdigest()
    rows=[]
    for profile in profiles:
        cpu,apis=load(profile)
        prg=ROOT/profile/"resident"/("math_"+profile+"_game_math.prg")
        for api in OPS:
            rows.append({"api":api,"variant":"resident:"+profile,
                         "placement":"resident-native",
                         "prg_sha256":hashlib.sha256(prg.read_bytes()).hexdigest(),
                         "reu_sha256":hashlib.sha256(REU[profile].read_bytes()).hexdigest()
                            if profile in REU else None,
                         **measure(cpu,apis[api],apis["MATH_X"],pairs,api)})
    plan=math_builder.create_plan(math_builder.operation_index(),
       ["UMUL24","SMUL24"],objective="size",zp_budget=0,ram_budget=2000)
    for code,io in placements:
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            manifest=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"scratch_base":io+0x40})
            variants={x["api"]:x["variant"] for x in manifest["operations"]}
            assert variants=={"MATH_UMUL24":"link:compact-zerozp",
                              "MATH_SMUL24":"link:compact-zerozp"},variants
            assert manifest["resource_use"]["zero_page_bytes"]==0
            payload=(folder/"math_selective.prg").read_bytes()
            assert payload[:2]==code.to_bytes(2,"little")
            cpu=CPU(bytearray(65536))
            cpu.mem[code:code+len(payload)-2]=payload[2:]
            entry={x["api"]:int(x["entry"][1:],16)
                   for x in manifest["operations"]}
            for api in OPS:
                rows.append({"api":api,"variant":"link:compact-zerozp",
                             "placement":"$%04X/IO=$%04X"%(code,io),
                             "linked_sha256":hashlib.sha256(payload).hexdigest(),
                             **measure(cpu,entry[api],io,pairs,api)})
    return {"status":"PASS","purpose":"historical donor triage, NOT automatic speed selection",
            "cases_per_api":CASES,"corpus_sha256":digest,
            "basis":"Mini6502 complete public entry through RTS, excluding caller JSR",
            "caveats":"Different physical profile/code placements; no physical PAL timing",
            "measurements":rows}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    report=collect()
    for api in OPS:
        cases=sorted((r for r in report["measurements"] if r["api"]==api),
                     key=lambda q:q["mean_cycles"])
        print("MUL24 HISTORICAL DONOR",api,json.dumps([
            (r["variant"],r["placement"],r["mean_cycles"],r["max_cycles"])
            for r in cases]),flush=True)
    print("MUL24 DONOR CORPUS",report["corpus_sha256"])
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
