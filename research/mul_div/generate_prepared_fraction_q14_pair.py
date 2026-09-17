#!/usr/bin/env python3
"""Generate Q14 fused strict-fraction SCALE2 V2 research kernel.

Contract:

    n,d : uint16, trusted 0 < n < d
    x,y : signed16

    m14 = round(n*16384/d)
    zx  = trunc_toward_zero(x*m14/16384)
    zy  = trunc_toward_zero(y*m14/16384)

Output:
    Z0:Z1 = zx
    Z2:Z3 = zy

Nearest Q14 is sufficient to guarantee <=1 integer error for the complete
signed16 component domain. For the normal multiply path m14 is shifted left two
bits and reused as a Q16 multiplier by the V2 native UMUL16 same_x core.

If rounding produces m14=$4000 (1.0), the routine takes an identity path instead
of trying to represent 65536 in a 16-bit multiplier.

Research hot path only: no 0<n<d checks and no stable API claim.
"""
from __future__ import annotations

import argparse
from pathlib import Path

X0, X1 = 0xC000, 0xC001
Y0, Y1 = 0xC004, 0xC005
Z0, Z1, Z2, Z3 = 0xC008, 0xC009, 0xC00A, 0xC00B
N0, N1 = 0xC010, 0xC011
D0, D1 = 0xC014, 0xC015

RN0, RN1 = 0x10, 0x11
RD0, RD1 = 0x12, 0x13
RQ0, RQ1 = 0x14, 0x15

P0, P1, P2, P3 = 0x21, 0x23, 0x25, 0x27
P4, P5, P6, P7 = 0x29, 0x2B, 0x2D, 0x2F
UMUL_SAME_X = 0x5400
UMUL_Y1_IMM = 0x541A


def _header(origin: int) -> str:
    return f"""; GENERATED Q14 FUSED POSITIVE-FRACTION SCALE2 RESEARCH
; trusted domain: 0 < N < D; X/Y signed16; Z0:1/Z2:3 outputs
X0=${X0:04X}\nX1=${X1:04X}\nY0=${Y0:04X}\nY1=${Y1:04X}
Z0=${Z0:04X}\nZ1=${Z1:04X}\nZ2=${Z2:04X}\nZ3=${Z3:04X}
N0=${N0:04X}\nN1=${N1:04X}\nD0=${D0:04X}\nD1=${D1:04X}
rn0=${RN0:02X}\nrn1=${RN1:02X}\nrd0=${RD0:02X}\nrd1=${RD1:02X}
rq0=${RQ0:02X}\nrq1=${RQ1:02X}
p0=${P0:02X}\np1=${P1:02X}\np2=${P2:02X}\np3=${P3:02X}
p4=${P4:02X}\np5=${P5:02X}\np6=${P6:02X}\np7=${P7:02X}
UMUL_SAMEX=${UMUL_SAME_X:04X}\nUMUL_Y1=${UMUL_Y1_IMM:04X}
.org ${origin:04X}
"""


def _apply_component(prefix: str, in_lo: str, in_hi: str,
                     out_lo: str, out_hi: str, final: bool) -> str:
    neg_tail = "    clc\n    rts\n" if final else f"    jmp {prefix}_done\n"
    pos_tail = "    clc\n    rts\n" if final else f"{prefix}_done:\n"
    return f"""    lda {in_hi}
    bpl {prefix}_pos
    sec
    lda #$00
    sbc {in_lo}
    tay
    lda #$00
    sbc {in_hi}
    sta UMUL_Y1
    jsr UMUL_SAMEX
    eor #$ff
    clc
    adc #$01
    sta {out_lo}
    tya
    eor #$ff
    adc #$00
    sta {out_hi}
{neg_tail}
{prefix}_pos:
    ldy {in_lo}
    sta UMUL_Y1
    jsr UMUL_SAMEX
    sta {out_lo}
    sty {out_hi}
{pos_tail}"""


def generate(origin: int = 0xE000) -> str:
    p = 'ratio_fraction_q14_scale2'
    out = [_header(origin)]
    out.append(f"""{p}:
    ; Trusted strict fraction. N begins as the legal remainder.
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

    for i in range(14):
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

    out.append(f"""    ; Insert the 14th quotient decision.
    rol rq0
    rol rq1
    sta rn1

    ; Round Q14 to nearest.
    asl rn0
    rol rn1
    bcs {p}_round
    lda rn1
    cmp rd1
    bcc {p}_rounded
    bne {p}_round
    lda rn0
    cmp rd0
    bcc {p}_rounded
{p}_round:
    inc rq0
    bne {p}_rounded
    inc rq1

{p}_rounded:
    ; Q14 may round to exactly 1.0 ($4000). That is an identity result.
    lda rq1
    and #$40
    bne {p}_identity

    ; Convert Q14 multiplier to Q16 so the native high-half multiply applies it.
    asl rq0
    rol rq1
    asl rq0
    rol rq1

    ; Bind the Q16-scaled magnitude once for both components.
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

""")
    out.append(_apply_component(f'{p}_x', 'X0', 'X1', 'Z0', 'Z1', False))
    out.append(_apply_component(f'{p}_y', 'Y0', 'Y1', 'Z2', 'Z3', True))
    out.append(f"""
{p}_identity:
    lda X0
    sta Z0
    lda X1
    sta Z1
    lda Y0
    sta Z2
    lda Y1
    sta Z3
    clc
    rts
""")
    return ''.join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=0xE000)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    text = generate(args.origin)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
