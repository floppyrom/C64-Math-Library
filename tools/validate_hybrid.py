#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, json, math, random, sys, time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
import source_relocation as sr
import validate_source_build as common

PROFILE='v5_hybrid_lowzp'
MASK=lambda b:(1<<b)-1

def unhx(s): return int(s[1:],16) if isinstance(s,str) and s.startswith('$') else int(s)
def wr(c,a,v,n):
    for i in range(n): c.mem[a+i]=(v>>(8*i))&255
def rd(c,a,n): return sum(c.mem[a+i]<<(8*i) for i in range(n))

def load_hybrid(kind):
    return common.load(PROFILE,ROOT/'build_hybrid'/kind)

def load_hybrid_no_init(kind):
    """Load a generated V5 image without calling MATH_INIT.

    V5 intentionally retains V1's zero-assumption contract for ordinary/safe
    entries.  READY-only entries still have their documented V1 precondition.
    """
    build=ROOT/'build_hybrid'/kind/PROFILE
    man=json.loads((build/'source_build_manifest.json').read_text())
    p=build/man['output_prg']; b=p.read_bytes(); ld=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[ld:ld+len(b)-2]=b[2:]
    c=CPU(mem); c.d=0
    pub={k:unhx(v) for k,v in man['public_entries'].items()}
    io=unhx(man['public_io'].split('-')[0])
    return c,pub,io,man

def load_release(profile):
    raw,init=sr.load_reference(profile)
    c=CPU(bytearray(raw)); c.mem[:]=init[:]  # MATH_INIT state, no REU needed for V2
    c.d=0
    P={n:a for n,a in sr.public_entries()}
    return c,P,0xC000

def call_div(c,P,I,name,nbits,dbits,n,d):
    N=I+0x10;D=I+0x14;Q=I+0x18;R=I+0x1c
    nn=nbits//8;dn=dbits//8;d &= MASK(dbits)
    wr(c,N,n,nn);wr(c,D,d,dn); beforeN=bytes(c.mem[N:N+nn]);beforeD=bytes(c.mem[D:D+dn])
    cy=c.call(P[name],2_000_000);q=rd(c,Q,nn);r=rd(c,R,dn)
    if d==0:
        assert c.c==1 and q==0 and r==0,(name,n,d,q,r,c.c)
    else:
        assert c.c==0 and (q,r)==divmod(n,d),(name,n,d,q,r,divmod(n,d),c.c)
    assert bytes(c.mem[N:N+nn])==beforeN and bytes(c.mem[D:D+dn])==beforeD
    return cy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--random-per-family',type=int,default=3000);ap.add_argument('--mixed',type=int,default=3000);a=ap.parse_args()
    t0=time.time(); out={'profile':PROFILE,'status':'PASS','tests':{}}

    # Full 45-entry public validation on both maps.
    for kind in ('reference','alternate'):
        r=common.validate(PROFILE,ROOT/'build_hybrid'/kind)
        out['tests'][f'common_{kind}']={'status':'PASS','public_entries':r['public_entries_executed'],'machine_calls':r['machine_calls']}

    # Authoritative V2 release model for exact direct-call cycle parity.
    v2,P2,I2=load_release('v2_pareto_fast')
    h,PH,IH,MH,_=load_hybrid('reference')
    rng=random.Random(0xC64A55A5)
    edges16=[0,1,2,3,7,15,16,31,127,128,255,256,257,0x7fff,0x8000,0xfffe,0xffff]
    edges24=[0,1,2,3,255,256,257,0xffff,0x10000,0x7fffff,0x800000,0xfffffe,0xffffff]
    edges32=[0,1,2,3,255,256,65535,65536,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
    parity={}
    specs=[('MATH_UDIV16',16,16,edges16),('MATH_UDIV24',24,24,edges24),('MATH_UDIV32_16',32,16,edges32)]
    for name,nb,db,edges in specs:
        count=0
        # Structured edge cross-product (divisor masked to width).
        for n in edges:
            for d in edges16 if db==16 else edges24:
                n &= MASK(nb); d &= MASK(db)
                ch=call_div(h,PH,IH,name,nb,db,n,d); cv=call_div(v2,P2,I2,name,nb,db,n,d)
                assert ch==cv,(name,'cycle mismatch',n,d,ch,cv);count+=1
        for _ in range(a.random_per_family):
            n=rng.randrange(1<<nb);d=rng.randrange(1<<db)
            ch=call_div(h,PH,IH,name,nb,db,n,d);cv=call_div(v2,P2,I2,name,nb,db,n,d)
            assert ch==cv,(name,'cycle mismatch',n,d,ch,cv);count+=1
        parity[name]={'cases':count,'cycle_vector_equal_to_v2':True}

    # Wider modulo aliases must inherit the same V2 cycle vector and semantics.
    for name,divname,nb,db in [('MATH_UMOD16','MATH_UDIV16',16,16),('MATH_UMOD24','MATH_UDIV24',24,24),('MATH_UMOD32_16','MATH_UDIV32_16',32,16)]:
        count=1000
        for _ in range(count):
            n=rng.randrange(1<<nb);d=rng.randrange(1<<db)
            ch=call_div(h,PH,IH,name,nb,db,n,d);cv=call_div(v2,P2,I2,name,nb,db,n,d)
            assert ch==cv,(name,'cycle mismatch',n,d,ch,cv)
        parity[name]={'cases':count,'cycle_vector_equal_to_v2':True}

    # Exhaustive UMOD8 domain (65,536 numerator/divisor pairs), with V2 parity.
    N=IH+0x10;D=IH+0x14;R=IH+0x1c;N2=I2+0x10;D2=I2+0x14;R2=I2+0x1c
    umod8_cases=0
    for n in range(256):
        for d in range(256):
            h.mem[N]=n;h.mem[D]=d;ch=h.call(PH['MATH_UMOD8'],10000);rh=h.mem[R]
            if ((n<<8)|d) % 16 == 0:
                v2.mem[N2]=n;v2.mem[D2]=d;cv=v2.call(P2['MATH_UMOD8'],10000);rv=v2.mem[R2]
                assert ch==cv and rh==rv and h.c==v2.c,(n,d,ch,cv,rh,rv,h.c,v2.c)
            assert (h.c==1 and rh==0) if d==0 else (h.c==0 and rh==n%d)
            umod8_cases+=1
    parity['MATH_UMOD8']={'cases':umod8_cases,'cycle_vector_equal_to_v2_sampled':True,'exhaustive_correctness':True}

    # Full phase domain for COS/SINCOS, exact result and V2 cycle parity.
    X=IH;Z=IH+8;X2=I2;Z2=I2+8
    for phase in range(256):
        h.mem[X]=phase;ch=h.call(PH['MATH_COS8'],10000);gh=h.mem[Z]
        v2.mem[X2]=phase;cv=v2.call(P2['MATH_COS8'],10000);gv=v2.mem[Z2]
        exp=round(127*math.cos(2*math.pi*phase/256))&255
        assert ch==cv and gh==gv==exp and h.c==v2.c==0
        h.mem[X]=phase;ch=h.call(PH['MATH_SINCOS8'],10000);gh=(h.mem[Z],h.mem[Z+1])
        v2.mem[X2]=phase;cv=v2.call(P2['MATH_SINCOS8'],10000);gv=(v2.mem[Z2],v2.mem[Z2+1])
        exp2=(round(127*math.sin(2*math.pi*phase/256))&255,exp)
        assert ch==cv and gh==gv==exp2 and h.c==v2.c==0
    parity['MATH_COS8']={'cases':256,'cycle_vector_equal_to_v2':True,'exhaustive':True}
    parity['MATH_SINCOS8']={'cases':256,'cycle_vector_equal_to_v2':True,'exhaustive':True}

    # Exhaustive signed-byte ATAN2: exact cycle-vector parity with the V2 fast
    # donor and <=1 phase-unit error over all 65,536 vectors.
    atan_cases=0; atan_total=0; atan_min=10**9; atan_max=0; atan_maxerr=0
    for rx in range(256):
        sx=rx if rx<128 else rx-256
        for ry in range(256):
            sy=ry if ry<128 else ry-256
            h.mem[IH]=rx; h.mem[IH+4]=ry; ch=h.call(PH['MATH_ATAN2_8'],10000); gh=h.mem[IH+8]
            v2.mem[I2]=rx; v2.mem[I2+4]=ry; cv=v2.call(P2['MATH_ATAN2_8'],10000); gv=v2.mem[I2+8]
            exp=0 if sx==0 and sy==0 else round((math.atan2(sy,sx)%(2*math.pi))*128/math.pi)&255
            er=min((gh-exp)&255,(exp-gh)&255)
            assert (ch,gh,h.c)==(cv,gv,v2.c),(rx,ry,ch,cv,gh,gv,h.c,v2.c)
            assert er<=1,(rx,ry,gh,exp,er)
            atan_cases+=1; atan_total+=ch; atan_min=min(atan_min,ch); atan_max=max(atan_max,ch); atan_maxerr=max(atan_maxerr,er)
    parity['MATH_ATAN2_8']={'cases':atan_cases,'cycle_vector_equal_to_v2':True,'exhaustive':True,
        'mean_cycles':atan_total/atan_cases,'min_cycles':atan_min,'max_cycles':atan_max,'max_phase_error':atan_maxerr}
    out['tests']['direct_v2_parity']=parity

    # Dynamic ZP confinement on both source maps. Fill every byte outside the
    # configured 31-byte window with a deterministic sentinel and verify that
    # repeated imported calls never modify any outside byte (including $00/$01).
    zp_results={}
    for kind in ('reference','alternate'):
        c,P,I,M,_=load_hybrid(kind)
        z0=int(M['normal_zp'].split('-')[0][1:],16);z1=int(M['normal_zp'].split('-')[1][1:],16)
        outside=[i for i in range(256) if not (z0<=i<=z1)]
        # Do not alter $00/$01 semantics after setting the sentinel; imported kernels must not touch them.
        for i in outside:c.mem[i]=(i*73+19)&255
        snap=bytes(c.mem[i] for i in outside)
        rr=random.Random(0x515A0000 + (0 if kind=='reference' else 1))
        for _ in range(1000):
            n=rr.randrange(1<<32);d=rr.randrange(1<<16)
            call_div(c,P,I,'MATH_UDIV32_16',32,16,n,d)
            c.mem[I]=rr.randrange(256);c.call(P['MATH_COS8'],10000)
            c.mem[I+0x10]=rr.randrange(256);c.mem[I+0x14]=rr.randrange(256);c.call(P['MATH_UMOD8'],10000)
        after=bytes(c.mem[i] for i in outside)
        assert after==snap,(kind,'outside-ZP corruption')
        zp_results[kind]={'window':M['normal_zp'],'bytes':31,'outside_bytes_unchanged':len(outside),'stress_iterations':1000}
    out['tests']['zp_confinement']=zp_results

    # V5 deliberately preserves V1's optional-init contract for ordinary/safe
    # entries.  Exercise imported and untouched paths from a cold PRG load,
    # with no MATH_INIT call in either reference or alternate map.
    noinit={}
    for kind in ('reference','alternate'):
        c,P,I,M=load_hybrid_no_init(kind)
        rr=random.Random(0x10A17 + (0 if kind=='reference' else 1))
        cases=0
        for i in range(1000):
            mode=i%7
            if mode==0:
                n=rr.randrange(1<<16); d=rr.randrange(1<<16); call_div(c,P,I,'MATH_UDIV16',16,16,n,d)
            elif mode==1:
                n=rr.randrange(1<<24); d=rr.randrange(1<<24); call_div(c,P,I,'MATH_UDIV24',24,24,n,d)
            elif mode==2:
                n=rr.randrange(1<<32); d=rr.randrange(1<<16); call_div(c,P,I,'MATH_UDIV32_16',32,16,n,d)
            elif mode==3:
                n=rr.randrange(256); d=rr.randrange(256); wr(c,I+0x10,n,1); wr(c,I+0x14,d,1); c.call(P['MATH_UMOD8'],10000)
                assert (c.c==1 and c.mem[I+0x1c]==0) if d==0 else (c.c==0 and c.mem[I+0x1c]==n%d)
            elif mode==4:
                ph=rr.randrange(256); c.mem[I]=ph; c.call(P['MATH_COS8'],10000)
                assert c.mem[I+8]==(round(127*math.cos(2*math.pi*ph/256))&255) and c.c==0
            elif mode==5:
                rx=rr.randrange(256); ry=rr.randrange(256); sx=rx if rx<128 else rx-256; sy=ry if ry<128 else ry-256
                c.mem[I]=rx; c.mem[I+4]=ry; c.call(P['MATH_ATAN2_8'],10000); got=c.mem[I+8]
                exp=0 if sx==0 and sy==0 else round((math.atan2(sy,sx)%(2*math.pi))*128/math.pi)&255
                assert min((got-exp)&255,(exp-got)&255)<=1 and c.c==0
            else:
                # Untouched V1 safe path also remains cold-load callable.
                x=rr.randrange(1<<16); y=rr.randrange(1<<16); wr(c,I,x,2); wr(c,I+4,y,2); c.call(P['MATH_UMUL16'],100000)
                assert rd(c,I+8,4)==x*y and c.c==0
            cases+=1
        noinit[kind]={'status':'PASS','cold_load_without_math_init':True,'cases':cases}
    out['tests']['optional_init_cold_load']=noinit

    # Mixed workload: imported and untouched V1 routines interleaved, looking for
    # stale/self-modifying state interactions that isolated tests can miss.
    c,P,I,M,_=load_hybrid('reference'); X=I;Y=I+4;Z=I+8;N=I+0x10;D=I+0x14;Q=I+0x18;R=I+0x1c
    rr=random.Random(0xD3A05)  # fixed seed
    for i in range(a.mixed):
        mode=i%6
        if mode==0:
            x=rr.randrange(1<<16);y=rr.randrange(1<<16);wr(c,X,x,2);wr(c,Y,y,2);c.call(P['MATH_UMUL16'],100000);assert rd(c,Z,4)==x*y
        elif mode==1:
            n=rr.randrange(1<<16);d=rr.randrange(1<<16);call_div(c,P,I,'MATH_UDIV16',16,16,n,d)
        elif mode==2:
            n=rr.randrange(1<<24);d=rr.randrange(1<<24);call_div(c,P,I,'MATH_UDIV24',24,24,n,d)
        elif mode==3:
            n=rr.randrange(1<<32);d=rr.randrange(1<<16);call_div(c,P,I,'MATH_UDIV32_16',32,16,n,d)
        elif mode==4:
            n=rr.randrange(1<<32);wr(c,N,n,4);c.call(P['MATH_ISQRT32'],100000);assert rd(c,Z,2)==math.isqrt(n)
        else:
            ph=rr.randrange(256);c.mem[X]=ph;c.call(P['MATH_SINCOS8'],10000);assert c.mem[Z]==(round(127*math.sin(2*math.pi*ph/256))&255)
    out['tests']['mixed_state_stress']={'iterations':a.mixed,'status':'PASS'}

    out['elapsed_seconds']=round(time.time()-t0,3)
    path=ROOT/'validation/hybrid/HYBRID_VALIDATION.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n')
    print('HYBRID PASS',json.dumps({'elapsed_seconds':out['elapsed_seconds'],'random_per_family':a.random_per_family,'mixed':a.mixed,'umod8':umod8_cases}))

if __name__=='__main__': main()
