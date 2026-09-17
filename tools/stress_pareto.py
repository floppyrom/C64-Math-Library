#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, random, sys, time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import validate_pareto as vp

MASK=lambda b:(1<<b)-1

def smul16_parity(out:Path,cases=50144):
    c,P,I,M=vp.load_custom(out); v,P2,I2=vp.load_v2(); rng=random.Random(0x516D16)
    edges=[0,1,2,0x7fff,0x8000,0xfffe,0xffff,0x4000,0xc000]
    seq=[]
    for x in edges:
        for y in edges: seq.append((x,y))
    while len(seq)<cases:
        seq.append((rng.randrange(1<<16),rng.randrange(1<<16)))
    for x,y in seq[:cases]:
        vp.wr(c,I,x,2);vp.wr(c,I+4,y,2);cy=c.call(P['MATH_SMUL16'],300000);o=vp.rd(c,I+8,4);cc=c.c
        vp.wr(v,I2,x,2);vp.wr(v,I2+4,y,2);cy2=v.call(P2['MATH_SMUL16'],300000);o2=vp.rd(v,I2+8,4);cc2=v.c
        assert (cy,o,cc)==(cy2,o2,cc2),(x,y,cy,cy2,hex(o),hex(o2),cc,cc2)
    return cases

def mixed_workload(out:Path,iterations=25000):
    c,P,I,M=vp.load_custom(out);rng=random.Random(0xC645A11)
    for i in range(iterations):
        m=i%11
        if m==0:
            x=rng.randrange(1<<8);y=rng.randrange(1<<8);vp.wr(c,I,x,1);vp.wr(c,I+4,y,1);c.call(P['MATH_UMUL8'],100000);assert vp.rd(c,I+8,2)==x*y
        elif m==1:
            x=rng.randrange(1<<16);y=rng.randrange(1<<16);vp.wr(c,I,x,2);vp.wr(c,I+4,y,2);c.call(P['MATH_UMUL16'],150000);assert vp.rd(c,I+8,4)==x*y
        elif m==2:
            x=rng.randrange(1<<24);y=rng.randrange(1<<24);vp.wr(c,I,x,3);vp.wr(c,I+4,y,3);c.call(P['MATH_UMUL24'],250000);assert vp.rd(c,I+8,6)==x*y
        elif m==3:
            x=rng.randrange(1<<32);y=rng.randrange(1<<32);vp.wr(c,I,x,4);vp.wr(c,I+4,y,4);c.call(P['MATH_UMUL32'],350000);assert vp.rd(c,I+8,8)==x*y
        elif m==4:
            x=rng.randrange(1<<16);y=rng.randrange(1<<16);vp.wr(c,I,x,2);vp.wr(c,I+4,y,2);c.call(P['MATH_SMUL16'],300000)
            sx=vp.signed(x,16);sy=vp.signed(y,16);assert vp.rd(c,I+8,4)==((sx*sy)&MASK(32))
        elif m==5:
            n=rng.randrange(1<<16);d=rng.randrange(1<<16);vp.wr(c,I+0x10,n,2);vp.wr(c,I+0x14,d,2);c.call(P['MATH_UDIV16'],300000)
            if d==0: assert c.c==1 and vp.rd(c,I+0x18,2)==0 and vp.rd(c,I+0x1c,2)==0
            else: assert c.c==0 and vp.rd(c,I+0x18,2)==n//d and vp.rd(c,I+0x1c,2)==n%d
        elif m==6:
            n=rng.randrange(1<<32);d=rng.randrange(1<<16);vp.wr(c,I+0x10,n,4);vp.wr(c,I+0x14,d,2);c.call(P['MATH_UDIV32_16'],2_000_000)
            if d==0: assert c.c==1 and vp.rd(c,I+0x18,4)==0 and vp.rd(c,I+0x1c,2)==0
            else: assert c.c==0 and vp.rd(c,I+0x18,4)==n//d and vp.rd(c,I+0x1c,2)==n%d
        elif m==7:
            n=rng.randrange(256);d=rng.randrange(256);c.mem[I+0x10]=n;c.mem[I+0x14]=d;c.call(P['MATH_UMOD8'],10000)
            assert (c.c==1 and c.mem[I+0x1c]==0) if d==0 else (c.c==0 and c.mem[I+0x1c]==n%d)
        elif m==8:
            ph=rng.randrange(256);c.mem[I]=ph;c.call(P['MATH_SINCOS8'],10000)
        elif m==9:
            rx=rng.randrange(256);ry=rng.randrange(256);sx=rx if rx<128 else rx-256;sy=ry if ry<128 else ry-256
            c.mem[I]=rx;c.mem[I+4]=ry;c.call(P['MATH_ATAN2_8'],10000);got=c.mem[I+8]
            import math
            exp=0 if sx==0 and sy==0 else round((math.atan2(sy,sx)%(2*math.pi))*128/math.pi)&255
            assert min((got-exp)&255,(exp-got)&255)<=1 and c.c==0
        else:
            n=rng.randrange(1<<32);vp.wr(c,I+0x10,n,4);c.call(P['MATH_ISQRT32'],200000);r=vp.rd(c,I+8,2);assert r*r<=n<(r+1)*(r+1)
    return iterations

def main():
    t=time.time();out,_=vp.build_point(176,'reference','stress_zp176_reference')
    s=smul16_parity(out)
    m=mixed_workload(out)
    z=vp.zp_guard(out,10000)
    result={'status':'PASS','smul16_v2_cycle_parity_cases':s,'mixed_workload_iterations':m,'zp_guard_iterations':z['iterations'],'outside_zp_bytes_unchanged':z['outside_bytes_unchanged'],'elapsed_seconds':round(time.time()-t,3)}
    q=ROOT/'validation/pareto/PARETO_STRESS.json';q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(result,indent=2)+'\n')
    print('PARETO STRESS PASS',json.dumps(result))

if __name__=='__main__':main()
