#!/usr/bin/env python3
"""Exact signed Q8.8 16x16>>8 from canonical signed full-width QS producer.

Source link the unmodified unsigned 233-byte quarter-square kernel and
two 511-byte tables, the signed high-word wrapper, and a 32-byte bounded
post-product arithmetic byte-slice. This is a private, independently
linkable public kernel until shared-source coalescing is qualified.
"""
from __future__ import annotations

from pathlib import Path
from mini6502 import Assembler
import selective_smul16_quartersquare as qs

ROOT=Path(__file__).resolve().parents[1]
ENTRY="FAST_SMUL16_SHR8_QUARTERSQUARE"
POST_SLOT=32
IMAGE_BYTES=qs.IMAGE_BYTES+POST_SLOT


def render_adapter(addr:int, prior_signed_entry:int, io:int):
    return f"""!cpu 6502
* = ${addr:04X}
{ENTRY}:
    jsr ${prior_signed_entry:04X}
    lda ${io+9:04X}
    sta ${io+8:04X}
    lda ${io+10:04X}
    sta ${io+9:04X}
    lda ${io+11:04X}
    sta ${io+10:04X}
    clc
    rts
"""


def assemble_image(code:int,io:int,scratch:int,root:Path=ROOT):
    base,labels,segments,after=qs.assemble_image(code,io,scratch,root)
    if after != code+qs.IMAGE_BYTES:
        raise ValueError("Signed QS16 base image moved")
    overlay,marked,_=Assembler().assemble(render_adapter(
        after,labels[qs.ENTRY],io))
    if marked.get(ENTRY)!=after or not overlay or max(overlay)>=after+POST_SLOT:
        raise ValueError("Signed QS16 SHR8 adapter outside its reserved slot")
    if min(overlay)!=after or sorted(overlay)!=list(range(after,max(overlay)+1)):
        raise ValueError("Signed QS16 SHR8 adapter is noncontiguous")
    image={a:0xea for a in range(code,code+IMAGE_BYTES)}
    image.update(base)
    image.update(overlay)
    return (image,{**labels,**marked},
        segments+[{"name":"SHR8_ADAPTER","start":"$%04X"%after,
                   "bytes":POST_SLOT}],code+IMAGE_BYTES)


if __name__=="__main__":
    for code,io,scratch in ((0x8000,0xc000,0xc040),(0x7123,0xc040,0xc080)):
        image,labels,segments,end=assemble_image(code,io,scratch)
        print("SMUL16 SHR8 QS PUBLIC",hex(code),len(image),
              hex(labels[ENTRY]),hex(end),flush=True)
