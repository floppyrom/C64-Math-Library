#!/usr/bin/env python3
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import load as load_resident,wr,rd
from validate_udiv32_16_integrated import load_source

P='v2_pareto_fast'; NVAL=0xfeac93; DVAL=0x0d3907

def setup(cpu,entry,io):
    wr(cpu.mem,io+0x10,NVAL,3); wr(cpu.mem,io+0x14,DVAL,3); cpu.mem[io+0x13]=0xA5
    sentinel=0xFF00; ret=(sentinel-1)&0xffff
    cpu.push(ret>>8);cpu.push(ret&255);cpu.pc=entry
    return sentinel

def trace(cpu,entry,io):
    sentinel=setup(cpu,entry,io); out=[]; steps=0
    while cpu.pc!=sentinel and steps<20000:
        pc=cpu.pc
        out.append((pc,cpu.a,cpu.x,cpu.y,cpu.c,cpu.sp))
        cpu.step();steps+=1
    return out,(rd(cpu.mem,io+0x18,3),rd(cpu.mem,io+0x1c,3),cpu.c),cpu.cycles

old,Ao=load_resident(P); new,An,io=load_source(P,'reference')
to,go,co=trace(old,Ao['MATH_UDIV24'],0xc000)
tn,gn,cn=trace(new,An['MATH_UDIV24'],io)
print('OLD',go,co,'NEW',gn,cn,'lens',len(to),len(tn))
# Same addresses are expected until an intentional redirect. Show first 30
# mismatched PCs/state tuples, plus contexts around first mismatch.
first=None
for i,(a,b) in enumerate(zip(to,tn)):
    if a!=b:
        first=i;break
print('first mismatch index',first)
if first is not None:
    for i in range(max(0,first-12),min(max(len(to),len(tn)),first+50)):
        print(i,'O',to[i] if i<len(to) else None,'N',tn[i] if i<len(tn) else None)
# Also list any execution through the latency helpers / patched sites using
# source labels from the source build manifest is unavailable here; print PCs
# unique to new trace compared with old.
so={x[0] for x in to};sn={x[0] for x in tn}
print('NEW_ONLY', [hex(x) for x in sorted(sn-so)[:120]])
