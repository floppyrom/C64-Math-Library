#!/usr/bin/env python3
"""Generate V2 prepared-ratio research kernels.

Research contract:

    PREP(n16,d16), |n|<=|d|, d!=0
        m = round(|n|*65536/|d|)
        retain sign(n/d)
        bind m as the persistent X operand of V2 native UMUL16

    APPLY(y16)
        trunc_toward_zero(y*sign*m/65536)

The approximation has a proved integer error bound of <=1 for signed16 y.
The fast APPLY intentionally uses the V2 record UMUL16 `same_x` entry, so PREP
state is invalidated by another call that rebinds that native multiply core.
This is research code, not a stable API or lifecycle yet.
"""
from __future__ import annotations

import argparse
from pathlib import Path

N0, N1 = 0xC010, 0xC011
D0, D1 = 0xC014, 0xC015
Y0, Y1 = 0xC004, 0xC005
Z0, Z1 = 0xC008, 0xC009

RN0, RN1 = 0x10, 0x11
RD0, RD1 = 0x12, 0x13
RQ0, RQ1 = 0x14, 0x15

# V2 record UMUL16 selected-core ABI.
P0, P1, P2, P3 = 0x21, 0x23, 0x25, 0x27
P4, P5, P6, P7 = 0x29, 0x2B, 0x2D, 0x2F
UMUL_SAME_X = 0x5400
UMUL_Y1_IMM = 0x541A

# Private ordinary-RAM research state. No incremental ZP beyond existing
# unsigned-division scratch + the V2 UMUL16 core state.
RATIO_SIGN = 0xC030
RATIO_MODE = 0xC031  # 0 general, 1 zero, 2 identity
RATIO_TMPSIGN = 0xC032


def header(origin: int) -> str:
    return f"""; GENERATED PREPARED-RATIO RESEARCH SOURCE - NOT A STABLE API
N0=${N0:04X}\nN1=${N1:04X}\nD0=${D0:04X}\nD1=${D1:04X}
Y0=${Y0:04X}\nY1=${Y1:04X}\nZ0=${Z0:04X}\nZ1=${Z1:04X}
rn0=${RN0:02X}\nrn1=${RN1:02X}\nrd0=${RD0:02X}\nrd1=${RD1:02X}
rq0=${RQ0:02X}\nrq1=${RQ1:02X}
p0=${P0:02X}\np1=${P1:02X}\np2=${P2:02X}\np3=${P3:02X}
p4=${P4:02X}\np5=${P5:02X}\np6=${P6:02X}\np7=${P7:02X}
UMUL_SAMEX=${UMUL_SAME_X:04X}\nUMUL_Y1=${UMUL_Y1_IMM:04X}
RATIO_SIGN=${RATIO_SIGN:04X}\nRATIO_MODE=${RATIO_MODE:04X}
RATIO_TMPSIGN=${RATIO_TMPSIGN:04X}
.org ${origin:04X}
"""


def prep_prefix(label: str) -> str:
    p = label
    return f"""{p}:
    lda N1
    eor D1
    and #$80
    sta RATIO_SIGN

    lda N0
    sta rn0
    lda N1
    sta rn1
    bpl {p}_npos
    sec
    lda #$00
    sbc rn0
    sta rn0
    lda #$00
    sbc rn1
    sta rn1
{p}_npos:
    lda D0
    sta rd0
    lda D1
    sta rd1
    bpl {p}_dpos
    sec
    lda #$00
    sbc rd0
    sta rd0
    lda #$00
    sbc rd1
    sta rd1
{p}_dpos:
    lda rd0
    ora rd1
    bne {p}_dnonzero
    jmp {p}_error
{p}_dnonzero:
    lda rn0
    ora rn1
    bne {p}_nnonzero
    lda #$01
    sta RATIO_MODE
    clc
    rts
{p}_nnonzero:
    lda rn1
    cmp rd1
    bcc {p}_fraction
    bne {p}_bad
    lda rn0
    cmp rd0
    bcc {p}_fraction
    beq {p}_identity
{p}_bad:
    jmp {p}_error
{p}_identity:
    lda #$02
    sta RATIO_MODE
    clc
    rts
{p}_fraction:
    lda #$00
    sta RATIO_MODE
    sta rq0
    sta rq1
"""


def bind_and_finish(prefix: str) -> str:
    p = prefix
    return f"""{p}_bind:
    lda rq0
    sta p0
    sta p2
    eor #$ff
    sta p1
    sta p3
    lda rq1
    sta p4
    sta p6
    eor #$ff
    sta p5
    sta p7
    clc
    rts
{p}_error:
    lda #$00
    sta RATIO_MODE
    sec
    rts
"""


def apply_source(label: str, origin: int) -> str:
    p = label
    return f""".org ${origin:04X}
{p}:
    lda RATIO_MODE
    beq {p}_general
    cmp #$01
    beq {p}_zero
    ; identity / negate identity
    lda RATIO_SIGN
    beq {p}_copy
    sec
    lda #$00
    sbc Y0
    sta Z0
    lda #$00
    sbc Y1
    sta Z1
    clc
    rts
{p}_copy:
    lda Y0
    sta Z0
    lda Y1
    sta Z1
    clc
    rts
{p}_zero:
    lda #$00
    sta Z0
    sta Z1
    clc
    rts
{p}_general:
    lda Y1
    eor RATIO_SIGN
    and #$80
    sta RATIO_TMPSIGN

    ; abs(y), then use the pre-bound ratio as native UMUL16 X.
    lda Y1
    bpl {p}_ypos
    sec
    lda #$00
    sbc Y0
    tay
    lda #$00
    sbc Y1
    sta UMUL_Y1
    jmp {p}_mul
{p}_ypos:
    ldy Y0
    sta UMUL_Y1
{p}_mul:
    jsr UMUL_SAMEX
    ; Native result bytes are z0, X, A, Y. Only high16=A:Y is needed.
    sta Z0
    sty Z1
    lda RATIO_TMPSIGN
    beq {p}_done
    sec
    lda #$00
    sbc Z0
    sta Z0
    lda #$00
    sbc Z1
    sta Z1
{p}_done:
    clc
    rts
"""


def generate_compact(origin: int = 0xE000, apply_origin: int = 0xE800) -> str:
    p = 'ratio_prep_compact'
    out = [header(origin), prep_prefix(p)]
    out.append(f"""    ldx #16
{p}_loop:
    asl rq0
    rol rq1
    asl rn0
    rol rn1
    bcs {p}_sub
    lda rn1
    cmp rd1
    bcc {p}_next
    bne {p}_sub
    lda rn0
    cmp rd0
    bcc {p}_next
{p}_sub:
    sec
    lda rn0
    sbc rd0
    sta rn0
    lda rn1
    sbc rd1
    sta rn1
    inc rq0
{p}_next:
    dex
    bne {p}_loop

    ; nearest Q0.16 rounding: round up iff 2*remainder >= divisor.
    asl rn0
    rol rn1
    bcs {p}_round
    lda rn1
    cmp rd1
    bcc {p}_bind
    bne {p}_round
    lda rn0
    cmp rd0
    bcc {p}_bind
{p}_round:
    inc rq0
    bne {p}_bind
    inc rq1
""")
    out.append(bind_and_finish(p))
    out.append(apply_source('ratio_apply', apply_origin))
    return ''.join(out)


def generate_unrolled(origin: int = 0xE000, apply_origin: int = 0xE800) -> str:
    p = 'ratio_prep_unrolled'
    out = [header(origin), prep_prefix(p)]
    # n<d on entry. The compare that branched here left C=0.
    out.append("    lda rn1\n")
    for i in range(16):
        out.append(f"""{p}_b{i}:
    rol rq0
    rol rq1
    rol rn0
    rol a
    bcs {p}_force{i}
    cmp rd1
    bcc {p}_no{i}
    bne {p}_take{i}
    ldx rn0
    cpx rd0
    bcc {p}_no{i}
{p}_take{i}:
    tax
    lda rn0
    sbc rd0
    sta rn0
    txa
    sbc rd1
    bcs {p}_no{i}
{p}_force{i}:
    ; 17th remainder bit guarantees one subtraction and quotient bit 1.
    tax
    lda rn0
    sbc rd0
    sta rn0
    txa
    sbc rd1
    sec
{p}_no{i}:
""")
    out.append(f"""    ; Insert the final quotient decision still held in Carry.
    rol rq0
    rol rq1
    sta rn1

    ; nearest Q0.16 rounding from the final remainder.
    asl rn0
    rol rn1
    bcs {p}_round
    lda rn1
    cmp rd1
    bcc {p}_bind
    bne {p}_round
    lda rn0
    cmp rd0
    bcc {p}_bind
{p}_round:
    inc rq0
    bne {p}_bind
    inc rq1
""")
    out.append(bind_and_finish(p))
    out.append(apply_source('ratio_apply', apply_origin))
    return ''.join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kind', choices=('compact', 'unrolled'), default='unrolled')
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=0xE000)
    ap.add_argument('--apply-origin', type=lambda s: int(s, 0), default=0xE800)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()

    if args.kind == 'compact':
        text = generate_compact(args.origin, args.apply_origin)
    else:
        text = generate_unrolled(args.origin, args.apply_origin)

    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
