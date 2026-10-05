#!/usr/bin/env python3
from pathlib import Path
import json, random, re, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m']
MASK=lambda b:(1<<b)-1
def si(v,b): return v-(1<<b) if v&(1<<(b-1)) else v
def unhx(s): return int(s[1:],16) if isinstance(s,str) and s.startswith('$') else int(s,0) if isinstance(s,str) else int(s)
def wr(c,a,v,n):
    for i in range(n): c.mem[a+i]=(v>>(8*i))&255
def rd(c,a,n): return sum(c.mem[a+i]<<(8*i) for i in range(n))
def edge_values(bits):
    m=MASK(bits); s=1<<(bits-1)
    vals=[0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]
    return list(dict.fromkeys(v&m for v in vals))
def load(profile,build):
    man=json.loads((build/profile/'source_build_manifest.json').read_text())
    prg=build/profile/man['output_prg']; b=prg.read_bytes(); ld=b[0]|b[1]<<8
    mem=bytearray(65536); mem[ld:ld+len(b)-2]=b[2:]
    reu=None
    if man.get('reu_image'):
        reu=bytearray((build/profile/man['reu_image']['file']).read_bytes())
    c=CPU(mem,reu=reu); c.d=0
    P={k:unhx(v) for k,v in man['public_entries'].items()}
    I=unhx(man['public_io'].split('-')[0])
    c.call(unhx(man['math_init']),2_000_000)
    return c,P,I
def bench(c,entry,I,pairs):
    total=0; mn=None; mx=None; errors=0
    for x,y in pairs:
        for i in range(4):
            c.mem[I+i]=(x>>(8*i))&255
            c.mem[I+4+i]=(y>>(8*i))&255
        before=bytes(c.mem[I:I+8])
        cy=c.call(entry,2_000_000)
        got=rd(c,I+8,8); exp=(si(x,32)*si(y,32))&MASK(64)
        if got!=exp or c.c!=0 or bytes(c.mem[I:I+8])!=before: errors+=1
        total+=cy; mn=cy if mn is None else min(mn,cy); mx=cy if mx is None else max(mx,cy)
    return {'cases':len(pairs),'errors':errors,'mean_cycles':total/len(pairs),'min_cycles':mn,'max_cycles':mx}
def main():
    build=ROOT/'build_source/reference'; out={'profiles':{}}
    e=edge_values(32)
    for pi,p in enumerate(PROFILES):
        c,P,I=load(p,build)
        rng=random.Random(0x5A17_0000 + pi*0x100 + 32)
        pairs=[(x,y) for x in e for y in e]+[(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(2048)]
        ordinary=bench(c,P['MATH_SMUL32'],I,pairs)
        rng=random.Random(0x5320_0000+pi)
        ready_pairs=[(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(1024)]
        ready=bench(c,P['MATH_SMUL32_READY'],I,ready_pairs)
        if ordinary['errors'] or ready['errors']: raise SystemExit((p,ordinary,ready))
        out['profiles'][p]={'MATH_SMUL32':ordinary,'MATH_SMUL32_READY':ready}
        print(p,'SMUL32',ordinary,'READY',ready,flush=True)
    path=ROOT/'validation/review/SMUL32_FAST31_V30_EVAL.json'
    path.write_text(json.dumps(out,indent=2)+'\n')
    print('WROTE',path)
if __name__=='__main__': main()
