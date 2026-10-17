#!/usr/bin/env python3
"""Two-relocation native x64sc correctness for weighted UMUL8+UMUL16 PRGs."""
import os
from pathlib import Path
import tempfile
import math_builder
import selective_linker
from native_selective_multiply import run_native, N


def main():
    vice = os.environ.get('VICE_WRAPPER')
    if not vice or not Path(vice).is_file():
        raise RuntimeError('VICE_WRAPPER must point to an operational x64sc executable')
    index = math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix='native_weighted_math_') as work:
        folder=Path(work)
        for idx,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(index,['UMUL8','UMUL16'],
                 objective='speed',workload_calls={'UMUL8':120,'UMUL16':20},
                 ram_budget=4096,zp_budget=4)
            man=selective_linker.build(plan,folder,memory={'code_base':code,'math_io':io})
            image=(folder/'math_selective.prg').read_bytes()
            entry={x['api']:int(x['entry'][1:],16) for x in man['operations']}
            for j,(api,bits) in enumerate((('MATH_UMUL8',8),('MATH_UMUL16',16))):
                sha=run_native(vice,image,entry[api],code,io,
                        'global_speed_%s_%04x'%(api,code),9400+idx*4+j,folder,bits=bits)
                total+=N
                print('NATIVE',api,hex(code),'PASS',sha,flush=True)
    assert total == 4*N
    print('NATIVE MIXED SPEED 2-map PASS',total)

if __name__=='__main__':
    main()
