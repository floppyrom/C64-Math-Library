#!/usr/bin/env python3
"""Generate a Quake64-native prepared strict-fraction ratio candidate.

This research candidate deliberately uses the tables Quake64 already ships:

    sqlo      $F000-$F1FF
    sqhi      $F200-$F3FF
    negsqlo   $F400-$F5FF
    negsqhi   $F600-$F7FF

Instead of calling a generic UMUL8 routine, PREP self-modifies the low operand
bytes of three absolute,Y quarter-square products for:

    m0, m1, |m1-m0|

APPLY then forms only the high 16 bits of abs(y16)*m16 with the same three-
product difference construction used by the Pareto UMUL16 work. The ratio is a
trusted positive strict fraction, so only the sign of y needs handling.

Quake scratch contract used by the prototype:

    nlo:nhi   $48:$49   unsigned n
    dlo:dhi   $4A:$4B   unsigned d on PREP entry
    ylo:yhi   $4C:$4D   signed component on APPLY entry (clobbered)
    rot0:rot1 $45:$46   signed result

PREP requires 0 < n < d <= 65535 and prepares
    m = floor(n*65536/d)          (rounding='floor')
or
    m = round(n*65536/d)          (rounding='nearest').

This is game-integration research, not a stable C64 Math Library ABI.
"""
from __future__ import annotations

import argparse
from pathlib import Path

# Quake64 math scratch/ZP names at fixed addresses.
MLO = 0x40
MHI = 0x41
YSIGN = 0x42
LLO = 0x43
LHI = 0x44
C0 = 0x45
C1 = 0x46
C2 = 0x47
NLO = 0x48
NHI = 0x49
PARITY = 0x4A
PDIFF_SIGN = 0x4B
YLO = 0x4C
YHI = 0x4D

SQLO = 0xF000
SQHI = 0xF200
NEGSQLO = 0xF400
NEGSQHI = 0xF600


def _header(origin: int, apply_origin: int) -> str:
    return f"""; GENERATED QUAKE64-NATIVE PREPARED FRACTION RESEARCH
; PREP input:  nlo:nhi / dlo:dhi, trusted 0<n<d
; APPLY input: ylo:yhi signed16 (clobbered)
; APPLY output: rot0:rot1 signed16
mlo=${MLO:02X}\nmhi=${MHI:02X}\nysign=${YSIGN:02X}
llo=${LLO:02X}\nlhi=${LHI:02X}\nrot0=${C0:02X}\nrot1=${C1:02X}\nrot2=${C2:02X}
nlo=${NLO:02X}\nnhi=${NHI:02X}\nparity=${PARITY:02X}\npdiff_sign=${PDIFF_SIGN:02X}
ylo=${YLO:02X}\nyhi=${YHI:02X}
SQLO=${SQLO:04X}\nSQHI=${SQHI:04X}\nNEGSQLO=${NEGSQLO:04X}\nNEGSQHI=${NEGSQHI:04X}
.org ${origin:04X}
"""


def _patch_multiplier(prefix: str, source: str) -> str:
    """Emit SMC patch code for one already-loaded 8-bit multiplier in A."""
    return f"""    sta {prefix}_sl+1
    sta {prefix}_sh+1
    eor #$ff
    sta {prefix}_nl+1
    sta {prefix}_nh+1
{source}"""


def _fixed_product(prefix: str, yexpr: str, outlo: str, outhi: str) -> str:
    """Inline one fixed 8x8 product using patched absolute,Y table operands."""
    return f"""    ldy {yexpr}
    sec
{prefix}_sl:
    lda SQLO,y
{prefix}_nl:
    sbc NEGSQLO,y
    sta {outlo}
{prefix}_sh:
    lda SQHI,y
{prefix}_nh:
    sbc NEGSQHI,y
    sta {outhi}
"""


def generate(origin: int = 0x9000, apply_origin: int = 0x9800,
             rounding: str = 'floor') -> str:
    if rounding not in ('floor', 'nearest'):
        raise ValueError(rounding)
    p = 'qfrac_prep'
    out = [_header(origin, apply_origin)]
    out.append(f"""{p}:
    ; d occupies parity/pdiff_sign on entry; copy it into the two SMC compare
    ; immediates used by the divider so those ZP bytes can later hold state.
    lda parity
    sta {p}_dlo_cmp+1
    sta {p}_dlo_sub+1
    lda pdiff_sign
    sta {p}_dhi_cmp+1
    sta {p}_dhi_sub+1

    ; quotient uses rot0:rot1, remainder stays nlo:nhi.
    lda #$00
    sta rot0
    sta rot1
    clc
    lda nhi
""")

    # The divisor is copied into instruction immediates because $4A/$4B are
    # reused after PREP as parity/PDIFF_SIGN state. Each step compares/subtracts
    # against the same d bytes through immediate operands.
    for i in range(16):
        out.append(f"""{p}_b{i}:
    rol rot0
    rol rot1
    rol nlo
    rol a
    bcs {p}_force{i}
{p}_dhi_cmp_{i}:
    cmp #$00
    bcc {p}_no{i}
    bne {p}_take{i}
    ldx nlo
{p}_dlo_cmp_{i}:
    cpx #$00
    bcc {p}_no{i}
{p}_take{i}:
    tax
    lda nlo
    sec
{p}_dlo_sub_{i}:
    sbc #$00
    sta nlo
    txa
{p}_dhi_sub_{i}:
    sbc #$00
    bcs {p}_no{i}
{p}_force{i}:
    ; 17th remainder bit guarantees one subtraction and quotient bit 1.
    tax
    lda nlo
    sec
{p}_dlo_force_{i}:
    sbc #$00
    sta nlo
    txa
{p}_dhi_force_{i}:
    sbc #$00
    sec
{p}_no{i}:
""")

    # We need all immediate divisor operands patched. The repeated labels above
    # are patched by a compact patch loop emitted below using absolute stores.
    # Since the mini assembler has no macro/loop-time label arithmetic, emit the
    # stores explicitly from Python.
    patch_lines = []
    for i in range(16):
        patch_lines.extend([
            f"    sta {p}_dlo_cmp_{i}+1",  # caller will load d0 before block
        ])
    # The initial draft labels qfrac_prep_dlo_cmp without suffix are not used;
    # replace the simple prefix with a real patch block by constructing source
    # below. We keep code generation straightforward and readable.

    # Rewrite prefix with per-step operand patching rather than dead labels.
    # Build a fresh prep body here.
    out = [_header(origin, apply_origin)]
    out.append(f"""{p}:
    ; Patch every immediate divisor operand once. PREP is expensive already;
    ; APPLY then needs no divisor state at all.
    lda parity
""")
    for i in range(16):
        out.append(f"    sta {p}_dlo_cmp_{i}+1\n    sta {p}_dlo_sub_{i}+1\n    sta {p}_dlo_force_{i}+1\n")
    out.append("    lda pdiff_sign\n")
    for i in range(16):
        out.append(f"    sta {p}_dhi_cmp_{i}+1\n    sta {p}_dhi_sub_{i}+1\n    sta {p}_dhi_force_{i}+1\n")
    out.append("""    lda #$00
    sta rot0
    sta rot1
    clc
    lda nhi
""")

    for i in range(16):
        out.append(f"""{p}_b{i}:
    rol rot0
    rol rot1
    rol nlo
    rol a
    bcs {p}_force{i}
{p}_dhi_cmp_{i}:
    cmp #$00
    bcc {p}_no{i}
    bne {p}_take{i}
    ldx nlo
{p}_dlo_cmp_{i}:
    cpx #$00
    bcc {p}_no{i}
{p}_take{i}:
    tax
    lda nlo
    sec
{p}_dlo_sub_{i}:
    sbc #$00
    sta nlo
    txa
{p}_dhi_sub_{i}:
    sbc #$00
    bcs {p}_no{i}
{p}_force{i}:
    tax
    lda nlo
    sec
{p}_dlo_force_{i}:
    sbc #$00
    sta nlo
    txa
{p}_dhi_force_{i}:
    sbc #$00
    sec
{p}_no{i}:
""")

    out.append("""    rol rot0
    rol rot1
    sta nhi
""")

    if rounding == 'nearest':
        # Compare doubled remainder against d. d bytes still exist as patched
        # immediates; use step-0 compare operands as canonical copies.
        out.append(f"""    asl nlo
    rol nhi
    bcs {p}_round
    lda nhi
{p}_round_dhi:
    cmp #$00
    bcc {p}_store
    bne {p}_round
    lda nlo
{p}_round_dlo:
    cmp #$00
    bcc {p}_store
{p}_round:
    inc rot0
    bne {p}_store
    inc rot1
{p}_store:
""")
        # Patch these two extra immediates too, but do it at PREP entry. Add
        # stores by inserting explicit patch instructions at the top is awkward;
        # instead copy d into ordinary scratch before it is repurposed.
        # We retain d0/d1 in mlo/mhi during PREP for the rounding compare.
        # The entry code below will have loaded them before the divide.
    else:
        out.append(f"{p}_store:\n")

    # At this point m=rot0:rot1. Prepare the three fixed multipliers by patching
    # low operand bytes of the absolute,Y table references.
    out.append("""    lda rot0
    sta qm0_sl+1
    sta qm0_sh+1
    eor #$ff
    sta qm0_nl+1
    sta qm0_nh+1

    lda rot1
    sta qm1_sl+1
    sta qm1_sh+1
    eor #$ff
    sta qm1_nl+1
    sta qm1_nh+1

    ; |m1-m0| and sign(m1-m0) become the third fixed multiplier/state.
    lda rot1
    sec
    sbc rot0
    bcs qfrac_diff_pos
    eor #$ff
    clc
    adc #$01
    sta qmd_sl+1
    sta qmd_sh+1
    eor #$ff
    sta qmd_nl+1
    sta qmd_nh+1
    lda #$80
    sta pdiff_sign
    clc
    rts
qfrac_diff_pos:
    sta qmd_sl+1
    sta qmd_sh+1
    eor #$ff
    sta qmd_nl+1
    sta qmd_nh+1
    lda #$00
    sta pdiff_sign
    clc
    rts

""")

    out.append(f".org ${apply_origin:04X}\nqfrac_apply_s16:\n")
    out.append("""    ; Magnitude/sign of the signed component. ylo:yhi is scratch.
    lda yhi
    and #$80
    sta ysign
    lda yhi
    bpl qfrac_mag_ready
    sec
    lda #$00
    sbc ylo
    sta ylo
    lda #$00
    sbc yhi
    sta yhi
qfrac_mag_ready:

""")
    out.append(_fixed_product('qm0', 'ylo', 'mlo', 'mhi'))
    out.append("\n")
    out.append(_fixed_product('qm1', 'yhi', 'llo', 'lhi'))
    out.append("""
    ; v=|y1-y0| and parity of byte-difference signs.
    lda yhi
    sec
    sbc ylo
    bcs qfrac_v_pos
    eor #$ff
    clc
    adc #$01
    tay
    lda pdiff_sign
    eor #$80
    sta parity
    jmp qfrac_q
qfrac_v_pos:
    tay
    lda pdiff_sign
    sta parity
qfrac_q:
""")
    # For Q the multiplicand is already in Y, so emit without LDY.
    out.append("""    sec
qmd_sl:
    lda SQLO,y
qmd_nl:
    sbc NEGSQLO,y
    sta nlo
qmd_sh:
    lda SQHI,y
qmd_nh:
    sbc NEGSQHI,y
    sta nhi

    ; S=M+L as 17-bit rot2:rot1:rot0.
    clc
    lda mlo
    adc llo
    sta rot0
    lda mhi
    adc lhi
    sta rot1
    lda #$00
    adc #$00
    sta rot2

    ; Same difference signs -> cross=M+L-Q; opposite -> M+L+Q.
    lda parity
    bne qfrac_cross_add
    sec
    lda rot0
    sbc nlo
    sta rot0
    lda rot1
    sbc nhi
    sta rot1
    lda rot2
    sbc #$00
    sta rot2
    bcs qfrac_combine
qfrac_cross_add:
    clc
    lda rot0
    adc nlo
    sta rot0
    lda rot1
    adc nhi
    sta rot1
    lda rot2
    adc #$00
    sta rot2

qfrac_combine:
    ; Product=M+(cross<<8)+(L<<16). Publish only bytes 2/3.
    lda mhi
    clc
    adc rot0
    lda llo
    adc rot1
    sta rot0
    lda lhi
    adc rot2
    sta rot1

    lda ysign
    beq qfrac_done
    sec
    lda #$00
    sbc rot0
    sta rot0
    lda #$00
    sbc rot1
    sta rot1
qfrac_done:
    clc
    rts
""")

    text = ''.join(out)

    # For nearest rounding we need an ordinary copy of d because the patch-state
    # bytes are repurposed. Insert two stores immediately after the entry label,
    # and use those bytes in the round compare by replacing the immediate form.
    if rounding == 'nearest':
        marker = f"{p}:\n"
        text = text.replace(marker, marker + "    lda parity\n    sta mlo\n    lda pdiff_sign\n    sta mhi\n", 1)
        text = text.replace(f"{p}_round_dhi:\n    cmp #$00", f"{p}_round_dhi:\n    cmp mhi")
        text = text.replace(f"{p}_round_dlo:\n    cmp #$00", f"{p}_round_dlo:\n    cmp mlo")
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounding', choices=('floor', 'nearest'), default='floor')
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=0x9000)
    ap.add_argument('--apply-origin', type=lambda s: int(s, 0), default=0x9800)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    text = generate(args.origin, args.apply_origin, args.rounding)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
