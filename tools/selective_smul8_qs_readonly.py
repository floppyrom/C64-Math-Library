#!/usr/bin/env python3
"""Stock-C64 signed 8x8 -> 16 from canonical no-SMC unsigned quarter-square.

Reuse the 73-byte UMUL8 QS producer and 511-byte LO/HI table planes
unaltered, and correct only the high signed product byte:
  signed(X)*signed(Y) = unsigned(X)*unsigned(Y)
    - (X & 0x80 ? unsigned(Y)<<8 : 0)
    - (Y & 0x80 ? unsigned(X)<<8 : 0) modulo 2^16.

Unlike the historic 46-byte V1 SMC source with four 511-entry tables,
this image is read-only code and data, needs no ZP, and uses just
two ordinary scratch bytes. It preserves X/Y, Z+2.. and stack depth.
"""
from __future__ import annotations
from pathlib import Path
from mini6502 import Assembler
import selective_fast_umul8 as fast8

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "FAST_SMUL8_QS_READONLY"
ADAPTER_BYTES = 64
IMAGE_BYTES = fast8.CODE_BYTES + 2*fast8.TABLE_ENTRIES + ADAPTER_BYTES


def render_adapter(addr:int, unsigned_entry:int, io:int):
    return f"""!cpu 6502
INPUT_X = ${io:04X}
INPUT_Y = ${io+4:04X}
OUTPUT_Z = ${io+8:04X}
* = ${addr:04X}
{ENTRY}:
    jsr ${unsigned_entry:04X}
    lda INPUT_X
    bpl QS_SIGN8_X_DONE
    sec
    lda OUTPUT_Z+1
    sbc INPUT_Y
    sta OUTPUT_Z+1
QS_SIGN8_X_DONE:
    lda INPUT_Y
    bpl QS_SIGN8_Y_DONE
    sec
    lda OUTPUT_Z+1
    sbc INPUT_X
    sta OUTPUT_Z+1
QS_SIGN8_Y_DONE:
    clc
    rts
"""


def assemble_image(code:int,io:int,scratch:int,root:Path=ROOT):
    if not 0x0200<=code<=0x10000-IMAGE_BYTES:
        raise ValueError("SMUL8 QS code/data image outside RAM")
    if not 0x0200<=io<=0x10000-32:
        raise ValueError("SMUL8 QS input/output outside RAM")
    if not 0x0200<=scratch<=0xffff-2:
        raise ValueError("SMUL8 QS scratch outside RAM")
    original, unsigned_entry, ranges, end = fast8.assemble(
        code,io,scratch,root)
    if unsigned_entry!=code or end!=code+IMAGE_BYTES-ADAPTER_BYTES:
        raise ValueError("Canonical unsigned 8bit QS geometry drifted")
    signed,labels,_=Assembler().assemble(render_adapter(end,code,io))
    if labels.get(ENTRY)!=end or not signed or min(signed)!=end:
        raise ValueError("Signed 8bit QS entry invalid")
    if max(signed)>=code+IMAGE_BYTES:
        raise ValueError("Signed 8bit QS adapter exceeds reserved size")
    if set(signed)!=set(range(end,max(signed)+1)):
        raise ValueError("Signed 8bit QS adapter non-contiguous")
    packed={i:0xea for i in range(code,code+IMAGE_BYTES)}
    packed.update(original)
    packed.update(signed)
    return packed,labels,ranges+[{
        "name":"SIGNED8_ADAPTER","start":"$%04X"%end,"bytes":ADAPTER_BYTES
    }],code+IMAGE_BYTES


if __name__=="__main__":
    for code,io,scratch in ((0x8000,0xc000,0xc040),(0x7123,0xc040,0xc080)):
        image,labels,ranges,end=assemble_image(code,io,scratch)
        print("SMUL8 READONLY QS",hex(code),len(image),
              hex(labels[ENTRY]),hex(end),flush=True)
