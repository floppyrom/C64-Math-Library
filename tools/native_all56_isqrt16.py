#!/usr/bin/env python3
"""Native VICE proof of both ISQRT16 variants inside all 56 linked operations.

Two complete memory placements and two source-pinned 56-export combinations.
96 deterministic public entry calls per configuration: 384 total. This is
combined-image ABI qualification rather than an exhaustive 56-operation run.
"""
from __future__ import annotations
import os
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import native_selective_isqrt16 as reference

MAPS = (0x2000, 0x4321)
VARIANTS = ('link:radix4-zerozp', 'link:square-table')


def main():
    vice = os.environ.get('VICE_WRAPPER', '')
    if not vice or not Path(vice).is_file():
        raise RuntimeError('VICE_WRAPPER must identify a working native x64sc')
    index = math_builder.operation_index()
    assert len(index) == 56
    reference.H, reference.INPUT, reference.OUTPUT = 0x1000, 0x9000, 0x9800
    checked = 0
    with tempfile.TemporaryDirectory(prefix='full56_isqrt16_native_') as tmp:
        output = Path(tmp)
        for k, code in enumerate(MAPS):
            # Globally choose the default 56-module size configuration once.
            # Reusing its certified 55 other choices for the table comparison
            # isolates the variant under test and avoids a second exponential
            # 56-way combinatorial optimization at unaligned page origins.
            baseline = math_builder.create_plan(
                index, sorted(index), objective='size',
                ram_budget=18000, zp_budget=4)
            memmap = {'code_base': code, 'math_io': 0xc000,
                      'zp_base': 0x50, 'scratch_base': 0xc020}
            chosen = linker.build(baseline, output, memory=memmap)
            assert next(x for x in chosen['operations'] if
                        x['api'] == 'MATH_ISQRT16')['variant'] == VARIANTS[0]
            pins = {item['api'].removeprefix('MATH_'): item['variant']
                    for item in chosen['operations']}
            for j, variant in enumerate(VARIANTS):
                if j == 0:
                    manifest = chosen
                else:
                    pins['ISQRT16'] = variant
                    locked = math_builder.create_plan(
                        index, sorted(index), objective='size',
                        ram_budget=18000, zp_budget=4, pins=pins)
                    manifest = linker.build(locked, output, memory=memmap)
                assert len(manifest['operations']) == 56
                res = manifest['resource_use']
                assert res['main_ram_total_bytes'] <= 18000
                assert res['zero_page_bytes'] <= 4
                prg = (output / 'math_selective.prg').read_bytes()
                assert prg[:2] == bytes((code & 255, code >> 8))
                assert 0x1300 <= code and code + len(prg) - 2 <= reference.INPUT
                root = next(x for x in manifest['operations']
                            if x['api'] == 'MATH_ISQRT16')
                assert root['variant'] == variant
                entry = int(root['entry'][1:], 16)
                tag = f'full56_root16_{code:04x}_{j}'
                digest = reference.verify(vice, prg, entry, code, 0xc000,
                                          tag, 8790+4*k+j, output)
                checked += reference.N
                print('FULL56 ISQRT16 NATIVE', hex(code), variant,
                      reference.N, 'PASS', digest, flush=True)
    assert checked == len(MAPS)*len(VARIANTS)*reference.N
    print('ALL-56 TWO-MAP BOTH ISQRT16 SOURCES NATIVE PASS', checked)

if __name__ == '__main__':
    main()
