#!/usr/bin/env python3
"""Real x64sc proof for four public Q/R exports within a 56-operation PRG.

The loader and test buffers live outside all linked code islands in BOTH
layouts. This is an integration smoke test, not a complete 56-API test nor a
physical C64 cycle benchmark. All tests run on the full combined image.
"""
from __future__ import annotations
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'routines/standalone_lab/portable'))
import math_builder
import selective_linker
import native_vice

MAPS = ((0x2000, 0x1000, 0x9000, 0x9800),
        (0x4321, 0x1000, 0x9000, 0x9800))
CHECKS = (('MATH_UDIV16', 16), ('MATH_UMOD16', 16),
          ('MATH_UDIV32_32', 32), ('MATH_UMOD32_32', 32))


def main():
    if not os.environ.get('VICE_WRAPPER') or not native_vice.VICE.is_file():
        raise RuntimeError('Real native x64sc is required in VICE_WRAPPER')
    index = math_builder.operation_index()
    assert len(index) == 56
    plan = math_builder.create_plan(index, sorted(index),
                                    objective='size', ram_budget=18000,
                                    zp_budget=4)
    checked = 0
    with tempfile.TemporaryDirectory(prefix='native_full56_') as tmp:
        folder = Path(tmp)
        for k, (code, harness, test_input, test_output) in enumerate(MAPS):
            manifest = selective_linker.build(
                plan, folder, memory={'code_base': code, 'math_io': 0xc000,
                                      'zp_base': 0x50, 'scratch_base': 0xc020})
            res = manifest['resource_use']
            assert (len(manifest['operations']) == 56
                    and res['main_ram_total_bytes'] <= 18000
                    and res['zero_page_bytes'] <= 4)
            prg = (folder / 'math_selective.prg').read_bytes()
            assert prg[:2] == bytes((code & 255, code >> 8))
            length = len(prg)-2
            assert (harness+0x300 <= code and code+length <= test_input
                    and test_input+0x500 <= test_output
                    and test_output+0x500 <= 0xc000)
            mem = bytearray(65536)
            mem[code:code+length] = prg[2:]
            entries = {x['api']: (int(x['entry'][1:], 16), x['variant'])
                       for x in manifest['operations']}
            native_vice.H = harness
            native_vice.INPUT = test_input
            native_vice.OUTPUT = test_output
            mp = {'INPUT_NUM': 0xc010, 'INPUT_DIV': 0xc014,
                  'OUTPUT_QUOT': 0xc018, 'OUTPUT_REM': 0xc01c}
            for i, (api, bits) in enumerate(CHECKS):
                entry, variant = entries[api]
                mod_only = (api == 'MATH_UMOD16' or
                            (api == 'MATH_UMOD32_32' and
                             variant != 'link:shared-aligned-zerozp'))
                proof = native_vice.check(
                    bytearray(mem), entry, bits, mp,
                    'full56_%04x_%s' % (code, api.lower()),
                    7990+4*k+i, folder, mod_only)
                assert proof['cases'] == 96
                checked += proof['cases']
                print('FULL56 NATIVE', hex(code), api, proof['cases'],
                      'PASS', flush=True)
    assert checked == 768
    print('ALL-56 TWO-MAP REAL VICE INTEGRATION PASS', checked)


if __name__ == '__main__':
    main()
