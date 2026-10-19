#!/usr/bin/env python3
"""Source-linked V2 fast split-tail 32/16 magnitude for signed 16<<8 division.

The canonical historical V2 unsigned 32/16 source is included verbatim by
selective_v2_fast_u3216; this file adds a dedicated 16-bit signed public
adapter. It stages abs(N16)<<8 directly in the original twelve-ZP donor
state rather than calling a restoring portable 24/16 loop.

The fixed 24-bit signed quotient wraps modulo 2^24 and signed remainder
has the original numerator sign. D=0 returns Q24=R16=0 and C=1.
Preserves public N0..3, D0..3, Q3, R2..3, and stack depth.
Only the canonical source's existing NMOS LAX/ANC opcodes are used.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
from mini6502 import Assembler
import selective_v2_fast_u3216 as v2

ROOT=Path(__file__).resolve().parents[1]
ENTRY="FAST_SDIV16_SHL8_V2"
SIGNED_OFFSET=v2.IMAGE_BYTES
SIGNED_SLOT=0x100
IMAGE_BYTES=SIGNED_OFFSET+SIGNED_SLOT

SIGNED_BODY="""
FAST_SDIV16_SHL8_V2:
    lda INPUT_DIV
    ora INPUT_DIV+1
    bne SHL16_NONZERO
    jmp SHL16_DIV_ZERO
SHL16_NONZERO:
    lda #$00
    sta ln0
    sta n1
    lda INPUT_NUM+1
    bmi SHL16_N_NEG
SHL16_N_POS:
    lda INPUT_NUM
    sta ln1
    lda INPUT_NUM+1
    sta n0
    jmp SHL16_N_DONE
SHL16_N_NEG:
    lda #$00
    sec
    sbc INPUT_NUM
    sta ln1
    lda #$00
    sbc INPUT_NUM+1
    sta n0
SHL16_N_DONE:
    lda INPUT_DIV+1
    bmi SHL16_D_NEG
SHL16_D_POS:
    lda INPUT_DIV
    sta d0
    lda INPUT_DIV+1
    sta d1
    jmp SHL16_D_DONE
SHL16_D_NEG:
    lda #$00
    sec
    sbc INPUT_DIV
    sta d0
    lda #$00
    sbc INPUT_DIV+1
    sta d1
SHL16_D_DONE:
    jsr div_u32_16
    lda INPUT_NUM+1
    eor INPUT_DIV+1
    bmi SHL16_Q_NEG
SHL16_Q_POS:
    lda lq0
    sta OUTPUT_QUOT
    lda lq1
    sta OUTPUT_QUOT+1
    lda q0
    sta OUTPUT_QUOT+2
    jmp SHL16_Q_DONE
SHL16_Q_NEG:
    lda #$00
    sec
    sbc lq0
    sta OUTPUT_QUOT
    lda #$00
    sbc lq1
    sta OUTPUT_QUOT+1
    lda #$00
    sbc q0
    sta OUTPUT_QUOT+2
SHL16_Q_DONE:
    lda INPUT_NUM+1
    bmi SHL16_R_NEG
SHL16_R_POS:
    lda r0
    sta OUTPUT_REM
    lda r1
    sta OUTPUT_REM+1
    clc
    rts
SHL16_R_NEG:
    lda #$00
    sec
    sbc r0
    sta OUTPUT_REM
    lda #$00
    sbc r1
    sta OUTPUT_REM+1
    clc
    rts
SHL16_DIV_ZERO:
    lda #$00
    sta OUTPUT_QUOT
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    sta OUTPUT_REM
    sta OUTPUT_REM+1
    sec
    rts
"""


def render(code:int,io:int,zp:int,root:Path=ROOT)->str:
    if not 0x1000<=code<=0x10000-IMAGE_BYTES:
        raise ValueError("V2 shifted signed source exceeds user RAM")
    return (v2.render(code,io,zp,root)+"\n* = $%04X\n"%(code+SIGNED_OFFSET)
            +SIGNED_BODY)


def assemble_image(code:int,io:int,zp:int,root:Path=ROOT):
    sparse,labels,_=Assembler().assemble(render(code,io,zp,root))
    donor,donor_labels,_=v2.assemble(code,io,zp,root)
    if any(sparse.get(addr)!=byte for addr,byte in donor.items()):
        raise ValueError("Canonical V2 unsigned donor changed")
    if labels.get(ENTRY)!=code+SIGNED_OFFSET:
        raise ValueError("Signed shifted public entry moved")
    signed=[a for a in sparse if a>=code+SIGNED_OFFSET]
    if (not signed or min(signed)!=code+SIGNED_OFFSET
        or max(signed)>=code+IMAGE_BYTES
        or sorted(signed)!=list(range(min(signed),max(signed)+1))):
        raise ValueError("Signed shifted source overflows slot")
    packed={a:0xea for a in range(code,code+IMAGE_BYTES)}
    packed.update(sparse)
    return packed,labels,[{"name":"KERNEL_CODE",
        "start":"$%04X"%code,"bytes":IMAGE_BYTES}],code+IMAGE_BYTES


def provenance(root:Path=ROOT):
    return {"canonical_v2_unsigned_sha256":v2.source_sha256(root),
            "signed_relocator_sha256":hashlib.sha256(
                (root/"tools/selective_v2_signed_shifted16.py").read_bytes()).hexdigest()}


if __name__=="__main__":
    for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
        memory,labels,_,end=assemble_image(code,io,zp)
        print("SIGNED V2 SHL16",hex(code),len(memory),
              hex(labels[ENTRY]),hex(end),flush=True)
