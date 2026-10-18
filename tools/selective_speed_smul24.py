#!/usr/bin/env python3
"""512 identical source-assembled public signed 24x24=>48 calls per Pareto variant.

Never substitute historical resident cycle means. Both alternative kernels are
assembled at the same origin/I/O, with their actual relocation, signed 48-bit
semantics and public X/Y/Z/C ABI checked per input.
"""
from __future__ import annotations
import hashlib
import random
from pathlib import Path
from mini6502 import Assembler, CPU, load_sparse
import selective_linker as linker
import selective_v2_fast_umul24 as v2

BASIS="cpu-model-smul24-public-biased-v2-512-v1"
FAST="link:v2-quarter-square"
COMPACT="link:compact-zerozp"
VARIANTS=frozenset((FAST,COMPACT))
CASES=512
CORPUS_SHA256="3a5112914567bb731f19df5e98cd4425be30fad9155f9132f2d715bc7ba9d042"
EDGE=(0,1,2,3,127,255,256,0x7fffff,0x800000,0x800001,
      0xfffffe,0xffffff)
RESOURCES={FAST:(2560,24,0),COMPACT:(227,0,9)}
MASK48=(1<<48)-1


def corpus():
    pairs=[(x,y) for x in EDGE for y in EDGE]
    r=random.Random(0x5A2424)
    pairs.extend((r.getrandbits(24),r.getrandbits(24))
                 for _ in range(CASES-len(pairs)))
    assert len(pairs)==CASES
    return pairs


def signed(v):
    return v-(1<<24) if v&0x800000 else v


def bench_smul24(modules,code,io,scratch,root:Path,zp=0x50):
    if set(modules)!=VARIANTS:
        raise ValueError("Signed24 Pareto source-set changed; requalify")
    cases=corpus()
    digest=hashlib.sha256(b"".join(
        x.to_bytes(3,"little")+y.to_bytes(3,"little")
        for x,y in cases)).hexdigest()
    if digest!=CORPUS_SHA256:
        raise ValueError("Signed24 benchmark input corpus changed")
    mean,maximum,source_hashes={},{},{}
    for name,mod in sorted(modules.items()):
        resource=(sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])
        if (resource!=RESOURCES[name] or
                bool(mod.get("v2_umul24"))!=(name==FAST) or
                bool(mod.get("multi_entry"))!=(name==FAST)):
            raise ValueError("Signed24 source/ZP/RAM ownership changed: "+name)
        if name==FAST:
            machine,labels,_,_=v2.assemble(code,io,zp,root)
        else:
            locations={"KERNEL_CODE":code,"INPUT_X":io,
                       "INPUT_Y":io+4,"OUTPUT_Z":io+8,
                       "TEMP_RAM":scratch}
            machine,labels,_=Assembler().assemble(
                linker.relocate_source(mod,locations,root))
        entry=labels[mod["entry"]]
        cpu=CPU(load_sparse(machine))
        sp=cpu.sp
        times=[]
        for i,(x,y) in enumerate(cases):
            xb=x.to_bytes(3,"little")
            yb=y.to_bytes(3,"little")
            cpu.mem[io:io+4]=xb+bytes([0x6a])
            cpu.mem[io+4:io+8]=yb+bytes([0xa5])
            cpu.mem[io+8:io+16]=bytes([0xcc]*6+[0x49,0x59])
            cpu.a=(x^i)&255
            cpu.x=(y>>8)&255
            cpu.y=(i*19)&255
            cpu.c=i&1
            cpu.d=0
            ticks=cpu.call(entry,100000)
            actual=int.from_bytes(cpu.mem[io+8:io+14],"little")
            if (actual!=(signed(x)*signed(y))&MASK48 or
                    cpu.c!=0 or cpu.sp!=sp or
                    bytes(cpu.mem[io:io+4])!=xb+bytes([0x6a]) or
                    bytes(cpu.mem[io+4:io+8])!=yb+bytes([0xa5]) or
                    bytes(cpu.mem[io+14:io+16])!=bytes([0x49,0x59])):
                raise ValueError("Signed24 public ABI failed "+
                                 repr((name,hex(x),hex(y),actual)))
            times.append(ticks)
        mean[name]=sum(times)/CASES
        maximum[name]=max(times)
        source_hashes[name]=hashlib.sha256(
            (root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS,"cases":CASES,"corpus_sha256":digest,
            "cpu_model_only":True,"mean_cycles":mean,"maximum_cycles":maximum,
            "source_sha256":source_hashes,"code_origin":"$%04X"%code,
            "io_origin":"$%04X"%io,
            "note":"Complete signed48 public calls at identical origins; excludes native PAL cycle timing"}
