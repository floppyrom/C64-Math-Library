#!/usr/bin/env python3
"""Experimental unrestricted 32/32 public Q/R/C with a certified V2 low-D path.

For D < 65536, call the exact historical V2 12-ZP 32/16 public producer,
zero-extend its R16 to R32, and retain its Q32/C flag. Otherwise tail-call
the certified 4-ZP standalone full-width 32/32 quotient/remainder producer.
Both paths preserve public N32/D32 and have correct D=0 Q=R=0/C=1 semantics.

Source research only, not builder-selected or resident-profile promotion.
The combined code is independently relocated in a single 3200-byte caller-
owned RAM image with 12 shared call-exclusive ZP bytes and no RAM scratch.
The original source bytes are not silently patched with ad hoc opcodes.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

from mini6502 import Assembler
import selective_v2_fast_u3216 as v2

ROOT=Path(__file__).resolve().parents[1]
WIDE_SOURCE="routines/standalone_lab/portable/div_u32_zptail.asm"
FAST_SOURCE=v2.SOURCE

FALLBACK_OFFSET=0xA00
FALLBACK_CORE=325
FALLBACK_TAIL=219
DISPATCH_OFFSET=0xC40
IMAGE_BYTES=0xC80
ZP_BYTES=12
API_DIV="FAST_UDIV32_32_HYBRID"
API_MOD="FAST_UMOD32_32_HYBRID"

def render_wide(code,io,zp,root=ROOT):
    source=(root/WIDE_SOURCE).read_text(encoding="utf-8")
    vals={
        "KERNEL_CODE":code+FALLBACK_OFFSET,
        "KERNEL_AUX":code+FALLBACK_OFFSET+FALLBACK_CORE,
        "INPUT_NUM":io+16,"INPUT_DIV":io+20,
        "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,
        "TEMP_ZP":zp,
    }
    for key,value in vals.items():
        pat=r"(?m)^"+re.escape(key)+r"\s*=\s*\$[0-9A-Fa-f]+\s*$"
        source,n=re.subn(pat,key+" = $%04X"%value,source)
        if n!=1:
            raise ValueError("Historical full-width ZP-tail donor binding changed: "+key)
    return source

def render_dispatch(code,io,low_entry,wide_entry):
    return f"""!cpu 6510
INPUT_DIV = ${io+20:04X}
OUTPUT_REM = ${io+28:04X}
FAST_LOW = ${low_entry:04X}
FULL_WIDE = ${wide_entry:04X}
* = ${code+DISPATCH_OFFSET:04X}
{API_DIV}:
{API_MOD}:
    lda INPUT_DIV+2
    ora INPUT_DIV+3
    bne HYBRID_FULL_WIDE
    jsr FAST_LOW
    lda #$00
    sta OUTPUT_REM+2
    sta OUTPUT_REM+3
    rts
HYBRID_FULL_WIDE:
    jmp FULL_WIDE
"""

def assemble(code,io,zp,root=ROOT):
    if not 2<=zp<=0xf4:
        raise ValueError("Hybrid public core reserves 12 non-port ZP bytes")
    if code<0x0200 or code+IMAGE_BYTES>0x10000 or io+32>0x10000:
        raise ValueError("Hybrid code/IO address range exceeds 64 KiB")
    v2image,v2labels,v2segments=v2.assemble(code,io,zp,root)
    if v2labels[v2.PUB_ENTRY]!=code+v2.WRAPPER_OFFSET:
        raise ValueError("Historical 32/16 public adapter entry relocated")
    wideimage,widelabels,_=Assembler().assemble(render_wide(code,io,zp,root))
    expected_wide=set(range(code+FALLBACK_OFFSET,
                            code+FALLBACK_OFFSET+FALLBACK_CORE+FALLBACK_TAIL))
    if set(wideimage)!=expected_wide:
        raise ValueError("Historical wide ZP-tail code/tail footprint changed")
    wide_entry=widelabels["FAST_UDIV32_PUBLIC"]
    dispatch,public_labels,_=Assembler().assemble(render_dispatch(
        code,io,v2labels[v2.PUB_ENTRY],wide_entry))
    if public_labels.get(API_DIV)!=code+DISPATCH_OFFSET or (
        public_labels.get(API_MOD)!=code+DISPATCH_OFFSET):
        raise ValueError("Hybrid public Q/R entry aliases no longer coincide")
    if not all(code+DISPATCH_OFFSET<=x<code+IMAGE_BYTES for x in dispatch):
        raise ValueError("Hybrid 32/32 public adapter overflowed code slot")
    union=set()
    for name,part in (("V2 historical 32/16",v2image),
                      ("full-width ZP-tail",wideimage),
                      ("public dispatch",dispatch)):
        overlap=union.intersection(part)
        if overlap:
            raise ValueError(name+" overlaps existing emitted code")
        union.update(part)
    if not all(code<=a<code+IMAGE_BYTES for a in union):
        raise ValueError("Hybrid source code escaped allocated main RAM")
    image={a:0xea for a in range(code,code+IMAGE_BYTES)}
    image.update(v2image)
    image.update(wideimage)
    image.update(dispatch)
    ranges=[{"name":"KERNEL_CODE","start":"$%04X"%code,
             "bytes":IMAGE_BYTES}]
    labels={API_DIV:public_labels[API_DIV],
            API_MOD:public_labels[API_MOD],
            "V2_LOW_ENTRY":v2labels[v2.PUB_ENTRY],
            "WIDE_ENTRY":wide_entry}
    return image,labels,ranges,code+IMAGE_BYTES

def source_sha256(root=ROOT):
    return {
        FAST_SOURCE:hashlib.sha256((root/FAST_SOURCE).read_bytes()).hexdigest(),
        WIDE_SOURCE:hashlib.sha256((root/WIDE_SOURCE).read_bytes()).hexdigest(),
    }

if __name__=="__main__":
    for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
        mem,labels,ranges,end=assemble(code,io,zp)
        print("HYBRID FULLWIDTH",hex(code),len(mem),labels,
              "public_entry",hex(labels[API_DIV]),flush=True)
