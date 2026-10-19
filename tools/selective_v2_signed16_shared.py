#!/usr/bin/env python3
"""Historical V2 unsigned 16/16 Q/R core with a direct signed public adapter.

The full canonical 1,481-byte immutable unsigned kernel is assembled from
routines/divide/udiv16_v2_zerozp.asm without edits. Its four input/output
addresses are rebound to an eight-byte ordinary RAM private workspace;
the new signed adapter normalizes N/D, calls the exact historical donor,
then signs Q/R to the public 16-bit results.

Two public exports share one code producer. The read-only source uses no
zero page, REU, writable-code tricks or initialization.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from mini6502 import Assembler

ROOT=Path(__file__).resolve().parents[1]
DONOR="routines/divide/udiv16_v2_zerozp.asm"
CANON="relocatable_source/v2_pareto_fast/udiv16_direct_fast.inc"
ENTRY_DIV="FAST_SDIV16_V2_SHARED"
ENTRY_MOD="FAST_SMOD16_V2_SHARED"
DONOR_BYTES=1481
ADAPTER_BYTES=224
IMAGE_BYTES=DONOR_BYTES+ADAPTER_BYTES
SCRATCH_BYTES=8


def render(code:int,io:int,scratch:int,root:Path=ROOT):
    original=(root/DONOR).read_text(encoding="utf-8")
    subst={
        "KERNEL_CODE = $8000":f"KERNEL_CODE = ${code:04X}",
        "INPUT_NUM = $C010":f"INPUT_NUM = ${scratch:04X}",
        "INPUT_DIV = $C014":f"INPUT_DIV = ${scratch+2:04X}",
        "OUTPUT_QUOT = $C018":f"OUTPUT_QUOT = ${scratch+4:04X}",
        "OUTPUT_REM = $C01C":f"OUTPUT_REM = ${scratch+6:04X}",
    }
    for old,new in subst.items():
        if original.count(old)!=1:
            raise ValueError("V2 donor public binding changed: "+old)
        original=original.replace(old,new)
    adapter=f"""
; Only the signed adapter uses caller public I/O addresses.
PUBLIC_NUM = ${io+16:04X}
PUBLIC_DIV = ${io+20:04X}
PUBLIC_QUOT = ${io+24:04X}
PUBLIC_REM = ${io+28:04X}
* = ${code+DONOR_BYTES:04X}
{ENTRY_DIV}:
{ENTRY_MOD}:
    lda PUBLIC_DIV
    ora PUBLIC_DIV+1
    bne V2_SIGN16_NONZERO
    jmp V2_SIGN16_ZERO
V2_SIGN16_NONZERO:
    lda PUBLIC_NUM
    sta INPUT_NUM
    lda PUBLIC_NUM+1
    sta INPUT_NUM+1
    bpl V2_SIGN16_NUM_ABS
    lda #0
    sec
    sbc INPUT_NUM
    sta INPUT_NUM
    lda #0
    sbc INPUT_NUM+1
    sta INPUT_NUM+1
V2_SIGN16_NUM_ABS:
    lda PUBLIC_DIV
    sta INPUT_DIV
    lda PUBLIC_DIV+1
    sta INPUT_DIV+1
    bpl V2_SIGN16_DIV_ABS
    lda #0
    sec
    sbc INPUT_DIV
    sta INPUT_DIV
    lda #0
    sbc INPUT_DIV+1
    sta INPUT_DIV+1
V2_SIGN16_DIV_ABS:
    jsr DU16F_div_u16
    lda PUBLIC_NUM+1
    eor PUBLIC_DIV+1
    bmi V2_SIGN16_QUOT_NEG
    lda OUTPUT_QUOT
    sta PUBLIC_QUOT
    lda OUTPUT_QUOT+1
    sta PUBLIC_QUOT+1
    jmp V2_SIGN16_Q_DONE
V2_SIGN16_QUOT_NEG:
    lda #0
    sec
    sbc OUTPUT_QUOT
    sta PUBLIC_QUOT
    lda #0
    sbc OUTPUT_QUOT+1
    sta PUBLIC_QUOT+1
V2_SIGN16_Q_DONE:
    lda PUBLIC_NUM+1
    bmi V2_SIGN16_REM_NEG
    lda OUTPUT_REM
    sta PUBLIC_REM
    lda OUTPUT_REM+1
    sta PUBLIC_REM+1
    clc
    rts
V2_SIGN16_REM_NEG:
    lda #0
    sec
    sbc OUTPUT_REM
    sta PUBLIC_REM
    lda #0
    sbc OUTPUT_REM+1
    sta PUBLIC_REM+1
    clc
    rts
V2_SIGN16_ZERO:
    lda #0
    sta PUBLIC_QUOT
    sta PUBLIC_QUOT+1
    sta PUBLIC_REM
    sta PUBLIC_REM+1
    sec
    rts
"""
    return original.rstrip()+"\n"+adapter


def assemble_image(code:int,io:int,scratch:int,root:Path=ROOT):
    if not 0x0200<=code<=0x10000-IMAGE_BYTES:
        raise ValueError("Signed16 shared V2 image exceeds address space")
    if not 0x0200<=io<=0x10000-32:
        raise ValueError("Signed16 public I/O outside address space")
    if not 0x0200<=scratch<=0x10000-SCRATCH_BYTES:
        raise ValueError("Signed16 private workspace outside address space")
    donor_source=(root/DONOR).read_text(encoding="utf-8")
    if "DU16F_div_u16" not in donor_source or "DU16F_cg_code_end:" not in donor_source:
        raise ValueError("Canonical V2 16/16 source unexpectedly changed")
    image,labels,_=Assembler().assemble(render(code,io,scratch,root))
    if labels.get(ENTRY_DIV)!=code+DONOR_BYTES or labels.get(ENTRY_MOD)!=labels[ENTRY_DIV]:
        raise ValueError("Signed shared public entry moved")
    if not image or min(image)!=code or max(image)>=code+IMAGE_BYTES:
        raise ValueError("V2 signed16 source exceeded code reservation")
    if not set(range(code+DONOR_BYTES,max(image)+1)).issubset(image):
        raise ValueError("Signed16 adapter has holes")
    packed={addr:0xea for addr in range(code,code+IMAGE_BYTES)}
    packed.update(image)
    return (packed,labels,[{"name":"KERNEL_CODE",
        "start":"$%04X"%code,"bytes":DONOR_BYTES},
        {"name":"SIGNED_ADAPTER","start":"$%04X"%(code+DONOR_BYTES),
         "bytes":ADAPTER_BYTES}],code+IMAGE_BYTES)


def provenance(root:Path=ROOT):
    return {DONOR:hashlib.sha256((root/DONOR).read_bytes()).hexdigest(),
            CANON:hashlib.sha256((root/CANON).read_bytes()).hexdigest()}


if __name__=="__main__":
    for code,io,scratch in ((0x8000,0xc000,0xc040),
                             (0x7123,0xc040,0xc080)):
        image,labels,_,end=assemble_image(code,io,scratch)
        print("V2 SIGNED16 PUBLIC SHARED",hex(code),len(image),
              hex(labels[ENTRY_DIV]),hex(end),flush=True)
