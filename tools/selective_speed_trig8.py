#!/usr/bin/env python3
"""Authenticated stock-C64 8-bit trig full public-call speed measurements.

SIN8, COS8 and SINCOS8 retain their original V1-V5 instruction bytes and
one immutable 256-byte shared sine plane. The operation-first speed objective
needs cycle measurements even though there is only one certified candidate.
All 256 phase bytes are measured, at each requested source relocation;
no floating-point regeneration and no inference from resident-only timings.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from mini6502 import Assembler,CPU,load_sparse
import selective_linker as linker
import selective_trig8 as trig

ENTRY={
    "MATH_SIN8":"FAST_SIN8",
    "MATH_COS8":"FAST_COS8",
    "MATH_SINCOS8":"FAST_SINCOS8",
}
CODE_BYTES={
    "MATH_SIN8":11,
    "MATH_COS8":15,
    "MATH_SINCOS8":22,
}
ID="link:resident-shared-table"
BASIS="v1-v5-shared-trig8-exact-public-256-v1"
COUNT=256


def benchmark(api:str,modules,code:int,io:int,unused:int,root:Path):
    if api not in ENTRY or set(modules)!={ID}:
        raise ValueError("Trig public module variant set changed")
    mod=modules[ID]
    if (mod["source"]!="routines/trig/"+api[5:].lower()+"_shared.asm"
        or mod["segments"]!=(("KERNEL_CODE",CODE_BYTES[api]),)
        or mod["entry"]!=ENTRY[api] or mod["zp"]!=0 or mod["scratch"]!=0
        or not mod.get("trig8")):
        raise ValueError("Canonical V1-V5 trig source/resource contract drift")
    table_base=trig.align_page(code+CODE_BYTES[api])
    if table_base+256>65536:
        raise ValueError("Trig table cannot fit")
    locations={"KERNEL_CODE":code,"SINE_TAB":table_base,
               "INPUT_X":io,"OUTPUT_Z":io+8}
    image,labels,_=Assembler().assemble(
        linker.relocate_source(mod,locations,root))
    if labels.get(mod["entry"])!=code or len(image)!=CODE_BYTES[api] or (
            set(image)!=set(range(code,code+CODE_BYTES[api]))):
        raise ValueError("Historical trig instruction geometry drift")
    image.update(trig.emit(table_base))
    cpu=CPU(load_sparse(image))
    sp=cpu.sp
    before=bytes(cpu.mem[code:code+CODE_BYTES[api]])
    table_before=bytes(cpu.mem[table_base:table_base+256])
    cycles=[]
    for phase in range(COUNT):
        cpu.mem[io]=phase
        cpu.mem[io+4]=0x5f
        cpu.mem[io+8]=0x55
        cpu.mem[io+9]=0x5a
        cpu.a=(phase*3)&255
        cpu.x=(phase^0x6a)&255
        cpu.y=(phase+31)&255
        cpu.c=phase&1
        cpu.d=0
        count=cpu.call(code,3000)
        expect=(trig.SINE_BYTES[(phase+64)&255]
                if api=="MATH_COS8" else trig.SINE_BYTES[phase])
        expected_high=(trig.SINE_BYTES[(phase+64)&255]
                       if api=="MATH_SINCOS8" else 0x5a)
        if ((cpu.mem[io+8],cpu.mem[io+9])!=(expect,expected_high)
            or (cpu.mem[io],cpu.mem[io+4])!=(phase,0x5f)
            or cpu.c!=0 or cpu.sp!=sp):
            raise ValueError("V1-V5 trig complete public ABI mismatch: "+
                  repr((api,hex(code),phase)))
        cycles.append(count)
    if (bytes(cpu.mem[code:code+CODE_BYTES[api]])!=before or
        bytes(cpu.mem[table_base:table_base+256])!=table_before):
        raise ValueError("Trig source mutated code/immutable table")
    return {
        "basis":BASIS,"cases":COUNT,
        "corpus_sha256":hashlib.sha256(bytes(range(COUNT))).hexdigest(),
        "mean_cycles":{ID:sum(cycles)/COUNT},
        "maximum_cycles":{ID:max(cycles)},
        "p95_cycles":{ID:sorted(cycles)[int(COUNT*.95)-1]},
        "source_sha256":{ID:hashlib.sha256(
            (root/mod["source"]).read_bytes()).hexdigest()},
        "cpu_model_only":True,
        "table_sha256":hashlib.sha256(trig.SINE_BYTES).hexdigest(),
        "code_origin":"$%04X"%code,
        "table_origin":"$%04X"%table_base,
        "io_origin":"$%04X"%io,
        "operation":api,
        "note":"Same complete phase-byte public ABI; original source only, one V1-V5 shared immutable sine plane; not physical PAL timing"
    }


def bench_sin8(modules,code,io,scratch,root):
    return benchmark("MATH_SIN8",modules,code,io,scratch,root)


def bench_cos8(modules,code,io,scratch,root):
    return benchmark("MATH_COS8",modules,code,io,scratch,root)


def bench_sincos8(modules,code,io,scratch,root):
    return benchmark("MATH_SINCOS8",modules,code,io,scratch,root)


if __name__=="__main__":
    for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
        for api in ENTRY:
            result=benchmark(api,linker.MODULES[api],code,io,0,Path(__file__).resolve().parents[1])
            print("TRIG8 MATCHED SOURCE",api,hex(code),
                  result["mean_cycles"],result["maximum_cycles"],flush=True)
