#!/usr/bin/env python3
"""Matched full-public-call signed shifted16 Pareto performance model.

Compares historical V2 unsigned 32/16 magnitude producer + signed 16<<8
adapter to original portable signed 24-step restoring kernel on identical
numerator/divisor pairs and complete public Q24/R16/C calls. CPU model only.
"""
from __future__ import annotations
import hashlib
import random
from pathlib import Path

from mini6502 import Assembler,CPU,load_sparse
import selective_v2_signed_shifted16 as fast
import selective_linker as linker

FAST="link:v2-signed-shifted-public"
SMALL="link:portable-zerozp"
BASIS="sdiv16-shl8-v2-signed-matched-public384-v1"
EDGE=(0,1,2,3,7,15,127,255,256,257,32767,32768,32769,65534,65535)
COUNT=384
SPEC={FAST:(2624,12,0),SMALL:(237,0,3)}


def corpus():
    pairs=[(n,d) for n in EDGE for d in EDGE]
    rng=random.Random(0x5D1688A2)
    pairs.extend((rng.randrange(65536),rng.randrange(65536))
                 for _ in range(COUNT-len(pairs)))
    assert len(pairs)==COUNT
    return pairs


def s16(v):
    return v-(1<<16) if v&32768 else v


def oracle(n,d):
    n=s16(n)<<8
    d=s16(d)
    if d==0:return 0,0,1
    q=abs(n)//abs(d)
    if (n<0)!=(d<0):q=-q
    rem=n-q*d
    return q&0xffffff,rem&0xffff,0


def bench_sdiv16_shl8(modules,code,io,scratch,root:Path,zp=0x50):
    if set(modules)!=set(SPEC):
        raise ValueError("Signed shifted16 source set changed; requalify")
    pairs=corpus()
    digest=hashlib.sha256(b"".join(
        n.to_bytes(2,"little")+d.to_bytes(2,"little")
        for n,d in pairs)).hexdigest()
    means,maxima,p95s,source_hashes={},{},{},{}
    for variant,mod in sorted(modules.items()):
        expected=(sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])
        if (expected!=SPEC[variant] or
           bool(mod.get("v2_signed_shifted16"))!=(variant==FAST)):
            raise ValueError("Signed shifted16 source/resource contract changed")
        if variant==FAST:
            image,labels,_,_=fast.assemble_image(code,io,zp,root)
        else:
            bindings={"KERNEL_CODE":code,
                      "INPUT_NUM":io+16,"INPUT_DIV":io+20,
                      "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,
                      "TEMP_RAM":scratch}
            image,labels,_=Assembler().assemble(
                linker.relocate_source(mod,bindings,root))
        entry=labels[mod["entry"]]
        cpu=CPU(load_sparse(image))
        sp=cpu.sp
        timings=[]
        for i,(n,d) in enumerate(pairs):
            nb=n.to_bytes(2,"little")+bytes((0xa5,0x5a))
            db=d.to_bytes(2,"little")+bytes((0x6b,0x7c))
            cpu.mem[io+16:io+20]=nb
            cpu.mem[io+20:io+24]=db
            cpu.mem[io+24:io+28]=bytes((0x42,0x43,0x44,0x45))
            cpu.mem[io+28:io+32]=bytes((0x51,0x52,0x53,0x54))
            cpu.a=(n+i)&255
            cpu.x=(d+i)&255
            cpu.y=(n^d^i)&255
            cpu.c=(n+d+i)&1
            cpu.d=0
            ticks=cpu.call(entry,65000)
            actual=(int.from_bytes(cpu.mem[io+24:io+27],"little"),
                    int.from_bytes(cpu.mem[io+28:io+30],"little"),cpu.c)
            if (actual!=oracle(n,d) or cpu.sp!=sp
                or cpu.mem[io+27]!=0x45
                or bytes(cpu.mem[io+30:io+32])!=bytes((0x53,0x54))
                or bytes(cpu.mem[io+16:io+20])!=nb
                or bytes(cpu.mem[io+20:io+24])!=db):
                raise ValueError("Signed shifted16 ABI mismatch "+
                    repr((variant,hex(code),n,d,actual,oracle(n,d))))
            timings.append(ticks)
        if any(cpu.mem[p]!=value for p,value in image.items()):
            raise ValueError("Signed shifted16 modifies executable image")
        means[variant]=sum(timings)/len(timings)
        maxima[variant]=max(timings)
        p95s[variant]=sorted(timings)[int(len(timings)*.95)-1]
        source_hashes[variant]=hashlib.sha256(
            (root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS,"cases":COUNT,"corpus_sha256":digest,
        "mean_cycles":means,"maximum_cycles":maxima,"p95_cycles":p95s,
        "source_sha256":source_hashes,
        "cpu_model_only":True,"code_origin":"$%04X"%code,
        "io_origin":"$%04X"%io,
        "note":"Identical full signed Q24/R16/C calls, not resident-profile timing"}
