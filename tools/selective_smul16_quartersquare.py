#!/usr/bin/env python3
"""Relocatable signed 16x16=>32 using the canonical unsigned QS producer.

The original UMUL16 233-byte quarter-square code and two 511-byte tables
are source-assembled unchanged. A bounded separate public entry performs
the exact two's-complement high-word corrections; neither caller operand
nor scratch semantics of the unsigned producer are changed.

Signed X*Y = unsigned X*Y - (X<0 ? Y<<16 : 0)
                          - (Y<0 ? X<<16 : 0) modulo 2**32.
Zero ZP, four ordinary scratch bytes, no SMC/REU/INIT. D=0.
"""
from __future__ import annotations
from pathlib import Path
import hashlib

from mini6502 import Assembler
import selective_fast_umul16 as unsigned

ROOT=Path(__file__).resolve().parents[1]
ENTRY="FAST_SMUL16_QUARTERSQUARE"
SIGNED_SLOT=96
IMAGE_BYTES=unsigned.CODE_BYTES+2*unsigned.TABLE_BYTES+SIGNED_SLOT


def render_adapter(address: int, code: int, io: int) -> str:
    return f"""!cpu 6502
INPUT_X = ${io:04X}
INPUT_Y = ${io+4:04X}
OUTPUT_Z = ${io+8:04X}
* = ${address:04X}
{ENTRY}:
    jsr ${code:04X}
    lda INPUT_X+1
    bpl QS_SIGN_X_DONE
    sec
    lda OUTPUT_Z+2
    sbc INPUT_Y
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    sbc INPUT_Y+1
    sta OUTPUT_Z+3
QS_SIGN_X_DONE:
    lda INPUT_Y+1
    bpl QS_SIGN_Y_DONE
    sec
    lda OUTPUT_Z+2
    sbc INPUT_X
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    sbc INPUT_X+1
    sta OUTPUT_Z+3
QS_SIGN_Y_DONE:
    clc
    rts
"""


def assemble_image(code: int, io: int, scratch: int, root: Path = ROOT):
    if not 0x0200 <= code <= 0x10000-IMAGE_BYTES:
        raise ValueError("Signed QS image outside RAM")
    if not 0x0200 <= io <= 0x10000-32:
        raise ValueError("Signed QS public I/O outside RAM")
    if not 0x0200 <= scratch <= 0xffff-4:
        raise ValueError("Signed QS scratch outside RAM")
    base, uentry, uranges, after_tables = unsigned.assemble(
        code, io, scratch, root)
    if uentry != code or after_tables != code+IMAGE_BYTES-SIGNED_SLOT:
        raise ValueError("Canonical UMUL16 QS geometry changed")
    sub, labels, _ = Assembler().assemble(
        render_adapter(after_tables,code,io))
    if labels.get(ENTRY)!=after_tables:
        raise ValueError("Signed QS public entry moved")
    if not sub or min(sub)!=after_tables or max(sub)>=after_tables+SIGNED_SLOT:
        raise ValueError("Signed QS adapter does not fit its independent slot")
    if sorted(sub)!=list(range(after_tables,max(sub)+1)):
        raise ValueError("Signed QS source is noncontiguous")
    image={a:0xea for a in range(code,code+IMAGE_BYTES)}
    image.update(base)
    image.update(sub)
    return (image, labels,
        uranges+[{"name":"SIGNED_ADAPTER","start":"$%04X"%after_tables,
                  "bytes":SIGNED_SLOT}],code+IMAGE_BYTES)


def provenance(root:Path=ROOT):
    return {
        "unsigned_qs_source_sha256":unsigned.source_sha256(root),
        "fast16_relocator_sha256":hashlib.sha256(
            (root/"tools/selective_fast_umul16.py").read_bytes()).hexdigest(),
        "fast8_table_sha256":hashlib.sha256(
            (root/"tools/selective_fast_umul8.py").read_bytes()).hexdigest(),
    }


if __name__=="__main__":
    for code,io,scratch in ((0x8000,0xc000,0xc040),
                             (0x7123,0xc040,0xc080)):
        image,labels,_,end=assemble_image(code,io,scratch)
        print("SMUL16 QS SIGNED",hex(code),len(image),
              "entry",hex(labels[ENTRY]),"end",hex(end),flush=True)
