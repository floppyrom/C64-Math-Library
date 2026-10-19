#!/usr/bin/env python3
"""Signed 16x16 full32 / signed16: canonical quarter-square plus V2 divider.

Source-composes the already independently qualified signed 16x16 producer
and the historical V2 signed 32/16 divider. Both donors and their private
ZP and immutable table contents remain unchanged; the adapter copies Z32
into the public volatile N32 then calls signed Q32/R16/C. Dividend,
quotient and remainder obey truncation toward zero.

This is an independently linkable *candidate*, not yet a code-coalesced
shared producer for multi-operation builds. No V1-V5 images are modified.
"""
from __future__ import annotations

from pathlib import Path
from mini6502 import Assembler
import selective_smul16_quartersquare as mul
import research_signed_v2_u3216 as div

ROOT=Path(__file__).resolve().parents[1]
ENTRY="FAST_SMULDIV16_SIGNED_QS_V2"
ADAPTER_BYTES=32
IMAGE_BYTES=mul.IMAGE_BYTES+div.IMAGE_BYTES+ADAPTER_BYTES


def render_entry(code:int,io:int,mul_entry:int,div_entry:int):
    return f"""!cpu 6510
OUTPUT_Z = ${io+8:04X}
INPUT_NUM = ${io+16:04X}
* = ${code:04X}
{ENTRY}:
    jsr ${mul_entry:04X}
    ldx #$03
SIGNED_MULDIV_COPY_Z_TO_N:
    lda OUTPUT_Z,x
    sta INPUT_NUM,x
    dex
    bpl SIGNED_MULDIV_COPY_Z_TO_N
    jsr ${div_entry:04X}
    rts
"""


def assemble_image(code:int,io:int,zp:int,scratch:int,root:Path=ROOT):
    if not 0x1000<=code<=0x10000-IMAGE_BYTES:
        raise ValueError("Signed muldiv source outside RAM")
    if not 0x200<=io<=0x10000-32:
        raise ValueError("Signed muldiv public I/O outside RAM")
    if not 2<=zp<=0xf4:
        raise ValueError("Signed V2 divider requires 12 reserved ZP bytes")
    if not 0x200<=scratch<=0xffff-4:
        raise ValueError("Signed quarter-square scratch outside RAM")
    multiplied,mul_labels,mul_ranges,end_mul=mul.assemble_image(
        code,io,scratch,root)
    divided,div_labels,metadata=div.assemble(end_mul,io,zp,root)
    end_div=end_mul+div.IMAGE_BYTES
    if (end_mul!=code+mul.IMAGE_BYTES or
        metadata["image_span_bytes"]!=div.IMAGE_BYTES):
        raise ValueError("Signed canonical source layouts drifted")
    extra,extra_labels,_=Assembler().assemble(render_entry(
        end_div,io,mul_labels[mul.ENTRY],div_labels[div.ENTRY]))
    if (extra_labels.get(ENTRY)!=end_div or not extra
        or min(extra)!=end_div or max(extra)>=end_div+ADAPTER_BYTES
        or set(extra)!=set(range(end_div,max(extra)+1))):
        raise ValueError("Signed muldiv direct adapter exceeds reserved slot")
    image={addr:0xea for addr in range(code,code+IMAGE_BYTES)}
    for part in (multiplied,divided,extra):
        for addr,value in part.items():
            if addr not in image:
                raise ValueError("Signed compound source overflow")
            image[addr]=value
    return (image,extra_labels,
        mul_ranges+[{"name":"HISTORICAL_SIGNED_V2_DIVIDER",
            "start":"$%04X"%end_mul,"bytes":div.IMAGE_BYTES},
            {"name":"SIGNED_MULDIV_PUBLIC_ENTRY",
            "start":"$%04X"%end_div,"bytes":ADAPTER_BYTES}],
        code+IMAGE_BYTES)


if __name__=="__main__":
    for code,io,zp,scratch in ((0x8000,0xc000,0x50,0xc040),
                               (0x7123,0xc040,0x70,0xc080)):
        image,labels,ranges,end=assemble_image(code,io,zp,scratch)
        print("SMULDIV16 SIGNED QS+V2",hex(code),"image",len(image),
              "entry",hex(labels[ENTRY]),"end",hex(end),flush=True)
