#!/usr/bin/env python3
"""Export a Quake-native prepared-fraction research kernel as an ACME include.

Two PREP Pareto points are supported:

  unrolled  fast 16-step fractional divider (~1 KiB complete kernel)
  compact   looped fractional divider (~360 B complete kernel)

Both share the same Quake-native SMC APPLY algorithm and arithmetic contract.
The benchmark generators use fixed research origins plus mini6502's explicit
accumulator spelling (for example `rol a`). A real Quake64 GAME build instead
follows Quake's ACME source stream, where accumulator mode is written `rol`.

The exporter therefore performs integration-only transformations:
  * choose the already benchmarked PREP generator;
  * remove the two fixed research `.org` directives;
  * normalize explicit accumulator shifts/rotates to ACME syntax.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from generate_quake64_prepared_fraction_smc import generate as generate_unrolled
from generate_quake64_prepared_fraction_smc_compact import generate as generate_compact

PROBE_PREP = 0x9000
PROBE_APPLY = 0x9800


def _acme_accumulator_syntax(text: str) -> str:
    # ACME 0.97 parses `rol a` as ROL of symbol `a`, not accumulator mode.
    # Benchmark generators retain the explicit spelling for mini6502; only the
    # real-game export is normalized.
    replacements = {
        '    asl a\n': '    asl\n',
        '    lsr a\n': '    lsr\n',
        '    rol a\n': '    rol\n',
        '    ror a\n': '    ror\n',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def export_source(rounding: str, prep: str = 'unrolled') -> str:
    if prep == 'unrolled':
        text = generate_unrolled(PROBE_PREP, PROBE_APPLY, rounding)
    elif prep == 'compact':
        text = generate_compact(PROBE_PREP, PROBE_APPLY, rounding)
    else:
        raise ValueError(prep)

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
        f'; PREP tier: {prep}\n'
        f'; Ratio rounding tier: {rounding}\n'
        '; Included sequentially in writable GAME RAM.\n'
        '; Accumulator shifts/rotates normalized for ACME 0.97 syntax.\n\n'
    )
    return banner + text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--prep', choices=('unrolled', 'compact'), default='unrolled')
    ap.add_argument('--rounding', choices=('nearest', 'floor'), default='nearest')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    text = export_source(args.rounding, args.prep)
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
