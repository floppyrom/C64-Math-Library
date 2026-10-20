#!/usr/bin/env python3
"""Matched complete public-call UDIV32_32 and UMOD32_32 cycle baselines.

Measures the two independently linkable DIV producers and the dedicated MOD
producer on identical unsigned 32/32 operand pairs, not incompatible historical
resident register-ABI kernel cycles. Full Q32/R32/C correctness, zero divisor,
preserved N32/D32, stack and executable immutability are prerequisites.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import random
import re

from mini6502 import Assembler, CPU, load_sparse
import selective_hybrid_u3232 as hybrid
import research_d65536_hybrid as d65536

SEED=0x3232C64
COUNT=384
EDGES=(0,1,2,7,255,256,65535,0x7fffffff,0x80000000,0xffffffff)
DIVISORS=(0,1,2,7,255,256,65535,0x10000,0x7fffffff,0x80000000,0xffffffff)
CORPUS_SHA256="96e691eace2ab60671c984c61b4adc567720f3116c5873f13d0a07fc47344acf"
BASE="cpu-model-unsigned-32by32-complete-public-q32-r32-v1"
EXPECTED={
    "MATH_UDIV32_32":frozenset(("link:zptail","link:aligned-zerozp",
                                  "link:shared-aligned-zerozp",
                                  "link:v2-lowdivisor-hybrid","link:d65536-hybrid")),
    "MATH_UMOD32_32":frozenset(("link:aligned-zerozp",
                                  "link:shared-aligned-zerozp",
                                  "link:v2-lowdivisor-hybrid","link:d65536-hybrid")),
}
RESOURCES={
    "link:zptail":((325,219),4,0),
    "link:aligned-zerozp":((325,251),0,4),
    "link:shared-aligned-zerozp":((325,251),0,4),
    "link:mod-aligned-zerozp":((250,225,21),0,4),
    "link:v2-lowdivisor-hybrid":((2496,),12,0),
    "link:d65536-hybrid":((2592,),12,0),
}

def corpus():
    rng=random.Random(SEED)
    pairs=[(n,d) for n in EDGES for d in DIVISORS]
    pairs.extend((rng.getrandbits(32),rng.getrandbits(32))
                 for _ in range(240))
    pairs.extend((rng.getrandbits(32),rng.choice(
        (0,1,2,255,256,65535,65536,0x80000000,0xffffffff)))
                 for _ in range(34))
    if len(pairs)!=COUNT:
        raise ValueError("32/32 corpus length changed")
    return pairs

def assemble_source(api,ident,mod,base,io,scratch,zp,root):
    if ident=="link:v2-lowdivisor-hybrid":
        expected=RESOURCES[ident]
        if (tuple(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])!=expected:
            raise ValueError(api+": source resource contract changed: "+ident)
        image,labels,ranges,end=hybrid.assemble(base,io,zp,root)
        if (end!=base+hybrid.IMAGE_BYTES or len(ranges)!=1 or
            set(image)!=set(range(base,end))):
            raise ValueError(api+": V2 hybrid packed source layout changed")
        return image,labels[mod["entry"]]
    if ident=="link:d65536-hybrid":
        expected=RESOURCES[ident]
        if ((tuple(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])!=expected
                or not mod.get("d65536_unsigned_u3232")):
            raise ValueError(api+": D65536 unsigned producer resource provenance changed")
        image,labels,end=d65536.assemble_unsigned(base,io,zp,root)
        if end!=base+d65536.IMAGE_BYTES or set(image)!=set(range(base,end)):
            raise ValueError(api+": D65536 unsigned packed source layout changed")
        return image,labels[mod["entry"]]
    parts=tuple(n for _,n in mod["segments"])
    expected=RESOURCES["link:mod-aligned-zerozp" if
        api=="MATH_UMOD32_32" and ident=="link:aligned-zerozp" else ident]
    if (parts,mod["zp"],mod["scratch"])!=expected:
        raise ValueError(api+": source resource contract changed: "+ident)
    source=(root/mod["source"]).read_text(encoding="utf-8")
    locations={"KERNEL_CODE":base,"KERNEL_AUX":base+parts[0],
               "KERNEL_ADAPTER":base+parts[0]+parts[1],
               "INPUT_NUM":io+16,"INPUT_DIV":io+20,
               "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,
               "TEMP_ZP":zp,"TEMP_RAM":scratch}
    for key in ("KERNEL_CODE","KERNEL_AUX","KERNEL_ADAPTER",
                "INPUT_NUM","INPUT_DIV","OUTPUT_QUOT","OUTPUT_REM",
                "TEMP_ZP","TEMP_RAM"):
        pat=r"(?m)^"+re.escape(key)+r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        if re.search(pat,source):
            source,n=re.subn(pat,key+" = $%04X"%locations[key],source)
            if n!=1:
                raise ValueError(api+": ambiguous source relocation "+key)
    machine,labels,_=Assembler().assemble(source)
    size=sum(parts)
    if set(machine)!=set(range(base,base+size)):
        raise ValueError(api+": expected contiguous relocated machine code")
    entry=labels.get(mod["entry"])
    if entry is None or not base<=entry<base+size:
        raise ValueError(api+": missing public entry: "+ident)
    return machine,entry

def benchmark(api,modules,base,io,scratch,root:Path,zp=0x50):
    if api not in EXPECTED or set(modules)!=EXPECTED[api]:
        raise ValueError(api+": candidate set changed; requalify")
    pairs=corpus()
    digest=hashlib.sha256(b"".join(
        n.to_bytes(4,"little")+d.to_bytes(4,"little") for n,d in pairs)).hexdigest()
    if digest!=CORPUS_SHA256:
        raise ValueError(api+": deterministic public-call operand corpus changed")
    means={}
    sources={}
    for ident,mod in sorted(modules.items()):
        if ident=="link:shared-aligned-zerozp" and (
            not mod.get("multi_entry") or
            mod.get("share_producer")!="unsigned-32by32-aligned-public-qr"):
            raise ValueError(api+": shared producer identity changed")
        if ident=="link:v2-lowdivisor-hybrid" and (
            not mod.get("hybrid_u3232") or not mod.get("multi_entry") or
            mod.get("share_producer")!="unsigned-32by32-v2-lowdivisor-public-qr"):
            raise ValueError(api+": V2 hybrid shared producer identity changed")
        if ident=="link:d65536-hybrid" and (
            not mod.get("d65536_unsigned_u3232") or not mod.get("multi_entry") or
            mod.get("share_producer")!="unsigned-32by32-d65536-public-qr"):
            raise ValueError(api+": D65536 producer identity changed")
        if mod.get("requires_reu") or mod.get("requires_writable_code"):
            raise ValueError(api+": candidate hardware requirement changed")
        code,entry=assemble_source(api,ident,mod,base,io,scratch,zp,root)
        cpu=CPU(load_sparse(code))
        sp=cpu.sp
        cycles=0
        for i,(n,d) in enumerate(pairs):
            nb=n.to_bytes(4,"little");db=d.to_bytes(4,"little")
            cpu.mem[io+16:io+20]=nb
            cpu.mem[io+20:io+24]=db
            cpu.mem[io+24:io+28]=b"\x55"*4
            cpu.mem[io+28:io+32]=b"\x66"*4
            cpu.d=0
            cpu.c=(n^d^i)&1
            cycles+=cpu.call(entry,150000)
            quotient=int.from_bytes(cpu.mem[io+24:io+28],"little")
            remainder=int.from_bytes(cpu.mem[io+28:io+32],"little")
            expected_q=n//d if d else 0
            expected_r=n%d if d else 0
            if ((api=="MATH_UDIV32_32" and quotient!=expected_q)
                or remainder!=expected_r
                or cpu.c!=int(d==0)
                or cpu.sp!=sp
                or cpu.mem[io+16:io+20]!=nb
                or cpu.mem[io+20:io+24]!=db):
                raise ValueError(api+": public Q/R/C/input/SP failed: "+repr(
                    (ident,hex(n),hex(d),hex(quotient),hex(remainder),cpu.c)))
        if any(cpu.mem[a]!=v for a,v in code.items()):
            raise ValueError(api+": source code mutation not allowed")
        means[ident]=cycles/COUNT
        sources[ident]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {
        "basis":BASE+"-"+api.lower(),"cases":COUNT,
        "corpus_sha256":digest,"cpu_model_only":True,
        "note":"Identical-input complete public Q32/R32 calls through RTS, C=1 on divisor zero; native VICE required for correctness, not CPU-model timing",
        "code_origin":"$%04X"%base,"io_origin":"$%04X"%io,
        "scratch_origin":"$%04X"%scratch,"zp_origin":"$%02X"%zp,
        "mean_cycles":means,"source_sha256":sources,
    }

def bench_udiv32_32(modules,base,io,scratch,root:Path,zp=0x50):
    return benchmark("MATH_UDIV32_32",modules,base,io,scratch,root,zp)

def bench_umod32_32(modules,base,io,scratch,root:Path,zp=0x50):
    return benchmark("MATH_UMOD32_32",modules,base,io,scratch,root,zp)
