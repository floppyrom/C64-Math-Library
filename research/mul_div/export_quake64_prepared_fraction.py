#!/usr/bin/env python3
"""Export the Quake-native prepared-fraction research kernel as an ACME include.

The benchmark generator uses two fixed research origins and the mini6502
assembler's explicit accumulator spelling (for example `rol a`). A real
Quake64 GAME build must instead follow Quake's ACME source stream, where the
accumulator form is written simply as `rol`.

This exporter therefore performs only integration-syntax transformations:
  * remove the two fixed research `.org` directives;
  * normalize explicit accumulator shifts/rotates to ACME syntax.

The arithmetic, branches, SMC operands, scratch addresses and quarter-square
table addresses remain identical to the benchmarked kernel.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from generate_quake64_prepared_fraction_smc import generate

PROBE_PREP = 0x9000
PROBE_APPLY = 0x9800


def _acme_accumulator_syntax(text: str) -> str:
    # ACME 0.97 parses `rol a` as ROL of symbol `a`, not accumulator mode.
    # The benchmark assembler accepts the explicit spelling, so keep that in
    # the generator and normalize only the real-game export.
    replacements = {
        '    asl a\n': '    asl\n',
        '    lsr a\n': '    lsr\n',
        '    rol a\n': '    rol\n',
        '    ror a\n': '    ror\n',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def export_source(rounding: str) -> str:
    text = generate(PROBE_PREP, PROBE_APPLY, rounding)
    for origin in (PROBE_PREP, PROBE_APPLY):
        marker = f'.org ${origin:04X}\n'
        if marker not in text:
            raise RuntimeError(f'missing expected research origin {marker.strip()}')
        text = text.replace(marker, '', 1)
    if '.org ' in text:
        raise RuntimeError('unexpected fixed origin remains in integration source')

    text = _acme_accumulator_syntax(text)
    for bad in ('    asl a\n', '    lsr a\n', '    rol a\n', '    ror a\n'):
        if bad in text:
            raise RuntimeError(f'unconverted ACME accumulator syntax: {bad.strip()}')

    banner = (
        '; Quake64 integration export from C64-Math-Library MUL_DIV research\n'
        '; Audited target: Kweepa/Quake64 @ '
        '7c84654946a60314568b709e7e7b97467fed69df\n'
        f'; Ratio rounding tier: {rounding}\n'
        '; Included sequentially before end_game; writable GAME RAM required.\n'
        '; Accumulator shifts/rotates normalized for ACME 0.97 syntax.\n\n'
    )
    return banner + text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounding', choices=('nearest', 'floor'), default='nearest')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    text = export_source(args.rounding)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
