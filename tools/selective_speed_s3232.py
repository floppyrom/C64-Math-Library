#!/usr/bin/env python3
"""Authenticated same-input, same-placement signed32/32 public-call speed model.

Portable and V2 hybrid share one deterministic 384-case public Q32/R32/C
operand corpus, each fully assembled with its actual source and API entry.
No historical resident mean can be supplied as this benchmark.
"""
from __future__ import annotations
import hashlib
import random
from pathlib import Path
from mini6502 import Assembler,CPU,load_sparse
import selective_linker as linker
import selective_signed_hybrid_u3232 as fast
import research_d65536_hybrid as d65536

BASIS="cpu-model-signed3232-public-paired-v2-hybrid-v1"
APIS=frozenset(("MATH_SDIV32_32","MATH_SMOD32_32"))
PORTABLE="link:portable-zerozp"
FAST="link:v2-hybrid-signed"
D65536="link:d65536-hybrid"
VARIANTS=frozenset((PORTABLE,FAST,D65536))
COUNTS={PORTABLE:(412,0,9),FAST:(2880,12,0),D65536:(2976,12,0)}
CASES=384
CORPUS_SHA256="435b05f1226c3663a8a788f04795348a3ee4e986fe6855a7f6ef56b5eba55adc"
N_EDGES=(0,1,2,3,127,255,65535,65536,65537,0x7fffffff,
         0x80000000,0x80000001,0xfffffffe,0xffffffff)
D_EDGES=(0,1,2,3,127,128,255,65535,65536,0x7fffffff,
         0x80000000,0xffffffff)


def corpus():
    rng=random.Random(0x5D3232)
    pairs=[(n,d) for n in N_EDGES for d in D_EDGES]
    pairs.extend((rng.getrandbits(32),rng.getrandbits(32))
                 for _ in range(CASES-len(pairs)))
    assert len(pairs)==CASES
    return pairs


def signed(n):
    return n-(1<<32) if n&0x80000000 else n


def reference(n,d):
    n,d=signed(n),signed(d)
    if d==0:
        return 0,0,1
    q=abs(n)//abs(d)
    if (n<0)!=(d<0):
        q=-q
    return q&0xffffffff,(n-q*d)&0xffffffff,0


def benchmark(api,modules,code,io,scratch,root:Path,zp=0x50):
    if api not in APIS or set(modules)!=VARIANTS:
        raise ValueError("Signed32/32 public speed candidate set changed")
    pairs=corpus()
    digest=hashlib.sha256(b"".join(
        n.to_bytes(4,"little")+d.to_bytes(4,"little")
        for n,d in pairs)).hexdigest()
    if digest!=CORPUS_SHA256:
        raise ValueError("Signed32/32 deterministic input corpus drifted")
    means,maximums,source_hashes={}, {}, {}
    for ident,module in sorted(modules.items()):
        budget=(sum(n for _,n in module["segments"]),module["zp"],
                module["scratch"])
        if budget!=COUNTS[ident] or not module.get("multi_entry"):
            raise ValueError("Signed32/32 resource contract changed "+ident)
        if bool(module.get("signed_hybrid_u3232"))!=(ident==FAST) or bool(module.get("d65536_signed_u3232"))!=(ident==D65536):
            raise ValueError("Signed32/32 emitter source provenance drifted")
        if ident==FAST:
            image,labels,_,end=fast.assemble(code,io,zp,root)
            if end!=code+2880:
                raise ValueError("signed hybrid image span changed")
        elif ident==D65536:
            image,labels,end=d65536.assemble_signed(code,io,zp,root)
            if end!=code+d65536.SIGNED_IMAGE_BYTES:
                raise ValueError("D65536 signed source image span changed")
        else:
            locations={"KERNEL_CODE":code,"INPUT_NUM":io+16,
                       "INPUT_DIV":io+20,"OUTPUT_QUOT":io+24,
                       "OUTPUT_REM":io+28,"TEMP_RAM":scratch}
            image,labels,_=Assembler().assemble(
                linker.relocate_source(module,locations,root))
        if set(image)!=set(range(code,code+budget[0])):
            raise ValueError("signed32/32 public source emitted wrong geometry")
        entry=labels[module["entry"]]
        cpu=CPU(load_sparse(image))
        before=dict(image)
        sp=cpu.sp
        samples=[]
        for i,(n,d) in enumerate(pairs):
            nb=n.to_bytes(4,"little")
            db=d.to_bytes(4,"little")
            cpu.mem[io+16:io+20]=nb
            cpu.mem[io+20:io+24]=db
            cpu.mem[io+24:io+32]=bytes([0xdd])*8
            cpu.a=(n^d)&255
            cpu.x=(n>>8)&255
            cpu.y=(d>>8)&255
            cpu.c=i&1
            cpu.d=0
            tick=cpu.call(entry,150000)
            got=(int.from_bytes(cpu.mem[io+24:io+28],"little"),
                 int.from_bytes(cpu.mem[io+28:io+32],"little"),cpu.c)
            if (got!=reference(n,d) or cpu.sp!=sp
                    or bytes(cpu.mem[io+16:io+20])!=nb
                    or bytes(cpu.mem[io+20:io+24])!=db):
                raise ValueError("signed32/32 ABI mismatch "+
                                 repr((ident,n,d,got)))
            samples.append(tick)
        if any(cpu.mem[a]!=v for a,v in before.items()):
            raise ValueError("signed32/32 unexpectedly modified executable code")
        means[ident]=sum(samples)/len(samples)
        maximums[ident]=max(samples)
        source_hashes[ident]=hashlib.sha256(
            (root/module["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS+"-"+api.lower(),"cases":CASES,
            "corpus_sha256":digest,"cpu_model_only":True,
            "mean_cycles":means,"maximum_cycles":maximums,
            "source_sha256":source_hashes,
            "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
            "note":"Complete public Q32/R32/C through RTS at identical placements; no hardware cycle claim"}


def bench_sdiv32_32(modules,code,io,scratch,root:Path,zp=0x50):
    return benchmark("MATH_SDIV32_32",modules,code,io,scratch,root,zp)


def bench_smod32_32(modules,code,io,scratch,root:Path,zp=0x50):
    return benchmark("MATH_SMOD32_32",modules,code,io,scratch,root,zp)
