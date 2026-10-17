#!/usr/bin/env python3
"""Matched complete-public-call UDIV32_16 / UMOD32_16 speed basis.

Quotient and remainder share both source kernels. Benchmarking each public
entry, including D=0 and C flag, avoids comparing historical native-only
register-ABI measurements with a source-linked public adapter.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import random
import re

from mini6502 import Assembler, CPU, load_sparse

BASIS="cpu-model-u3216-public-quotient-remainder-identical-inputs-v1"
SEED=0x32160B17
EDGES=(0,1,2,3,255,256,65535,0x7fffffff,0x80000000,0xffffffff)
DIVISORS=(0,1,2,3,7,127,255,256,257,32768,65535)
COUNT=384
CORPUS_SHA256="d3c5e882c9ee52461ca764dc50b4b9f7d9203bf378ac5a25be3692168bb053e1"
APIS=frozenset(("MATH_UDIV32_16","MATH_UMOD32_16"))
EXPECTED=frozenset(("link:portable-restoring","link:accumulator-remainder",
                    "link:accum-unrolled-32"))
RESOURCES={
    "link:portable-restoring":(162,0,3),
    "link:accumulator-remainder":(131,0,1),
    "link:accum-unrolled-32":(1771,0,1),
}

def corpus():
    rng=random.Random(SEED)
    pairs=[(n,d) for n in EDGES for d in DIVISORS]
    pairs.extend((rng.getrandbits(32),rng.getrandbits(16))
                 for _ in range(206))
    pairs.extend((rng.getrandbits(32),
                  rng.choice((1,2,3,7,255,256,65535)))
                 for _ in range(68))
    assert len(pairs)==COUNT
    return pairs

def assemble_source(ident,mod,code,io,scratch,root):
    source=(root/mod["source"]).read_text(encoding="utf-8")
    bindings={
        "KERNEL_CODE":code,"INPUT_NUM":io+16,"INPUT_DIV":io+20,
        "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,
        "TEMP_RAM":scratch,
    }
    for key,value in bindings.items():
        pat=r"(?m)^"+re.escape(key)+r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        source,number=re.subn(pat,key+" = $%04X"%value,source)
        if number!=1:
            raise ValueError(ident+": missing 32/16 source binding: "+key)
    image,labels,_=Assembler().assemble(source)
    size=RESOURCES[ident][0]
    if set(image)!=set(range(code,code+size)):
        raise ValueError(ident+": changed code size or address geometry")
    entry=labels.get(mod["entry"])
    if entry is None or not code<=entry<code+size:
        raise ValueError(ident+": public entry label moved")
    return image,entry

def benchmark(api,modules,code,io,scratch,root:Path):
    if api not in APIS:
        raise ValueError("No public 32/16 speed basis for "+api)
    if set(modules)!=EXPECTED:
        raise ValueError(api+": candidate set changed; new speed proof required")
    pairs=corpus()
    digest=hashlib.sha256(b"".join(
        n.to_bytes(4,"little")+d.to_bytes(2,"little") for n,d in pairs
    )).hexdigest()
    if digest!=CORPUS_SHA256:
        raise ValueError(api+": matched operand corpus changed")
    totals={}
    hashes={}
    for ident,mod in sorted(modules.items()):
        resources=(sum(s for _,s in mod["segments"]),mod["zp"],mod["scratch"])
        if resources!=RESOURCES[ident]:
            raise ValueError(api+": kernel resource ownership changed: "+ident)
        if (mod.get("requires_reu") or mod.get("requires_writable_code")
            or mod.get("share_producer") not in (
                "unsigned-32by16-restoring","unsigned-32by16-accum",
                "unsigned-32by16-accum-unrolled")
            or not mod.get("multi_entry")):
            raise ValueError(api+": hardware/sharing contract changed: "+ident)
        image,entry=assemble_source(ident,mod,code,io,scratch,root)
        cpu=CPU(load_sparse(image))
        sp=cpu.sp
        cycles=0
        for i,(n,d) in enumerate(pairs):
            nbytes=n.to_bytes(4,"little")
            dbytes=d.to_bytes(2,"little")
            cpu.mem[io+16:io+20]=nbytes
            cpu.mem[io+20:io+22]=dbytes
            cpu.mem[io+24:io+28]=b"\x55"*4
            cpu.mem[io+28:io+32]=b"\x66\x66\x69\xab"
            cpu.d=0
            cpu.c=(i^n^d)&1
            cycles+=cpu.call(entry,20000)
            q=int.from_bytes(cpu.mem[io+24:io+28],"little")
            rem=int.from_bytes(cpu.mem[io+28:io+30],"little")
            expected=(n//d if d else 0,n%d if d else 0,int(d==0))
            if ((q,rem,cpu.c)!=expected or cpu.sp!=sp or
                cpu.mem[io+16:io+20]!=nbytes or
                cpu.mem[io+20:io+22]!=dbytes or
                cpu.mem[io+30:io+32]!=b"\x69\xab"):
                raise ValueError(api+": public Q/R/C or memory ABI mismatch: "+
                    repr((ident,hex(n),hex(d),(q,rem,cpu.c),expected)))
        if any(cpu.mem[addr]!=byte for addr,byte in image.items()):
            raise ValueError(api+": non-SMC executable unexpectedly modified")
        totals[ident]=cycles/COUNT
        hashes[ident]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {
        "basis":BASIS+"-"+api.lower(),
        "cases":COUNT,"corpus_sha256":digest,
        "cpu_model_only":True,
        "note":"Public 32/16 Q32+R16, divide-by-zero and carry, through RTS; CPU model only; input corpus includes small and arbitrary divisors",
        "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
        "scratch_origin":"$%04X"%scratch,
        "mean_cycles":totals,"source_sha256":hashes,
    }

def bench_udiv32_16(modules,code,io,scratch,root:Path):
    return benchmark("MATH_UDIV32_16",modules,code,io,scratch,root)

def bench_umod32_16(modules,code,io,scratch,root:Path):
    return benchmark("MATH_UMOD32_16",modules,code,io,scratch,root)
