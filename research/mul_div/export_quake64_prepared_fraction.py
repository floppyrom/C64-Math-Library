#!/usr/bin/env python3
"""Export the Quake-native prepared-fraction research kernel as an ACME include.

The benchmark generator uses two fixed research origins so its PREP/APPLY
sections can be patched into isolated test memory. A real Quake64 GAME build
must instead let the kernel follow the existing source stream so `end_game`
and `checkheap.py` see the exact occupied bytes.

This exporter removes only those two research `.org` directives. All algorithm,
SMC operands, Quake scratch addresses and table addresses remain identical to
the benchmarked kernel.

Example from the C64-Math-Library checkout:

    python research/mul_div/export_quake64_prepared_fraction.py \
        --rounding nearest \
        --output /path/to/Quake64/src/prepared_fraction_smc.asm

Then apply `QUAKE64_NEARCLIP_EXPERIMENT.patch` to the audited Quake64 snapshot.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from generate_quake64_prepared_fraction_smc import generate

PROBE_PREP = 0x9000
PROBE_APPLY = 0x9800


def export_source(rounding: str) -> str:
    text = generate(PROBE_PREP, PROBE_APPLY, rounding)
    for origin in (PROBE_PREP, PROBE_APPLY):
        marker = f'.org ${origin:04X}\n'
        if marker not in text:
            raise RuntimeError(f'missing expected research origin {marker.strip()}')
        text = text.replace(marker, '', 1)
    if '.org ' in text:
        raise RuntimeError('unexpected fixed origin remains in integration source')
    banner = (
        '; Quake64 integration export from C64-Math-Library MUL_DIV research\n'
        '; Audited target: Kweepa/Quake64 @ '
        '7c84654946a60314568b709e7e7b97467fed69df\n'
        f'; Ratio rounding tier: {rounding}\n'
        '; Included sequentially before end_game; writable GAME RAM required.\n\n'
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
