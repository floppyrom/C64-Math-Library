#!/usr/bin/env python3
"""Authentic historical V1–V5 shared signed8 Q/R full-public CPU-model speed.

Both SDIV8 and SMOD8 map to *the same* 530-byte V1 source-linked producer.
The speed objective previously failed closed because no per-call cycle
provenance was registered, despite exhaustive correctness/native qualification.

This module does not introduce or prefer any slower new kernel. It times
identical signed N8/D8 pairs for the original source at each requested
relocation and 1-ZP layout, checking Q/R/C, high-byte sentinels, operands,
stack and immutable code. CPU-model cycles are not PAL/VIC-II timing.
"""
from __future__ import annotations
import hashlib
import random
from pathlib import Path
from mini6502 import Assembler,CPU,load_sparse
import selective_linker as linker

VARIANT="link:v1-shared-producer"
OPS=("MATH_SDIV8","MATH_SMOD8")
COUNT=512
BASIS="v1-v5-shared-sdiv8-smod8-public-512-v1"
EDGES=(0,1,2,3,7,15,16,17,31,32,63,64,127,128,129,254,255)


def corpus():
    cases=[(n,d) for n in EDGES for d in EDGES]
    rng=random.Random(0x5D1808C6)
    cases.extend((rng.randrange(256),rng.choice((0,1,2,3,7,15,16,31,32,64,128,255)))
                 for _ in range(128))
    cases.extend((rng.randrange(256),rng.randrange(256))
                 for _ in range(COUNT-len(cases)))
    if len(cases)!=COUNT:
        raise ValueError("Shared signed8 corpus size drift")
    return cases


def oracle(n,d):
    a=n if n<128 else n-256
    b=d if d<128 else d-256
    if b==0: return 0,0,1
    q=abs(a)//abs(b)
    if (a<0)!=(b<0): q=-q
    return q&255,(a-q*b)&255,0


def bench(api,modules,code,io,zp,root:Path):
    if api not in OPS or set(modules)!={VARIANT}:
        raise ValueError("V1 signed8 source set changed")
    mod=modules[VARIANT]
    if (mod["source"]!="routines/divide/sdiv8_v1_resident.asm"
        or mod["segments"]!=(("KERNEL_CODE",530),)
        or mod["entry"]!="FAST_SDIV8_V1"
        or mod["zp"]!=1 or mod["scratch"]!=0
        or not mod.get("sdiv8_v1")
        or mod.get("share_producer")!="v1-signed-division8"):
        raise ValueError("V1 shared signed8 source/resource ABI drift")
    locations={"KERNEL_CODE":code,"INPUT_NUM":io+16,
               "INPUT_DIV":io+20,"OUTPUT_QUOT":io+24,
               "OUTPUT_REM":io+28,"TEMP_ZP":zp}
    image,labels,_=Assembler().assemble(linker.relocate_source(
        mod,locations,root))
    entry=labels[mod["entry"]]
    if entry!=code+8 or set(image)!=set(range(code,code+530)):
        raise ValueError("Historical signed8 source geometry drift")
    cpu=CPU(load_sparse(image))
    stack=cpu.sp
    pristine=bytes(cpu.mem[code:code+530])
    cases=corpus()
    digest=hashlib.sha256(bytes(v for n,d in cases for v in (n,d))).hexdigest()
    ticks=[]
    for i,(n,d) in enumerate(cases):
        nb=bytes((n,0xa5,0x5a,0x67))
        db=bytes((d,0x6b,0x7c,0x8d))
        cpu.mem[io+16:io+20]=nb
        cpu.mem[io+20:io+24]=db
        cpu.mem[io+24:io+28]=bytes((0x51,0x52,0x53,0x54))
        cpu.mem[io+28:io+32]=bytes((0x61,0x62,0x63,0x64))
        cpu.a=(n+i)&255;cpu.x=(d+i)&255;cpu.y=(n^d^i)&255
        cpu.c=(n+d+i)&1;cpu.d=0
        ticks.append(cpu.call(entry,50000))
        result=(cpu.mem[io+24],cpu.mem[io+28],cpu.c)
        if (result!=oracle(n,d) or cpu.sp!=stack
            or bytes(cpu.mem[io+16:io+20])!=nb
            or bytes(cpu.mem[io+20:io+24])!=db
            or bytes(cpu.mem[io+25:io+28])!=bytes((0x52,0x53,0x54))
            or bytes(cpu.mem[io+29:io+32])!=bytes((0x62,0x63,0x64))):
            raise ValueError("V1 signed8 full public ABI mismatch "+
                             repr((api,code,n,d,result,oracle(n,d))))
    if bytes(cpu.mem[code:code+530])!=pristine:
        raise ValueError("Historical V1 signed8 source modified executable code")
    return {
      "basis":BASIS,"cases":COUNT,"cpu_model_only":True,
      "mean_cycles":{VARIANT:sum(ticks)/COUNT},
      "maximum_cycles":{VARIANT:max(ticks)},
      "p95_cycles":{VARIANT:sorted(ticks)[int(COUNT*.95)-1]},
      "corpus_sha256":digest,
      "source_sha256":{VARIANT:hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()},
      "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
      "zp_origin":"$%02X"%zp,"operation":api,
      "note":"Complete public signed Q8/R8/C original shared V1–V5 producer; not hardware PAL/IRQ timing"
    }


def bench_sdiv8(modules,code,io,zp,root):
    return bench("MATH_SDIV8",modules,code,io,zp,root)


def bench_smod8(modules,code,io,zp,root):
    return bench("MATH_SMOD8",modules,code,io,zp,root)
