#!/usr/bin/env python3
"""Matched complete signed Q8.8 16x16>>8 quarter-square speed model."""
from __future__ import annotations
import hashlib
import random
from pathlib import Path
from mini6502 import Assembler,CPU,load_sparse

import selective_linker as linker
import selective_smul16_shr8_quartersquare as fast
import selective_speed_smul16 as base

FAST="link:qs-signed-shr8-public"
SMALL="link:compact-zerozp"
BASIS="smul16-shr8-exact-public512-qs-v1"
COUNT=512
RESOURCES={FAST:(1383,0,4),SMALL:(184,0,6)}


def corpus():
    return base.corpus()


def oracle(x,y):
    return ((base.signed(x)*base.signed(y))>>8)&0xffffff


def bench_smul16_shr8(modules,code,io,scratch,root:Path):
    if set(modules)!=set(RESOURCES):
        raise ValueError("SMUL16_SHR8 candidates changed: requalify")
    cases=corpus()
    digest=hashlib.sha256(b"".join(x.to_bytes(2,"little")+
            y.to_bytes(2,"little") for x,y in cases)).hexdigest()
    means,maximum,p95,sourcehash={},{},{},{}
    for variant,mod in sorted(modules.items()):
        sizes=(sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])
        if sizes!=RESOURCES[variant] or bool(mod.get("smul16_shr8_qs"))!=(variant==FAST):
            raise ValueError("SMUL16_SHR8 source resource mismatch")
        if variant==FAST:
            image,labels,_,_=fast.assemble_image(code,io,scratch,root)
        else:
            bindings={"KERNEL_CODE":code,"INPUT_X":io,
                "INPUT_Y":io+4,"OUTPUT_Z":io+8,"TEMP_RAM":scratch}
            image,labels,_=Assembler().assemble(
                linker.relocate_source(mod,bindings,root))
        entry=labels[mod["entry"]]
        cpu=CPU(load_sparse(image))
        sp=cpu.sp
        times=[]
        for i,(x,y) in enumerate(cases):
            xb=x.to_bytes(2,"little")+bytes((0xa5,0x5a))
            yb=y.to_bytes(2,"little")+bytes((0x6b,0x7c))
            cpu.mem[io:io+4]=xb
            cpu.mem[io+4:io+8]=yb
            cpu.mem[io+8:io+16]=bytes((0x99,0x88,0x77,0x66,0xdd,0xdd,0xdd,0xdd))
            cpu.a=(x+i)&255
            cpu.x=(y+i)&255
            cpu.y=(x^y^i)&255
            cpu.c=(x+y+i)&1
            cpu.d=0
            ticks=cpu.call(entry,60000)
            value=int.from_bytes(cpu.mem[io+8:io+11],"little")
            if (value!=oracle(x,y) or cpu.c!=0 or cpu.sp!=sp
                or bytes(cpu.mem[io:io+4])!=xb
                or bytes(cpu.mem[io+4:io+8])!=yb
                or bytes(cpu.mem[io+12:io+16])!=bytes((0xdd,))*4):
                raise ValueError("SMUL16_SHR8 ABI mismatch "+
                       repr((variant,code,x,y,value,oracle(x,y))))
            times.append(ticks)
        if any(cpu.mem[a]!=byte for a,byte in image.items()):
            raise ValueError("SMUL16_SHR8 unexpectedly changed executable image")
        means[variant]=sum(times)/len(times)
        maximum[variant]=max(times)
        p95[variant]=sorted(times)[int(len(times)*.95)-1]
        sourcehash[variant]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS,"cases":COUNT,"cpu_model_only":True,
        "corpus_sha256":digest,"mean_cycles":means,
        "maximum_cycles":maximum,"p95_cycles":p95,
        "source_sha256":sourcehash,"code_origin":"$%04X"%code,
        "io_origin":"$%04X"%io,
        "note":"Full signed shifted Q24 public-call timing, not resident profile timing"}
