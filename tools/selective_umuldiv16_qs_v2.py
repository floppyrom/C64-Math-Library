#!/usr/bin/env python3
"""Unsigned 16x16 full product / 16 quotient, direct historical fast fusion.

This source-linked experiment connects the *unchanged* 233-byte quarter-
square unsigned 16x16 producer (with two immutable 511-byte table planes)
to the unchanged canonical V2 32/16 split-tail divider, rather than linking
the very slow 288-byte restoring portable compound operation.

Both component sources retain their native binary ABI and table layouts.
The public UMULDIV16 entry composes them by copying Z32 to volatile N32
before V2 division. X16/Y16/D16 remain untouched. D=0 means Q32/R16=0,
C=1; otherwise Q32=floor((X*Y)/D), R16=(X*Y)%D and C=0. Z and N are
publicly volatile; Q/R high sentinel bytes and caller stack preserved.
"""
from __future__ import annotations

from pathlib import Path
from mini6502 import Assembler
import selective_fast_umul16 as umul
import selective_v2_fast_u3216 as udiv

ROOT=Path(__file__).resolve().parents[1]
ENTRY="FAST_UMULDIV16_QS_V2"
POST_BYTES=32
IMAGE_BYTES=umul.CODE_BYTES+umul.TABLE_BYTES*2+udiv.IMAGE_BYTES+POST_BYTES


def render_entry(code:int,io:int,umul_entry:int,udiv_entry:int)->str:
    return f"""!cpu 6510
OUTPUT_Z = ${io+8:04X}
INPUT_NUM = ${io+16:04X}
* = ${code:04X}
{ENTRY}:
    jsr ${umul_entry:04X}
    ldx #$03
MULDIV16_COPY_Z_TO_N:
    lda OUTPUT_Z,x
    sta INPUT_NUM,x
    dex
    bpl MULDIV16_COPY_Z_TO_N
    jsr ${udiv_entry:04X}
    rts
"""


def assemble_image(code:int,io:int,zp:int,scratch:int,root:Path=ROOT):
    if not 0x200<=code<=0x10000-IMAGE_BYTES:
        raise ValueError("Fused unsigned 16x16/16 code origin invalid")
    if not 0x200<=io<=0x10000-32:
        raise ValueError("Fused unsigned 16x16/16 public ABI outside RAM")
    if not 0x02<=zp<=0xf4:
        raise ValueError("V2 divider must own 12 non-port zero-page bytes")
    if not 0x0200<=scratch<=0xffff-4:
        raise ValueError("QS16 scratch outside RAM")
    multiply,entry,ranges,end_mul=umul.assemble(
        code,io,scratch,root)
    div,labels,div_ranges,end_div=udiv.assemble_image(
        end_mul,io,zp,root)
    if entry!=code or end_div!=code+IMAGE_BYTES-POST_BYTES:
        raise ValueError("Canonical multiplication/division producer layouts drifted")
    adapter,entry_labels,_=Assembler().assemble(
        render_entry(end_div,io,entry,labels[udiv.PUB_ENTRY]))
    if (entry_labels.get(ENTRY)!=end_div or not adapter
        or min(adapter)!=end_div
        or max(adapter)>=end_div+POST_BYTES
        or set(adapter)!=set(range(end_div,max(adapter)+1))):
        raise ValueError("Fused compound public entry does not fit 32-byte slot")
    image={addr:0xea for addr in range(code,code+IMAGE_BYTES)}
    for part in (multiply,div,adapter):
        for addr,val in part.items():
            if addr not in image:
                raise ValueError("Fused source outside packed image")
            image[addr]=val
    return (image,entry_labels,
            ranges+[{"name":"HISTORICAL_V2_DIVIDER",
                      "start":"$%04X"%end_mul,"bytes":udiv.IMAGE_BYTES},
                    {"name":"MULDIV16_PUBLIC_ENTRY",
                      "start":"$%04X"%end_div,"bytes":POST_BYTES}],
            code+IMAGE_BYTES)


if __name__=="__main__":
    for code,io,zp,scratch in ((0x8000,0xc000,0x50,0xc040),
                              (0x7123,0xc040,0x70,0xc080)):
        image,labels,ranges,end=assemble_image(code,io,zp,scratch)
        print("UMULDIV16 QS+V2 fused",hex(code),"image",len(image),
              "entry",hex(labels[ENTRY]),"end",hex(end),flush=True)
