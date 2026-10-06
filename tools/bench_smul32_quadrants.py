#!/usr/bin/env python3
from pathlib import Path
import random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler,CPU
from assemble_sources import preprocess,parse_config

PROFILE="v2_pareto_fast"
SRC=ROOT/"relocatable_source"/PROFILE/"math_relocatable.asm"
CFG=ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc"
MASK=(1<<64)-1

def wr(m,a,v):
    for i in range(4): m[a+i]=(v>>(8*i))&255
def rd(m,a):
    return sum(m[a+i]<<(8*i) for i in range(8))
def s32(v): return v-(1<<32) if v&0x80000000 else v

def main():
    text=preprocess(SRC,CFG); md,labels,const=Assembler().assemble(text)
    mem=bytearray(65536)
    for a,b in md.items():mem[a]=b
    cfg=parse_config(CFG);io=cfg["MATH_IO"]
    cpu=CPU(mem);cpu.d=0
    init=labels.get("MATH_INIT",const.get("MATH_INIT"))
    entry=labels.get("MATH_SMUL32",const.get("MATH_SMUL32"))
    cpu.call(init,2_000_000)
    rng=random.Random(0x51504C49)
    specs=[
      ("q0_pos_pos",0,0),
      ("q1_pos_neg",0,1),
      ("q2_neg_pos",1,0),
      ("nn_neg_neg",1,1),
    ]
    for name,sx,sy in specs:
        pairs=[]
        for _ in range(20000):
            x=rng.randrange(0x80000000,1<<32) if sx else rng.randrange(0,0x80000000)
            y=rng.randrange(0x80000000,1<<32) if sy else rng.randrange(0,0x80000000)
            pairs.append((x,y))
        total=0;lo=None;hi=None
        for x,y in pairs:
            wr(cpu.mem,io,x);wr(cpu.mem,io+4,y)
            cy=cpu.call(entry,2_000_000)
            got=rd(cpu.mem,io+8);exp=(s32(x)*s32(y))&MASK
            if got!=exp or cpu.c!=0: raise AssertionError((name,hex(x),hex(y),hex(got),hex(exp),cpu.c))
            total+=cy;lo=cy if lo is None else min(lo,cy);hi=cy if hi is None else max(hi,cy)
        print(f"{name} mean={total/len(pairs):.6f} min={lo} max={hi}")

if __name__=="__main__":main()
