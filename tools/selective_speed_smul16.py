#!/usr/bin/env python3
"""Same-input full public signed 16x16->32 CPU-model speed qualification."""
from __future__ import annotations

import hashlib
import random
from pathlib import Path

from mini6502 import Assembler, CPU, load_sparse
import selective_smul16_quartersquare as qs
import selective_linker as linker

FAST="link:qs-signed-public"
SMALL="link:compact-zerozp"
BASIS="smul16-quarter-square-signed-public512-v1"
SIZES={FAST:(1351,0,4), SMALL:(161,0,6)}
COUNT=512
EDGE=(0,1,2,3,7,15,127,128,255,256,257,1023,
      16384,32767,32768,32769,65534,65535,0x8001,0xff00)


def corpus():
    rng=random.Random(0x5C6416A2)
    result=[(x,y) for x in EDGE for y in EDGE]
    result.extend((rng.randrange(65536),rng.randrange(65536))
                  for _ in range(COUNT-len(result)))
    assert len(result)==COUNT
    return result


def signed(n):
    return n-65536 if n&0x8000 else n


def bench_smul16(modules,code,io,scratch,root:Path):
    if set(modules)!=set(SIZES):
        raise ValueError("SMUL16 candidate set changed: requalify")
    cases=corpus()
    digest=hashlib.sha256(b"".join(
        x.to_bytes(2,"little")+y.to_bytes(2,"little")
        for x,y in cases)).hexdigest()
    mean,maximum,p95,source_sha={},{},{},{}
    for variant,mod in sorted(modules.items()):
        resources=(sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])
        if resources!=SIZES[variant] or bool(mod.get("smul16_qs"))!=(variant==FAST):
            raise ValueError("SMUL16 certified resource contract changed")
        if variant==FAST:
            image,labels,_,_=qs.assemble_image(code,io,scratch,root)
        else:
            bindings={
              "KERNEL_CODE":code,"INPUT_X":io,"INPUT_Y":io+4,
              "OUTPUT_Z":io+8,"TEMP_RAM":scratch
            }
            image,labels,_=Assembler().assemble(
                linker.relocate_source(mod,bindings,root))
        entry=labels[mod["entry"]]
        cpu=CPU(load_sparse(image))
        sp=cpu.sp
        times=[]
        for k,(x,y) in enumerate(cases):
            xb=x.to_bytes(2,"little")+bytes((0xa5,0x5a))
            yb=y.to_bytes(2,"little")+bytes((0x6b,0x7c))
            cpu.mem[io:io+4]=xb
            cpu.mem[io+4:io+8]=yb
            cpu.mem[io+8:io+16]=bytes((0x99,0x88,0x77,0x66,0xdd,0xdd,0xdd,0xdd))
            cpu.a=(x+k)&255
            cpu.x=(y+k)&255
            cpu.y=(x^y^k)&255
            cpu.c=(x+y+k)&1
            cpu.d=0
            cycles=cpu.call(entry,60000)
            product=int.from_bytes(cpu.mem[io+8:io+12],"little")
            expected=(signed(x)*signed(y))&0xffffffff
            if (product!=expected or cpu.c!=0 or cpu.sp!=sp
                or bytes(cpu.mem[io:io+4])!=xb
                or bytes(cpu.mem[io+4:io+8])!=yb
                or bytes(cpu.mem[io+12:io+16])!=bytes((0xdd,))*4):
                raise ValueError("SMUL16 public ABI mismatch: "+repr((variant,x,y,product,expected)))
            times.append(cycles)
        if any(cpu.mem[a]!=v for a,v in image.items()):
            raise ValueError("SMUL16 signed source unexpectedly writes executable image")
        mean[variant]=sum(times)/len(times)
        maximum[variant]=max(times)
        p95[variant]=sorted(times)[int(len(times)*.95)-1]
        source_sha[variant]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS,"cases":COUNT,
      "mean_cycles":mean,"maximum_cycles":maximum,"p95_cycles":p95,
      "cpu_model_only":True,"corpus_sha256":digest,
      "source_sha256":source_sha,
      "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
      "note":"Matched complete signed public calls, not resident 16x16 instruction timings"}
