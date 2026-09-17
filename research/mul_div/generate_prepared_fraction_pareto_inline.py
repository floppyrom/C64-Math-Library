#!/usr/bin/env python3
"""Generate a strict-fraction prepared ratio for the shipped V2 Pareto tables.

This candidate specializes the actual Pareto-Fast quarter-square geometry rather
than assuming the record_umul16_17zp research core is installed.

PREP(n,d), trusted 0<n<d:
    m = round(n*65536/d)   [default]
    or floor(n*65536/d)    [--rounding floor]

    m0, m1 and |m1-m0| are patched into three fixed-X quarter-square multiply
    sites used by APPLY. Only the sign of m1-m0 remains as ordinary RAM state.

APPLY_S16(y):
    signed16 result = trunc_toward_zero(y*m/65536)

The fixed-X product uses the balanced Jameson/TobyLobster normalization form:
negative byte differences are normalized before table lookup, so each product
needs only three PREP patch writes (SBC #X, sum-low base, sum-high base). APPLY
therefore avoids the installed UMUL8 core's dynamic pointer binding and all
three JSR/RTS pairs while reusing the same table bank.

The floor variant intentionally trades a small accuracy-frequency increase for
removing PREP's final rounding stage. Both nearest and floor retain a maximum
integer error of <=1 for signed16 applied values.

Research only. Code must reside in writable RAM. No stable API is modified.
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

MLO, MHI = 0x10, 0x11
LLO, LHI = 0x12, 0x13
C0, C1, C2 = 0x14, 0x15, 0x16
YA0, YA1 = 0x17, 0x18
YSIGN, PARITY = 0x19, 0x1A
QLO, QHI = 0x1B, 0x1C

PDIFF_SIGN = 0xC036

SQR_LO = 0x6800
SQR_HI = 0x6A00


def _header(origin: int, apply_origin: int, rounding: str) -> str:
    return f"""; GENERATED V2 PARETO FIXED-X PREPARED-FRACTION RESEARCH
; trusted 0<N<D; rounding={rounding}; code must be writable
N0=${N0:04X}\nN1=${N1:04X}\nD0=${D0:04X}\nD1=${D1:04X}
Y0=${Y0:04X}\nY1=${Y1:04X}\nZ0=${Z0:04X}\nZ1=${Z1:04X}
rn0=${RN0:02X}\nrn1=${RN1:02X}\nrd0=${RD0:02X}\nrd1=${RD1:02X}
rq0=${RQ0:02X}\nrq1=${RQ1:02X}
mlo=${MLO:02X}\nmhi=${MHI:02X}\nllo=${LLO:02X}\nlhi=${LHI:02X}
c0=${C0:02X}\nc1=${C1:02X}\nc2=${C2:02X}
ya0=${YA0:02X}\nya1=${YA1:02X}\nysign=${YSIGN:02X}
parity=${PARITY:02X}\nqlo=${QLO:02X}\nqhi=${QHI:02X}
PDIFF_SIGN=${PDIFF_SIGN:04X}
SQR_LO=${SQR_LO:04X}\nSQR_HI=${SQR_HI:04X}
.org ${origin:04X}
"""


def _fixed_mul(name: str, low: str, high: str) -> str:
    """Inline prepared-X balanced 8x8 product. Input Y; output low/high."""
    return f"""    sec
    tya
{name}_sbc:
    sbc #$00
    bcs {name}_diff_ready
    sbc #$00
    eor #$ff
{name}_diff_ready:
    tax
{name}_sumlo:
    lda SQR_LO,y
    sbc SQR_LO,x
    sta {low}
{name}_sumhi:
    lda SQR_HI,y
    sbc SQR_HI,x
    sta {high}
"""


def _patch_three(prefix: str) -> str:
    # SQR_LO/SQR_HI are page aligned; patch only each absolute operand low byte.
    return f"""    sta {prefix}_sbc+1
    sta {prefix}_sumlo+1
    sta {prefix}_sumhi+1
"""


def generate(origin: int = 0xE000, apply_origin: int = 0xE800,
             rounding: str = 'nearest') -> str:
    if rounding not in ('nearest', 'floor'):
        raise ValueError(rounding)
    p = 'ratio_fraction_prep_pareto_inline'
    out = [_header(origin, apply_origin, rounding)]
    out.append(f"""{p}:
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

    out.append("    rol rq0\n    rol rq1\n")
    if rounding == 'nearest':
        out.append(f"""    sta rn1
    asl rn0
    rol rn1
    bcs {p}_round
    lda rn1
    cmp rd1
    bcc {p}_patch
    bne {p}_round
    lda rn0
    cmp rd0
    bcc {p}_patch
{p}_round:
    inc rq0
    bne {p}_patch
    inc rq1
""")

    out.append(f"""{p}_patch:
    ; m0 becomes fixed X for the first product.
    lda rq0
""")
    out.append(_patch_three('rapi_m'))
    out.append("    ; m1 becomes fixed X for the second product.\n    lda rq1\n")
    out.append(_patch_three('rapi_l'))
    out.append(f"""    ; Third fixed X is |m1-m0|; retain only its sign as state.
    sec
    sbc rq0
    bcs {p}_diff_pos
    eor #$ff
    clc
    adc #$01
""")
    out.append(_patch_three('rapi_q'))
    out.append(f"""    lda #$80
    sta PDIFF_SIGN
    clc
    rts
{p}_diff_pos:
""")
    out.append(_patch_three('rapi_q'))
    out.append(f"""    lda #$00
    sta PDIFF_SIGN
    clc
    rts

.org ${apply_origin:04X}
ratio_fraction_apply_pareto_inline_s16:
    lda Y0
    sta ya0
    lda Y1
    and #$80
    sta ysign
    lda Y1
    sta ya1
    bpl rapi_mag_ready
    sec
    lda #$00
    sbc ya0
    sta ya0
    lda #$00
    sbc ya1
    sta ya1
rapi_mag_ready:

    ; M=m0*y0. m0 was patched by PREP.
    ldy ya0
""")
    out.append(_fixed_mul('rapi_m', 'mlo', 'mhi'))
    out.append("""
    ; L=m1*y1. m1 was patched by PREP.
    ldy ya1
""")
    out.append(_fixed_mul('rapi_l', 'llo', 'lhi'))
    out.append("""
    ; v=|y1-y0| and parity of byte-difference signs.
    lda ya1
    sec
    sbc ya0
    bcs rapi_v_pos
    eor #$ff
    clc
    adc #$01
    tay
    lda #$80
    eor PDIFF_SIGN
    sta parity
    jmp rapi_q_start
rapi_v_pos:
    tay
    lda PDIFF_SIGN
    sta parity

rapi_q_start:
    ; Q=|m1-m0|*|y1-y0|. Fixed X was patched by PREP.
""")
    out.append(_fixed_mul('rapi_q', 'qlo', 'qhi'))
    out.append("""
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

    lda parity
    bne rapi_cross_add
    sec
    lda c0
    sbc qlo
    sta c0
    lda c1
    sbc qhi
    sta c1
    lda c2
    sbc #$00
    sta c2
    bcs rapi_combine
rapi_cross_add:
    clc
    lda c0
    adc qlo
    sta c0
    lda c1
    adc qhi
    sta c1
    lda c2
    adc #$00
    sta c2

rapi_combine:
    ; M+(cross<<8)+(L<<16): retain bytes 2 and 3 only.
    lda mhi
    clc
    adc c0
    lda llo
    adc c1
    sta Z0
    lda lhi
    adc c2
    sta Z1

    lda ysign
    beq rapi_done
    sec
    lda #$00
    sbc Z0
    sta Z0
    lda #$00
    sbc Z1
    sta Z1
rapi_done:
    clc
    rts
""")
    return ''.join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounding', choices=('nearest', 'floor'), default='nearest')
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=0xE000)
    ap.add_argument('--apply-origin', type=lambda s: int(s, 0), default=0xE800)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    text = generate(args.origin, args.apply_origin, args.rounding)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
