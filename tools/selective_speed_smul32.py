#!/usr/bin/env python3
"""Matched signed full64 public-call cycle basis for three independent SMUL32 sources.

No historical register-ABI core-only cycle numbers are compared. Source-assembled
calls use exactly the same signed input corpus with public I/O preservation.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import random
import re
from mini6502 import Assembler,CPU,load_sparse
import selective_fast31_umul32 as fast31

BASIS="cpu-model-smul32-full64-public-identical-inputs-v1"
SEED=0xC6435132
EDGES=(0,1,2,255,256,65535,0x7fffffff,0x80000000,0xffffffff)
COUNT=192
CORPUS_SHA256="928b2da2262eca3c95347f97698ae45d1e01a54bddca98d00ee7d9482b90a8f9"
EXPECTED=frozenset(("link:compact-zerozp","link:unified-375","link:fast31-v2-signed",
                    "link:fast31-shared-full64"))
EXPECTED_RESOURCES={
    "link:compact-zerozp":(293,0,12),
    "link:unified-375":(375,0,12),
    "link:fast31-v2-signed":(2560,31,0),
    "link:fast31-shared-full64":(2560,31,0),
}
MASK=(1<<64)-1

def signed(x):
    return x-(1<<32) if x&0x80000000 else x

def corpus():
    rng=random.Random(SEED)
    pairs=[(a,b) for a in EDGES for b in EDGES]
    pairs.extend((rng.getrandbits(32),rng.getrandbits(32))
                 for _ in range(COUNT-len(pairs)))
    return pairs

def source_assemble(ident,mod,code,io,scratch,zp,root):
    if ident in ("link:fast31-v2-signed", "link:fast31-shared-full64"):
        shared=ident=="link:fast31-shared-full64"
        image,entry,ranges,end=fast31.assemble(
            code,io,zp,root,source_path=mod["source"],
            entry_label="FAST_UMUL32_FAST31" if shared else mod["entry"])
        if end!=fast31.layout(code)[1]:
            raise ValueError("SMUL32 FAST31 page-aligned geometry changed")
        src=fast31.render(fast31.layout(code)[0],io,zp,root,
                          source_path=mod["source"])
        _,labels,_=Assembler().assemble(src)
        entry=labels[mod["entry"]]
        if (entry==code) == shared:
            raise ValueError("SMUL32 FAST31 signed entry geometry changed")
        mutable={a+1 for k,a in labels.items() if k.startswith("SMC_")}
        if len(mutable)!=10:
            raise ValueError("SMUL32 FAST31 self-modifying whitelist changed")
        return image,entry,mutable
    src=(root/mod["source"]).read_text(encoding="utf-8")
    values={"KERNEL_CODE":code,"INPUT_X":io,"INPUT_Y":io+4,
            "OUTPUT_Z":io+8,"TEMP_RAM":scratch}
    for key,value in values.items():
        pat=r"(?m)^"+re.escape(key)+r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        src,count=re.subn(pat,key+" = $%04X"%value,src)
        if count!=1:
            raise ValueError("SMUL32 missing source binding: "+key)
    image,labels,_=Assembler().assemble(src)
    expected=EXPECTED_RESOURCES[ident][0]
    if set(image)!=set(range(code,code+expected)):
        raise ValueError("SMUL32 code geometry changed")
    if labels[mod["entry"]] not in image:
        raise ValueError("SMUL32 entry outside code")
    return image,labels[mod["entry"]],set()

def bench_smul32(modules,code,io,scratch,root:Path,zp=0x50):
    if set(modules)!=EXPECTED:
        raise ValueError("SMUL32 matched-input candidate set changed; requalify")
    cases=corpus()
    digest=hashlib.sha256(b"".join(
        x.to_bytes(4,"little")+y.to_bytes(4,"little") for x,y in cases)).hexdigest()
    if digest!=CORPUS_SHA256:
        raise ValueError("SMUL32 signed corpus digest changed")
    cycles={}
    hashes={}
    for ident,mod in sorted(modules.items()):
        res=(sum(n for _,n in mod["segments"]),mod["zp"],mod["scratch"])
        if res!=EXPECTED_RESOURCES[ident]:
            raise ValueError("SMUL32 memory contract changed: "+ident)
        if mod.get("requires_reu") or (mod.get("requires_writable_code") and
                                       ident not in ("link:fast31-v2-signed",
                                                     "link:fast31-shared-full64")):
            raise ValueError("SMUL32 hardware contract changed")
        memory,entry,mutable=source_assemble(ident,mod,code,io,scratch,zp,root)
        cpu=CPU(load_sparse(memory))
        stack=cpu.sp
        total=0
        for i,(x,y) in enumerate(cases):
            xb=x.to_bytes(4,"little"); yb=y.to_bytes(4,"little")
            cpu.mem[io:io+4]=xb
            cpu.mem[io+4:io+8]=yb
            cpu.mem[io+8:io+16]=b"\xa5"*8
            cpu.c=(i^x^y)&1
            cpu.d=0
            total+=cpu.call(entry,120000)
            output=int.from_bytes(cpu.mem[io+8:io+16],"little")
            if (output != (signed(x)*signed(y))&MASK or cpu.c or cpu.sp!=stack
                or cpu.mem[io:io+4]!=xb or cpu.mem[io+4:io+8]!=yb):
                raise ValueError("SMUL32 candidate failed signed full64 public ABI: "+
                                 repr((ident,hex(x),hex(y),hex(output))))
        if any(cpu.mem[a]!=b for a,b in memory.items() if a not in mutable):
            raise ValueError("SMUL32 candidate executable/table image mutated: "+ident)
        cycles[ident]=total/COUNT
        hashes[ident]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {"basis":BASIS,"cases":COUNT,"corpus_sha256":digest,"cpu_model_only":True,
            "note":"Signed full64 identical-input complete public calls through RTS; CPU-model only, not native VICE cycle claim",
            "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
            "scratch_origin":"$%04X"%scratch,"zp_origin":"$%02X"%zp,
            "mean_cycles":cycles,"source_sha256":hashes}
