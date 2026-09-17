#!/usr/bin/env python3
"""Generate chunked carry-pipelined Quake64 prepared-fraction PREP variants.

The compact loop is small but reloads/compares a memory high remainder every
bit. The full unrolled PREP is fast but costs about 1 KiB and leaves only 34 B
of E1M2 heap slack in the real Quake build.

This generator explores the middle Pareto region. It keeps the unrolled
algorithm's high remainder live in A and its quotient decision live in Carry,
but repeats a small block of 1/2/4/8 bit steps through a ZP group counter.
DEC/BNE preserve both A and Carry, so no remainder reload is needed at group
boundaries.

Existing Quake scratch `mul_a` ($08) is used as the PREP-only group counter; it
is dead before APPLY and therefore adds no ZP allocation.

Research contract is unchanged:
    0 < n < d <= 65535
    nearest/floor Q0.16 m
    same Quake-native SMC APPLY as the proven unrolled candidate
"""
from __future__ import annotations

import argparse
from pathlib import Path

from generate_quake64_prepared_fraction_smc import generate as generate_unrolled

VALID_CHUNKS = (1, 2, 4, 8)


def _step(prefix: str, i: int) -> str:
    return f"""{prefix}_b{i}:
    rol rot0
    rol rot1
    rol nlo
    rol a
    bcs {prefix}_force{i}
    cmp dhi
    bcc {prefix}_no{i}
    bne {prefix}_take{i}
    ldx nlo
    cpx dlo
    bcc {prefix}_no{i}
{prefix}_take{i}:
    tax
    lda nlo
    sbc dlo
    sta nlo
    txa
    sbc dhi
    bcs {prefix}_no{i}
{prefix}_force{i}:
    tax
    lda nlo
    sbc dlo
    sta nlo
    txa
    sbc dhi
    sec
{prefix}_no{i}:
"""


def _chunked_prep(chunk: int, rounding: str) -> str:
    if chunk not in VALID_CHUNKS:
        raise ValueError(chunk)
    if rounding not in ('floor', 'nearest'):
        raise ValueError(rounding)

    groups = 16 // chunk
    p = f'qfrac_chunk{chunk}'
    out = [f"""qfrac_prep:
    ; Trusted interpolation invariant: 0 < n < d.
    ; Carry-pipelined {chunk}-bit block repeated {groups} times.
    lda #$00
    sta rot0
    sta rot1
    lda #{groups}
    sta mlo                  ; existing Quake mul_a scratch, PREP-only counter
    clc
    lda nhi
{p}_loop:
"""]
    for i in range(chunk):
        out.append(_step(p, i))

    out.append(f"""    ; DEC/BNE preserve A and Carry, so the next group continues
    ; the remainder and quotient-decision pipeline without a reload.
    dec mlo
    bne {p}_loop

    ; Final quotient decision remains in Carry.
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
    bcc qfrac_prep_patch
    bne {p}_round
    lda nlo
    cmp dlo
    bcc qfrac_prep_patch
{p}_round:
    inc rot0
    bne qfrac_prep_patch
    inc rot1
""")
    return ''.join(out)


def generate(origin: int = 0x9000, apply_origin: int = 0x9800,
             rounding: str = 'nearest', chunk: int = 4) -> str:
    base = generate_unrolled(origin, apply_origin, rounding)
    prep_at = base.index('qfrac_prep:\n')
    patch_at = base.index('qfrac_prep_patch:\n')
    return base[:prep_at] + _chunked_prep(chunk, rounding) + base[patch_at:]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--chunk', type=int, choices=VALID_CHUNKS, default=4)
    ap.add_argument('--rounding', choices=('nearest', 'floor'), default='nearest')
    ap.add_argument('--origin', type=lambda s: int(s, 0), default=0x9000)
    ap.add_argument('--apply-origin', type=lambda s: int(s, 0), default=0x9800)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    text = generate(args.origin, args.apply_origin, args.rounding, args.chunk)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
