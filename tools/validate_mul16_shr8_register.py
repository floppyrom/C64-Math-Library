#!/usr/bin/env python3
"""Validate all-profile 16-bit fixed-point multiply register-return adapters."""
from pathlib import Path
import json, random, re, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
KINDS=('reference','alternate')
BUILD=ROOT/'build_source'
HYBRID=ROOT/'build_hybrid'
SEED=0x16F80016
UDELTA={'v1_balanced':31,'v2_pareto_fast':27,'v3_reu_512k':27,'v4_reu_16m':27,'v5_hybrid_lowzp':31}
SDELTA={p:31 for p in PROFILES}

def parse_inc(path):
    out={}
    for line in path.read_text().splitlines():
        m=re.match(r'\s*([A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
        if m: out[m.group(1)]=int(m.group(2),16)
    return out

def load(profile,kind):
    d=(HYBRID if profile=='v5_hybrid_lowzp' else BUILD)/kind/profile
    man=json.loads((d/'source_build_manifest.json').read_text())
    prg=(d/man['output_prg']).read_bytes()
    lo=prg[0]|(prg[1]<<8)
    mem=bytearray(65536);mem[lo:lo+len(prg)-2]=prg[2:]
    reu=bytearray((d/man['reu_image']['file']).read_bytes()) if man.get('reu_image') else None
    api=parse_inc(d/'math_api.inc')
    cpu=CPU(mem,reu=reu);cpu.d=0;cpu.call(api['MATH_INIT'],2_000_000)
    return cpu,api

def s16(v): return v-0x10000 if v&0x8000 else v

def corpus():
    edges=(0,1,2,3,0x7f,0x80,0xff,0x100,0x101,0x7fff,0x8000,0x8001,0xfffe,0xffff)
    out=[(x,y) for x in edges for y in edges]
    rng=random.Random(SEED)
    out.extend((rng.randrange(65536),rng.randrange(65536)) for _ in range(10_000))
    return out

def wr16(mem,a,v):
    mem[a]=v&255;mem[a+1]=(v>>8)&255
def rd(mem,a,n):
    return sum(mem[a+i]<<(8*i) for i in range(n))

def run(profile,kind,cases):
    cpu,api=load(profile,kind);X=api['MATH_X'];Y=api['MATH_Y'];Z=api['MATH_Z']
    uv=[];us=[];sv=[];ss=[];errors=0
    for x,y in cases:
        wr16(cpu.mem,X,x);wr16(cpu.mem,Y,y)
        bx=bytes(cpu.mem[X:X+2]);by=bytes(cpu.mem[Y:Y+2])
        cy=cpu.call(api['MATH_UMUL16'],20_000)
        exp=(x*y)&0xffffffff
        if rd(cpu.mem,Z,4)!=exp or cpu.c!=0 or bytes(cpu.mem[X:X+2])!=bx or bytes(cpu.mem[Y:Y+2])!=by:
            errors+=1
            if errors<=8: print('UMUL16 ERROR',profile,kind,hex(x),hex(y),hex(rd(cpu.mem,Z,4)),hex(exp),cpu.c)
        wr16(cpu.mem,X,x);wr16(cpu.mem,Y,y)
        scy=cpu.call(api['MATH_UMUL16_SHR8'],20_000)
        sexp=((x*y)>>8)&0xffffff
        if rd(cpu.mem,Z,3)!=sexp or cpu.c!=0 or scy!=cy+UDELTA[profile]:
            errors+=1
            if errors<=8: print('UMUL16_SHR8 ERROR',profile,kind,hex(x),hex(y),scy,cy,hex(rd(cpu.mem,Z,3)),hex(sexp))
        uv.append(cy);us.append(scy)

        wr16(cpu.mem,X,x);wr16(cpu.mem,Y,y)
        bx=bytes(cpu.mem[X:X+2]);by=bytes(cpu.mem[Y:Y+2])
        sc=cpu.call(api['MATH_SMUL16'],20_000)
        prod=s16(x)*s16(y); pexp=prod&0xffffffff
        if rd(cpu.mem,Z,4)!=pexp or cpu.c!=0 or bytes(cpu.mem[X:X+2])!=bx or bytes(cpu.mem[Y:Y+2])!=by:
            errors+=1
            if errors<=8: print('SMUL16 ERROR',profile,kind,hex(x),hex(y),hex(rd(cpu.mem,Z,4)),hex(pexp),cpu.c)
        wr16(cpu.mem,X,x);wr16(cpu.mem,Y,y)
        ssc=cpu.call(api['MATH_SMUL16_SHR8'],20_000)
        qexp=(prod>>8)&0xffffff
        if rd(cpu.mem,Z,3)!=qexp or cpu.c!=0 or ssc!=sc+SDELTA[profile]:
            errors+=1
            if errors<=8: print('SMUL16_SHR8 ERROR',profile,kind,hex(x),hex(y),ssc,sc,hex(rd(cpu.mem,Z,3)),hex(qexp))
        sv.append(sc);ss.append(ssc)
    if errors: raise AssertionError(f'{profile} {kind}: {errors} errors')
    def stats(v): return {'mean_cycles':sum(v)/len(v),'min_cycles':min(v),'max_cycles':max(v)}
    return {'cases':len(cases),'umul16':stats(uv),'umul16_shr8':stats(us),
            'smul16':stats(sv),'smul16_shr8':stats(ss),
            '_uv':uv,'_us':us,'_sv':sv,'_ss':ss}

def main():
    cases=corpus();res={}
    for p in PROFILES:
        res[p]={}
        for k in KINDS:
            r=run(p,k,cases);res[p][k]=r
            print(f"{p} {k} PASS {r['cases']} U={r['umul16']['mean_cycles']:.6f} "
                  f"U>>8={r['umul16_shr8']['mean_cycles']:.6f} "
                  f"S={r['smul16']['mean_cycles']:.6f} S>>8={r['smul16_shr8']['mean_cycles']:.6f}")
        for key in ('_uv','_us','_sv','_ss'):
            if res[p]['reference'][key]!=res[p]['alternate'][key]:
                raise AssertionError(f'{p}: reference/alternate {key} cycle vectors differ')
    for key in ('_uv','_us'):
        if res['v1_balanced']['reference'][key]!=res['v5_hybrid_lowzp']['reference'][key]:
            raise AssertionError(f'V1/V5 unsigned family differs: {key}')
        base=res['v2_pareto_fast']['reference'][key]
        for p in ('v3_reu_512k','v4_reu_16m'):
            if res[p]['reference'][key]!=base: raise AssertionError(f'V2-V4 unsigned family differs: {p} {key}')
    # Signed base corpora can differ across profile implementations, but the adapter
    # deltas above are required exactly per case in every profile.
    clean={}
    for p in PROFILES:
        clean[p]={}
        for k in KINDS:
            r=res[p][k]
            clean[p][k]={'cases':r['cases'],'umul16':r['umul16'],'umul16_shr8':r['umul16_shr8'],
                         'smul16':r['smul16'],'smul16_shr8':r['smul16_shr8']}
    out=ROOT/'validation/multiply_refresh/MUL16_SHR8_REGISTER_VALIDATION.json'
    out.write_text(json.dumps({
      'status':'PASS','seed':hex(SEED),
      'basis':'2026-10-06 all-profile 16-bit fixed-point register-return corpus; unsigned deltas +31 V1/V5 and +27 V2-V4; signed delta +31 all profiles; public entry cycles include RTS and exclude caller JSR/input stores',
      'results':clean},indent=2)+'\n')
    print('MUL16 SHR8 REGISTER-RETURN PASS')

if __name__=='__main__': main()
