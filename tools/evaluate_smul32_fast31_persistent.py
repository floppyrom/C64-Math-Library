#!/usr/bin/env python3
from pathlib import Path
import json, random, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
PROFILES=['v2_pareto_fast','v3_reu_512k','v4_reu_16m']
REU={'v3_reu_512k','v4_reu_16m'}
MASK64=(1<<64)-1
def si32(v): return v-(1<<32) if v&0x80000000 else v
def unhx(s): return int(s[1:],16) if isinstance(s,str) and s.startswith('$') else int(s,0)
def wr(c,a,v,n):
    for i in range(n): c.mem[a+i]=(v>>(8*i))&255
def rd(c,a,n): return sum(c.mem[a+i]<<(8*i) for i in range(n))
def load(p):
    d=ROOT/'build_source/reference'/p
    m=json.loads((d/'source_build_manifest.json').read_text())
    b=(d/m['output_prg']).read_bytes(); ld=b[0]|b[1]<<8
    mem=bytearray(65536); mem[ld:ld+len(b)-2]=b[2:]
    reu=bytearray((d/m['reu_image']['file']).read_bytes()) if m.get('reu_image') else None
    c=CPU(mem,reu=reu); c.d=0
    P={k:unhx(v) for k,v in m['public_entries'].items()}
    I=unhx(m['public_io'].split('-')[0])
    c.call(unhx(m['math_init']),2_000_000)
    return c,P,I
def bench(c,ent,I,pairs,signed=False,shr=False):
    cy=[]; err=0
    for x,y in pairs:
        wr(c,I,x,4); wr(c,I+4,y,4); before=bytes(c.mem[I:I+8])
        n=c.call(ent,2_000_000); cy.append(n)
        prod=(si32(x)*si32(y)) if signed else x*y
        if shr: want=(prod>>16)&((1<<48)-1); got=rd(c,I+8,6)
        else: want=prod&MASK64; got=rd(c,I+8,8)
        if got!=want or c.c!=0 or bytes(c.mem[I:I+8])!=before: err+=1
    return {'cases':len(pairs),'errors':err,'mean_cycles':sum(cy)/len(cy),'min_cycles':min(cy),'max_cycles':max(cy)}
def main():
    out={'profiles':{}}
    edge=[0,1,2,3,0x7fffffff,0x80000000,0x80000001,0xfffffffe,0xffffffff]
    for pi,p in enumerate(PROFILES):
        c,P,I=load(p); rng=random.Random(0xC0FFEE+pi)
        pairs=[(x,y) for x in edge for y in edge]+[(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(5000)]
        rr={}
        for name,signed,shr in [
            ('MATH_SMUL32',True,False),('MATH_UMUL32',False,False),
            ('MATH_SMUL32_SHR16',True,True),('MATH_UMUL32_SHR16',False,True),
            ('MATH_SMUL32_READY',True,False),('MATH_UMUL32_READY',False,False)]:
            rr[name]=bench(c,P[name],I,pairs,signed,shr)
            if rr[name]['errors']: raise SystemExit((p,name,rr[name]))
            print(p,name,rr[name],flush=True)
        out['profiles'][p]=rr
    path=ROOT/'validation/review/SMUL32_FAST31_PERSISTENT_ZP_EVAL.json'
    path.write_text(json.dumps(out,indent=2)+'\n')
    print('WROTE',path)
if __name__=='__main__': main()
