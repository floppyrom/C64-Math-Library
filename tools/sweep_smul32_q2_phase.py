#!/usr/bin/env python3
from pathlib import Path
import random, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler, CPU
from assemble_sources import preprocess, parse_config

PROFILE="v2_pareto_fast"
SRC=ROOT/"relocatable_source"/PROFILE/"math_relocatable.asm"
CFG=ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc"
ORIGIN="*= REG_KERNEL+$1500"
MASK64=(1<<64)-1

def wr(mem,a,v,n=4):
    for i in range(n): mem[a+i]=(v>>(8*i))&255

def rd(mem,a,n=8):
    return sum(mem[a+i]<<(8*i) for i in range(n))

def s32(v):
    return v-(1<<32) if v&0x80000000 else v

def assemble(text):
    md,labels,const=Assembler().assemble(text)
    mem=bytearray(65536)
    for a,b in md.items(): mem[a]=b
    return md,labels,const,mem

def bench(text,pairs,io):
    md,labels,const,mem=assemble(text)
    cpu=CPU(mem); cpu.d=0
    init=labels.get("MATH_INIT",const.get("MATH_INIT"))
    entry=labels.get("MATH_SMUL32",const.get("MATH_SMUL32"))
    cpu.call(init,2_000_000)
    total=0; lo=None; hi=None
    for x,y in pairs:
        wr(cpu.mem,io,x); wr(cpu.mem,io+4,y)
        cy=cpu.call(entry,2_000_000)
        got=rd(cpu.mem,io+8)
        exp=(s32(x)*s32(y))&MASK64
        if got!=exp or cpu.c!=0:
            raise AssertionError((hex(x),hex(y),hex(got),hex(exp),cpu.c))
        total+=cy; lo=cy if lo is None else min(lo,cy); hi=cy if hi is None else max(hi,cy)
    return total/len(pairs),lo,hi,labels,md

def main():
    base=preprocess(SRC,CFG)
    if ORIGIN not in base:
        raise SystemExit("q2 origin marker not found")
    cfg=parse_config(CFG); io=cfg["MATH_IO"]
    rng=random.Random(0x5132FACE)
    edge_x=[0x80000000,0x80000001,0x80000002,0xfffffffd,0xfffffffe,0xffffffff]
    edge_y=[0,1,2,3,7,15,127,128,255,0x7ffffffe,0x7fffffff]
    pairs=[(x,y) for x in edge_x for y in edge_y]
    pairs += [(rng.randrange(0x80000000,1<<32),rng.randrange(0,0x80000000)) for _ in range(6000)]

    bmean,blo,bhi,blabels,bmd=bench(base,pairs,io)
    bs=blabels["S32V28_q2_fast_core_start"]
    be=blabels["S32V28_q2_cg_code_end"]
    occupied=set(bmd)
    print(f"baseline start=0x{bs:04x} end=0x{be:04x} bytes={be-bs} mean={bmean:.6f} min={blo} max={bhi}")
    rows=[]
    for delta in range(-12,13):
        if delta==0:
            rows.append((bmean,delta,blo,bhi,bs,be))
            continue
        ns=bs+delta; ne=be+delta
        collision=[a for a in range(ns,ne) if a in occupied and not (bs<=a<be)]
        if collision:
            print(f"delta={delta:+d} SKIP collision first=0x{collision[0]:04x} count={len(collision)}")
            continue
        off=0x1500+delta
        repl=f"*= REG_KERNEL+${off:04X}"
        text=base.replace(ORIGIN,repl,1)
        try:
            mean,lo,hi,labels,md=bench(text,pairs,io)
        except Exception as e:
            print(f"delta={delta:+d} FAIL {type(e).__name__}: {e}")
            continue
        start=labels["S32V28_q2_fast_core_start"]; end=labels["S32V28_q2_cg_code_end"]
        rows.append((mean,delta,lo,hi,start,end))
        print(f"delta={delta:+d} start=0x{start:04x} mean={mean:.6f} diff={mean-bmean:+.6f} min={lo} max={hi}")
    print("ranking:")
    for mean,delta,lo,hi,start,end in sorted(rows):
        print(f"delta={delta:+d} mean={mean:.6f} diff={mean-bmean:+.6f} start=0x{start:04x} min={lo} max={hi}")

if __name__=="__main__":
    main()
