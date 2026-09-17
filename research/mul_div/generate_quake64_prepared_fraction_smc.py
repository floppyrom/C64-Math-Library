#!/usr/bin/env python3
"""Generate a Quake64-native prepared strict-fraction ratio candidate.

This candidate targets the actual Quake64 math layout at commit
7c84654946a60314568b709e7e7b97467fed69df and reuses the 2 KiB quarter-square
bank the game already loads under KERNAL:

    sqlo      $F000-$F1FF
    sqhi      $F200-$F3FF
    negsqlo   $F400-$F5FF
    negsqhi   $F600-$F7FF

PREP computes a Q0.16 strict fraction, then self-modifies three absolute,Y
quarter-square products for m0, m1 and |m1-m0|. APPLY uses the same three-
product difference construction as the Pareto 16x16 work, but each 8x8 product
is now an inline fixed-multiplier lookup against tables Quake already owns.

Actual Quake scratch contract:

    nlo:nhi   $5E:$5F   unsigned n / remainder
    dlo:dhi   $60:$61   unsigned d during PREP; APPLY parity/diff-sign after
    ylo:yhi   $62:$63   signed component input (clobbered)
    rot0:rot1 $40:$41   signed APPLY result

Additional scratch is the game's existing math scratch $08-$0C and rot2 $42.
No new zero-page allocation is required for the prototype.

PREP requires 0 < n < d <= 65535 and prepares either floor or nearest Q0.16.
This is game-integration research, not a stable C64 Math Library ABI.
"""
from __future__ import annotations

import argparse
from pathlib import Path

# Existing Quake64 math scratch.
MLO = 0x08       # mul_a
MHI = 0x09       # mul_b
LLO = 0x0A       # prod_l
LHI = 0x0B       # prod_h
YSIGN = 0x0C     # mul_sign
C0 = 0x40        # rot0
C1 = 0x41        # rot1
C2 = 0x42        # rot2
NLO = 0x5E
NHI = 0x5F
DLO = 0x60       # becomes parity after PREP
DHI = 0x61       # becomes sign(m1-m0) after PREP
YLO = 0x62
YHI = 0x63

SQLO = 0xF000
SQHI = 0xF200
NEGSQLO = 0xF400
NEGSQHI = 0xF600


def _header(origin: int, apply_origin: int) -> str:
    return f"""; GENERATED QUAKE64-NATIVE PREPARED FRACTION RESEARCH
; PREP input:  nlo:nhi / dlo:dhi, trusted 0<n<d
; APPLY input: ylo:yhi signed16 (clobbered)
; APPLY output: rot0:rot1 signed16
mlo=${MLO:02X}\nmhi=${MHI:02X}\nllo=${LLO:02X}\nlhi=${LHI:02X}\nysign=${YSIGN:02X}
rot0=${C0:02X}\nrot1=${C1:02X}\nrot2=${C2:02X}
nlo=${NLO:02X}\nnhi=${NHI:02X}\ndlo=${DLO:02X}\ndhi=${DHI:02X}
ylo=${YLO:02X}\nyhi=${YHI:02X}
SQLO=${SQLO:04X}\nSQHI=${SQHI:04X}\nNEGSQLO=${NEGSQLO:04X}\nNEGSQHI=${NEGSQHI:04X}
.org ${origin:04X}
"""


def _fixed_product(prefix: str, yexpr: str, outlo: str, outhi: str) -> str:
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


def _patch_fixed(prefix: str, value_expr: str) -> str:
    return f"""    lda {value_expr}
    sta {prefix}_sl+1
    sta {prefix}_sh+1
    eor #$ff
    sta {prefix}_nl+1
    sta {prefix}_nh+1
"""


def generate(origin: int = 0x9000, apply_origin: int = 0x9800,
             rounding: str = 'floor') -> str:
    if rounding not in ('floor', 'nearest'):
        raise ValueError(rounding)
    p = 'qfrac_prep'
    out = [_header(origin, apply_origin)]
    out.append(f"""{p}:
    ; Trusted interpolation invariant: 0 < n < d.
    ; n is already a legal initial remainder. Generate 16 fractional bits into
    ; rot0:rot1 using the same constrained carry pipeline as MUL_DIV research.
    lda #$00
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
    cmp dhi
    bcc {p}_no{i}
    bne {p}_take{i}
    ldx nlo
    cpx dlo
    bcc {p}_no{i}
{p}_take{i}:
    tax
    lda nlo
    sbc dlo
    sta nlo
    txa
    sbc dhi
    bcs {p}_no{i}
{p}_force{i}:
    ; Carry-out from ROL A is the implicit 17th remainder bit. One subtract is
    ; necessary/sufficient and the generated quotient bit is one.
    tax
    lda nlo
    sbc dlo
    sta nlo
    txa
    sbc dhi
    sec
{p}_no{i}:
""")

    out.append("""    ; Final quotient decision remains in Carry.
    rol rot0
    rol rot1
    sta nhi
""")

    if rounding == 'nearest':
        out.append(f"""    ; Round Q0.16 to nearest iff 2*remainder >= d.
    asl nlo
    rol nhi
    bcs {p}_round
    lda nhi
    cmp dhi
    bcc {p}_patch
    bne {p}_round
    lda nlo
    cmp dlo
    bcc {p}_patch
{p}_round:
    inc rot0
    bne {p}_patch
    inc rot1
""")
    else:
        out.append(f"{p}_patch:\n")

    # Patch multiplier m0/m1 directly into three inline fixed products.
    out.append(_patch_fixed('qm0', 'rot0'))
    out.append(_patch_fixed('qm1', 'rot1'))
    out.append("""
    ; Prepare |m1-m0| and retain its sign in dhi. d is dead after PREP.
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
    sta dhi
    clc
    rts
qfrac_diff_pos:
    sta qmd_sl+1
    sta qmd_sh+1
    eor #$ff
    sta qmd_nl+1
    sta qmd_nh+1
    lda #$00
    sta dhi
    clc
    rts

""")

    out.append(f".org ${apply_origin:04X}\nqfrac_apply_s16:\n")
    out.append("""    ; Magnitude/sign of signed component. ylo:yhi is scratch.
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
    ; v=|y1-y0|. dlo is now parity scratch; dhi is prepared diff sign.
    lda yhi
    sec
    sbc ylo
    bcs qfrac_v_pos
    eor #$ff
    clc
    adc #$01
    tay
    lda dhi
    eor #$80
    sta dlo
    jmp qfrac_q
qfrac_v_pos:
    tay
    lda dhi
    sta dlo
qfrac_q:
    sec
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

    ; Same difference signs -> S-Q; opposite -> S+Q.
    lda dlo
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
    ; Product=M+(cross<<8)+(L<<16). Only bytes 2 and 3 are required.
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
    return ''.join(out)


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
