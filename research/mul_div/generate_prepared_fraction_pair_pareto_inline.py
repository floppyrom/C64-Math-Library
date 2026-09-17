#!/usr/bin/env python3
"""Generate the shipped-V2 fused strict-fraction SCALE2 research kernel.

This is the corrected profile-native version of the earlier SCALE2 idea. It
uses the quarter-square geometry actually shipped by V2 Pareto-Fast, not the
historical standalone record UMUL16 ABI.

Trusted semantic contract:

    0 < n < d <= 65535
    x,y are signed16

    m  = floor(n*65536/d)          [default]
      or round(n*65536/d)          [--rounding nearest]

    zx = trunc_toward_zero(x*m/65536)
    zy = trunc_toward_zero(y*m/65536)

Inputs:
    X0:X1 = signed x
    Y0:Y1 = signed y
    N0:N1 = unsigned n
    D0:D1 = unsigned d

Outputs:
    Z0:Z1 = signed zx
    Z2:Z3 = signed zy

The fractional PREP patches one shared fixed-X 16x16 high-half multiply body.
The body is then used twice inside the same call. Because prepared state never
escapes the routine, there is no lifecycle hazard from an intervening UMUL16.

Research only. Code must reside in writable RAM. No stable API is modified.
"""
from __future__ import annotations

import argparse
from pathlib import Path

X0, X1 = 0xC000, 0xC001
Y0, Y1 = 0xC004, 0xC005
Z0, Z1, Z2, Z3 = 0xC008, 0xC009, 0xC00A, 0xC00B
N0, N1 = 0xC010, 0xC011
D0, D1 = 0xC014, 0xC015

# All transient bytes are inside V2's already-owned arithmetic scratch range.
RN0, RN1 = 0x10, 0x11
RD0, RD1 = 0x12, 0x13
RQ0, RQ1 = 0x14, 0x15
MLO, MHI = 0x10, 0x11
LLO, LHI = 0x12, 0x13
C0, C1, C2 = 0x14, 0x15, 0x16
YA0, YA1 = 0x17, 0x18
YSIGN, PARITY = 0x19, 0x1A
QLO, QHI = 0x1B, 0x1C
PDIFF_SIGN, PASS = 0x1D, 0x1E

SQR_LO = 0x6800
SQR_HI = 0x6A00


def _header(origin: int, rounding: str) -> str:
    return f"""; GENERATED V2 PARETO FUSED STRICT-FRACTION SCALE2 RESEARCH
; trusted 0<N<D; X/Y signed16; rounding={rounding}; writable code required
X0=${X0:04X}\nX1=${X1:04X}\nY0=${Y0:04X}\nY1=${Y1:04X}
Z0=${Z0:04X}\nZ1=${Z1:04X}\nZ2=${Z2:04X}\nZ3=${Z3:04X}
N0=${N0:04X}\nN1=${N1:04X}\nD0=${D0:04X}\nD1=${D1:04X}
rn0=${RN0:02X}\nrn1=${RN1:02X}\nrd0=${RD0:02X}\nrd1=${RD1:02X}
rq0=${RQ0:02X}\nrq1=${RQ1:02X}
mlo=${MLO:02X}\nmhi=${MHI:02X}\nllo=${LLO:02X}\nlhi=${LHI:02X}
c0=${C0:02X}\nc1=${C1:02X}\nc2=${C2:02X}
ya0=${YA0:02X}\nya1=${YA1:02X}\nysign=${YSIGN:02X}
parity=${PARITY:02X}\nqlo=${QLO:02X}\nqhi=${QHI:02X}
pdiff_sign=${PDIFF_SIGN:02X}\npass=${PASS:02X}
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
    return f"""    sta {prefix}_sbc+1
    sta {prefix}_sumlo+1
    sta {prefix}_sumhi+1
"""


def generate(origin: int = 0xE000, rounding: str = 'floor') -> str:
    if rounding not in ('nearest', 'floor'):
        raise ValueError(rounding)

    p = 'ratio_fraction_scale2_pareto_inline'
    out = [_header(origin, rounding)]
    out.append(f"""{p}:
    ; Trusted semantic domain: n is already a legal initial remainder.
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
    ; m0 is fixed X for the first byte product.
    lda rq0
""")
    out.append(_patch_three('rs2_m'))
    out.append("    ; m1 is fixed X for the second byte product.\n    lda rq1\n")
    out.append(_patch_three('rs2_l'))
    out.append(f"""    ; Third fixed X is |m1-m0|. Keep only its difference sign.
    sec
    sbc rq0
    bcs {p}_diff_pos
    eor #$ff
    clc
    adc #$01
""")
    out.append(_patch_three('rs2_q'))
    out.append(f"""    lda #$80
    sta pdiff_sign
    jmp {p}_begin
{p}_diff_pos:
""")
    out.append(_patch_three('rs2_q'))
    out.append(f"""    lda #$00
    sta pdiff_sign

{p}_begin:
    ; First component comes from public X. Second pass will load public Y.
    lda #$00
    sta pass
    lda X0
    sta ya0
    lda X1
    sta ya1

{p}_component:
    lda ya1
    and #$80
    sta ysign
    lda ya1
    bpl {p}_mag_ready
    sec
    lda #$00
    sbc ya0
    sta ya0
    lda #$00
    sbc ya1
    sta ya1
{p}_mag_ready:

    ; M=m0*y0.
    ldy ya0
""")
    out.append(_fixed_mul('rs2_m', 'mlo', 'mhi'))
    out.append("""
    ; L=m1*y1.
    ldy ya1
""")
    out.append(_fixed_mul('rs2_l', 'llo', 'lhi'))
    out.append(f"""
    ; v=|y1-y0| and parity of byte-difference signs.
    lda ya1
    sec
    sbc ya0
    bcs {p}_v_pos
    eor #$ff
    clc
    adc #$01
    tay
    lda #$80
    eor pdiff_sign
    sta parity
    jmp {p}_q_start
{p}_v_pos:
    tay
    lda pdiff_sign
    sta parity

{p}_q_start:
    ; Q=|m1-m0|*|y1-y0|.
""")
    out.append(_fixed_mul('rs2_q', 'qlo', 'qhi'))
    out.append(f"""
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
    bne {p}_cross_add
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
    bcs {p}_combine
{p}_cross_add:
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

{p}_combine:
    ; Product bytes 2/3 only. Reuse qlo/qhi as result scratch.
    lda mhi
    clc
    adc c0
    lda llo
    adc c1
    sta qlo
    lda lhi
    adc c2
    sta qhi

    lda ysign
    beq {p}_sign_done
    sec
    lda #$00
    sbc qlo
    sta qlo
    lda #$00
    sbc qhi
    sta qhi
{p}_sign_done:
    lda pass
    bne {p}_second

    ; Publish X result, then loop once over the unchanged public Y component.
    lda qlo
    sta Z0
    lda qhi
    sta Z1
    inc pass
    lda Y0
    sta ya0
    lda Y1
    sta ya1
    jmp {p}_component

{p}_second:
    lda qlo
    sta Z2
    lda qhi
    sta Z3
    clc
    rts
""")
    return ''.join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounding', choices=('nearest', 'floor'), default='floor')
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=0xE000)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    text = generate(args.origin, args.rounding)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
