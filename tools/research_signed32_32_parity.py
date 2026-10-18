#!/usr/bin/env python3
"""Source-independent donor triage for signed 32/32 DIV and MOD.

Same deterministic operands, public I/O, carry and stack checks for all five
released resident images and the linked portable source at two placements.
Historical profiles are not relocatable sources and are NOT auto-selectable.
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
from validate_signed_division import PROFILES, REU, load_profile

ROOT = Path(__file__).resolve().parents[1]
OPS = ("MATH_SDIV32_32", "MATH_SMOD32_32")
NE = (0,1,2,3,127,255,65535,65536,0x7fffffff,0x80000000,
      0x80000001,0xfffffffe,0xffffffff)
DE = (0,1,2,3,127,255,65535,0x7fffffff,0x80000000,0xffffffff)


def corpus(count=192):
    if count < 1:
        raise ValueError("count must be positive")
    pairs = [(n,d) for n in NE for d in DE][:count]
    rng = random.Random(0x5323232)
    pairs.extend((rng.getrandbits(32),rng.getrandbits(32))
                 for _ in range(count-len(pairs)))
    return pairs


def signed(n):
    return n-(1<<32) if n&0x80000000 else n


def expected(n,d):
    n,d=signed(n),signed(d)
    if not d:
        return 0,0,1
    q=abs(n)//abs(d)
    if (n<0)!=(d<0):
        q=-q
    return q&0xffffffff,(n-q*d)&0xffffffff,0


def measure(cpu,entry,io,pairs,api):
    sp=cpu.sp
    samples=[]
    groups={"zero_divisor":[],"quotient_zero":[],"general":[]}
    for i,(n,d) in enumerate(pairs):
        nb=n.to_bytes(4,"little")
        db=d.to_bytes(4,"little")
        cpu.mem[io+16:io+20]=nb
        cpu.mem[io+20:io+24]=db
        cpu.mem[io+24:io+32]=bytes((0xcc,)*4+(0xdd,)*4)
        cpu.a=(i*17+3)&255
        cpu.x=(i*31+5)&255
        cpu.y=(i*13+7)&255
        cpu.c=i&1
        cpu.d=0
        ticks=cpu.call(entry,150000)
        got=(int.from_bytes(cpu.mem[io+24:io+28],"little"),
             int.from_bytes(cpu.mem[io+28:io+32],"little"),cpu.c)
        want=expected(n,d)
        if (got!=want or bytes(cpu.mem[io+16:io+20])!=nb
                or bytes(cpu.mem[io+20:io+24])!=db or cpu.sp!=sp):
            raise AssertionError((api,i,n,d,got,want))
        group="zero_divisor" if d==0 else (
            "quotient_zero" if want[0]==0 else "general")
        groups[group].append(ticks)
        samples.append(ticks)
    sorted_ticks=sorted(samples)
    return {"calls":len(samples),
            "mean_cycles":round(sum(samples)/len(samples),3),
            "max_cycles":max(samples),
            "p95_cycles":sorted_ticks[(95*len(samples)+99)//100-1],
            "buckets":{k:{"calls":len(v),
                           "mean_cycles":round(sum(v)/len(v),3) if v else None}
                       for k,v in groups.items()}}


def collect(count=192,profiles=PROFILES,placements=((0x8000,0xc000),
                                                  (0x7123,0xc040))):
    pairs=corpus(count)
    digest=hashlib.sha256(b"".join(n.to_bytes(4,"little")+
        d.to_bytes(4,"little") for n,d in pairs)).hexdigest()
    rows=[]
    for profile in profiles:
        cpu,apis=load_profile(profile)
        prg=ROOT/profile/"resident"/("math_"+profile+"_game_math.prg")
        for api in OPS:
            rows.append({"api":api,"variant":"resident:"+profile,
                "placement":"resident-native",
                "source_prg_sha256":hashlib.sha256(prg.read_bytes()).hexdigest(),
                "reu_sha256":hashlib.sha256(REU[profile].read_bytes()).hexdigest()
                   if profile in REU else None,
                **measure(cpu,apis[api],0xc000,pairs,api)})
    index=math_builder.operation_index()
    plan=math_builder.create_plan(index,
        ["SDIV32_32","SMOD32_32"],objective="size",
        zp_budget=0,ram_budget=453)
    for code,io in placements:
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)
            manifest=linker.build(plan,path,memory={
                "code_base":code,"math_io":io,"scratch_base":io+0x40})
            assert len(manifest["link_order"])==1
            assert manifest["resource_use"]["main_ram_total_bytes"]==453
            assert manifest["resource_use"]["zero_page_bytes"]==0
            prg=(path/"math_selective.prg").read_bytes()
            assert prg[:2]==code.to_bytes(2,"little")
            cpu=CPU(bytearray(65536))
            cpu.mem[code:code+len(prg)-2]=prg[2:]
            entries={op["api"]:int(op["entry"][1:],16)
                     for op in manifest["operations"]}
            assert len(set(entries.values()))==1
            for api in OPS:
                rows.append({"api":api,"variant":"link:portable-zerozp",
                    "placement":f"0x{code:04X}/0x{io:04X}",
                    "linked_sha256":hashlib.sha256(prg).hexdigest(),
                    **measure(cpu,entries[api],io,pairs,api)})
    return {"status":"PASS","cases":count,"corpus_sha256":digest,
            "qualification":"Research triage only, not source import or speed-selector parity",
            "measurement_basis":"Mini6502 public entry-through-RTS",
            "limits":"Historical resident placement differs from linked source; no PAL/IRQ/REU transport timing",
            "measurements":rows}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--cases",type=int,default=192)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    result=collect(args.cases)
    for api in OPS:
        rows=sorted((r for r in result["measurements"] if r["api"]==api),
                    key=lambda r:r["mean_cycles"])
        print("SIGNED3232 DONOR TRIAGE",api,
            json.dumps([(r["variant"],r["placement"],r["mean_cycles"],
                         r["max_cycles"]) for r in rows]),flush=True)
    print("SIGNED3232 CORPUS",result["corpus_sha256"],flush=True)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
