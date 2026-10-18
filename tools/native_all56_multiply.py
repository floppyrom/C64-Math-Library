#!/usr/bin/env python3
"""Real VICE proof of six MUL APIs while all 56 routines share one PRG.

Two independently relocated complete builds exercise unsigned and signed 8-,
16-, 24-bit multiplication through original public entrypoints. Both direct
arithmetic results and caller input/sentinel preservation are checked by the
individual source-certified VICE oracles. This is not full catalog coverage,
a simultaneous mixed-call workload, or physical machine cycle measurement.
"""
from __future__ import annotations
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import math_builder
import selective_linker
import native_selective_multiply as u16
import native_selective_smul8 as s8
import native_selective_smul16 as s16
import native_selective_umul24 as u24
import native_selective_smul24 as s24

MAPS = ((0x2000, 0x1000, 0x9000, 0x9800),
        (0x4321, 0x1000, 0x9000, 0x9800))
CHECKS = (('MATH_UMUL8', u16), ('MATH_SMUL8', s8),
          ('MATH_UMUL16', u16), ('MATH_SMUL16', s16),
          ('MATH_UMUL24', u24), ('MATH_SMUL24', s24))
N = 96


def main():
    vice = os.environ.get('VICE_WRAPPER', '')
    if not vice or not Path(vice).is_file():
        raise RuntimeError('Set VICE_WRAPPER to a real native x64sc executable')
    index = math_builder.operation_index()
    assert len(index) == 56
    plan = math_builder.create_plan(index, sorted(index),
                                    objective='size', ram_budget=18000,
                                    zp_budget=4)
    total = 0
    with tempfile.TemporaryDirectory(prefix='all56_mul_native_') as tmp:
        folder = Path(tmp)
        for k, (code, harness, inp, out) in enumerate(MAPS):
            man = selective_linker.build(
                plan, folder, memory={'code_base': code, 'math_io': 0xc000,
                                      'zp_base': 0x50, 'scratch_base': 0xc020})
            resources = man['resource_use']
            assert (len(man['operations']) == 56
                    and resources['main_ram_total_bytes'] <= 18000
                    and resources['zero_page_bytes'] <= 4)
            prg = (folder / 'math_selective.prg').read_bytes()
            assert prg[:2] == bytes((code & 255, code >> 8))
            # All independent multiplication oracles write at most 17 output
            # stripes, each $80 apart; none may touch executable or public IO.
            assert (harness + 0x300 <= code
                    and code + len(prg) - 2 <= inp
                    and inp + 0x500 <= out
                    and out + 17 * 0x80 <= 0xc000)
            entries = {op['api']: int(op['entry'][1:], 16)
                       for op in man['operations']}
            for _, verifier in CHECKS:
                verifier.H = harness
                verifier.INPUT = inp
                verifier.OUTPUT = out
            for j, (api, verifier) in enumerate(CHECKS):
                tag = 'all56_mul_%04x_%s' % (code, api.lower())
                port = 8350 + k*16 + j
                entry = entries[api]
                if api == 'MATH_UMUL8':
                    digest = u16.run_native(vice, prg, entry, code, 0xc000,
                                            tag, port, folder, bits=8)
                elif api == 'MATH_SMUL8':
                    digest = s8.verify(vice, prg, entry, code, 0xc000,
                                       tag, port, folder, api)
                else:
                    digest = verifier.run_native(vice, prg, entry, code,
                                                  0xc000, tag, port, folder)
                total += N
                print('ALL56 MUL NATIVE', hex(code), api, N,
                      'PASS', digest, flush=True)
    assert total == len(MAPS) * len(CHECKS) * N, total
    print('ALL-56 TWO-MAP MUL NATIVE PASS', total)


if __name__ == '__main__':
    main()
