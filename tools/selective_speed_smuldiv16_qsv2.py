#!/usr/bin/env python3
"""Matched complete public signed X16*Y16/D16 source-model speed frontier."""
from __future__ import annotations

import hashlib
import random
from pathlib import Path
from mini6502 import Assembler,CPU,load_sparse
import selective_linker as linker
import selective_smuldiv16_qs_v2 as fast

FAST="link:signed-qs-v2-fused"
SMALL="link:portable-zerozp"
BASIS="smuldiv16-signedqs-v2-matched-public512-v1"
COUNT=512
RESOURCES={FAST:(4263,12,4),SMALL:(439,0,6)}
EDGE=(0,1,2,3,7,15,255,256,257,1023,32767,32768,
      32769,65534,65535)


def s16(n):
    return n-65536 if n&32768 else n


def corpus():
    rng=random.Random(0x5D164416)
    cases=[]
    for x in EDGE:
        for y in (0,1,7,255,256,32768,65535):
            for d in (0,1,2,257,65535):
                cases.append((x,y,d))
    cases=cases[:320]
    cases.extend((rng.randrange(65536),rng.randrange(65536),
                  rng.randrange(65536)) for _ in range(COUNT-len(cases)))
    assert len(cases)==COUNT
    return cases


def oracle(x,y,d):
    product=s16(x)*s16(y)
    signed_d=s16(d)
    if signed_d==0:
        return product&0xffffffff,0,0,1
    q=abs(product)//abs(signed_d)
    if (product<0)!=(signed_d<0):
        q=-q
    rem=product-q*signed_d
    return product&0xffffffff,q&0xffffffff,rem&0xffff,0


def bench_smuldiv16(modules,code,io,scratch,root:Path,zp=0x50):
    if set(modules)!=set(RESOURCES):
        raise ValueError("Signed compound candidate set changed")
    cases=corpus()
    digest=hashlib.sha256(b"".join(
        x.to_bytes(2,"little")+y.to_bytes(2,"little")+d.to_bytes(2,"little")
        for x,y,d in cases)).hexdigest()
    mean,maximum,p95,sourcehash={},{},{},{}
    for variant,mod in sorted(modules.items()):
        resources=(sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])
        if (resources!=RESOURCES[variant] or
                bool(mod.get("smuldiv16_qsv2"))!=(variant==FAST)):
            raise ValueError("SMULDIV16 source resource contract drifted")
        if variant==FAST:
            image,labels,_,_=fast.assemble_image(code,io,zp,scratch,root)
        else:
            bindings={"KERNEL_CODE":code,"INPUT_X":io,"INPUT_Y":io+4,
                "OUTPUT_Z":io+8,"INPUT_NUM":io+16,"INPUT_DIV":io+20,
                "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,"TEMP_RAM":scratch}
            image,labels,_=Assembler().assemble(
                linker.relocate_source(mod,bindings,root))
        entry=labels[mod["entry"]]
        cpu=CPU(load_sparse(image))
        sp=cpu.sp
        times=[]
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
            cycles=cpu.call(entry,100000)
            product,quot,rem,carry=oracle(x,y,d)
            got=(int.from_bytes(cpu.mem[io+8:io+12],"little"),
                 int.from_bytes(cpu.mem[io+16:io+20],"little"),
                 int.from_bytes(cpu.mem[io+24:io+28],"little"),
                 int.from_bytes(cpu.mem[io+28:io+30],"little"),cpu.c)
            expected=(product,product,quot,rem,carry)
            if (got!=expected or cpu.sp!=sp or
                    bytes(cpu.mem[io:io+4])!=xb or
                    bytes(cpu.mem[io+4:io+8])!=yb or
                    bytes(cpu.mem[io+20:io+24])!=db or
                    bytes(cpu.mem[io+30:io+32])!=bytes((0x65,0x87))):
                raise ValueError("Signed muldiv16 public mismatch "+
                    repr((variant,hex(code),x,y,d,got,expected)))
            times.append(cycles)
        if variant==FAST and any(cpu.mem[addr]!=v for addr,v in image.items()):
            raise ValueError("Signed compound modifies executable code")
        mean[variant]=sum(times)/COUNT
        maximum[variant]=max(times)
        p95[variant]=sorted(times)[int(COUNT*.95)-1]
        sourcehash[variant]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS,"cases":COUNT,"cpu_model_only":True,
        "corpus_sha256":digest,"mean_cycles":mean,
        "maximum_cycles":maximum,"p95_cycles":p95,
        "source_sha256":sourcehash,"code_origin":"$%04X"%code,
        "io_origin":"$%04X"%io,
        "note":"Full signed X16*Y16/D16 Q32/R16/C public-call cycles, not resident V2 kernel timing"}
