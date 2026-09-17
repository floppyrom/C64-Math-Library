#!/usr/bin/env python3
"""Generate a width-knee actual-core V2 Pareto MUL_DIV16 hybrid.

This extends `generate_umuldiv16_pareto.py` with runtime operand-width knees:

  x<256 and y<256   -> one shipped V2 UMUL8
  exactly one <256  -> two shipped V2 UMUL8 calls (16x8 -> 24)
  otherwise         -> actual shipped 3xUMUL8 UMUL16 construction

Every path then shares the same quotient-class dispatch:

  product fits 16 bits -> q=0 / q=1 direct exits, then native UDIV16
  wider product        -> bounded-fit test + constrained 16-step tail

The specialization is dynamic and semantic: it exploits operand width available
at runtime rather than a benchmark constant. The broad 16x16 path pays a small
dispatch cost, so this is intentionally a separate Pareto point.

Research only; no stable API or shipped profile is changed.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from generate_umuldiv16_pareto import (
    C2,
    D0,
    D1,
    I_UDIV16,
    I_UMUL8,
    LHI,
    LLO,
    MD0,
    MD1,
    MHI,
    MLO,
    MR0,
    MQ0,
    MQ1,
    PHI,
    QLO,
    UMUL8_LO,
    UR0,
    UR1,
    X0,
    X1,
    Y0,
    Y1,
    Z0,
    Z1,
    Z2,
    Z3,
    _fail,
    _header,
    _multiply_live,
    _tail,
)


def _one_umul8(prefix: str) -> str:
    """Both operands are bytes; emit a 16-bit product in $10/$11."""
    return f"""{prefix}_both8:
    ldx X0
    ldy Y0
    jsr I_UMUL8
    sta mhi
    lda UMUL8_LO
    sta mlo
    lda #$00
    sta mr0
    ; A=0 is product byte3.
    jmp {prefix}_product_ready
"""


def _x8_y16(prefix: str) -> str:
    """X is byte-sized, Y is 16-bit; emit 24-bit product live."""
    return f"""{prefix}_x8:
    lda Y1
    beq {prefix}_both8

    ; low partial X0*Y0
    ldx X0
    ldy Y0
    jsr I_UMUL8
    sta mhi
    lda UMUL8_LO
    sta mlo

    ; high partial X0*Y1
    ldx X0
    ldy Y1
    jsr I_UMUL8
    sta c2
    lda UMUL8_LO
    clc
    adc mhi
    sta mhi
    lda c2
    adc #$00
    sta mr0
    lda #$00
    jmp {prefix}_product_ready
"""


def _x16_y8(prefix: str) -> str:
    """Y is byte-sized, X is 16-bit; emit 24-bit product live."""
    return f"""{prefix}_y8:
    ; low partial X0*Y0
    ldx X0
    ldy Y0
    jsr I_UMUL8
    sta mhi
    lda UMUL8_LO
    sta mlo

    ; high partial X1*Y0
    ldx X1
    ldy Y0
    jsr I_UMUL8
    sta c2
    lda UMUL8_LO
    clc
    adc mhi
    sta mhi
    lda c2
    adc #$00
    sta mr0
    lda #$00
    jmp {prefix}_product_ready
"""


def _hybrid_dispatch(prefix: str) -> str:
    return f"""{prefix}_product_ready:
    ; A=product byte3, mr0=byte2, mhi:mlo=low16.
    sta phi
    ora mr0
    bne {prefix}_general

    ; product fits 16 bits. q=0 when product<d.
    lda mhi
    cmp md1
    bcc {prefix}_q0
    bne {prefix}_small_ge
    lda mlo
    cmp md0
    bcc {prefix}_q0

{prefix}_small_ge:
    ; rem=product-d. rem<d => q=1.
    sec
    lda mlo
    sbc md0
    sta c2
    lda mhi
    sbc md1
    sta qlo
    cmp md1
    bcc {prefix}_q1
    bne {prefix}_small_div
    lda c2
    cmp md0
    bcc {prefix}_q1

{prefix}_small_div:
    ; Product is already native UDIV16 numerator $10/$11.
    lda md0
    sta llo
    lda md1
    sta lhi
    jsr I_UDIV16
    bcc {prefix}_small_ok
    jmp {prefix}_fail
{prefix}_small_ok:
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

{prefix}_q0:
    lda #$00
    sta Z0
    sta Z1
    lda mlo
    sta Z2
    lda mhi
    sta Z3
    clc
    rts

{prefix}_q1:
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

{prefix}_general:
    lda phi
    cmp md1
    bcc {prefix}_b0
    beq {prefix}_general_check_low
    jmp {prefix}_fail
{prefix}_general_check_low:
    ldx mr0
    cpx md0
    bcc {prefix}_b0
    jmp {prefix}_fail
"""


def generate(origin: int = 0xE000) -> str:
    p = 'umpw'
    out = [_header(origin)]
    out.append(f"""umuldiv16_pareto_width_hybrid:
    lda D0
    sta md0
    lda D1
    sta md1
    ora md0
    bne {p}_nonzero
""")
    out.append(_fail(f'{p}_fail'))
    out.append(f"""{p}_nonzero:
    ; Fast width dispatch. Broad 16x16 reaches the actual-core path.
    lda X1
    beq {p}_x8_stub
    lda Y1
    bne {p}_full16
    jmp {p}_y8
{p}_x8_stub:
    jmp {p}_x8

{p}_full16:
""")
    out.append(_multiply_live(p))
    out.append(f"    jmp {p}_product_ready\n")
    out.append(_x8_y16(p))
    out.append(_one_umul8(p))
    out.append(_x16_y8(p))
    out.append(_hybrid_dispatch(p))
    out.append(_tail(p))
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
