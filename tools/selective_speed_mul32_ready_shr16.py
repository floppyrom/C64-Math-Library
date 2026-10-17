#!/usr/bin/env python3
"""Same-corpus complete public-call CPU-model speed for READY/SHR16 32x32 APIs.

READY is state-independent for these published selective variants; do not use
historical register-ABI or prepared-state timings. SHR16 measures the six-byte
Q48 public result, rather than borrowing any full64 multiply cycle counts.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import re

from mini6502 import Assembler, CPU, load_sparse
import selective_fast31_umul32 as fast31
import selective_speed_umul32 as unsigned
import selective_speed_smul32 as signed_speed

FAST="link:fast31-shared-full64"
EXPECTED=frozenset(("link:compact-zerozp","link:unified-375",FAST))
RESOURCE_BYTES={
    "MATH_UMUL32_READY":204,
    "MATH_SMUL32_READY":293,
    "MATH_UMUL32_SHR16":245,
    "MATH_SMUL32_SHR16":334,
}
COUNT=192
MASK=(1<<64)-1

def _assemble(ident,mod,code,io,scratch,zp,root,api):
    if ident==FAST:
        image,_,ranges,end=fast31.assemble(
            code,io,zp,root,source_path=mod["source"],
            entry_label="FAST_UMUL32_FAST31")
        if end!=fast31.layout(code)[1] or len(ranges)!=6:
            raise ValueError(api+": FAST31 page-aligned source geometry changed")
        source=fast31.render(fast31.layout(code)[0],io,zp,root,
                             source_path=mod["source"])
        _,labels,_=Assembler().assemble(source)
        entry=labels[mod["entry"]]
        if not code<=entry<code+fast31.CODE_SLOT:
            raise ValueError(api+": FAST31 public entry outside code slot")
        mutable={v+1 for name,v in labels.items() if name.startswith("SMC_")}
        if (len(mutable)!=10 or
            not all(code<=v<code+fast31.CODE_SLOT for v in mutable)):
            raise ValueError(api+": FAST31 SMC whitelist changed")
        return image,entry,mutable
    source=(root/mod["source"]).read_text(encoding="utf-8")
    replacements={
        "KERNEL_CODE":code,"INPUT_X":io,"INPUT_Y":io+4,
        "OUTPUT_Z":io+8,"TEMP_RAM":scratch}
    for key,value in replacements.items():
        pat=r"(?m)^"+re.escape(key)+r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        source,count=re.subn(pat,key+" = $%04X"%value,source)
        if count!=1:
            raise ValueError(api+": missing source binding: "+key)
    image,labels,_=Assembler().assemble(source)
    expected=375 if ident=="link:unified-375" else RESOURCE_BYTES[api]
    if set(image)!=set(range(code,code+expected)):
        raise ValueError(api+": standalone code geometry changed: "+ident)
    entry=labels[mod["entry"]]
    if not code<=entry<code+expected:
        raise ValueError(api+": invalid public entry: "+ident)
    return image,entry,frozenset()

def bench(api,modules,code,io,scratch,root:Path,zp=0x50):
    if api not in RESOURCE_BYTES:
        raise ValueError("Unsupported speed ABI: "+api)
    if set(modules)!=EXPECTED:
        raise ValueError(api+": candidate set changed; requalify same-corpus basis")
    is_signed=api.startswith("MATH_SMUL")
    is_shift=api.endswith("_SHR16")
    donor=signed_speed if is_signed else unsigned
    pairs=donor.corpus()
    if len(pairs)!=COUNT:
        raise ValueError(api+": corpus length changed")
    digest=hashlib.sha256(b"".join(
        x.to_bytes(4,"little")+y.to_bytes(4,"little") for x,y in pairs
    )).hexdigest()
    if digest!=donor.CORPUS_SHA256:
        raise ValueError(api+": deterministic input corpus fingerprint mismatch")
    metrics={}
    sources={}
    for ident,mod in sorted(modules.items()):
        resources=(sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])
        expected=(2560,31,0) if ident==FAST else (
            (375,0,12) if ident=="link:unified-375"
            else (RESOURCE_BYTES[api],0,12))
        if resources!=expected:
            raise ValueError(api+": candidate resources changed: "+ident)
        if mod.get("requires_reu") or (
            bool(mod.get("requires_writable_code"))!=(ident==FAST)):
            raise ValueError(api+": candidate hardware contract changed: "+ident)
        if ident==FAST and (
            not mod.get("fast31_shared") or
            mod.get("share_producer")!="fast31-dual-public-full64"):
            raise ValueError(api+": shared fast31 provenance changed")
        image,entry,mutable=_assemble(ident,mod,code,io,scratch,zp,root,api)
        cpu=CPU(load_sparse(image))
        stack=cpu.sp
        cycles=0
        for i,(x,y) in enumerate(pairs):
            xb=x.to_bytes(4,"little")
            yb=y.to_bytes(4,"little")
            cpu.mem[io:io+4]=xb
            cpu.mem[io+4:io+8]=yb
            cpu.mem[io+8:io+16]=b"\xa5"*8
            cpu.d=0
            cpu.c=(i^x^y)&1
            cycles+=cpu.call(entry,125000)
            product=(signed_speed.signed(x)*signed_speed.signed(y))&MASK if is_signed else x*y
            correct=(product>>16) if is_shift else product
            width=6 if is_shift else 8
            got=int.from_bytes(cpu.mem[io+8:io+8+width],"little")
            if (got!=correct or cpu.c!=0 or cpu.sp!=stack or
                cpu.mem[io:io+4]!=xb or cpu.mem[io+4:io+8]!=yb):
                raise ValueError(api+": public-call/ABI check failed: "+
                                 repr((ident,hex(x),hex(y),hex(got),hex(correct))))
        if any(cpu.mem[addr]!=value for addr,value in image.items()
               if addr not in mutable):
            raise ValueError(api+": executable/table image mutated: "+ident)
        metrics[ident]=cycles/COUNT
        sources[ident]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {
        "basis":"cpu-model-"+api.lower()+"-complete-public-identical-inputs-v1",
        "cases":COUNT,"corpus_sha256":digest,"cpu_model_only":True,
        "note":"Same-input complete READY or Q48 SHR16 public calls through RTS; CPU-model only, not VICE elapsed timing",
        "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
        "scratch_origin":"$%04X"%scratch,"zp_origin":"$%02X"%zp,
        "mean_cycles":metrics,"source_sha256":sources,
    }

def bench_umul32_ready(modules,code,io,scratch,root:Path,zp=0x50):
    return bench("MATH_UMUL32_READY",modules,code,io,scratch,root,zp)

def bench_smul32_ready(modules,code,io,scratch,root:Path,zp=0x50):
    return bench("MATH_SMUL32_READY",modules,code,io,scratch,root,zp)

def bench_umul32_shr16(modules,code,io,scratch,root:Path,zp=0x50):
    return bench("MATH_UMUL32_SHR16",modules,code,io,scratch,root,zp)

def bench_smul32_shr16(modules,code,io,scratch,root:Path,zp=0x50):
    return bench("MATH_SMUL32_SHR16",modules,code,io,scratch,root,zp)
