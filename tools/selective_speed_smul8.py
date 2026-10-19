#!/usr/bin/env python3
"""Same-corpus historical SMC vs read-only quarter-square signed8 speed model.

This measures *full public calls*, including source-linked independent
V1 table setup and signed8 corrected QS call. It never compares old
resident-only cycles with new wrapped calls and never treats CPU-model
cycles as physical VIC/IRQ/PAL timing.

Each candidate is assembled through the actual operation-first linker
under an explicit pin and objective=size; the outer speed selector
therefore does not recursively call this benchmark.
"""
from __future__ import annotations
import hashlib
import random
import tempfile
from pathlib import Path
from mini6502 import CPU

OLD="link:v1-resident-smc"
NEW="link:qs-readonly"
BASIS="smul8-source-linked-public512-smc-vs-readonly-qs-v1"
CASES=512
EXPECTED=frozenset((OLD,NEW))
EDGES=(0,1,2,3,15,16,17,63,64,127,128,129,254,255)


def corpus():
    result=[(x,y) for x in EDGES for y in EDGES]
    rng=random.Random(0x5A6438)
    result.extend((rng.randrange(256),rng.randrange(256))
                  for _ in range(CASES-len(result)))
    assert len(result)==CASES
    return result


def bench_smul8(modules,code,io,scratch,root:Path):
    import math_builder
    import selective_linker as linker
    if set(modules)!=EXPECTED:
        raise ValueError("SMUL8 authenticated Pareto source set changed")
    data=corpus()
    digest=hashlib.sha256(bytes(z for x,y in data for z in (x,y))).hexdigest()
    means,maximum,p95,hashes={},{},{},{}
    index=math_builder.operation_index()
    for variant,mod in sorted(modules.items()):
        historical=variant==OLD
        if (mod["zp"]!=0 or
            mod["scratch"]!=(0 if historical else 2) or
            bool(mod.get("smul8_v1"))!=historical or
            bool(mod.get("smul8_qs"))==historical):
            raise ValueError("SMUL8 canonical resource flags changed")
        ram=2336 if historical else 1193
        plan=math_builder.create_plan(index,["SMUL8"],
              objective="size",pins={"SMUL8":variant},
              ram_budget=ram,zp_budget=0)
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            man=linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,
                "scratch_base":scratch},root=root)
            if (man["operations"][0]["variant"]!=variant or
                man["resource_use"]["main_ram_total_bytes"]>ram or
                man["resource_use"]["zero_page_bytes"]!=0):
                raise ValueError("SMUL8 public resource contract changed")
            prg=(folder/"math_selective.prg").read_bytes()
            load=int.from_bytes(prg[:2],"little")
            if load!=code:
                raise ValueError("SMUL8 unexpected code origin")
            mem=bytearray(65536)
            mem[load:load+len(prg)-2]=prg[2:]
            cpu=CPU(mem)
            sp=cpu.sp
            entry=int(man["operations"][0]["entry"][1:],16)
            ticks=[]
            for k,(x,y) in enumerate(data):
                mem[io]=x
                mem[io+1]=0xa5
                mem[io+4]=y
                mem[io+5]=0x5a
                mem[io+8:io+12]=bytes((0xcc,0xdd,0x42,0x43))
                cpu.a=(x+y+k)&255
                cpu.x=(x^y^k)&255
                cpu.y=(x+k)&255
                cpu.c=(y+k)&1
                cpu.d=0
                cycles=cpu.call(entry,5000)
                sx=x-(256 if x&128 else 0)
                sy=y-(256 if y&128 else 0)
                if (int.from_bytes(mem[io+8:io+10],"little") != ((sx*sy)&65535)
                    or cpu.c!=0 or cpu.sp!=sp or
                    (mem[io],mem[io+1],mem[io+4],mem[io+5])!=(x,0xa5,y,0x5a)
                    or mem[io+10:io+12]!=bytes((0x42,0x43))):
                    raise ValueError("SMUL8 full-public ABI mismatch "+repr((variant,x,y)))
                ticks.append(cycles)
            means[variant]=sum(ticks)/len(ticks)
            maximum[variant]=max(ticks)
            p95[variant]=sorted(ticks)[int(CASES*.95)-1]
            hashes[variant]=hashlib.sha256(
                (root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS,"cases":CASES,
            "corpus_sha256":digest,"cpu_model_only":True,
            "mean_cycles":means,"maximum_cycles":maximum,
            "p95_cycles":p95,"source_sha256":hashes,
            "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
            "note":"Two source-linked and same-input public signed16 returns; native PAL frame timing not claimed"}
