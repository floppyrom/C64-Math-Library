#!/usr/bin/env python3
"""Real VICE dual-map validation for budget-selected historical 0-ZP UDIV16."""
from __future__ import annotations
import os,tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"routines/standalone_lab/portable"))
import math_builder,selective_linker
from native_vice import VICE,check
ROOT=Path(__file__).resolve().parents[1]

def main():
    vice=os.environ.get('VICE_WRAPPER','')
    if not vice or not VICE.is_file():raise RuntimeError('VICE_WRAPPER must locate real x64sc')
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix='u16_v2_native_') as td:
        folder=Path(td)
        for k,(base,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            for j,(budget,zp,variant) in enumerate(((355,2,'link:biased'),(1513,0,'link:v2-zerozp'))):
                plan=math_builder.create_plan(index,['UDIV16'],objective='speed',
                    ram_budget=budget,zp_budget=zp)
                man=selective_linker.build(plan,folder,memory={'code_base':base,'math_io':io})
                entry=man['operations'][0]
                assert entry['variant']==variant,(entry['variant'],variant)
                prg=(folder/'math_selective.prg').read_bytes()
                mem=bytearray(65536);mem[base:base+len(prg)-2]=prg[2:]
                mapped={'INPUT_NUM':io+16,'INPUT_DIV':io+20,'OUTPUT_QUOT':io+24,'OUTPUT_REM':io+28}
                row=check(mem,int(entry['entry'][1:],16),16,mapped,
                    f'speed_u16_{base:04x}_{j}',8800+k*2+j,folder,False)
                total+=row['cases']
                print('NATIVE SELECTED UDIV16',hex(base),variant,row['cases'],'PASS',flush=True)
    assert total==384,total
    print('TWO-MAP ZERO-ZP UDIV16 NATIVE PASS',total)
if __name__=='__main__':main()
