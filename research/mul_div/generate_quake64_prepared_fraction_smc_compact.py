#!/usr/bin/env python3
"""Generate a compact PREP variant of the Quake64 prepared-fraction kernel.

The existing Quake-native candidate unrolls all 16 fractional-division steps.
That is fast but consumes ~1 KiB in a GAME image whose real heap gate is much
tighter than the earlier placement model suggested.

This candidate keeps the exact same SMC APPLY tail and Q0.16 contract but
replaces only PREP's unrolled divider with a compact 16-iteration loop.

Research contract:
    0 < n < d <= 65535
    m = floor(n*65536/d) or round-nearest according to the selected tier
    APPLY result = trunc_toward_zero(signed16_component * m / 65536)

Research only; no stable API is changed.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from generate_quake64_prepared_fraction_smc import generate as generate_unrolled


def _compact_prep(rounding: str) -> str:
    if rounding not in ('floor', 'nearest'):
        raise ValueError(rounding)

    out = ["""qfrac_prep:
    ; Trusted interpolation invariant: 0 < n < d.
    ; Compact restoring fractional divide. n is the initial remainder and
    ; rot0:rot1 accumulates the 16 quotient bits directly.
    lda #$00
    sta rot0
    sta rot1
    ldx #16
qfrac_compact_loop:
    asl rot0
    rol rot1
    asl nlo
    rol nhi
    bcs qfrac_compact_sub
    lda nhi
    cmp dhi
    bcc qfrac_compact_next
    bne qfrac_compact_sub
    lda nlo
    cmp dlo
    bcc qfrac_compact_next
qfrac_compact_sub:
    sec
    lda nlo
    sbc dlo
    sta nlo
    lda nhi
    sbc dhi
    sta nhi
    inc rot0
qfrac_compact_next:
    dex
    bne qfrac_compact_loop
"""]

    if rounding == 'nearest':
        out.append("""
    ; Round Q0.16 to nearest iff 2*remainder >= d.
    asl nlo
    rol nhi
    bcs qfrac_compact_round
    lda nhi
    cmp dhi
    bcc qfrac_prep_patch
    bne qfrac_compact_round
    lda nlo
    cmp dlo
    bcc qfrac_prep_patch
qfrac_compact_round:
    inc rot0
    bne qfrac_prep_patch
    inc rot1
""")

    return ''.join(out)


def generate(origin: int = 0x9000, apply_origin: int = 0x9800,
             rounding: str = 'nearest') -> str:
    # Reuse the proven patch/install and APPLY source byte-for-byte. Only the
    # qfrac_prep divider body is replaced.
    base = generate_unrolled(origin, apply_origin, rounding)
    prep_marker = 'qfrac_prep:\n'
    patch_marker = 'qfrac_prep_patch:\n'
    prep_at = base.index(prep_marker)
    patch_at = base.index(patch_marker)
    return base[:prep_at] + _compact_prep(rounding) + base[patch_at:]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounding', choices=('nearest', 'floor'), default='nearest')
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
