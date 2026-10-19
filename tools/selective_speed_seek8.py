#!/usr/bin/env python3
"""Measured public-call CPU-model cycles for four ORIGINAL shared SEEK8 DDA entries.

The same canonical generated RAM-operand 651-byte source is retained and
assembled without instruction changes. A deterministic 256-case corpus
includes INIT and the three STEP entry semantics, eight sprite slots,
stationary/near/far targets, and speeds at exact public I/O addresses.

For STEP models, INIT establishes the correct durable per-slot state
before the measured STEP call. INIT setup cycles are NOT charged to STEP:
each caller operation has its own explicit workload frequency. This is
a CPU model, not actual PAL/VIC/IRQ frame execution timing.
"""
from __future__ import annotations
import hashlib
import random
from pathlib import Path
from mini6502 import CPU,load_sparse
import selective_seek8 as seek

BASIS="seek8-original-shared-dda-full-public256-v1"
COUNT=256
VARIANT="link:generated-dda"
API_NAMES={
    "MATH_SEEK8_INIT":"seek8_init",
    "MATH_SEEK8_STEP":"seek8_step",
    "MATH_SEEK8_STEP_INT":"seek8_step_int",
    "MATH_SEEK8_STEP1":"seek8_step1",
}


def corpus():
    rng=random.Random(0x5EE8DDA)
    edges=[0,1,2,3,7,15,63,64,127,128,192,254,255]
    cases=[]
    for slot in range(8):
        for i in range(8):
            sx=edges[(i+slot)%len(edges)]
            sy=edges[(i*3+slot)%len(edges)]
            tx=sx if i%4==0 else edges[(i*5+slot+1)%len(edges)]
            ty=sy if i%3==0 else edges[(i*7+slot+3)%len(edges)]
            speed=((0,1),(0,2),(0x80,1),(0x80,0x81))[i%4]
            cases.append((slot,sx,sy,tx,ty,*speed))
    while len(cases)<COUNT:
        slot=rng.randrange(8)
        sx=rng.randrange(256);sy=rng.randrange(256)
        tx=sx if len(cases)%11==0 else rng.randrange(256)
        ty=sy if len(cases)%13==0 else rng.randrange(256)
        speeds=((0,1),(0,2),(0x80,1),(0x80,0x81),(0xff,1))
        spl,sph=speeds[len(cases)%len(speeds)]
        cases.append((slot,sx,sy,tx,ty,spl,sph))
    assert len(cases)==COUNT
    return cases


def measured(api,modules,code,io,scratch,root:Path):
    if api not in API_NAMES or set(modules)!={VARIANT}:
        raise ValueError("SEEK8 speed source/API frontier changed; requalify")
    m=modules[VARIANT]
    if (m["entry"]!=API_NAMES[api] or m["zp"]!=0 or
        m["scratch"]!=19 or m["persistent_state"]!=160 or
        sum(n for _,n in m["segments"])!=651 or
        m.get("share_producer")!="seek8-dda" or not m.get("seek8")):
        raise ValueError("Historical shared SEEK8 source resource contract changed")
    state=(scratch+seek.INIT_SCRATCH_BYTES+7)&~7
    if state+seek.STATE_BYTES>65536:
        raise ValueError("SEEK8 speed-model state outside RAM")
    if set(range(state,state+seek.STATE_BYTES)) & set(range(code,code+seek.CODE_BYTES)):
        raise ValueError("SEEK8 speed-model state overlaps executable image")
    image,labels,_,end=seek.assemble(code,io,scratch,state,root)
    if end!=code+seek.CODE_BYTES or labels[m["entry"]] not in image:
        raise ValueError("SEEK8 measured export moved")
    cpu=CPU(load_sparse(image));sp=cpu.sp
    observations=[]
    cases=corpus()
    for index,(slot,sx,sy,tx,ty,spl,sph) in enumerate(cases):
        cpu.mem[state+slot]=sx
        cpu.mem[state+8+slot]=sy
        cpu.mem[io]=tx
        cpu.mem[io+4]=ty
        cpu.mem[io+16:io+18]=bytes((spl,sph))
        cpu.x=slot;cpu.d=0
        if api != "MATH_SEEK8_INIT":
            cpu.call(labels["seek8_init"],120000)
            if cpu.x!=slot:
                raise ValueError("SEEK8 setup violated slot ABI")
        cpu.a=(index+sx)&255
        cpu.y=(ty+index)&255
        cpu.c=(index+slot)&1
        cpu.x=slot
        ticks=cpu.call(labels[m["entry"]],120000)
        if (cpu.x!=slot or cpu.sp!=sp or
            cpu.mem[io]!=tx or cpu.mem[io+4]!=ty or
            bytes(cpu.mem[io+16:io+18])!=bytes((spl,sph))):
            raise ValueError("SEEK8 public input, speed or stack corrupted")
        if api=="MATH_SEEK8_INIT" and cpu.c!=int(sx==tx and sy==ty):
            raise ValueError("SEEK8 INIT arrival carry disagrees with public state")
        observations.append(ticks)
    if any(cpu.mem[addr]!=v for addr,v in image.items()):
        raise ValueError("SEEK8 source unexpectedly mutated")
    return {
        "basis":BASIS+"-"+api,
        "cases":COUNT,"cpu_model_only":True,
        "corpus_sha256":hashlib.sha256(bytes(
            x for case in cases for x in case)).hexdigest(),
        "mean_cycles":{VARIANT:sum(observations)/len(observations)},
        "maximum_cycles":{VARIANT:max(observations)},
        "p95_cycles":{VARIANT:sorted(observations)[int(len(observations)*.95)-1]},
        "source_sha256":{VARIANT:hashlib.sha256(
            (root/m["source"]).read_bytes()).hexdigest()},
        "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
        "note":"Original shared SEEK8 DDA per-public-entry cycles; STEP excludes mandatory INIT setup, requires durable 160-byte state; CPU model not PAL time",
    }


def bench_seek8_init(mod,code,io,scratch,root:Path):
    return measured("MATH_SEEK8_INIT",mod,code,io,scratch,root)
def bench_seek8_step(mod,code,io,scratch,root:Path):
    return measured("MATH_SEEK8_STEP",mod,code,io,scratch,root)
def bench_seek8_step_int(mod,code,io,scratch,root:Path):
    return measured("MATH_SEEK8_STEP_INT",mod,code,io,scratch,root)
def bench_seek8_step1(mod,code,io,scratch,root:Path):
    return measured("MATH_SEEK8_STEP1",mod,code,io,scratch,root)
