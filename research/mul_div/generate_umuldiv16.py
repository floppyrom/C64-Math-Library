#!/usr/bin/env python3
"""Generate MUL_DIV16 research kernels.

All generated sources use the reference memory map and are research artifacts,
not stable API implementations. The direct-core variants are currently V2-only
because they intentionally depend on the selected native UMUL16 contract.
"""
from __future__ import annotations

import argparse
from pathlib import Path

MATH_UMUL16 = 0x3020
MATH_UDIV32_16 = 0x31B0

INTERNAL_UDIV16 = {
    'v1': 0x4200,
    'v2': 0x420C,
}

# V2 native UMUL16 selected core. This is the validated record kernel behind
# the public wrapper, and therefore assumes V2 MATH_INIT has run.
V2_UMUL16_CORE = 0x53EC
V2_UMUL16_X0 = 0x21
V2_UMUL16_X1 = 0x29
V2_UMUL16_Y1_IMM = 0x541A
V2_UMUL16_Z0 = 0x31

X0, X1 = 0xC000, 0xC001
Y0, Y1 = 0xC004, 0xC005
Z0, Z1, Z2, Z3 = 0xC008, 0xC009, 0xC00A, 0xC00B
N0, N1, N2, N3 = 0xC010, 0xC011, 0xC012, 0xC013
D0, D1 = 0xC014, 0xC015
Q0, Q1, Q2, Q3 = 0xC018, 0xC019, 0xC01A, 0xC01B
R0, R1 = 0xC01C, 0xC01D

# Existing resident unsigned-division ZP ABI. These bytes are already owned by
# the library and can be reused after multiplication returns.
MN0, MN1 = 0x10, 0x11
MD0, MD1 = 0x12, 0x13
MQ0, MQ1 = 0x14, 0x15
MR0, MR1 = 0x16, 0x17


def _common(origin: int, internal_udiv16: int | None = None) -> str:
    extra = '' if internal_udiv16 is None else f'I_UDIV16=${internal_udiv16:04X}\n'
    return f"""; GENERATED MUL_DIV RESEARCH SOURCE - NOT A STABLE API
MATH_UMUL16=${MATH_UMUL16:04X}
{extra}X0=${X0:04X}
X1=${X1:04X}
Y0=${Y0:04X}
Y1=${Y1:04X}
Z0=${Z0:04X}
Z1=${Z1:04X}
Z2=${Z2:04X}
Z3=${Z3:04X}
D0=${D0:04X}
D1=${D1:04X}
mn0=${MN0:02X}
mn1=${MN1:02X}
md0=${MD0:02X}
md1=${MD1:02X}
mq0=${MQ0:02X}
mq1=${MQ1:02X}
mr0=${MR0:02X}
mr1=${MR1:02X}
.org ${origin:04X}
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
    ; ROL A produced a 17th remainder bit. The previous remainder was < d,
    ; so one subtraction is both necessary and sufficient and qbit=1.
    tax
    lda mr0
    sbc md0
    sta mr0
    txa
    sbc md1
    sec
{prefix}_no{i}:
""")
    out.append("""    ; Final trial decision is still in Carry.
    rol mq0
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


def generate_bounded(origin: int = 0xE000) -> str:
    """Public-UMUL16 handoff + constrained 16-step divide tail."""
    out = [_common(origin)]
    out.append("""umuldiv16_bounded:
    jsr MATH_UMUL16
    lda D0
    sta md0
    lda D1
    sta md1
    ora md0
    bne md_nonzero
""")
    out.append(_fail('md_fail'))
    out.append("""md_nonzero:
    lda Z0
    sta mq0
    lda Z1
    sta mq1
    lda Z2
    sta mr0
    lda Z3
    cmp md1
    bcc md_b0
    bne md_fail
    lda Z2
    cmp md0
    bcs md_fail
    lda Z3
""")
    out.append(_tail('md'))
    return ''.join(out)


def generate_hybrid(profile: str = 'v2', origin: int = 0xE000) -> str:
    """Public UMUL16 plus native UDIV16 fast path for 16-bit products."""
    if profile not in INTERNAL_UDIV16:
        raise ValueError(f'no certified internal UDIV16 address for {profile}')
    out = [_common(origin, INTERNAL_UDIV16[profile])]
    out.append("""umuldiv16_hybrid:
    jsr MATH_UMUL16
    lda Z2
    ora Z3
    bne mh_general
    lda Z0
    sta mn0
    lda Z1
    sta mn1
    lda D0
    sta md0
    lda D1
    sta md1
    jsr I_UDIV16
    bcc mh_small_ok
""")
    out.append(_fail('mh_fail'))
    out.append("""mh_small_ok:
    lda mq0
    sta Z0
    lda mq1
    sta Z1
    lda mr0
    sta Z2
    lda mr1
    sta Z3
    clc
    rts
mh_general:
    lda D0
    sta md0
    lda D1
    sta md1
    ora md0
    bne mh_nonzero
    jmp mh_fail
mh_nonzero:
    lda Z0
    sta mq0
    lda Z1
    sta mq1
    lda Z2
    sta mr0
    lda Z3
    cmp md1
    bcc mh_b0
    bne mh_overflow
    lda Z2
    cmp md0
    bcs mh_overflow
    lda Z3
    jmp mh_b0
mh_overflow:
    jmp mh_fail
""")
    out.append(_tail('mh'))
    return ''.join(out)


def _v2_bind_and_call() -> str:
    return f"""    lda X0
    sta ${V2_UMUL16_X0:02X}
    lda X1
    sta ${V2_UMUL16_X1:02X}
    lda Y1
    sta ${V2_UMUL16_Y1_IMM:04X}
    ldy Y0
    jsr ${V2_UMUL16_CORE:04X}
"""


def generate_direct_v2(origin: int = 0xE000) -> str:
    """V2 native UMUL16 -> constrained tail without public Z32 handoff."""
    out = [_common(origin), 'umuldiv16_direct_v2:\n']
    # Copy/check d before multiplication. It costs nothing extra on successful
    # calls and makes d=0 a very cheap exit.
    out.append("""    lda D0
    sta md0
    lda D1
    sta md1
    ora md0
    bne dc_d_ok
    jmp dc_fail
dc_d_ok:
""")
    out.append(_v2_bind_and_call())
    out.append(f"""    sta mr0                 ; product byte2
    stx mq1                 ; product byte1
    lda ${V2_UMUL16_Z0:02X}
    sta mq0                 ; product byte0
    tya                     ; product byte3 / initial remainder high
    cmp md1
    bcc dc_b0
    bne dc_fail
    ldx mr0
    cpx md0
    bcc dc_b0
""")
    out.append(_fail('dc_fail'))
    out.append(_tail('dc'))
    return ''.join(out)


def generate_direct_hybrid_v2(origin: int = 0xE000) -> str:
    """V2 direct multiply with q=0/q=1 small-product specializations.

    For a 16-bit product, direct q=0/q=1 exits avoid even the native UDIV16
    call. Larger small-product quotients use native UDIV16; nonzero product high
    words fall through to the general constrained tail.
    """
    out = [_common(origin, INTERNAL_UDIV16['v2']), 'umuldiv16_direct_hybrid_v2:\n']
    out.append("""    lda D0
    sta md0
    lda D1
    sta md1
    ora md0
    bne dh_d_ok
    jmp dh_fail
dh_d_ok:
""")
    out.append(_v2_bind_and_call())
    out.append(f"""    sta mr0                 ; product byte2
    tya
    ora mr0
    bne dh_general

    ; 16-bit product lives in ${V2_UMUL16_Z0:02X}:X. q=0 and q=1 dominate
    ; byte/small-coordinate workloads, so resolve them without a divider call.
    txa
    cmp md1
    bcc dh_q0
    bne dh_small_ge_d
    lda ${V2_UMUL16_Z0:02X}
    cmp md0
    bcc dh_q0

dh_small_ge_d:
    sec
    lda ${V2_UMUL16_Z0:02X}
    sbc md0
    sta mr0
    txa
    sbc md1
    sta mr1
    cmp md1
    bcc dh_q1
    bne dh_small_div
    lda mr0
    cmp md0
    bcc dh_q1

dh_small_div:
    lda ${V2_UMUL16_Z0:02X}
    sta mn0
    stx mn1
    jsr I_UDIV16
    lda mq0
    sta Z0
    lda mq1
    sta Z1
    lda mr0
    sta Z2
    lda mr1
    sta Z3
    rts                     ; C remains 0 from native UDIV16

dh_q0:
    lda #$00
    sta Z0
    sta Z1
    lda ${V2_UMUL16_Z0:02X}
    sta Z2
    stx Z3
    clc
    rts

dh_q1:
    lda #$01
    sta Z0
    lda #$00
    sta Z1
    lda mr0
    sta Z2
    lda mr1
    sta Z3
    clc
    rts

dh_general:
    stx mq1                 ; product byte1
    lda ${V2_UMUL16_Z0:02X}
    sta mq0                 ; product byte0
    tya                     ; product byte3
    cmp md1
    bcc dh_b0
    bne dh_fail
    ldx mr0
    cpx md0
    bcc dh_b0
""")
    out.append(_fail('dh_fail'))
    out.append(_tail('dh'))
    return ''.join(out)


def generate_composed(origin: int = 0xE800) -> str:
    """Public UMUL16 + public UDIV32_16 reference composition."""
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
    ap.add_argument(
        '--kind',
        choices=('bounded', 'hybrid', 'direct-v2', 'direct-hybrid-v2', 'composed'),
        default='bounded',
    )
    ap.add_argument('--profile', choices=('v1', 'v2'), default='v2')
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=None)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()

    origin = 0xE000 if args.origin is None else args.origin
    if args.kind == 'bounded':
        text = generate_bounded(origin)
    elif args.kind == 'hybrid':
        text = generate_hybrid(args.profile, origin)
    elif args.kind == 'direct-v2':
        text = generate_direct_v2(origin)
    elif args.kind == 'direct-hybrid-v2':
        text = generate_direct_hybrid_v2(origin)
    else:
        text = generate_composed(0xE800 if args.origin is None else args.origin)

    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
