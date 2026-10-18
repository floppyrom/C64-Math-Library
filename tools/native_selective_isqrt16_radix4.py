#!/usr/bin/env python3
"""Qualify size/speed-selected 16-bit tableless and table kernels in real VICE."""
from pathlib import Path
import os
import tempfile
import math_builder
import selective_linker as linker
import native_selective_isqrt16 as native


def main():
    vice=os.environ.get('VICE_WRAPPER','')
    if not Path(vice).is_file():
        raise RuntimeError('Native VICE_WRAPPER must identify x64sc')
    idx=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix='isqrt16_two_map_') as tmp:
        dest=Path(tmp)
        total=0
        for k,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            for j,(ram,expected) in enumerate(((175,'link:radix4-zerozp'),(1100,'link:square-table'))):
                plan=math_builder.create_plan(idx,['ISQRT16'],objective='speed',ram_budget=ram,zp_budget=0)
                man=linker.build(plan,dest,memory={'code_base':code,'math_io':io,
                              'scratch_base':io+32})
                selfile=dest/'math_selective.prg'
                assert man['operations'][0]['variant']==expected
                assert man['resource_use']['main_ram_total_bytes']<=ram
                entry=int(man['operations'][0]['entry'][1:],16)
                digest=native.verify(vice,selfile.read_bytes(),entry,code,io,
                                    f'isqrt16_{k}_{j}',8200+k*4+j,dest)
                total+=native.N
                print('ISQRT16 NATIVE',hex(code),expected,native.N,'PASS',digest,flush=True)
        assert total==384
        print('ISQRT16 BOTH SPEED BUDGET VARIANTS NATIVE PASS',total)

if __name__=='__main__':main()
