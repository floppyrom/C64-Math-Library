#!/usr/bin/env python3
"""Generate actual-core V2 Pareto MUL_DIV16 research kernels.

The historical `direct_v2` experiment targeted the separate
record_umul16_17zp research ABI. This file instead fuses the implementation
actually shipped in V2 Pareto-Fast:

    I_UMUL8  = $5300
    I_UMUL16 = $5400 = integrated 3xUMUL8 construction

The 3xUMUL8 construction is inlined and its live product bytes are handed
directly to the constrained divide state. All scratch remains in V2's existing
normal transient ZP window $10-$20. Research only; no stable API is changed.
"""
from __future__ import annotations

import argparse
from pathlib import Path

I_UMUL8 = 0x5300
I_UDIV16 = 0x420C
UMUL8_LO = 0x3D

X0, X1 = 0xC000, 0xC001
Y0, Y1 = 0xC004, 0xC005
Z0, Z1, Z2, Z3 = 0xC008, 0xC009, 0xC00A, 0xC00B
D0, D1 = 0xC014, 0xC015

# Multiply scratch mirrors pareto_umul16.a.
MLO, MHI = 0x10, 0x11
LLO, LHI = 0x12, 0x13
SIGN, QHI = 0x14, 0x15
C0, C1, C2 = 0x16, 0x17, 0x18
QLO = 0x19

# Divide reinterpretation after multiply is complete.
MQ0, MQ1 = 0x14, 0x15
MR0 = 0x16
MD0, MD1 = 0x1A, 0x1B  # unused by shipped 3xUMUL8 construction
PHI = 0x1C             # hybrid-only saved product byte3

# Native UDIV16 ABI for small-product fallback.
MN0, MN1 = 0x10, 0x11
UR0, UR1 = 0x16, 0x17


def _header(origin: int) -> str:
    return f"""; GENERATED ACTUAL-V2 PARETO MUL_DIV RESEARCH
X0=${X0:04X}\nX1=${X1:04X}\nY0=${Y0:04X}\nY1=${Y1:04X}
Z0=${Z0:04X}\nZ1=${Z1:04X}\nZ2=${Z2:04X}\nZ3=${Z3:04X}
D0=${D0:04X}\nD1=${D1:04X}
I_UMUL8=${I_UMUL8:04X}\nI_UDIV16=${I_UDIV16:04X}\nUMUL8_LO=${UMUL8_LO:02X}
mlo=${MLO:02X}\nmhi=${MHI:02X}\nllo=${LLO:02X}\nlhi=${LHI:02X}
sign=${SIGN:02X}\nqhi=${QHI:02X}\nc0=${C0:02X}\nc1=${C1:02X}\nc2=${C2:02X}\nqlo=${QLO:02X}
mq0=${MQ0:02X}\nmq1=${MQ1:02X}\nmr0=${MR0:02X}\nmd0=${MD0:02X}\nmd1=${MD1:02X}\nphi=${PHI:02X}
mn0=${MN0:02X}\nmn1=${MN1:02X}\nur0=${UR0:02X}\nur1=${UR1:02X}
.org ${origin:04X}
"""


def _fail(label: str) -> str:
    return f"""{label}:
    lda #$00
    sta Z0
    sta Z1
    sta Z2
    sta Z3
    sec
    rts
"""


def _multiply_live(prefix: str) -> str:
    """Shipped V2 3xUMUL8 math ending in tail-ready live product state.

    exit: mq0=byte0, mq1=byte1, mr0=byte2, A=byte3.
    MLO/MHI also contain byte0/byte1, so a 16-bit product is already in the
    native UDIV16 numerator slots $10/$11.
    """
    return f"""    ; M=a*c
    ldx X0
    ldy Y0
    jsr I_UMUL8
    sta mhi
    lda UMUL8_LO
    sta mlo

    ; L=b*d
    ldx X1
    ldy Y1
    jsr I_UMUL8
    sta lhi
    lda UMUL8_LO
    sta llo

    ; u=|b-a| and first difference sign.
    lda #$00
    sta sign
    lda X1
    sec
    sbc X0
    bcs {prefix}_ux_ready
    dec sign
    eor #$ff
    clc
    adc #$01
{prefix}_ux_ready:
    tax

    ; v=|d-c|; SIGN==0 means same difference sign.
    lda Y1
    sec
    sbc Y0
    bcs {prefix}_vy_ready
    eor #$ff
    clc
    adc #$01
    inc sign
{prefix}_vy_ready:
    tay

    ; Q=u*v.
    jsr I_UMUL8
    sta qhi
    lda UMUL8_LO
    sta qlo

    ; S=M+L as 17-bit c2:c1:c0.
    lda mlo
    clc
    adc llo
    sta c0
    lda mhi
    adc lhi
    sta c1
    lda #$00
    adc #$00
    sta c2

    lda sign
    bne {prefix}_cross_add
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
    bcs {prefix}_combine
{prefix}_cross_add:
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

{prefix}_combine:
    ; Product=M+(cross<<8)+(L<<16). Keep byte0/1 also in $10/$11.
    lda mhi
    clc
    adc c0
    sta mhi              ; final byte1
    lda llo
    adc c1
    sta mr0              ; final byte2
    lda mlo
    sta mq0              ; final byte0
    lda mhi
    sta mq1              ; final byte1
    lda lhi
    adc c2               ; A=final byte3
"""


def _tail(prefix: str) -> str:
    out: list[str] = []
    for i in range(16):
        out.append(f"""{prefix}_b{i}:
    rol mq0
    rol mq1
    rol mr0
    rol a
    bcs {prefix}_force{i}
    cmp md1
    bcc {prefix}_no{i}
    bne {prefix}_take{i}
    ldx mr0
    cpx md0
    bcc {prefix}_no{i}
{prefix}_take{i}:
    tax
    lda mr0
    sbc md0
    sta mr0
    txa
    sbc md1
    bcs {prefix}_no{i}
{prefix}_force{i}:
    tax
    lda mr0
    sbc md0
    sta mr0
    txa
    sbc md1
    sec
{prefix}_no{i}:
""")
    out.append("""    rol mq0
    rol mq1
    sta Z3
    lda mr0
    sta Z2
    lda mq0
    sta Z0
    lda mq1
    sta Z1
    clc
    rts
""")
    return ''.join(out)


def _start(prefix: str, entry: str) -> str:
    return f"""{entry}:
    lda D0
    sta md0
    lda D1
    sta md1
    ora md0
    bne {prefix}_nonzero
"""


def generate_direct(origin: int = 0xE000) -> str:
    p = 'umpd'
    out = [_header(origin), _start(p, 'umuldiv16_pareto_direct'), _fail(f'{p}_fail')]
    out.append(f'{p}_nonzero:\n')
    out.append(_multiply_live(p))
    out.append(f"""    ; quotient fits uint16 iff product_hi16 < divisor
    cmp md1
    bcc {p}_b0
    bne {p}_fail
    ldx mr0
    cpx md0
    bcs {p}_fail
""")
    out.append(_tail(p))
    return ''.join(out)


def generate_direct_hybrid(origin: int = 0xE000) -> str:
    """Direct handoff plus q=0/q=1 and native UDIV16 for 16-bit products."""
    p = 'umph'
    out = [_header(origin), _start(p, 'umuldiv16_pareto_direct_hybrid'), _fail(f'{p}_fail')]
    out.append(f'{p}_nonzero:\n')
    out.append(_multiply_live(p))
    out.append(f"""    ; Save byte3 because the small-product dispatch destroys A.
    sta phi
    ora mr0
    bne {p}_general

    ; product fits 16 bits and already resides in mn1:mn0 ($11:$10).
    ; q=0 when product<d.
    lda mn1
    cmp md1
    bcc {p}_q0
    bne {p}_small_ge
    lda mn0
    cmp md0
    bcc {p}_q0

{p}_small_ge:
    ; rem=product-d. If rem<d then q=1 exactly.
    sec
    lda mn0
    sbc md0
    sta c2
    lda mn1
    sbc md1
    sta qlo
    cmp md1
    bcc {p}_q1
    bne {p}_small_div
    lda c2
    cmp md0
    bcc {p}_q1

{p}_small_div:
    ; Native UDIV16 expects d in $12/$13; product is already in $10/$11.
    lda md0
    sta llo
    lda md1
    sta lhi
    jsr I_UDIV16
    bcs {p}_fail
    lda mq0
    sta Z0
    lda mq1
    sta Z1
    lda ur0
    sta Z2
    lda ur1
    sta Z3
    clc
    rts

{p}_q0:
    lda #$00
    sta Z0
    sta Z1
    lda mn0
    sta Z2
    lda mn1
    sta Z3
    clc
    rts

{p}_q1:
    lda #$01
    sta Z0
    lda #$00
    sta Z1
    lda c2
    sta Z2
    lda qlo
    sta Z3
    clc
    rts

{p}_general:
    lda phi
    ; high16 != 0. Apply the ordinary bounded-fit test before the 16-step tail.
    cmp md1
    bcc {p}_b0
    bne {p}_fail
    ldx mr0
    cpx md0
    bcs {p}_fail
""")
    out.append(_tail(p))
    return ''.join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kind', choices=('direct', 'direct_hybrid'), default='direct')
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=0xE000)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    text = generate_direct(args.origin) if args.kind == 'direct' else generate_direct_hybrid(args.origin)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
