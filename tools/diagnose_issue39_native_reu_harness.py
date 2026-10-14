#!/usr/bin/env python3
"""Fast harness model smoke-test to separate REU issues from native monitor."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import CPU
from native_issue39_reu_multiply_modes import P,OPS,H,INPUT,OUTPUT,STRIDE,COUNT,api,pairs,build
from validate_turbo_relocation import parse_inc
def run(profile,entry,bits):
    prg=(R/profile/"resident"/f"math_{profile}_game_math.prg").read_bytes()
    reup=R/profile/"reu"/("c64_math_v3_512k_game_math.reu" if profile==P[0] else "c64_math_v4_16m_game_math.reu")
    mem=bytearray(65536)
    load=int.from_bytes(prg[:2],"little")
    mem[load:load+len(prg)-2]=prg[2:]
    code,stop=build(api(profile),entry,bits)
    mem[H:H+len(code)]=code
    mem[stop]=0x60
    for i,(x,y) in enumerate(pairs(bits)):
        n=bits//8
        for j in range(8):
            val=(x>>(8*j))&255 if j<n else ((y>>(8*(j-4)))&255 if 4<=j<4+n else 0x5c)
            mem[INPUT+j*STRIDE+i]=val
    c=CPU(mem,reu=bytearray(reup.read_bytes()))
    c.d=0
    try:cycles=c.call(H,100_000_000)
    except Exception as e:
        print("MODEL ERROR",profile,entry,"at PC",hex(c.pc),"A",hex(c.a),"X",hex(c.x),"Y",hex(c.y),"SP",hex(c.sp),"cycles",getattr(c,"cycles",None),repr(e),flush=True)
        raise
    print("MODEL HARNESS COMPLETED",profile,entry,"cycles",cycles,"PC",hex(c.pc),"SP",hex(c.sp),"OUTPUT0",[hex(c.mem[OUTPUT+j*STRIDE]) for j in range(8)],flush=True)
    for i,(x,y) in enumerate(pairs(bits)):
        got=sum(c.mem[OUTPUT+j*STRIDE+i]<<(8*j) for j in range(bits//4))
        assert got==x*y,(profile,entry,i,hex(x),hex(y),hex(got),hex(x*y))
    return {"entry":entry,"calls":COUNT,"cycles_for_entire_harness":cycles,"pass":True}
def main():
    out={}
    for p in P:
        out[p]={}
        for entry,bits in OPS+((("MATH_REU_QS16",16),) if p==P[1] else ()):
            out[p][entry]=run(p,entry,bits)
    print("MODEL NATIVE-SHAPED HARNESS PASS",sum(v["calls"] for e in out.values() for v in e.values()),flush=True)
if __name__=="__main__":main()
