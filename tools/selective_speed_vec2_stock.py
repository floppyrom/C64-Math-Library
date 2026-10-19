#!/usr/bin/env python3
"""Exact original V1/V5 VEC2_NORMALIZE_Q8_8 public-call cycle provenance.

One historical stock source, not a new approximation. Reuse the certified
log-ratio/table image with its original eight bounded NMOS LDX abs,Y
self-modifying high bytes. Measure complete public Q8.8 inputs -> Q1.15
output and carry on 512 deterministic pairs at two RAM/code relocations.
CPU model timings are not physical PAL, VIC-II or IRQ frame timings.
"""
from __future__ import annotations

import hashlib
import json
import random
import tempfile
from pathlib import Path

from mini6502 import CPU
from normalize_model import normalized_reference

ROOT=Path(__file__).resolve().parents[1]
DESIGN_PATH="validation/normalize/LOG_RATIO_TABLE_DESIGN.json"
EXPECTED_SOURCE="routines/vector/vec2_normalize_q8_8_source.asm"
VARIANT="link:certified-stock"
BASIS="vec2-normalize-original-v1v5-full-public512-v1"
COUNT=512
EDGE=(-32768,-32767,-16384,-4096,-256,-255,-128,-2,-1,0,
       1,2,127,128,255,256,4096,16384,32766,32767)
CORPUS_SHA256="a6d2fd929b035a31916e1c1674f8b204d0c8ee4ed81c8a7590e8cb04b6dd3242"


def corpus():
    pairs=[(x,y) for x in EDGE for y in EDGE]
    rng=random.Random(0x56454332)
    pairs.extend((rng.randrange(-32768,32768),
                  rng.randrange(-32768,32768))
                 for _ in range(COUNT-len(pairs)))
    assert len(pairs)==COUNT
    packed=b"".join((x&65535).to_bytes(2,"little")+
                    (y&65535).to_bytes(2,"little") for x,y in pairs)
    if hashlib.sha256(packed).hexdigest()!=CORPUS_SHA256:
        raise ValueError("Historical normalized Q8.8 corpus drift")
    return pairs


def bench_vec2_normalize(modules,code,io,scratch,root:Path=ROOT,zp=0x50):
    if set(modules)!={VARIANT}:
        raise ValueError("Unknown VEC2 candidates: requalify shared source")
    mod=modules[VARIANT]
    if (mod["source"]!=EXPECTED_SOURCE
        or mod["segments"]!=(("KERNEL_CODE",3587),)
        or mod["zp"]!=4 or mod["scratch"]!=0
        or not mod.get("vec2_stock") or not mod.get("requires_writable_code")):
        raise ValueError("Original V1/V5 VEC2 source/resource contract changed")
    import math_builder
    import selective_linker as linker
    plan=math_builder.create_plan(
        math_builder.operation_index(root),["VEC2_NORMALIZE_Q8_8"],
        objective="size",pins={"VEC2_NORMALIZE_Q8_8":VARIANT},
        zp_budget=4,ram_budget=4000)
    design=json.loads((root/DESIGN_PATH).read_text(encoding="utf-8"))
    pairs=corpus()
    with tempfile.TemporaryDirectory(prefix="vec2_speed_public_") as td:
        dest=Path(td)
        man=linker.build(plan,dest,root=root,memory={
            "code_base":code,"math_io":io,"zp_base":zp,
            "scratch_base":scratch})
        res=man["resource_use"]
        origin=(code+255)&~255
        span=origin+3587-code
        if (res["image_span_bytes"]!=span
            or res["zero_page_bytes"]!=4
            or res["private_ram_scratch_bytes"]!=0
            or man["operations"][0]["variant"]!=VARIANT):
            raise ValueError("VEC2 source-linked alignment/ZP budget changed")
        image=(dest/"math_selective.prg").read_bytes()
        if image[:2]!=code.to_bytes(2,"little") or len(image)!=span+2:
            raise ValueError("VEC2 source-linked byte-span mismatch")
        mem=bytearray(65536)
        mem[code:code+span]=image[2:]
        original=bytes(mem[code:code+span])
        cpu=CPU(mem)
        entry=int(man["operations"][0]["entry"][1:],16)
        if entry!=origin+0xe00:
            raise ValueError("Original normalized Q8.8 public export moved")
        initial_sp=cpu.sp
        cycles=[]
        for k,(x,y) in enumerate(pairs):
            bx=(x&65535).to_bytes(2,"little")
            by=(y&65535).to_bytes(2,"little")
            mem[io:io+2]=bx
            mem[io+4:io+6]=by
            mem[io+8:io+12]=bytes((0xdd,0xee,0xaa,0x55))
            mem[io+2:io+4]=bytes((0x5a,0xa5))
            mem[io+6:io+8]=bytes((0x6b,0xb6))
            cpu.a=(k+x)&255
            cpu.x=(k+y)&255
            cpu.y=(x^y^k)&255
            cpu.c=k&1
            cpu.d=0
            ticks=cpu.call(entry,120000)
            actual=(int.from_bytes(mem[io+8:io+10],"little",signed=True),
                    int.from_bytes(mem[io+10:io+12],"little",signed=True))
            expect=normalized_reference(x,y,design)
            if (actual!=expect or cpu.c!=int(not(x or y))
                or mem[io:io+2]!=bx or mem[io+4:io+6]!=by
                or mem[io+2:io+4]!=bytes((0x5a,0xa5))
                or mem[io+6:io+8]!=bytes((0x6b,0xb6))
                or cpu.sp!=initial_sp):
                raise ValueError("Historical VEC2 full public ABI mismatch "+
                                 repr((hex(code),x,y,actual,expect,cpu.c)))
            cycles.append(ticks)
        # Historical SMC must be retained precisely, not mistakenly
        # described as immutable code or permitted in ROM.
        modified=[i for i,(a,b) in enumerate(zip(
            mem[code:code+span],original)) if a!=b]
        if len(modified)>8:
            raise ValueError("Original VEC2 modified too many code bytes")
        for offset in modified:
            absolute=code+offset
            if not(origin+0x500<=absolute<origin+0x900):
                raise ValueError("VEC2 self-modified code outside quadrant")
            if offset<2 or original[offset-2]!=0xbe or original[offset-1]!=0:
                raise ValueError("VEC2 SMC was not LDX absolute,Y high byte")
        return {"basis":BASIS,"cases":COUNT,
                "corpus_sha256":CORPUS_SHA256,"cpu_model_only":True,
                "mean_cycles":{VARIANT:sum(cycles)/COUNT},
                "p95_cycles":{VARIANT:sorted(cycles)[int(.95*COUNT)-1]},
                "maximum_cycles":{VARIANT:max(cycles)},
                "source_sha256":{VARIANT:hashlib.sha256(
                    (root/mod["source"]).read_bytes()).hexdigest()},
                "table_design_sha256":hashlib.sha256(
                    (root/DESIGN_PATH).read_bytes()).hexdigest(),
                "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
                "zp_origin":"$%02X"%zp,
                "note":"Original stock SMC/log-ratio source, full public Q1.15/C, 512 pairs; CPU model only"}
