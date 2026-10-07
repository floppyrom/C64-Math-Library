#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
import source_relocation as sr
import validate_hybrid as H

def wr(mem,a,v,n):
    for i in range(n): mem[a+i]=(v>>(8*i))&255

def trace_call(cpu,entry,io,n=1,d=1,limit=2000):
    N=io+0x10;D=io+0x14
    wr(cpu.mem,N,n,3);wr(cpu.mem,D,d,3)
    sentinel=0xff00;ret=sentinel-1
    cpu.push(ret>>8);cpu.push(ret&255);cpu.pc=entry
    start=cpu.cycles; seq=[]
    for k in range(limit):
        pc=cpu.pc;before=cpu.cycles
        cpu.step();seq.append((pc,cpu.cycles-before,cpu.pc,cpu.a,cpu.x,cpu.y,cpu.c,cpu.z))
        if cpu.pc==sentinel:return cpu.cycles-start,seq
    raise RuntimeError('limit')

def runs(seq):
    out=[];last=None
    for rec in seq:
        pc=rec[0]
        if last and pc==last[2]:
            last[2]=rec[2];last[3]+=1;last[4]+=rec[1]
        else:
            last=[pc,rec[0],rec[2],1,rec[1]];out.append(last)
    return out

# V2 current generated source build, not stale resident, is the parity donor.
from validate_source_build import load as load_source
v2,P2,I2,_,_=load_source('v2_pareto_fast',ROOT/'build_v5trace'/'reference')
h,PH,IH,_,_=H.load_hybrid('reference')
for tag,cpu,P,I in [('V2',v2,P2,I2),('V5',h,PH,IH)]:
    cy,seq=trace_call(cpu,P['MATH_UDIV24'],I)
    print(tag,'cycles',cy,'entry',hex(P['MATH_UDIV24']),'steps',len(seq))
    print(tag,'first80')
    for r in seq[:80]: print(tag,hex(r[0]),'->',hex(r[2]),'dc',r[1],'A/X/Y/C/Z',r[3:])
    print(tag,'last40')
    for r in seq[-40:]: print(tag,hex(r[0]),'->',hex(r[2]),'dc',r[1],'A/X/Y/C/Z',r[3:])
    print(tag,'critical')
    for a in [P['MATH_UDIV24'],P['MATH_UDIV32_16']]:
        print(hex(a),bytes(cpu.mem[a:a+0x50]).hex())
print('V5 UDIV24 TRACE DONE')
