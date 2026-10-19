#!/usr/bin/env python3
"""Identical public-call full Q32/R16/C benchmark for UMULDIV16 Pareto."""
from __future__ import annotations
import hashlib
import random
from pathlib import Path
from mini6502 import Assembler,CPU,load_sparse

import selective_linker as linker
import selective_umuldiv16_qs_v2 as producer

FAST="link:qs-v2-fused"
SMALL="link:portable-zerozp"
BASIS="umuldiv16-canonical-qs-v2-public512-v1"
COUNT=512
RESOURCES={FAST:(3655,12,4),SMALL:(288,0,6)}
EDGE=(0,1,2,3,7,15,255,256,257,1023,32767,32768,
      32769,65534,65535)


def corpus():
    rng=random.Random(0xC6416D17)
    vals=[]
    for x in EDGE:
        for y in (0,1,7,255,256,32768,65535):
            for d in (0,1,2,257,65535):
                vals.append((x,y,d))
    vals=vals[:320]
    vals.extend((rng.randrange(65536),rng.randrange(65536),
                 rng.randrange(65536)) for _ in range(COUNT-len(vals)))
    assert len(vals)==COUNT
    return vals


def oracle(x,y,d):
    product=x*y
    if d==0:return product,0,0,1
    return product,product//d,product%d,0


def bench_umuldiv16(modules,code,io,scratch,root:Path,zp=0x50):
    if set(modules)!=set(RESOURCES):
        raise ValueError("Compound UMULDIV16 candidate set changed")
    cases=corpus()
    digest=hashlib.sha256(b"".join(
        x.to_bytes(2,"little")+y.to_bytes(2,"little")+d.to_bytes(2,"little")
        for x,y,d in cases)).hexdigest()
    mean,maximum,p95,hashes={},{},{},{}
    for variant,mod in sorted(modules.items()):
        resources=(sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])
        if resources!=RESOURCES[variant] or bool(mod.get("umuldiv16_qsv2"))!=(variant==FAST):
            raise ValueError("Compound UMULDIV16 source resource contract changed")
        if variant==FAST:
            image,labels,_,_=producer.assemble_image(code,io,zp,scratch,root)
        else:
            bindings={
                "KERNEL_CODE":code,"INPUT_X":io,"INPUT_Y":io+4,
                "OUTPUT_Z":io+8,"INPUT_NUM":io+16,
                "INPUT_DIV":io+20,"OUTPUT_QUOT":io+24,
                "OUTPUT_REM":io+28,"TEMP_RAM":scratch
            }
            image,labels,_=Assembler().assemble(
                linker.relocate_source(mod,bindings,root))
        entry=labels[mod["entry"]]
        cpu=CPU(load_sparse(image))
        sp=cpu.sp
        timings=[]
        for k,(x,y,d) in enumerate(cases):
            xb=x.to_bytes(2,"little")+bytes((0xa5,0x5a))
            yb=y.to_bytes(2,"little")+bytes((0x6b,0x7c))
            db=d.to_bytes(2,"little")+bytes((0xe1,0xe2))
            cpu.mem[io:io+4]=xb
            cpu.mem[io+4:io+8]=yb
            cpu.mem[io+8:io+12]=bytes((0x88,))*4
            cpu.mem[io+16:io+20]=bytes((0x77,))*4
            cpu.mem[io+20:io+24]=db
            cpu.mem[io+24:io+28]=bytes((0x99,))*4
            cpu.mem[io+28:io+32]=bytes((0x21,0x43,0x65,0x87))
            cpu.a=(x+k)&255
            cpu.x=(y+k)&255
            cpu.y=(d+k)&255
            cpu.c=(x+y+d+k)&1
            cpu.d=0
            ticks=cpu.call(entry,80000)
            product,q,rem,carry=oracle(x,y,d)
            got=(int.from_bytes(cpu.mem[io+8:io+12],"little"),
                 int.from_bytes(cpu.mem[io+16:io+20],"little"),
                 int.from_bytes(cpu.mem[io+24:io+28],"little"),
                 int.from_bytes(cpu.mem[io+28:io+30],"little"),
                 cpu.c)
            want=(product,product,q,rem,carry)
            if (got!=want or cpu.sp!=sp or
                bytes(cpu.mem[io:io+4])!=xb or
                bytes(cpu.mem[io+4:io+8])!=yb or
                bytes(cpu.mem[io+20:io+24])!=db or
                bytes(cpu.mem[io+30:io+32])!=bytes((0x65,0x87))):
                raise ValueError("UMULDIV16 public ABI mismatch "+
                    repr((variant,hex(code),x,y,d,got,want)))
            timings.append(ticks)
        if variant==FAST and any(cpu.mem[p]!=v for p,v in image.items()):
            raise ValueError("UMULDIV16 canonical fused executable image modified")
        mean[variant]=sum(timings)/len(timings)
        maximum[variant]=max(timings)
        p95[variant]=sorted(timings)[int(COUNT*.95)-1]
        hashes[variant]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS,"cases":COUNT,"cpu_model_only":True,
        "corpus_sha256":digest,"mean_cycles":mean,
        "maximum_cycles":maximum,"p95_cycles":p95,
        "source_sha256":hashes,"code_origin":"$%04X"%code,
        "io_origin":"$%04X"%io,
        "note":"Complete signed-free X16*Y16/D16 public Q32/R16/C calls, NOT resident V2 division timing"}
