#!/usr/bin/env python3
"""Standalone source-backed full-width V2 high-word root producer probe."""
from __future__ import annotations
import math
import random
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler, CPU

SOURCE=ROOT/"routines/roots/isqrt32_v2_highword_selective.asm"
BASE=0x8000
SQLO=0x9000
SQHI=0x9100
GUESS=0x9200
IO=0xc000
ZP=0x90

def cases():
    values=[0,1,2,3,4,7,8,9,15,16,17,24,25,26,255,256,257,
            65534,65535,65536,65537,0x7fffffff,0x80000000,
            0xfffffffe,0xffffffff]
    for x in (0,1,2,3,15,16,127,128,255,256,257,32767,32768,
              65534,65535):
        values.extend(y for y in range(x*x-2,x*x+3) if 0<=y<=0xffffffff)
    rng=random.Random(0x3215A2)
    values.extend(rng.getrandbits(32) for _ in range(2200))
    values.extend((rng.getrandbits(16)<<16)|(rng.randrange(256)) for _ in range(500))
    return list(dict.fromkeys(values))

def run():
    machine,labels,_=Assembler().assemble(SOURCE.read_text())
    code=[p for p in machine if BASE<=p<0x9000]
    assert min(code)==BASE and code==list(range(BASE,BASE+len(code))) or set(code)==set(range(BASE,BASE+len(code)))
    for page in (SQLO,SQHI,GUESS):
        assert set(range(page,page+256))<=set(machine)
    assert len(machine)==len(code)+768,(len(machine),len(code))
    for i in range(256):
        assert machine[SQLO+i]==((i*i)&255)
        assert machine[SQHI+i]==((i*i)>>8)
        assert machine[GUESS+i]==math.isqrt((i<<8)|255)
    cpu=CPU(bytearray(65536))
    for p,b in machine.items():cpu.mem[p]=b
    entry=labels["LCB40"]
    assert entry==BASE
    old=bytes(cpu.mem[BASE:BASE+len(code)])
    sp=cpu.sp;total=0
    inputs=cases()
    for i,n in enumerate(inputs):
        cpu.mem[IO+16:IO+20]=n.to_bytes(4,"little")
        cpu.mem[IO+8:IO+12]=b"\x55\x55\x96\x69"
        cpu.x=i&255;cpu.y=(i*31)&255
        x,y=cpu.x,cpu.y
        cpu.c=i&1;cpu.d=0
        cycles=cpu.call(entry,85000)
        got=int.from_bytes(cpu.mem[IO+8:IO+10],"little")
        assert got==math.isqrt(n),(i,hex(n),got,math.isqrt(n))
        assert cpu.mem[IO+8:IO+12][2:]==b"\x96\x69"
        assert cpu.mem[IO+16:IO+20]==n.to_bytes(4,"little")
        assert (cpu.x,cpu.y,cpu.sp,cpu.c)==(x,y,sp,0)
        total+=cycles
    assert bytes(cpu.mem[BASE:BASE+len(code)])==old,"code changed"
    print("V2 ROOT32 highword PASS",len(inputs),"code",len(code),
          "table",768,"zp",7,"cycle mean",total/len(inputs),flush=True)
if __name__=="__main__":run()
