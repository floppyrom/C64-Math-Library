#!/usr/bin/env python3
"""Validate and benchmark candidate wide-intermediate MULDIV16 primitives.

Candidate ABI (not yet part of PUBLIC_API_COMPLETE.csv):
  REG_GAME_API+$54  unsigned: (X16*Y16)/D16 -> Q32,R16
  REG_GAME_API+$57  signed:   (X16*Y16)/D16 -> Q32,R16, trunc toward zero

X/Y/D are preserved. N is implementation scratch. Divide-by-zero returns C=1
and zero Q/R, matching the selected public division engines.
"""
from __future__ import annotations
from pathlib import Path
import json, random, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
BUILD=ROOT/'build_muldiv16'
HYBRID=ROOT/'build_hybrid'

def unhx(v):
    return int(v[1:],16) if isinstance(v,str) and v.startswith('$') else int(v)

def wr(mem,a,v,n):
    for i in range(n): mem[a+i]=(v>>(8*i))&255

def rd(mem,a,n):
    return sum(mem[a+i]<<(8*i) for i in range(n))

def s16(v):
    v&=0xffff
    return v-0x10000 if v&0x8000 else v

def truncdiv(n,d):
    q=abs(n)//abs(d)
    if (n<0)^(d<0): q=-q
    return q,n-q*d

def load(profile,kind):
    d=(HYBRID if profile=='v5_hybrid_lowzp' else BUILD)/kind/profile
    man=json.loads((d/'source_build_manifest.json').read_text())
    p=d/man['output_prg']
    b=p.read_bytes(); lo=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[lo:lo+len(b)-2]=b[2:]
    reu=None
    ri=man.get('reu_image')
    if ri:
        rp=d/ri.get('file',Path(ri.get('path','')).name)
        if not rp.exists() and ri.get('path'): rp=d/Path(ri['path']).name
        if rp.exists(): reu=bytearray(rp.read_bytes())
    cpu=CPU(mem,reu=reu); cpu.d=0
    init=unhx(man['math_init']); cpu.call(init,2_000_000)
    api={k:unhx(v) for k,v in man['public_entries'].items()}
    io=unhx(man['public_io'].split('-')[0])
    # Candidate slots immediately follow the last stable seek entry.
    u=api['MATH_SEEK16_STEP1']+3
    s=u+3
    return cpu,api,io,u,s

def edge16_signed_bits():
    vals=[0,1,2,3,7,15,16,31,127,128,255,256,257,0x7fff,0x8000,0x8001,0xff00,0xfffe,0xffff]
    return list(dict.fromkeys(x&0xffff for x in vals))

def vectors():
    e=edge16_signed_bits()
    unsigned=[]
    for x in e:
        for y in e:
            for d in (0,1,2,3,7,255,256,257,0x7fff,0x8000,0xffff):
                unsigned.append((x,y,d))
    signed=list(unsigned)
    r=random.Random(0x4D554C44)
    unsigned += [(r.randrange(1<<16),r.randrange(1<<16),r.randrange(1<<16)) for _ in range(5000)]
    signed += [(r.randrange(1<<16),r.randrange(1<<16),r.randrange(1<<16)) for _ in range(5000)]
    # Quotient/remainder boundaries and exact-divisibility cases.
    for d in (1,2,3,5,7,15,31,127,255,256,257,1023,32767,32768,65535):
        for x,y in ((0xffff,0xffff),(0x8000,0x8000),(0x7fff,0x7fff),(d,1),(d,2),(d,0xffff)):
            unsigned.append((x&0xffff,y&0xffff,d))
            signed.append((x&0xffff,y&0xffff,d))
    return list(dict.fromkeys(unsigned)),list(dict.fromkeys(signed))

def call_unsigned(cpu,entry,io,x,y,d):
    X,Y,N,D,Q,R=io,io+4,io+0x10,io+0x14,io+0x18,io+0x1c
    wr(cpu.mem,X,x,2); wr(cpu.mem,Y,y,2); wr(cpu.mem,D,d,2)
    bx=bytes(cpu.mem[X:X+2]); by=bytes(cpu.mem[Y:Y+2]); bd=bytes(cpu.mem[D:D+2])
    cy=cpu.call(entry,4_000_000)
    q=rd(cpu.mem,Q,4); r=rd(cpu.mem,R,2)
    if d==0: exp=(0,0,1)
    else:
        product=x*y
        eq,er=divmod(product,d)
        exp=(eq&0xffffffff,er&0xffff,0)
    got=(q,r,cpu.c)
    ok=(got==exp and bytes(cpu.mem[X:X+2])==bx and bytes(cpu.mem[Y:Y+2])==by and bytes(cpu.mem[D:D+2])==bd)
    return cy,ok,got,exp

def call_signed(cpu,entry,io,xb,yb,db):
    X,Y,D,Q,R=io,io+4,io+0x14,io+0x18,io+0x1c
    wr(cpu.mem,X,xb,2); wr(cpu.mem,Y,yb,2); wr(cpu.mem,D,db,2)
    bx=bytes(cpu.mem[X:X+2]); by=bytes(cpu.mem[Y:Y+2]); bd=bytes(cpu.mem[D:D+2])
    cy=cpu.call(entry,4_000_000)
    q=rd(cpu.mem,Q,4); r=rd(cpu.mem,R,2)
    x,y,d=s16(xb),s16(yb),s16(db)
    if d==0: exp=(0,0,1)
    else:
        eq,er=truncdiv(x*y,d)
        exp=(eq&0xffffffff,er&0xffff,0)
    got=(q,r,cpu.c)
    ok=(got==exp and bytes(cpu.mem[X:X+2])==bx and bytes(cpu.mem[Y:Y+2])==by and bytes(cpu.mem[D:D+2])==bd)
    return cy,ok,got,exp

def stats(v):
    return {'cases':len(v),'mean_cycles':sum(v)/len(v),'min_cycles':min(v),'max_cycles':max(v)}

def run():
    uv,sv=vectors()
    out={'status':'PASS','candidate':{'unsigned_address_offset':'REG_GAME_API+$0054','signed_address_offset':'REG_GAME_API+$0057'},'profiles':{}}
    for p in PROFILES:
        per={}
        ref_vectors={}
        for kind in ('reference','alternate'):
            cpu,api,io,uent,sent=load(p,kind)
            # Stubs must be JMPs and the signed helper must sit below the seek island.
            assert cpu.mem[uent]==0x4c,(p,kind,'unsigned candidate stub',hex(uent),hex(cpu.mem[uent]))
            assert cpu.mem[sent]==0x4c,(p,kind,'signed candidate stub',hex(sent),hex(cpu.mem[sent]))
            uc=[];sc=[];errs=[]
            for x,y,d in uv:
                cy,ok,got,exp=call_unsigned(cpu,uent,io,x,y,d)
                if not ok:
                    errs.append({'kind':'unsigned','x':hex(x),'y':hex(y),'d':hex(d),'got':got,'exp':exp})
                    if len(errs)>=8: break
                uc.append(cy)
            if not errs:
                for x,y,d in sv:
                    cy,ok,got,exp=call_signed(cpu,sent,io,x,y,d)
                    if not ok:
                        errs.append({'kind':'signed','x':hex(x),'y':hex(y),'d':hex(d),'got':got,'exp':exp})
                        if len(errs)>=8: break
                    sc.append(cy)
            if errs: raise AssertionError((p,kind,errs))
            per[kind]={'unsigned':stats(uc),'signed':stats(sc)}
            if kind=='reference': ref_vectors={'unsigned':uc,'signed':sc}
            else:
                assert uc==ref_vectors['unsigned'],(p,'unsigned relocation cycle mismatch')
                assert sc==ref_vectors['signed'],(p,'signed relocation cycle mismatch')
                per[kind]['cycle_vector_equal_to_reference']=True
        out['profiles'][p]=per
        print(p,json.dumps(per,sort_keys=True),flush=True)
    path=ROOT/'validation/research/MULDIV16_CANDIDATE.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+'\n')
    print('MULDIV16 CANDIDATE PASS',len(uv),'unsigned',len(sv),'signed cases per profile/map')

if __name__=='__main__':
    run()
