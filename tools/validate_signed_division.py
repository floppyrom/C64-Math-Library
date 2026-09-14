#!/usr/bin/env python3
from pathlib import Path
import argparse, json, random, re, sys, time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from mini6502 import CPU

PROFILES = ['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
REU = {
    'v3_reu_512k': ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu',
    'v4_reu_16m': ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu',
}

def mask(bits): return (1 << bits) - 1

def sgn(v,bits):
    return v - (1 << bits) if v & (1 << (bits-1)) else v

def wr(mem,a,v,n):
    for i in range(n): mem[a+i] = (v >> (8*i)) & 0xff

def rd(mem,a,n):
    return sum(mem[a+i] << (8*i) for i in range(n))

def parse_api(profile):
    out={}
    for line in (ROOT/profile/'resident/math_api.inc').read_text().splitlines():
        m=re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
        if m: out[m.group(1)] = int(m.group(2),16)
    return out

def load_profile(profile):
    prg=ROOT/profile/'resident'/f'math_{profile}_game_math.prg'
    b=prg.read_bytes(); load=b[0]|b[1]<<8
    mem=bytearray(65536); mem[load:load+len(b)-2]=b[2:]
    reu=bytearray(REU[profile].read_bytes()) if profile in REU else None
    cpu=CPU(mem,reu=reu); cpu.d=0; cpu.call(0x3280,2_000_000)
    return cpu,parse_api(profile)

def div_expected(nraw,nbits,draw,dbits,qbits,rbits,shift=0):
    n=sgn(nraw,nbits) << shift
    d=sgn(draw,dbits)
    if d == 0:
        return 0,0,1
    q=abs(n)//abs(d)
    if (n<0) ^ (d<0): q=-q
    r=n-q*d
    return q & mask(qbits), r & mask(rbits), 0

def edge(bits):
    s=1<<(bits-1);m=mask(bits)
    return list(dict.fromkeys(x&m for x in [0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))

def run_cases(cpu,entry,cases,nbits,dbits,qbits,rbits,shift=0):
    N,D,Q,R=0xc010,0xc014,0xc018,0xc01c
    nn=(nbits+7)//8;dn=(dbits+7)//8;qn=(qbits+7)//8;rn=(rbits+7)//8
    errors=0;total=0;mi=None;ma=None
    for nr,dr in cases:
        wr(cpu.mem,N,nr,nn);wr(cpu.mem,D,dr,dn)
        bn=bytes(cpu.mem[N:N+nn]);bd=bytes(cpu.mem[D:D+dn])
        cy=cpu.call(entry,4_000_000)
        eq,er,ec=div_expected(nr,nbits,dr,dbits,qbits,rbits,shift)
        gq=rd(cpu.mem,Q,qn);gr=rd(cpu.mem,R,rn)
        if (gq,gr,cpu.c)!=(eq,er,ec) or bytes(cpu.mem[N:N+nn])!=bn or bytes(cpu.mem[D:D+dn])!=bd:
            errors+=1
            if errors<=4:
                print('ERROR',hex(entry),nbits,dbits,hex(nr),hex(dr),'got',hex(gq),hex(gr),cpu.c,'exp',hex(eq),hex(er),ec)
        total+=cy;mi=cy if mi is None else min(mi,cy);ma=cy if ma is None else max(ma,cy)
    return {'cases':len(cases),'errors':errors,'mean_cycles':total/len(cases),'min_cycles':mi,'max_cycles':ma}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--profile',choices=PROFILES);a=ap.parse_args()
    run=[a.profile] if a.profile else PROFILES
    result={};start=time.time()
    defs=[
      ('MATH_SDIV8',8,8,8,8,0),('MATH_SDIV16',16,16,16,16,0),
      ('MATH_SDIV24',24,24,24,24,0),('MATH_SDIV32_16',32,16,32,16,0),
      ('MATH_SDIV32_32',32,32,32,32,0),('MATH_SDIV16_SHL8',16,16,24,16,8),
    ]
    aliases=[('MATH_SMOD8','MATH_SDIV8',8,8,8,8,0),('MATH_SMOD16','MATH_SDIV16',16,16,16,16,0),
             ('MATH_SMOD24','MATH_SDIV24',24,24,24,24,0),('MATH_SMOD32_16','MATH_SDIV32_16',32,16,32,16,0),
             ('MATH_SMOD32_32','MATH_SDIV32_32',32,32,32,32,0)]
    for p in run:
        pi=PROFILES.index(p)
        cpu,api=load_profile(p);pr={}
        for name,nb,db,qb,rb,sh in defs:
            if name=='MATH_SDIV8' and p in ('v1_balanced','v2_pareto_fast','v3_reu_512k'):
                cases=[(n,d) for n in range(256) for d in range(256)]
                mode='exhaustive'
            else:
                en=edge(nb);ed=edge(db);cases=[(n,d) for n in en for d in ed]
                rng=random.Random(0xD1000000+pi*0x10000+nb*0x100+db+sh)
                count=4096 if name!='MATH_SDIV32_32' else 6144
                cases += [(rng.randrange(1<<nb),rng.randrange(1<<db)) for _ in range(count)]
                # Guarantee a useful zero-divisor slice.
                cases += [(rng.randrange(1<<nb),0) for _ in range(128)]
                mode='structured_random'
            r=run_cases(cpu,api[name],cases,nb,db,qb,rb,sh);r['mode']=mode;pr[name]=r
        # Alias regressions: smaller deterministic corpus, same quotient/remainder semantics.
        for ai,(name,base,nb,db,qb,rb,sh) in enumerate(aliases):
            rng=random.Random(0xA1100000+pi*0x1000+ai)
            cases=[(n,d) for n in edge(nb) for d in edge(db)]
            cases += [(rng.randrange(1<<nb),rng.randrange(1<<db)) for _ in range(1024)]
            pr[name]=run_cases(cpu,api[name],cases,nb,db,qb,rb,sh)
        if any(x['errors'] for x in pr.values()): raise AssertionError((p,pr))
        result[p]=pr;print(p,'PASS',sum(x['cases'] for x in pr.values()),'signed division/modulo calls',flush=True)
    out={'status':'PASS','profiles':result,'summary':{'profiles':len(run),'machine_calls':sum(x['cases'] for p in result.values() for x in p.values()),'elapsed_seconds':round(time.time()-start,2)}}
    path=ROOT/'validation/review/SIGNED_DIVISION_VALIDATION.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n')
    print('SIGNED DIVISION PASS',out['summary']['machine_calls'],'calls')
if __name__=='__main__': main()
