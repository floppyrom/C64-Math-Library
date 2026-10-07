#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from source_relocation import load_reference, trace
from mini6502 import REV, SIZE

profiles=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')
for p in profiles:
    raw,_=load_reference(p); seen=trace(p,raw)
    refs=set()
    for pc in seen:
        oc=raw[pc]
        if oc not in REV: continue
        op,mode=REV[oc]
        if mode in ('abs','absx','absy','ind'):
            a=raw[pc+1]|(raw[pc+2]<<8); refs.add(a)
    runs=[]; a=0x1000
    while a<=0x2fff:
        if a in seen or a in refs or raw[a] not in (0x00,0xEA):
            a+=1; continue
        s=a
        while a<=0x2fff and a not in seen and a not in refs and raw[a] in (0x00,0xEA):
            a+=1
        if a-s>=64: runs.append((s,a-1,a-s))
    print('\n',p,'zero/nop unreferenced REG_LOW runs >=64')
    for s,e,n in sorted(runs,key=lambda x:(-x[2],x[0]))[:30]:
        print(hex(s),hex(e),n)
print('MULDIV16 HOLE SURVEY DONE')
