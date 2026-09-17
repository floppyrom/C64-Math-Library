#!/usr/bin/env python3
"""Generate a profile-native V2 strict-fraction SCALE2 research kernel.

Contract (trusted hot path):

    0 < n < d <= 65535
    x,y signed16

    m  = Q0.16 approximation of n/d
    zx = trunc_toward_zero(x*m/65536)
    zy = trunc_toward_zero(y*m/65536)

Input vectors:
    X0:X1 = x
    Y0:Y1 = y
    N0:N1 = n
    D0:D1 = d

Output:
    Z0:Z1 = zx
    Z2:Z3 = zy

The implementation uses the actually shipped V2 Pareto quarter-square tables.
PREP patches one shared fixed-X high-half multiply helper, then the helper is
called twice with register-fed signed components. No prepared state is exposed
past the single SCALE2 call.

Research only: code must be writable and no public API is modified.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from generate_prepared_fraction_pareto_inline import (
    C0, C1, C2, D0, D1, LHI, LLO, MHI, MLO, N0, N1,
    PARITY, PDIFF_SIGN, QHI, QLO, RD0, RD1, RN0, RN1, RQ0, RQ1,
    SQR_HI, SQR_LO, X0, X1, Y0, Y1, YA0, YA1, YSIGN,
    Z0, Z1, _fixed_mul, _patch_three,
)

Z2, Z3 = Z0 + 2, Z0 + 3


def _header(origin: int, rounding: str) -> str:
    return f"""; GENERATED V2 PROFILE-NATIVE SCALE2 FRACTION RESEARCH
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
PDIFF_SIGN=${PDIFF_SIGN:04X}
SQR_LO=${SQR_LO:04X}\nSQR_HI=${SQR_HI:04X}
.org ${origin:04X}
"""


def _apply_reg_source() -> str:
    """A=component high, Y=component low -> A=result high, X=result low."""
    out = [r'''scale2_apply_reg:
    sty ya0
    sta ya1
    lda #$00
    sta ysign
    lda ya1
    bpl s2ar_mag_ready
    lda #$80
    sta ysign
    sec
    lda #$00
    sbc ya0
    sta ya0
    lda #$00
    sbc ya1
    sta ya1
s2ar_mag_ready:

    ; M=m0*y0. m0 was patched by PREP.
    ldy ya0
''']
    out.append(_fixed_mul('s2ar_m', 'mlo', 'mhi'))
    out.append(r'''
    ; L=m1*y1. m1 was patched by PREP.
    ldy ya1
''')
    out.append(_fixed_mul('s2ar_l', 'llo', 'lhi'))
    out.append(r'''
    ; v=|y1-y0| and parity of the two byte-difference signs.
    lda ya1
    sec
    sbc ya0
    bcs s2ar_v_pos
    eor #$ff
    clc
    adc #$01
    tay
    lda #$80
    eor PDIFF_SIGN
    sta parity
    jmp s2ar_q_start
s2ar_v_pos:
    tay
    lda PDIFF_SIGN
    sta parity

s2ar_q_start:
''')
    out.append(_fixed_mul('s2ar_q', 'qlo', 'qhi'))
    out.append(r'''
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
    bne s2ar_cross_add
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
    bcs s2ar_combine
s2ar_cross_add:
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

s2ar_combine:
    ; Form only product bytes 2 and 3 (high half of magnitude product).
    lda mhi
    clc
    adc c0              ; product byte1, discarded
    lda llo
    adc c1
    sta c0              ; result low
    lda lhi
    adc c2
    sta c1              ; result high

    lda ysign
    beq s2ar_return
    sec
    lda #$00
    sbc c0
    sta c0
    lda #$00
    sbc c1
    sta c1
s2ar_return:
    ldx c0
    lda c1
    rts
''')
    return ''.join(out)


def generate(origin: int = 0xE000, rounding: str = 'nearest') -> str:
    if rounding not in ('nearest', 'floor'):
        raise ValueError(rounding)
    p = 'scale2_fraction_pareto'
    out = [_header(origin, rounding)]
    out.append(f'''{p}:
    ; Trusted semantic invariant: 0 < N < D. N is initial remainder.
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
''')

    for i in range(16):
        out.append(f'''{p}_b{i}:
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
''')

    out.append('    rol rq0\n    rol rq1\n')
    if rounding == 'nearest':
        out.append(f'''    sta rn1
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
''')

    out.append(f'''{p}_patch:
    ; Install the three fixed X magnitudes into one shared APPLY helper.
    lda rq0
''')
    out.append(_patch_three('s2ar_m'))
    out.append('    lda rq1\n')
    out.append(_patch_three('s2ar_l'))
    out.append(f'''    sec
    sbc rq0
    bcs {p}_diff_pos
    eor #$ff
    clc
    adc #$01
''')
    out.append(_patch_three('s2ar_q'))
    out.append(f'''    lda #$80
    sta PDIFF_SIGN
    jmp {p}_apply
{p}_diff_pos:
''')
    out.append(_patch_three('s2ar_q'))
    out.append(f'''    lda #$00
    sta PDIFF_SIGN

{p}_apply:
    ; Feed X directly as A:Y to the shared signed high-half helper.
    ldy X0
    lda X1
    jsr scale2_apply_reg
    stx Z0
    sta Z1

    ; Reuse the same prepared ratio for Y.
    ldy Y0
    lda Y1
    jsr scale2_apply_reg
    stx Z2
    sta Z3
    clc
    rts

''')
    out.append(_apply_reg_source())
    return ''.join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounding', choices=('nearest', 'floor'), default='nearest')
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
