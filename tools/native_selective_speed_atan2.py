#!/usr/bin/env python3
"""Real x64sc validation of BOTH RAM-budget-selected ATAN2_8 public PRGs."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker
import native_selective_atan2

ROOT=Path(__file__).resolve().parents[1]
MAPS=((0x8000,0xc000),(0x7123,0xc040))
VARIANTS=((800,'link:compact','compact'),(1312,'link:sum-fast','sum-fast'))

def main():
    vice=os.environ.get('VICE_WRAPPER','')
    if not Path(vice).is_file():
        raise RuntimeError('VICE_WRAPPER must point to working x64sc')
    index=math_builder.operation_index(ROOT)
    total=0
    with tempfile.TemporaryDirectory(prefix='atan2_speed_native_') as directory:
        folder=Path(directory)
        for k,(code,io) in enumerate(MAPS):
            for j,(budget,expected,kind) in enumerate(VARIANTS):
                plan=math_builder.create_plan(index,['ATAN2_8'],objective='speed',
                        zp_budget=0,ram_budget=budget)
                man=selective_linker.build(plan,folder,root=ROOT,
                        memory={'code_base':code,'math_io':io})
                item=man['operations'][0]
                if item['variant']!=expected or int(item['entry'][1:],16)!=code:
                    raise ValueError('ATAN2 speed selector output differs from qualified source')
                if man['resource_use']['main_ram_total_bytes']>budget:
                    raise ValueError('ATAN2 budget overrun')
                result=native_selective_atan2.run_native(
                    folder/'math_selective.prg',kind,code,io,8550+k*4+j,folder)
                total+=result['case_count']
                print('NATIVE ATAN2 SELECTED',hex(code),budget,expected,
                      result['case_count'],'PASS',flush=True)
    assert total==len(MAPS)*len(VARIANTS)*native_selective_atan2.N
    print('NATIVE ATAN2 SPEED SELECTION PASS',total)

if __name__=='__main__':main()
