#!/usr/bin/env python3
"""Matched 512-divisor public ABI speed basis for stock Q16 reciprocal.

Compare the unmodified 99-byte restoring source and the V3/V4-inspired
zero-ZP fast threshold gate, including divide-by-zero, input preservation,
Q3 and all remainder sentinels. Never import REU resident timings.
"""
from __future__ import annotations

import hashlib
import random
from pathlib import Path

from mini6502 import Assembler, CPU, load_sparse
import selective_linker as linker
import selective_recip16_threshold as thresholds
import selective_recip16_table as table_fast

BASIS = "stock-c64-recip16-v3v4-threshold-public512-v1"
FAST = "link:threshold-zerozp"
SMALL = "link:compact-zerozp"
TABLE = "link:threshold-tables-zerozp"
EXPECTED = frozenset((FAST, SMALL, TABLE))
SIZE = {FAST: 448, SMALL: 99, TABLE: 1544}
COUNT = 512
CORPUS_SHA256 = "037d4fad53f2034a11a1b87ed5fee34f04a26eee998377c77ebe5586e283712b"
EDGE = (0,1,2,3,4,5,7,15,16,17,31,32,63,64,127,128,
        255,256,257,511,512,1023,1024,2047,2048,4095,
        4096,4097,4369,8191,8192,16383,16384,21845,21846,
        32767,32768,32769,65535)


def corpus():
    edges = [x for q in range(1, 16)
             for x in range(65536//(q+1),65536//(q+1)+3)]
    ds = list(EDGE)+edges
    rng = random.Random(0xC6416ECB)
    ds.extend(rng.randrange(4097) for _ in range(160))
    ds.extend(rng.randrange(65536) for _ in range(COUNT-len(ds)))
    assert len(ds)==COUNT
    return ds


def assemble(ident, module, code, io, scratch, root: Path):
    if ident == FAST:
        image, labels, _, _ = thresholds.assemble_image(code, io, scratch, root)
        return image, labels[module["entry"]]
    if ident == TABLE:
        image, labels, _, _ = table_fast.assemble_image(code,io,root)
        return image, labels[module["entry"]]
    bindings = {
        "KERNEL_CODE":code, "INPUT_NUM":io+16,
        "INPUT_DIV":io+20, "OUTPUT_QUOT":io+24,
        "OUTPUT_REM":io+28, "TEMP_RAM":scratch,
    }
    image, labels, _ = Assembler().assemble(
        linker.relocate_source(module, bindings, root))
    if set(image) != set(range(code,code+99)):
        raise ValueError("Compact reciprocal kernel geometry changed")
    return image, labels[module["entry"]]


def bench_urecip16_q16(modules,code,io,scratch,root:Path):
    if set(modules)!=EXPECTED:
        raise ValueError("Unknown reciprocal candidates; requalify")
    ds=corpus()
    digest=hashlib.sha256(b"".join(d.to_bytes(2,"little") for d in ds)).hexdigest()
    if digest!=CORPUS_SHA256:
        raise ValueError("Reciprocal corpus changed")
    costs, maxima, p95s, hashes = {}, {}, {}, {}
    for ident,mod in sorted(modules.items()):
        if (sum(n for _,n in mod["segments"])!=SIZE[ident]
            or mod["zp"]!=0 or mod["scratch"]!=(0 if ident==TABLE else 1)
            or bool(mod.get("recip16_table"))!=(ident==TABLE)
            or bool(mod.get("recip16_threshold"))!=(ident==FAST)
            or mod.get("requires_reu") or mod.get("requires_writable_code")):
            raise ValueError("Reciprocal source resource contract changed")
        image, entry = assemble(ident,mod,code,io,scratch,root)
        cpu=CPU(load_sparse(image))
        sp=cpu.sp
        timings=[]
        for i,d in enumerate(ds):
            divisor=d.to_bytes(2,"little")+bytes((0x5a,0xa5))
            cpu.mem[io+20:io+24]=divisor
            cpu.mem[io+16:io+20]=bytes((0xde,0xad,0xbe,0xef))
            cpu.mem[io+24:io+28]=bytes((0x55,0xaa,0x77,0xcc))
            cpu.mem[io+28:io+32]=bytes((0x12,0x34,0x56,0x78))
            cpu.a=(d+i)&255
            cpu.x=(d^i)&255
            cpu.y=(d-i)&255
            cpu.c=i&1
            cpu.d=0
            ticks=cpu.call(entry,50000)
            q=int.from_bytes(cpu.mem[io+24:io+27],"little")
            expected=(65536//d if d else 0,int(d==0))
            if ((q,cpu.c)!=expected or
                cpu.mem[io+27]!=0xcc or
                cpu.mem[io+28:io+32]!=bytes((0x12,0x34,0x56,0x78)) or
                cpu.mem[io+16:io+20]!=bytes((0xde,0xad,0xbe,0xef)) or
                cpu.mem[io+20:io+24]!=divisor or cpu.sp!=sp):
                raise ValueError("Reciprocal public contract mismatch: "+
                                 repr((ident,hex(code),d,(q,cpu.c),expected)))
            timings.append(ticks)
        if any(cpu.mem[p]!=val for p,val in image.items()):
            raise ValueError("Reciprocal unexpectedly modifies executable code")
        costs[ident]=sum(timings)/len(timings)
        maxima[ident]=max(timings)
        p95s[ident]=sorted(timings)[int(len(timings)*0.95)-1]
        hashes[ident]=hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest()
    return {
       "basis":BASIS, "cases":COUNT,"cpu_model_only":True,
       "corpus_sha256":digest,
       "mean_cycles":costs,"maximum_cycles":maxima,
       "p95_cycles":p95s,"source_sha256":hashes,
       "code_origin":"$%04X"%code,"io_origin":"$%04X"%io,
       "note":"Identical-input complete public Q24/C cycles, not REU or PAL timing",
    }
