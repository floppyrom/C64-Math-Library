#!/usr/bin/env python3
"""Real x64sc proof for twelve public DIV/MOD exports within a 56-operation PRG.

The loader and test buffers live outside all linked code islands in BOTH
layouts. This is a representative arithmetic integration test, not a complete 56-API test nor a
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
import native_selective_u24 as native_u24
import native_selective_sdiv8 as native_s8
import native_selective_sdiv16 as native_s16

MAPS = ((0x2000, 0x1000, 0x9000, 0x9800),
        (0x4321, 0x1000, 0x9000, 0x9800))
CHECKS = (('MATH_UDIV8', 8), ('MATH_UMOD8', 8),
          ('MATH_UDIV16', 16), ('MATH_UMOD16', 16),
          ('MATH_UDIV32_32', 32), ('MATH_UMOD32_32', 32))
EXTRA_CHECKS = (('MATH_UDIV24', native_u24), ('MATH_UMOD24', native_u24),
                ('MATH_SDIV8', native_s8), ('MATH_SMOD8', native_s8),
                ('MATH_SDIV16', native_s16), ('MATH_SMOD16', native_s16))
CALLS_PER_API_PER_MAP = 96
TOTAL_CALLS = len(MAPS) * (len(CHECKS) + len(EXTRA_CHECKS)) * CALLS_PER_API_PER_MAP



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
            # Signed16 verifier uses 17 output stripes of $80 bytes.
            # No harness, test operand, output, or public IO may overlap
            # an executable or other live region of the combined image.
            assert (harness+0x300 <= code and code+length <= test_input
                    and test_input+0x500 <= test_output
                    and test_output+17*0x80 <= 0xc000)
            mem = bytearray(65536)
            mem[code:code+length] = prg[2:]
            entries = {x['api']: (int(x['entry'][1:], 16), x['variant'])
                       for x in manifest['operations']}
            for module in (native_vice, native_u24, native_s8, native_s16):
                module.H = harness
                module.INPUT = test_input
                module.OUTPUT = test_output
            mp = {'INPUT_NUM': 0xc010, 'INPUT_DIV': 0xc014,
                  'OUTPUT_QUOT': 0xc018, 'OUTPUT_REM': 0xc01c}
            for i, (api, bits) in enumerate(CHECKS):
                entry, variant = entries[api]
                mod_only = (api in ('MATH_UMOD8', 'MATH_UMOD16') or
                            (api == 'MATH_UMOD32_32' and
                             variant != 'link:shared-aligned-zerozp'))
                proof = native_vice.check(
                    bytearray(mem), entry, bits, mp,
                    'full56_%04x_%s' % (code, api.lower()),
                    7990+16*k+i, folder, mod_only)
                assert proof['cases'] == CALLS_PER_API_PER_MAP
                checked += proof['cases']
                print('FULL56 NATIVE', hex(code), api, proof['cases'],
                      'PASS', flush=True)
            for j, (api, module) in enumerate(EXTRA_CHECKS):
                entry, variant = entries[api]
                tag = 'full56_%04x_%s' % (code, api.lower())
                port = 7990 + 16*k + len(CHECKS) + j
                if module is native_u24:
                    # Unlike most UMOD public routines, the shared
                    # UDIV24/UMOD24 kernel writes both Q24 and R24.
                    digest = module.native(os.environ['VICE_WRAPPER'],
                                           bytearray(mem), entry, code,
                                           0xc000, tag, port, folder)
                else:
                    # These signed kernels return both Q and R and preserve
                    # the public input bytes; reuse their independent
                    # sign, overflow and divide-by-zero VICE oracle.
                    digest = module.verify(os.environ['VICE_WRAPPER'], prg,
                                           entry, code, 0xc000, tag, port,
                                           folder)
                checked += CALLS_PER_API_PER_MAP
                print('FULL56 NATIVE', hex(code), api,
                      CALLS_PER_API_PER_MAP, 'PASS', digest, flush=True)
    assert checked == TOTAL_CALLS, (checked, TOTAL_CALLS)
    print('ALL-56 TWO-MAP REAL VICE INTEGRATION PASS', checked)


if __name__ == '__main__':
    main()
