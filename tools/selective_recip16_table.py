#!/usr/bin/env python3
"""Exact stock C64 Q16 reciprocal, three direct tables + threshold bisection.

For denominator 1..255, use exact 24-bit quotient tables (3*256 bytes).
For denominator 256, Q24=256. For >=257, quotient is 1..255 and is
recovered by eight 16-bit comparisons against floor(65536/k), k=1..255,
stored as two 256-byte threshold pages. This is a new stock-C64
realization of the old V3/V4 integer-threshold reciprocal idea, NOT a
relocation of V3/V4's REU routine. No REU or ZP; no code modification.

Source-linked output preserves Q3, R0..R3, divisor and all sentinels.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from mini6502 import Assembler

ROOT=Path(__file__).resolve().parents[1]
DONOR="v3_reu_512k/standalone/recip_u16_u24_q16.asm"
ENTRY="FAST_URECIP16_Q16_TABLE"
CODE_SLOT=256
DATA_BYTES=5*256+8
IMAGE_BYTES=CODE_SLOT+DATA_BYTES


def render(code: int, io: int) -> str:
    h=[
       "!cpu 6510",
       "KERNEL_CODE = $%04X"%code,
       "INPUT_DIV = $%04X"%(io+20),
       "OUTPUT_QUOT = $%04X"%(io+24),
       "* = KERNEL_CODE",
       ENTRY+":",
       "    lda INPUT_DIV+1",
       "    bne RECIP_TABLE_LARGE",
       "    lda INPUT_DIV",
       "    beq RECIP_TABLE_ZERO",
       "    tax",
       "    lda RECIP_QLO,x",
       "    sta OUTPUT_QUOT",
       "    lda RECIP_QMID,x",
       "    sta OUTPUT_QUOT+1",
       "    lda RECIP_QHI,x",
       "    sta OUTPUT_QUOT+2",
       "    clc",
       "    rts",
       "RECIP_TABLE_LARGE:",
       "    cmp #$01",
       "    bne RECIP_TABLE_BINARY",
       "    lda INPUT_DIV",
       "    bne RECIP_TABLE_BINARY",
       "    lda #$00",
       "    sta OUTPUT_QUOT",
       "    sta OUTPUT_QUOT+2",
       "    lda #$01",
       "    sta OUTPUT_QUOT+1",
       "    clc",
       "    rts",
       "RECIP_TABLE_BINARY:",
       "    lda #$00",
       "    sta OUTPUT_QUOT",
       "    ldx #$07",
       "RECIP_TABLE_STEP:",
       "    lda RECIP_POWERS,x",
       "    ora OUTPUT_QUOT",
       "    tay",
       "    lda INPUT_DIV+1",
       "    cmp RECIP_THI,y",
       "    bcc RECIP_TABLE_TAKE",
       "    bne RECIP_TABLE_SKIP",
       "    lda INPUT_DIV",
       "    cmp RECIP_TLO,y",
       "    bcc RECIP_TABLE_TAKE",
       "    bne RECIP_TABLE_SKIP",
       "RECIP_TABLE_TAKE:",
       "    sty OUTPUT_QUOT",
       "RECIP_TABLE_SKIP:",
       "    dex",
       "    bpl RECIP_TABLE_STEP",
       "    lda #$00",
       "    sta OUTPUT_QUOT+1",
       "    sta OUTPUT_QUOT+2",
       "    clc",
       "    rts",
       "RECIP_TABLE_ZERO:",
       "    lda #$00",
       "    sta OUTPUT_QUOT",
       "    sta OUTPUT_QUOT+1",
       "    sta OUTPUT_QUOT+2",
       "    sec",
       "    rts",
    ]
    tables={}
    for name,shift in (("RECIP_QLO",0),("RECIP_QMID",8),("RECIP_QHI",16)):
        tables[name]=[((65536//d if d else 0)>>shift)&255
                      for d in range(256)]
    ts=[65535 if k<2 else 65536//k for k in range(256)]
    tables["RECIP_TLO"]=[v&255 for v in ts]
    tables["RECIP_THI"]=[v>>8 for v in ts]
    tables["RECIP_POWERS"]=[1<<k for k in range(8)]
    at=code+CODE_SLOT
    for name,values in tables.items():
        h.append("* = $%04X"%at)
        h.append(name+":")
        for i in range(0,len(values),16):
            h.append("    !byte "+", ".join("$%02X"%x for x in values[i:i+16]))
        at+=len(values)
    if at!=code+IMAGE_BYTES:
        raise ValueError("Reciprocal table footprint changed")
    return "\n".join(h)+"\n"


def assemble_image(code:int,io:int,root:Path=ROOT):
    if not 0x200<=code<0x10000-IMAGE_BYTES:
        raise ValueError("Table-backed reciprocal code origin outside RAM")
    if not 0x200<=io<=0x10000-32:
        raise ValueError("Table-backed reciprocal I/O outside RAM")
    memory,labels,_=Assembler().assemble(render(code,io))
    if labels.get(ENTRY)!=code:
        raise ValueError("Table-backed reciprocal public entry moved")
    if not all(code<=addr<code+IMAGE_BYTES for addr in memory):
        raise ValueError("Reciprocal source escaped reserved image")
    code_addresses=[x for x in memory if code<=x<code+CODE_SLOT]
    if not code_addresses or max(code_addresses)>=code+CODE_SLOT:
        raise ValueError("Reciprocal code island overflow")
    expected_tables=set(range(code+CODE_SLOT,code+IMAGE_BYTES))
    if not expected_tables.issubset(memory):
        raise ValueError("Reciprocal threshold tables incomplete")
    packed={addr:0xea for addr in range(code,code+IMAGE_BYTES)}
    packed.update(memory)
    return packed,labels,[{"name":"KERNEL_CODE",
                           "start":"$%04X"%code,"bytes":IMAGE_BYTES}],code+IMAGE_BYTES


def provenance(root:Path=ROOT):
    return hashlib.sha256((root/DONOR).read_bytes()).hexdigest()


if __name__=="__main__":
    for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
        image,labels,_,end=assemble_image(code,io)
        print("RECIP16 EXACT TABLE",hex(code),"bytes",len(image),
              "entry",hex(labels[ENTRY]),"end",hex(end),flush=True)
