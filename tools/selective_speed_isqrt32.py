#!/usr/bin/env python3
"""Fail-closed same-corpus ISQRT32 CPU-model speed basis for two link-ready sources.

This is a strict *single-operation* objective. Both original source-assembled
variants are measured under identical N32 inputs, selected code/I/O placement
and actual scratch locations. No resident profile benchmark is mixed in.
"""
from __future__ import annotations

import hashlib
from math import isqrt
from pathlib import Path
import random
import re
from mini6502 import Assembler,CPU,load_sparse

BASIS="cpu-model-isqrt32-v2-highword-versus-radix4-identical-inputs-v1"
SEED=0xC643225
COUNT=512
EXPECTED_VARIANTS=frozenset(("link:radix4-zerozp","link:v2-highword-source"))
EXPECTED_CORPUS_SHA256="f2a1e49ca20b8763b4ba27557a473dac2410b8019dd74035454923f2b409df16"
EDGES=(0,1,2,3,4,7,8,9,15,16,17,24,25,26,255,256,257,
       65534,65535,65536,65537,0x7fffffff,0x80000000,
       0xfffffffe,0xffffffff)
BOUNDARY_ROOTS=(0,1,2,3,15,16,127,128,255,256,257,32767,32768,65534,65535)


def corpus():
    values=list(EDGES)
    for root in BOUNDARY_ROOTS:
        values.extend(v for v in range(root*root-2,root*root+3)
                      if 0<=v<2**32)
    values=list(dict.fromkeys(values))
    rng=random.Random(SEED)
    seen=set(values)
    while len(values)<COUNT:
        n=rng.getrandbits(32)
        if n not in seen:
            values.append(n)
            seen.add(n)
    assert len(values)==COUNT
    return values


def source_assemble(mod,origin,io,scratch,zp,root):
    n=sum(x for _,x in mod["segments"])
    symbols={
        "KERNEL_CODE":origin,"INPUT_NUM":io+16,"OUTPUT_Z":io+8,
        "TEMP_ZP":zp,"TEMP_RAM":scratch,
        "SQ_SQUARE_LO":origin+192,
        "SQ_SQUARE_HI":origin+448,
        "SQ_GUESS":origin+704,
    }
    program=(root/mod["source"]).read_text(encoding="utf-8")
    for key in (p for p,_ in mod["segments"]):
        if key not in symbols:raise ValueError("ISQRT32 unknown segment "+key)
    keys={name for name,_ in mod["segments"]}|{"INPUT_NUM","OUTPUT_Z"}
    if mod["zp"]:keys.add("TEMP_ZP")
    if mod["scratch"]:keys.add("TEMP_RAM")
    for key in keys:
        pat=r"(?m)^"+re.escape(key)+r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        program,count=re.subn(pat,key+" = $%04X"%symbols[key],program)
        if count!=1:raise ValueError("ISQRT32 source binding changed: "+key)
    image,labels,_=Assembler().assemble(program)
    if set(image)!=set(range(origin,origin+n)):
        raise ValueError("ISQRT32 source/segment geometry changed")
    entry=labels.get(mod["entry"])
    if entry!=origin:raise ValueError("ISQRT32 entry point changed")
    return image,entry,n


def bench_isqrt32(modules,origin,io,scratch,root:Path,zp=0x50):
    if set(modules)!=EXPECTED_VARIANTS:
        raise ValueError("ISQRT32 candidate set changed; requalify matched corpus")
    values=corpus()
    corpus_sha=hashlib.sha256(b"".join(n.to_bytes(4,"little") for n in values)).hexdigest()
    if corpus_sha!=EXPECTED_CORPUS_SHA256:
        raise ValueError("ISQRT32 same-input corpus changed")
    cycles,code_sizes,hashes={},{},{}
    for ident,mod in sorted(modules.items()):
        expected=(204,0,10) if ident=="link:radix4-zerozp" else (960,7,0)
        if (sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])!=expected:
            raise ValueError("ISQRT32 variant resources changed: "+ident)
        if mod.get("requires_writable_code") or mod.get("requires_reu"):
            raise ValueError("ISQRT32 hardware requirement changed: "+ident)
        machine,entry,size=source_assemble(mod,origin,io,scratch,zp,root)
        cpu=CPU(load_sparse(machine))
        stack=cpu.sp
        total=0
        for j,n in enumerate(values):
            source=n.to_bytes(4,"little")
            cpu.mem[io+16:io+20]=source
            cpu.mem[io+8:io+12]=b"\x55\x55\x96\x69"
            cpu.x=j&255;cpu.y=(j*37)&255
            x,y=cpu.x,cpu.y
            cpu.c=j&1;cpu.d=0
            total+=cpu.call(entry,90000)
            got=int.from_bytes(cpu.mem[io+8:io+10],"little")
            if (got!=isqrt(n) or cpu.c!=0 or
                cpu.mem[io+8:io+12][2:]!=b"\x96\x69" or
                cpu.mem[io+16:io+20]!=source or
                (cpu.x,cpu.y,cpu.sp)!=(x,y,stack)):
                raise ValueError("ISQRT32 speed corpus ABI failure: "+
                                 repr((ident,hex(n),got)))
        cycles[ident]=total/COUNT
        code_sizes[ident]=size
        hashes[ident]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {
        "basis":BASIS,"cases":COUNT,"corpus_sha256":corpus_sha,
        "cpu_model_only":True,
        "note":"Identical 6502 CPU-model calls at requested code/I/O/ZP/RAM maps; no native VIC/REU/IRQ wall-clock timing and no mixed-operation speed certification",
        "code_origin":"$%04X"%origin,
        "io_origin":"$%04X"%io,
        "scratch_origin":"$%04X"%scratch,
        "zp_origin":"$%02X"%zp,
        "mean_cycles":cycles,
        "code_bytes":code_sizes,
        "source_sha256":hashes,
    }
