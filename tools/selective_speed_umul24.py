#!/usr/bin/env python3
"""Same-input complete-public-call speed basis: historical V2 UMUL24 vs compact.

Both sources are assembled at identical code/data/I/O origins; the data
consists of 512 edge/random operand pairs. This CPU-model basis is only
eligible for speed-first selection after native VICE qualification.
"""
from __future__ import annotations
import hashlib
import random
from pathlib import Path
from mini6502 import Assembler,CPU,load_sparse
import selective_linker as linker
import selective_v2_fast_umul24 as v2

BASIS="cpu-model-umul24-public-biased-V2-512-v1"
FAST="link:v2-quarter-square"
COMPACT="link:compact-zerozp"
VARIANTS=frozenset((FAST,COMPACT))
CASES=512
CORPUS_SHA256="528baa842ce1bc6d9dec54bd7c6d40881cf97c9f2e8a1fcd300885076aab843a"
EDGE=(0,1,2,3,7,127,128,255,256,257,65535,65536,
      0x7fffff,0x800000,0x800001,0xfffffe,0xffffff)
RESOURCE={FAST:(2560,24,0),COMPACT:(156,0,9)}


def corpus():
    pairs=[(x,y) for x in EDGE for y in EDGE]
    rng=random.Random(0x5A24682)
    pairs.extend((rng.getrandbits(24),rng.getrandbits(24))
                 for _ in range(CASES-len(pairs)))
    assert len(pairs)==CASES
    return pairs


def bench_umul24(modules,code,io,scratch,root:Path,zp=0x50):
    if set(modules)!=VARIANTS:
        raise ValueError("UMUL24 has lost one of the source-qualified Pareto variants")
    pairs=corpus()
    digest=hashlib.sha256(b"".join(
        x.to_bytes(3,"little")+y.to_bytes(3,"little")
        for x,y in pairs)).hexdigest()
    if digest!=CORPUS_SHA256:
        raise ValueError("UMUL24 identical-input corpus drifted")
    means,maxima,source_hashes={}, {}, {}
    for name,mod in sorted(modules.items()):
        footprint=(sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])
        if footprint!=RESOURCE[name] or bool(mod.get("v2_umul24"))!=(name==FAST):
            raise ValueError("UMUL24 source or private-memory contract drifted")
        if name==FAST:
            machine,labels,_,_ = v2.assemble(code,io,zp,root)
        else:
            labels0={"KERNEL_CODE":code,"INPUT_X":io,"INPUT_Y":io+4,
                     "OUTPUT_Z":io+8,"TEMP_RAM":scratch}
            machine,labels,_=Assembler().assemble(
                linker.relocate_source(mod,labels0,root))
        entry=labels[mod["entry"]]
        cpu=CPU(load_sparse(machine));sp=cpu.sp
        times=[]
        for i,(x,y) in enumerate(pairs):
            xb=x.to_bytes(3,"little");yb=y.to_bytes(3,"little")
            cpu.mem[io:io+4]=xb+bytes([0x6a])
            cpu.mem[io+4:io+8]=yb+bytes([0xa5])
            cpu.mem[io+8:io+16]=bytes([0xcc]*6+[0x49,0x59])
            cpu.a=(x^i)&255;cpu.x=(y>>8)&255;cpu.y=(i*19)&255
            cpu.c=i&1;cpu.d=0
            cycles=cpu.call(entry,100000)
            if (int.from_bytes(cpu.mem[io+8:io+14],"little")!=(x*y)&((1<<48)-1)
                    or cpu.c or cpu.sp!=sp
                    or bytes(cpu.mem[io:io+4])!=xb+bytes([0x6a])
                    or bytes(cpu.mem[io+4:io+8])!=yb+bytes([0xa5])
                    or bytes(cpu.mem[io+14:io+16])!=bytes([0x49,0x59])):
                raise ValueError("UMUL24 full public ABI failed: "+repr((name,x,y)))
            times.append(cycles)
        means[name]=sum(times)/CASES
        maxima[name]=max(times)
        source_hashes[name]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS,"corpus_sha256":digest,"cases":CASES,
            "cpu_model_only":True,
            "mean_cycles":means,"maximum_cycles":maxima,
            "source_sha256":source_hashes,
            "code_origin":"$%04X"%code,
            "io_origin":"$%04X"%io,
            "note":"same 512 complete public calls at identical code origin; actual linked placement may differ; no native hardware timing"}
