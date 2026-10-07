#!/usr/bin/env python3
"""Validate and benchmark narrow-divisor latency escape paths for UDIV24/UDIV32_32."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from validate_unsigned_division import load as load_resident,wr,rd
from validate_udiv32_16_integrated import load_source

PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')

def one(cpu,entry,io,n,d,nb,db,sentinel=None):
    N,D,Q,R=io+0x10,io+0x14,io+0x18,io+0x1c
    nn=nb//8;dn=db//8
    wr(cpu.mem,N,n,nn);wr(cpu.mem,D,d,dn)
    if sentinel is not None: cpu.mem[N+nn]=sentinel
    bn=bytes(cpu.mem[N:N+nn]);bd=bytes(cpu.mem[D:D+dn])
    cy=cpu.call(entry,4_000_000)
    q=rd(cpu.mem,Q,nn);r=rd(cpu.mem,R,dn)
    if d==0: exp=(0,0,1)
    else:
        qq,rr=divmod(n,d);exp=(qq&((1<<nb)-1),rr&((1<<db)-1),0)
    got=(q,r,cpu.c)
    ok=got==exp and bytes(cpu.mem[N:N+nn])==bn and bytes(cpu.mem[D:D+dn])==bd
    if sentinel is not None: ok=ok and cpu.mem[N+nn]==sentinel
    return cy,ok,got,exp

def st(v): return {'cases':len(v),'mean_cycles':sum(v)/len(v),'min_cycles':min(v),'max_cycles':max(v)}
def paired(old,new,eo,en,io_new,vec,nb,db,sentinel=None):
    oc=[];nc=[];errs=[]
    for n,d in vec:
        a,ok1,g1,e=one(old,eo,0xc000,n,d,nb,db,sentinel)
        b,ok2,g2,_=one(new,en,io_new,n,d,nb,db,sentinel)
        if not(ok1 and ok2):
            errs.append({'n':hex(n),'d':hex(d),'old':g1,'new':g2,'exp':e})
            if len(errs)>=8: break
        oc.append(a);nc.append(b)
    if errs: raise AssertionError(errs)
    delta=[a-b for a,b in zip(oc,nc)]
    return {'old':st(oc),'new':st(nc),'saved_mean_cycles':sum(delta)/len(delta),
            'min_saved_cycles':min(delta),'max_saved_cycles':max(delta),
            'slower_cases':sum(x<0 for x in delta),'equal_cases':sum(x==0 for x in delta),
            '_delta':delta}

def corpora():
    r=random.Random(0x1A7E6C)
    u24=[(r.randrange(1<<24),r.randrange(1,1<<24)) for _ in range(12000)]
    n24=[(r.randrange(1<<24),r.randrange(1,1<<16)) for _ in range(12000)]
    q024=[]
    for _ in range(4000):
        d=r.randrange(1,1<<16);n=r.randrange(d);q024.append((n,d))
    h24=[]
    for d in [1,2,3,7,15,16,31,63,127,128,255,256,257,511,1023,4095,16383,32767,65535]:
        for n in [0,1,d-1,d,d+1,0xffff,0x10000,0x7fffff,0xffffff,max(0,0xffffff-d)]:
            if 0<=n<1<<24:h24.append((n,d))

    u32=[(r.getrandbits(32),r.randrange(1,1<<32)) for _ in range(12000)]
    n32=[(r.getrandbits(32),r.randrange(1,1<<16)) for _ in range(12000)]
    w32=[(r.getrandbits(32),r.randrange(1<<16,1<<32)) for _ in range(5000)]
    d17=[(r.getrandbits(32),r.randrange(0x10000,0x20000)) for _ in range(12000)]
    for d in [0x10000,0x10001,0x10002,0x100ff,0x10100,0x17fff,0x1fffe,0x1ffff]:
        for n in [0,1,d-1,d,d+1,0xffff,0x10000,0xffffff,0x7fffffff,0xfffffffe,0xffffffff]:
            if 0<=n<=0xffffffff:d17.append((n,d))
    h32=[]
    for d in [0,1,2,3,7,15,255,256,257,511,1023,4095,65535,65536,65537,0x7fffffff,0xffffffff]:
        for n in [0,1,max(0,d-1),d,min(0xffffffff,d+1),0xffff,0x10000,0xffffff,0x7fffffff,0xffffffff]:
            if 0<=n<=0xffffffff:h32.append((n,d))
    return {'u24':u24,'n24':n24,'q024':q024,'h24':h24,'u32':u32,'n32':n32,'d17':d17,'w32':w32,'h32':h32}

def main():
    C=corpora();out={'status':'PASS','profiles':{}}
    for p in PROFILES:
        old,Aold=load_resident(p); new,Anew,Inew=load_source(p,'reference'); alt,Aalt,Ialt=load_source(p,'alternate')
        rows={}
        for tag in ('u24','n24','q024','h24'):
            rows[tag]=paired(old,new,Aold['MATH_UDIV24'],Anew['MATH_UDIV24'],Inew,C[tag],24,24,0xA5)
        for tag in ('u32','n32','d17','w32','h32'):
            rows[tag]=paired(old,new,Aold['MATH_UDIV32_32'],Anew['MATH_UDIV32_32'],Inew,C[tag],32,32)
        # The UDIV24 q=0 prefix must remain cycle-identical.  The revised
        # UDIV32 width dispatch may improve the common wide path, but may not
        # make any sampled wide or dedicated 17-bit-divisor case slower.
        assert all(x==0 for x in rows['q024']['_delta']),(p,'UDIV24 q0 path changed',rows['q024'])
        # Three-way width classification makes D3!=0 about four cycles faster.
        # The rare D3=0,D2>=2 band pays at most six cycles for that classifier.
        assert min(rows['w32']['_delta'])>=-6 and rows['w32']['slower_cases']<=len(C['w32'])//100,(p,'UDIV32/32 wide dispatch regression',rows['w32'])
        assert all(x>=0 for x in rows['d17']['_delta']),(p,'UDIV32/32 D17 regression',rows['d17'])
        # Alternate-map exactness on deterministic subsets.
        for ent,tag,nb,db,sent in [('MATH_UDIV24','h24',24,24,0x5A),('MATH_UDIV32_32','h32',32,32,None),('MATH_UDIV32_32','d17',32,32,None)]:
            avec=C[tag] if tag!='d17' else C[tag][:2048]
            for n,d in avec:
                _,ok,g,e=one(alt,Aalt[ent],Ialt,n,d,nb,db,sent)
                if not ok: raise AssertionError((p,'alternate',ent,hex(n),hex(d),g,e))
        for v in rows.values(): v.pop('_delta',None)
        out['profiles'][p]=rows
        print(p,json.dumps(rows,sort_keys=True),flush=True)
    path=ROOT/'validation/research/DIVISION_LATENCY_ESCAPE.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+'\n')
    print('DIVISION LATENCY ESCAPE PASS')
if __name__=='__main__':main()
