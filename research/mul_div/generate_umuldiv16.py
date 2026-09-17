#!/usr/bin/env python3
"""Generate the first MUL_DIV research kernels.

The generated source is intentionally reference-map research code. It calls the
stable MATH_UMUL16 entry and reuses the resident unsigned-division ZP ABI at
$12-$16 after multiplication has returned.
"""
from __future__ import annotations

import argparse
from pathlib import Path

MATH_UMUL16 = 0x3020
MATH_UDIV32_16 = 0x31B0

X0, X1 = 0xC000, 0xC001
Y0, Y1 = 0xC004, 0xC005
Z0, Z1, Z2, Z3 = 0xC008, 0xC009, 0xC00A, 0xC00B
N0, N1, N2, N3 = 0xC010, 0xC011, 0xC012, 0xC013
D0, D1 = 0xC014, 0xC015
Q0, Q1, Q2, Q3 = 0xC018, 0xC019, 0xC01A, 0xC01B
R0, R1 = 0xC01C, 0xC01D

# Existing resident unsigned-division ZP ABI. These bytes are already part of
# the library footprint; the fused candidate does not add profile ZP.
MD0, MD1 = 0x12, 0x13
MQ0, MQ1 = 0x14, 0x15
MR0 = 0x16


def _header(origin: int) -> str:
    return f"""; GENERATED MUL_DIV RESEARCH SOURCE - NOT A STABLE API\n\
; exact unsigned bounded (X16*Y16)/D16\n\
; success: Z0:Z1=quotient, Z2:Z3=remainder, C=0\n\
; error (D=0 or quotient>$ffff): Z0..Z3=0, C=1\n\
; decimal mode must be clear; A/X/Y volatile\n\
MATH_UMUL16=${MATH_UMUL16:04X}\n\
X0=${X0:04X}\nX1=${X1:04X}\nY0=${Y0:04X}\nY1=${Y1:04X}\n\
Z0=${Z0:04X}\nZ1=${Z1:04X}\nZ2=${Z2:04X}\nZ3=${Z3:04X}\n\
D0=${D0:04X}\nD1=${D1:04X}\n\
md0=${MD0:02X}\nmd1=${MD1:02X}\nmq0=${MQ0:02X}\nmq1=${MQ1:02X}\nmr0=${MR0:02X}\n\
.org ${origin:04X}\n"""


def generate_bounded(origin: int = 0xE000) -> str:
    out = [_header(origin)]
    out.append("""umuldiv16_bounded:
    jsr MATH_UMUL16

    ; Copy divisor into the resident division ZP ABI and reject d=0.
    lda D0
    sta md0
    lda D1
    sta md1
    ora md0
    bne md_nonzero
md_fail:
    lda #$00
    sta Z0
    sta Z1
    sta Z2
    sta Z3
    sec
    rts

md_nonzero:
    ; Product is Z3:Z2:Z1:Z0.  A 16-bit quotient exists iff high16 < d.
    ; Seed the constrained divider before the range test while A is free.
    lda Z0
    sta mq0
    lda Z1
    sta mq1
    lda Z2
    sta mr0

    lda Z3
    cmp md1
    bcc md_b0              ; C=0 and A already holds remainder high
    bne md_fail
    lda Z2
    cmp md0
    bcs md_fail
    lda Z3                 ; low-word compare left C=0

""")

    # A holds remainder high. mq0/mq1 are the low product word and become the
    # quotient pipeline. mr0 is remainder low. Each trial result is left in C
    # for the following ROLs. This is the same useful carry pipeline as the
    # resident UDIV32/16 constrained low-word tail.
    for i in range(16):
        out.append(f"""md_b{i}:
    rol mq0
    rol mq1
    rol mr0
    rol a
    bcs md_force{i}
    cmp md1
    bcc md_no{i}
    bne md_take{i}
    ldx mr0
    cpx md0
    bcc md_no{i}
md_take{i}:
    tax
    lda mr0
    sbc md0
    sta mr0
    txa
    sbc md1
    bcs md_no{i}            ; successful 16-bit trial => quotient bit 1
md_force{i}:
    ; ROL A produced a 17th remainder bit. Since prior remainder < d,
    ; one subtraction is both necessary and sufficient.
    tax
    lda mr0
    sbc md0
    sta mr0
    txa
    sbc md1
    sec                     ; implicit 17th bit guarantees quotient bit 1
md_no{i}:
""")

    out.append("""    ; The final trial bit is still in Carry. Insert it now.
    rol mq0
    rol mq1

    ; Publish quotient and remainder in Z[0..3].
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
    return "".join(out)


def generate_composed(origin: int = 0xE800) -> str:
    """Reference wrapper with exactly the same bounded-result contract."""
    return f"""; GENERATED MUL_DIV COMPOSED BASELINE - NOT A STABLE API
MATH_UMUL16=${MATH_UMUL16:04X}
MATH_UDIV32_16=${MATH_UDIV32_16:04X}
Z0=${Z0:04X}
Z1=${Z1:04X}
Z2=${Z2:04X}
Z3=${Z3:04X}
N0=${N0:04X}
N1=${N1:04X}
N2=${N2:04X}
N3=${N3:04X}
Q0=${Q0:04X}
Q1=${Q1:04X}
Q2=${Q2:04X}
Q3=${Q3:04X}
R0=${R0:04X}
R1=${R1:04X}
.org ${origin:04X}
umuldiv16_composed:
    jsr MATH_UMUL16
    lda Z0
    sta N0
    lda Z1
    sta N1
    lda Z2
    sta N2
    lda Z3
    sta N3
    jsr MATH_UDIV32_16
    bcs composed_fail
    lda Q2
    ora Q3
    bne composed_fail
    lda Q0
    sta Z0
    lda Q1
    sta Z1
    lda R0
    sta Z2
    lda R1
    sta Z3
    clc
    rts
composed_fail:
    lda #$00
    sta Z0
    sta Z1
    sta Z2
    sta Z3
    sec
    rts
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kind', choices=('bounded', 'composed'), default='bounded')
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=None)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()

    if args.kind == 'bounded':
        text = generate_bounded(0xE000 if args.origin is None else args.origin)
    else:
        text = generate_composed(0xE800 if args.origin is None else args.origin)

    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
