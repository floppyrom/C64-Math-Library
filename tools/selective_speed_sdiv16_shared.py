#!/usr/bin/env python3
"""Matched source-and-ABI performance for historical V2 signed Q/R shared16."""
from __future__ import annotations
import hashlib
import random
from pathlib import Path
from mini6502 import Assembler, CPU, load_sparse
import selective_v2_signed16_shared as fast

FAST="link:v2-signed-shared"
SMALL="link:portable-zerozp"
COUNT=384
EDGE=(0,1,2,3,7,15,127,128,255,256,257,1023,32767,32768,32769,65534,65535)
SPEC={FAST:(1705,0,8),SMALL:(206,0,3)}
ROOT=Path(__file__).resolve().parents[1]


def corpus():
    rng=random.Random(0x5D1616B2)
    pairs=[(n,d) for n in EDGE for d in EDGE]
    pairs.extend((rng.randrange(65536),rng.randrange(65536))
                 for _ in range(COUNT-len(pairs)))
    assert len(pairs)==COUNT
    return pairs


def signed(v):
    return v-65536 if v&0x8000 else v


def oracle(n,d):
    a,b=signed(n),signed(d)
    if b==0:return 0,0,1
    q=abs(a)//abs(b)
    if (a<0)!=(b<0):q=-q
    rem=a-q*b
    return q&65535,rem&65535,0


def bench_sdiv16(modules,code,io,scratch,root:Path=ROOT):
    if set(modules)!=set(SPEC):
        raise ValueError("Signed16 source set changed, requalify")
    import selective_linker as linker
    cases=corpus()
    digest=hashlib.sha256(b"".join(
        n.to_bytes(2,"little")+d.to_bytes(2,"little")
        for n,d in cases)).hexdigest()
    means,maxima,p95s,sources={},{},{},{}
    for ident,mod in sorted(modules.items()):
        if (sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])!=SPEC[ident]:
            raise ValueError("Signed16 shared resources changed "+ident)
        if bool(mod.get("signed16_v2_shared"))!=(ident==FAST):
            raise ValueError("Historical V2 signed source identity changed")
        if ident==FAST:
            image,labels,_,_=fast.assemble_image(code,io,scratch,root)
        else:
            bindings={"KERNEL_CODE":code,
              "INPUT_NUM":io+16,"INPUT_DIV":io+20,
              "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,
              "TEMP_RAM":scratch}
            image,labels,_=Assembler().assemble(linker.relocate_source(
                mod,bindings,root))
        entry=labels[mod["entry"]]
        cpu=CPU(load_sparse(image))
        sp=cpu.sp
        ticks=[]
        for i,(n,d) in enumerate(cases):
            nb=n.to_bytes(2,"little")+bytes((0x5a,0xa5))
            db=d.to_bytes(2,"little")+bytes((0x7c,0x6b))
            cpu.mem[io+16:io+20]=nb
            cpu.mem[io+20:io+24]=db
            cpu.mem[io+24:io+28]=bytes((0x55,0x44,0x33,0x22))
            cpu.mem[io+28:io+32]=bytes((0x99,0x88,0x77,0x66))
            cpu.a=(n+i)&255
            cpu.x=(d^i)&255
            cpu.y=(n^d^i)&255
            cpu.c=(n+d+i)&1
            cpu.d=0
            ticks.append(cpu.call(entry,40000))
            actual=(int.from_bytes(cpu.mem[io+24:io+26],"little"),
                    int.from_bytes(cpu.mem[io+28:io+30],"little"),cpu.c)
            if (actual!=oracle(n,d) or cpu.sp!=sp
                or bytes(cpu.mem[io+16:io+20])!=nb
                or bytes(cpu.mem[io+20:io+24])!=db
                or bytes(cpu.mem[io+26:io+28])!=bytes((0x33,0x22))
                or bytes(cpu.mem[io+30:io+32])!=bytes((0x77,0x66))):
                raise ValueError("Signed16 Q/R/C/input/SP mismatch "+
                                 repr((ident,code,n,d,actual,oracle(n,d))))
        if any(cpu.mem[a]!=value for a,value in image.items()):
            raise ValueError("Historical V2 signed code was modified")
        means[ident]=sum(ticks)/len(ticks)
        maxima[ident]=max(ticks)
        p95s[ident]=sorted(ticks)[int(len(ticks)*.95)-1]
        sources[ident]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":"signed16-qr-v2-historical-public384-v1","cases":COUNT,
        "mean_cycles":means,"maximum_cycles":maxima,"p95_cycles":p95s,
        "corpus_sha256":digest,"cpu_model_only":True,
        "source_sha256":sources,
        "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
        "note":"Identical full public signed Q16/R16/C calls, not historical native-resident timings"}
