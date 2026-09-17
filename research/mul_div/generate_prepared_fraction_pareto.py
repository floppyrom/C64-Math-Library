#!/usr/bin/env python3
"""Generate a prepared strict-fraction kernel for the *actual* V2 Pareto core.

Unlike the earlier record-core experiment, this candidate matches the shipped
V2 resident implementation:

    I_UMUL8  = $5300
    UMUL8 low result = $3D
    I_UMUL16 = $5400 is the integrated 3xUMUL8 public-I/O kernel

Contract:

    PREP(n16,d16), trusted 0 < n < d
        m = round(n*65536/d)
        precompute m byte-difference state

    APPLY_S16(y16)
        result = trunc_toward_zero(y*m/65536)

The APPLY computes only the high 16 bits and uses three calls to the selected
V2 UMUL8 kernel, with a prepared Karatsuba/difference-product multiplier.
No assumption is made about the unrelated record_umul16_17zp source image.

Research only: no domain checks and no stable API.
"""
from __future__ import annotations

import argparse
from pathlib import Path

N0, N1 = 0xC010, 0xC011
D0, D1 = 0xC014, 0xC015
Y0, Y1 = 0xC004, 0xC005
Z0, Z1 = 0xC008, 0xC009

# PREP scratch. V2 divisions already own/reuse this transient range.
RN0, RN1 = 0x10, 0x11
RD0, RD1 = 0x12, 0x13
RQ0, RQ1 = 0x14, 0x15

# APPLY scratch, also within the normal V2 transient arithmetic window.
MLO, MHI = 0x10, 0x11
LLO, LHI = 0x12, 0x13
C0, C1, C2 = 0x14, 0x15, 0x16
YA0, YA1 = 0x17, 0x18
YSIGN, PARITY, QHI = 0x19, 0x1A, 0x1B

I_UMUL8 = 0x5300
UMUL8_LO = 0x3D

# Private ordinary-RAM prepared state.
PM0 = 0xC033
PM1 = 0xC034
PDIFF = 0xC035
PDIFF_SIGN = 0xC036  # $80 iff m1-m0 < 0


def _header(origin: int, apply_origin: int) -> str:
    return f"""; GENERATED V2 PARETO PREPARED-FRACTION RESEARCH
; PREP: trusted 0<N<D, m=round(N*65536/D)
; APPLY: signed Y16 -> signed high16(Y*m), <=1 integer error vs exact Y*N/D
N0=${N0:04X}\nN1=${N1:04X}\nD0=${D0:04X}\nD1=${D1:04X}
Y0=${Y0:04X}\nY1=${Y1:04X}\nZ0=${Z0:04X}\nZ1=${Z1:04X}
rn0=${RN0:02X}\nrn1=${RN1:02X}\nrd0=${RD0:02X}\nrd1=${RD1:02X}
rq0=${RQ0:02X}\nrq1=${RQ1:02X}
mlo=${MLO:02X}\nmhi=${MHI:02X}\nllo=${LLO:02X}\nlhi=${LHI:02X}
c0=${C0:02X}\nc1=${C1:02X}\nc2=${C2:02X}
ya0=${YA0:02X}\nya1=${YA1:02X}\nysign=${YSIGN:02X}
parity=${PARITY:02X}\nqhi=${QHI:02X}
I_UMUL8=${I_UMUL8:04X}\nUMUL8_LO=${UMUL8_LO:02X}
PM0=${PM0:04X}\nPM1=${PM1:04X}\nPDIFF=${PDIFF:04X}\nPDIFF_SIGN=${PDIFF_SIGN:04X}
.org ${origin:04X}
"""


def generate(origin: int = 0xE000, apply_origin: int = 0xE800) -> str:
    p = 'ratio_fraction_prep_pareto'
    out = [_header(origin, apply_origin)]
    out.append(f"""{p}:
    ; Trusted interpolation invariant: 0 < N < D.
    lda N0
    sta rn0
    lda N1
    sta rn1
    lda D0
    sta rd0
    lda D1
    sta rd1
    lda #$00
    sta rq0
    sta rq1
    clc
    lda rn1
""")

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
    tax
    lda rn0
    sbc rd0
    sta rn0
    txa
    sbc rd1
    sec
{p}_no{i}:
""")

    out.append(f"""    ; Final quotient decision.
    rol rq0
    rol rq1
    sta rn1

    ; Round Q0.16 m to nearest using the final remainder.
    asl rn0
    rol rn1
    bcs {p}_round
    lda rn1
    cmp rd1
    bcc {p}_store
    bne {p}_round
    lda rn0
    cmp rd0
    bcc {p}_store
{p}_round:
    inc rq0
    bne {p}_store
    inc rq1

{p}_store:
    lda rq0
    sta PM0
    lda rq1
    sta PM1

    ; Precompute |m1-m0| and its sign once for the 3-product APPLY.
    sec
    sbc rq0
    bcs {p}_diff_pos
    eor #$ff
    clc
    adc #$01
    sta PDIFF
    lda #$80
    sta PDIFF_SIGN
    clc
    rts
{p}_diff_pos:
    sta PDIFF
    lda #$00
    sta PDIFF_SIGN
    clc
    rts

.org ${apply_origin:04X}
ratio_fraction_apply_pareto_s16:
    ; Preserve public Y, build magnitude in transient scratch.
    lda Y0
    sta ya0
    lda Y1
    and #$80
    sta ysign
    lda Y1
    sta ya1
    bpl rap_mag_ready
    sec
    lda #$00
    sbc ya0
    sta ya0
    lda #$00
    sbc ya1
    sta ya1
rap_mag_ready:

    ; M = m0*y0.
    ldx PM0
    ldy ya0
    jsr I_UMUL8
    sta mhi
    lda UMUL8_LO
    sta mlo

    ; L = m1*y1.
    ldx PM1
    ldy ya1
    jsr I_UMUL8
    sta lhi
    lda UMUL8_LO
    sta llo

    ; v=|y1-y0| and parity of the two byte-difference signs.
    lda ya1
    sec
    sbc ya0
    bcs rap_v_pos
    eor #$ff
    clc
    adc #$01
    tay
    lda #$80
    eor PDIFF_SIGN
    sta parity
    jmp rap_q
rap_v_pos:
    tay
    lda PDIFF_SIGN
    sta parity

rap_q:
    ; Q = |m1-m0| * |y1-y0|.
    ldx PDIFF
    jsr I_UMUL8
    sta qhi

    ; S=M+L as 17-bit c2:c1:c0.
    clc
    lda mlo
    adc llo
    sta c0
    lda mhi
    adc lhi
    sta c1
    lda #$00
    adc #$00
    sta c2

    ; Same difference signs -> cross=M+L-Q; opposite -> M+L+Q.
    lda parity
    bne rap_cross_add
    sec
    lda c0
    sbc UMUL8_LO
    sta c0
    lda c1
    sbc qhi
    sta c1
    lda c2
    sbc #$00
    sta c2
    bcs rap_combine
rap_cross_add:
    clc
    lda c0
    adc UMUL8_LO
    sta c0
    lda c1
    adc qhi
    sta c1
    lda c2
    adc #$00
    sta c2

rap_combine:
    ; Product=M+(cross<<8)+(L<<16). Only bytes 2 and 3 are required.
    lda mhi
    clc
    adc c0              ; discard byte1, retain carry into byte2
    lda llo
    adc c1
    sta Z0
    lda lhi
    adc c2
    sta Z1

    lda ysign
    beq rap_done
    sec
    lda #$00
    sbc Z0
    sta Z0
    lda #$00
    sbc Z1
    sta Z1
rap_done:
    clc
    rts
""")
    return ''.join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=0xE000)
    ap.add_argument('--apply-origin', type=lambda s: int(s, 0), default=0xE800)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    text = generate(args.origin, args.apply_origin)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
