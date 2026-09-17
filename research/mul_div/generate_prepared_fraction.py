#!/usr/bin/env python3
"""Generate strict positive-fraction prepared-ratio V2 research kernels.

Research contract:

    PREP(n16,d16)
        requires 0 < n < d <= 65535
        m = round(n*65536/d)

    APPLY_S16(y16)
        trunc_toward_zero(y*m/65536)

The ratio is positive by contract; only the applied component is signed.
Two state policies mirror generate_prepared_ratio.py:

  fast  bind m into the current V2 native UMUL16 X state and use same_x.
  safe  keep m in private RAM and rebind through generic UMUL16 on each APPLY.

No input-domain checks are emitted. This is a research hot-path contract, not a
stable API. A checked/public wrapper can be designed only if this point wins the
resident-image and real-game integration gates.
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

P0, P1, P2, P3 = 0x21, 0x23, 0x25, 0x27
P4, P5, P6, P7 = 0x29, 0x2B, 0x2D, 0x2F
UMUL_GENERIC = 0x53EC
UMUL_SAME_X = 0x5400
UMUL_Y1_IMM = 0x541A

RATIO_M0 = 0xC033
RATIO_M1 = 0xC034


def header(origin: int) -> str:
    return f"""; GENERATED POSITIVE-FRACTION RATIO RESEARCH - NOT A STABLE API
N0=${N0:04X}\nN1=${N1:04X}\nD0=${D0:04X}\nD1=${D1:04X}
Y0=${Y0:04X}\nY1=${Y1:04X}\nZ0=${Z0:04X}\nZ1=${Z1:04X}
rn0=${RN0:02X}\nrn1=${RN1:02X}\nrd0=${RD0:02X}\nrd1=${RD1:02X}
rq0=${RQ0:02X}\nrq1=${RQ1:02X}
p0=${P0:02X}\np1=${P1:02X}\np2=${P2:02X}\np3=${P3:02X}
p4=${P4:02X}\np5=${P5:02X}\np6=${P6:02X}\np7=${P7:02X}
UMUL_GENERIC=${UMUL_GENERIC:04X}\nUMUL_SAMEX=${UMUL_SAME_X:04X}\nUMUL_Y1=${UMUL_Y1_IMM:04X}
RATIO_M0=${RATIO_M0:04X}\nRATIO_M1=${RATIO_M1:04X}
.org ${origin:04X}
"""


def bind_finish(label: str, state: str) -> str:
    if state == 'fast':
        body = f"""{label}_bind:
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
"""
    elif state == 'safe':
        body = f"""{label}_bind:
    lda rq0
    sta RATIO_M0
    lda rq1
    sta RATIO_M1
"""
    else:
        raise ValueError(state)
    return body + "    clc\n    rts\n"


def apply_source(origin: int, state: str) -> str:
    if state == 'fast':
        mul = "    jsr UMUL_SAMEX\n"
    elif state == 'safe':
        mul = """    lda RATIO_M0
    sta p0
    lda RATIO_M1
    sta p4
    jsr UMUL_GENERIC
"""
    else:
        raise ValueError(state)

    return f""".org ${origin:04X}
ratio_fraction_apply_s16:
    lda Y1
    bpl ratio_fraction_apply_pos

    ; Negative component: multiply the magnitude, then negate A:Y directly.
    sec
    lda #$00
    sbc Y0
    tay
    lda #$00
    sbc Y1
    sta UMUL_Y1
{mul}    eor #$ff
    clc
    adc #$01
    sta Z0
    tya
    eor #$ff
    adc #$00
    sta Z1
    clc
    rts

ratio_fraction_apply_pos:
    ldy Y0
    ; A still contains the non-negative high byte loaded from Y1.
    sta UMUL_Y1
{mul}    sta Z0
    sty Z1
    clc
    rts
"""


def generate_unrolled(origin: int = 0xE000, apply_origin: int = 0xE800,
                      state: str = 'fast') -> str:
    p = 'ratio_fraction_prep'
    out = [header(origin)]
    out.append(f"""{p}:
    ; Trusted hot-path domain: 0 < N < D. Copy the positive fraction only.
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

    out.append(f"""    rol rq0
    rol rq1
    sta rn1

    ; Round Q0.16 magnitude to nearest.
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
    out.append(bind_finish(p, state))
    out.append(apply_source(apply_origin, state))
    return ''.join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--state', choices=('fast', 'safe'), default='fast')
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=0xE000)
    ap.add_argument('--apply-origin', type=lambda s: int(s, 0), default=0xE800)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()

    text = generate_unrolled(args.origin, args.apply_origin, args.state)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
