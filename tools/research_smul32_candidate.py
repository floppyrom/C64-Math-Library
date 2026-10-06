#!/usr/bin/env python3
from pathlib import Path
import random,re,sys,json,time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

BUILD=ROOT/'build_source/reference/v2_pareto_fast'
PRG=BUILD/'math_v2_pareto_fast_source_built.prg'
INC=BUILD/'math_api.inc'
IO=0xC000
MASK=(1<<64)-1

def parse_api(path):
    out={}
    for line in path.read_text().splitlines():
        m=re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
        if m: out[m.group(1)]=int(m.group(2),16)
    return out

def wr(mem,a,v,n=4):
    for i in range(n): mem[a+i]=(v>>(8*i))&0xff

def rd(mem,a,n=8):
    return sum(mem[a+i]<<(8*i) for i in range(n))

def sv(v,bits=32):
    return v-(1<<bits) if v&(1<<(bits-1)) else v

def edge_values():
    m=(1<<32)-1;s=1<<31
    vals=[0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]
    return list(dict.fromkeys(x&m for x in vals))

def main():
    api=parse_api(INC)
    b=PRG.read_bytes();load=b[0]|b[1]<<8
    mem=bytearray(65536);mem[load:load+len(b)-2]=b[2:]
    cpu=CPU(mem);cpu.d=0
    cpu.call(api['MATH_INIT'],2_000_000)
    e=edge_values()
    pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x5A17_0000+1*0x100+32)
    pairs += [(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(2048)]
    # Additional stress is deliberately independent of the canonical profile corpus.
    stress=random.Random(0x51A32C0)
    pairs += [(stress.randrange(1<<31),stress.randrange(1<<31)) for _ in range(20000)]

    total=0;mn=None;mx=None;errors=0
    quad={k:[0,0] for k in ('PP','PN','NP','NN')}
    for x,y in pairs:
        wr(cpu.mem,IO,x);wr(cpu.mem,IO+4,y)
        before=bytes(cpu.mem[IO:IO+8])
        cy=cpu.call(api['MATH_SMUL32'],2_000_000)
        got=rd(cpu.mem,IO+8)
        exp=(sv(x)*sv(y))&MASK
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+8])!=before:
            errors+=1
            if errors<=8:
                print('ERROR',hex(x),hex(y),hex(got),hex(exp),'C',cpu.c)
        total+=cy;mn=cy if mn is None else min(mn,cy);mx=cy if mx is None else max(mx,cy)
        q=('N' if x>>31 else 'P')+('N' if y>>31 else 'P')
        quad[q][0]+=cy;quad[q][1]+=1
    out={
      'status':'PASS' if errors==0 else 'FAIL',
      'cases':len(pairs),'errors':errors,'mean_cycles':total/len(pairs),
      'min_cycles':mn,'max_cycles':mx,
      'quadrants':{q:{'cases':n,'mean_cycles':s/n if n else None} for q,(s,n) in quad.items()}
    }
    print('SMUL32_RESEARCH_RESULT '+json.dumps(out,sort_keys=True))
    if errors: raise SystemExit(1)
if __name__=='__main__': main()
