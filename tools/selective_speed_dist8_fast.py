#!/usr/bin/env python3
"""Exact V1 stock-C64 DIST8_FAST full-public source-cycle qualification.

The 61-byte canonical max(abs(x),abs(y))+floor(min/2) source is already
linked, correct and natively proven. Authenticate its speed under 512
identical signed8 operand pairs; do not install a slower alternative or
compare incompatible resident-only cycle tables.
"""
from __future__ import annotations
import hashlib
import random
from pathlib import Path
from mini6502 import Assembler,CPU,load_sparse
import selective_linker as linker

ID="link:resident-approx"
BASIS="v1-dist8-fast-exact-512-full-public-v1"
COUNT=512
EDGE=(0,1,2,3,7,15,16,17,31,32,63,64,127,128,129,254,255)


def corpus():
    pairs=[(x,y) for x in EDGE for y in EDGE]
    rng=random.Random(0xD1578FA)
    pairs.extend((rng.randrange(256),rng.randrange(256))
                 for _ in range(COUNT-len(pairs)))
    assert len(pairs)==COUNT
    return pairs


def reference(x,y):
    ax=abs(x if x<128 else x-256)
    ay=abs(y if y<128 else y-256)
    return (max(ax,ay)+(min(ax,ay)//2))&255


def bench_dist8_fast(modules,code,io,scratch,root:Path):
    if set(modules)!={ID}:
        raise ValueError("DIST8_FAST original source variant changed")
    mod=modules[ID]
    if (mod["source"]!="routines/game/dist8_fast.asm"
        or mod["segments"]!=(("KERNEL_CODE",61),)
        or mod["entry"]!="FAST_DIST8_FAST"
        or mod["zp"]!=0 or mod["scratch"]!=2
        or not mod.get("dist8")
        or mod.get("requires_reu") or mod.get("requires_writable_code")):
        raise ValueError("DIST8_FAST original source/resource drift")
    locations={"KERNEL_CODE":code,"INPUT_X":io,"INPUT_Y":io+4,
               "OUTPUT_Z":io+8,"TEMP_RAM":scratch}
    image,labels,_=Assembler().assemble(
        linker.relocate_source(mod,locations,root))
    if (labels[mod["entry"]]!=code
        or set(image)!=set(range(code,code+61))):
        raise ValueError("DIST8_FAST original 61-byte geometry changed")
    cpu=CPU(load_sparse(image))
    before=bytes(cpu.mem[code:code+61])
    sp=cpu.sp
    cases=corpus()
    times=[]
    for k,(x,y) in enumerate(cases):
        cpu.mem[io:io+4]=bytes((x,0xa5,0x5a,0x67))
        cpu.mem[io+4:io+8]=bytes((y,0x6b,0x7c,0x8d))
        cpu.mem[io+8:io+12]=bytes((0x42,0x43,0x44,0x45))
        cpu.a=(x+k)&255
        cpu.x=(y+k)&255
        cpu.y=(x^y^k)&255
        cpu.c=(x+y+k)&1
        cpu.d=0
        ticks=cpu.call(code,3000)
        if (cpu.mem[io+8]!=reference(x,y)
            or bytes(cpu.mem[io+9:io+12])!=bytes((0x43,0x44,0x45))
            or bytes(cpu.mem[io:io+4])!=bytes((x,0xa5,0x5a,0x67))
            or bytes(cpu.mem[io+4:io+8])!=bytes((y,0x6b,0x7c,0x8d))
            or cpu.c!=0 or cpu.sp!=sp):
            raise ValueError("DIST8_FAST original public ABI mismatch "+repr((x,y)))
        times.append(ticks)
    if bytes(cpu.mem[code:code+61])!=before:
        raise ValueError("Historical V1 DIST8_FAST executable bytes changed")
    return {"basis":BASIS,"cases":COUNT,"cpu_model_only":True,
      "mean_cycles":{ID:sum(times)/COUNT},
      "maximum_cycles":{ID:max(times)},
      "p95_cycles":{ID:sorted(times)[int(COUNT*.95)-1]},
      "corpus_sha256":hashlib.sha256(
        bytes(v for x,y in cases for v in (x,y))).hexdigest(),
      "source_sha256":{ID:hashlib.sha256(
        (root/mod["source"]).read_bytes()).hexdigest()},
      "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
      "note":"Original V1 61-byte signed8 approximate distance; complete 6502 source public cycles, not physical PAL timing"}


if __name__=="__main__":
    import selective_linker
    for origin,io,scratch in ((0x8000,0xc000,0xc040),
                              (0x7123,0xc040,0xc080)):
        z=bench_dist8_fast(selective_linker.MODULES["MATH_DIST8_FAST"],
                           origin,io,scratch,Path(__file__).resolve().parents[1])
        print("V1 DIST8_FAST PUBLIC",hex(origin),
              z["mean_cycles"],z["maximum_cycles"],flush=True)
