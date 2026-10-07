#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from source_relocation import load_reference, trace
from mini6502 import REV, SIZE

ranges={
 'v2_pareto_fast':(0x25B2,0x263F),
 'v3_reu_512k':(0x26B2,0x273F),
 'v4_reu_16m':(0x25B2,0x263F),
}
for p,(lo,hi) in ranges.items():
    raw,_=load_reference(p)
    seen=trace(p,raw)
    reachable=sorted(a for a in seen if lo<=a<=hi)
    nonzero=[(a,raw[a]) for a in range(lo,hi+1) if raw[a] not in (0x00,0xEA)]
    # Scan reachable code for absolute data references into the proposed hole.
    refs=[]
    for pc in seen:
        oc=raw[pc]
        if oc not in REV: continue
        op,mode=REV[oc]
        if mode in ('abs','absx','absy','ind'):
            a=raw[pc+1]|(raw[pc+2]<<8)
            if lo<=a<=hi: refs.append((pc,op,mode,a))
    print(p,hex(lo),hex(hi),'bytes',hi-lo+1,'reachable',len(reachable),'nonzero_or_non_nop',len(nonzero),'direct_refs',len(refs))
    print(' first_nonzero',[(hex(a),hex(v)) for a,v in nonzero[:16]])
    print(' refs',[(hex(pc),op,mode,hex(a)) for pc,op,mode,a in refs[:16]])
    assert not reachable,(p,'stable control flow enters candidate hole',reachable[:8])
    assert not refs,(p,'stable code references candidate hole',refs[:8])
    assert not nonzero,(p,'candidate hole is not empty/NOP',nonzero[:8])
print('MULDIV16 SIGNED HOLE PROOF PASS')
