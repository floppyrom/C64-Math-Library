#!/usr/bin/env python3
"""Signed 32/32 Q32/R32/C around the qualified unsigned V2 hybrid magnitude.

Relocatable, source-authenticated producer with a single shared SDIV/SMOD
public entry. Non-reentrant: reserves the unsigned hybrid's 12 ZP bytes.
No new tables or SMC. Original V1–V5 code remains unchanged.
"""
from __future__ import annotations
from pathlib import Path
from mini6502 import Assembler
import selective_hybrid_u3232 as unsigned

ROOT=Path(__file__).resolve().parents[1]
UNSIGNED_BYTES=unsigned.IMAGE_BYTES
WRAPPER_BYTES=0x180
IMAGE_BYTES=UNSIGNED_BYTES+WRAPPER_BYTES
ZP_BYTES=unsigned.ZP_BYTES
PUBLIC_DIV="FAST_SDIV32_32_V2MAG"
PUBLIC_MOD="FAST_SMOD32_32_V2MAG"


def render(code,io,unsigned_entry):
    origin=code+UNSIGNED_BYTES
    return f"""!cpu 6510
INPUT_NUM = $%04X
INPUT_DIV = $%04X
OUTPUT_QUOT = $%04X
OUTPUT_REM = $%04X
UNSIGNED_DIV = $%04X
* = $%04X
%s:
%s:
    lda INPUT_DIV
    ora INPUT_DIV+1
    ora INPUT_DIV+2
    ora INPUT_DIV+3
    bne DIVISOR_NONZERO
    jmp UNSIGNED_DIV
DIVISOR_NONZERO:
    lda INPUT_NUM+3
    pha
    lda INPUT_DIV+3
    pha
    lda INPUT_NUM+3
    bpl N_POSITIVE
    lda #0
    sec
    sbc INPUT_NUM
    sta INPUT_NUM
    lda #0
    sbc INPUT_NUM+1
    sta INPUT_NUM+1
    lda #0
    sbc INPUT_NUM+2
    sta INPUT_NUM+2
    lda #0
    sbc INPUT_NUM+3
    sta INPUT_NUM+3
N_POSITIVE:
    lda INPUT_DIV+3
    bpl D_POSITIVE
    lda #0
    sec
    sbc INPUT_DIV
    sta INPUT_DIV
    lda #0
    sbc INPUT_DIV+1
    sta INPUT_DIV+1
    lda #0
    sbc INPUT_DIV+2
    sta INPUT_DIV+2
    lda #0
    sbc INPUT_DIV+3
    sta INPUT_DIV+3
D_POSITIVE:
    jsr UNSIGNED_DIV
    pla
    bpl D_RESTORED
    lda #0
    sec
    sbc INPUT_DIV
    sta INPUT_DIV
    lda #0
    sbc INPUT_DIV+1
    sta INPUT_DIV+1
    lda #0
    sbc INPUT_DIV+2
    sta INPUT_DIV+2
    lda #0
    sbc INPUT_DIV+3
    sta INPUT_DIV+3
D_RESTORED:
    pla
    bpl N_RESTORED
    lda #0
    sec
    sbc INPUT_NUM
    sta INPUT_NUM
    lda #0
    sbc INPUT_NUM+1
    sta INPUT_NUM+1
    lda #0
    sbc INPUT_NUM+2
    sta INPUT_NUM+2
    lda #0
    sbc INPUT_NUM+3
    sta INPUT_NUM+3
N_RESTORED:
    lda INPUT_NUM+3
    eor INPUT_DIV+3
    bpl Q_SIGN_READY
    lda #0
    sec
    sbc OUTPUT_QUOT
    sta OUTPUT_QUOT
    lda #0
    sbc OUTPUT_QUOT+1
    sta OUTPUT_QUOT+1
    lda #0
    sbc OUTPUT_QUOT+2
    sta OUTPUT_QUOT+2
    lda #0
    sbc OUTPUT_QUOT+3
    sta OUTPUT_QUOT+3
Q_SIGN_READY:
    lda INPUT_NUM+3
    bpl R_SIGN_READY
    lda #0
    sec
    sbc OUTPUT_REM
    sta OUTPUT_REM
    lda #0
    sbc OUTPUT_REM+1
    sta OUTPUT_REM+1
    lda #0
    sbc OUTPUT_REM+2
    sta OUTPUT_REM+2
    lda #0
    sbc OUTPUT_REM+3
    sta OUTPUT_REM+3
R_SIGN_READY:
    clc
    rts
""" % (io+16,io+20,io+24,io+28,unsigned_entry,origin,
       PUBLIC_DIV,PUBLIC_MOD)


def assemble(code,io,zp,root=ROOT):
    if not 0x0200 <= code or code+IMAGE_BYTES>0x10000:
        raise ValueError("Signed V2 32/32 code origin out of range")
    if not 0<=io<=0xffdf:
        raise ValueError("Signed V2 32/32 public I/O out of range")
    uimage,ulabels,_,end=unsigned.assemble(code,io,zp,root)
    if end!=code+UNSIGNED_BYTES or len(uimage)!=UNSIGNED_BYTES:
        raise ValueError("Qualified unsigned hybrid source layout changed")
    fragment,labels,_=Assembler().assemble(
        render(code,io,ulabels[unsigned.API_DIV]))
    expected=code+UNSIGNED_BYTES
    if (labels.get(PUBLIC_DIV)!=expected or labels.get(PUBLIC_MOD)!=expected
            or not set(fragment)
            or min(fragment)<expected
            or max(fragment)>=code+IMAGE_BYTES):
        raise ValueError("Signed wrapper exceeded reserved source segment")
    if set(fragment)&set(uimage):
        raise ValueError("Signed/unsigned machine code overlaps")
    image={at:0xea for at in range(code,code+IMAGE_BYTES)}
    image.update(uimage)
    image.update(fragment)
    ranges=[{"name":"KERNEL_CODE","start":"$%04X"%code,
             "bytes":IMAGE_BYTES}]
    return image,{PUBLIC_DIV:expected,PUBLIC_MOD:expected,
                  "UNSIGNED_ENTRY":ulabels[unsigned.API_DIV]},ranges,code+IMAGE_BYTES


if __name__=="__main__":
    for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
        memory,labels,ranges,end=assemble(code,io,zp)
        print("SIGNED32_32_V2_MAGNITUDE",hex(code),len(memory),labels)
