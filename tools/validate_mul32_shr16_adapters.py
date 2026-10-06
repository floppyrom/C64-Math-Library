#!/usr/bin/env python3
"""Validate all-profile 32-bit SHR16 fixed-point adapters and exact cycle deltas."""
from pathlib import Path
import json, random, re, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
KINDS=('reference','alternate')
BUILD=ROOT/'build_source'
HYBRID=ROOT/'build_hybrid'
SEED=0x32160032
DELTA=63
MASK32=(1<<32)-1
MASK64=(1<<64)-1
MASK48=(1<<48)-1

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

def wr32(mem,a,v):
    for i in range(4): mem[a+i]=(v>>(8*i))&255
def rd(mem,a,n):
    return sum(mem[a+i]<<(8*i) for i in range(n))
def s32(v):
    return v-(1<<32) if v&0x80000000 else v

def corpus():
    e=(0,1,2,3,0x7f,0x80,0xff,0x100,0xffff,0x10000,0x7fffffff,0x80000000,0x80000001,0xfffffffe,0xffffffff)
    out=[(x,y) for x in e for y in e]
    rng=random.Random(SEED)
    out.extend((rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(4096))
    return out

def stats(v): return {'mean_cycles':sum(v)/len(v),'min_cycles':min(v),'max_cycles':max(v)}

def run(profile,kind,cases):
    cpu,api=load(profile,kind);X=api['MATH_X'];Y=api['MATH_Y'];Z=api['MATH_Z']
    ub=[];us=[];sb=[];ss=[];errors=0
    for x,y in cases:
        wr32(cpu.mem,X,x);wr32(cpu.mem,Y,y); bx=bytes(cpu.mem[X:X+4]);by=bytes(cpu.mem[Y:Y+4])
        c0=cpu.call(api['MATH_UMUL32'],100_000); exp=(x*y)&MASK64
        if rd(cpu.mem,Z,8)!=exp or cpu.c!=0 or bytes(cpu.mem[X:X+4])!=bx or bytes(cpu.mem[Y:Y+4])!=by:
            errors+=1
            if errors<=6: print('UMUL32 ERROR',profile,kind,hex(x),hex(y))
        wr32(cpu.mem,X,x);wr32(cpu.mem,Y,y)
        c1=cpu.call(api['MATH_UMUL32_SHR16'],100_000); q=(x*y>>16)&MASK48
        if rd(cpu.mem,Z,6)!=q or cpu.c!=0 or c1!=c0+DELTA:
            errors+=1
            if errors<=6: print('UMUL32_SHR16 ERROR',profile,kind,hex(x),hex(y),c0,c1,hex(rd(cpu.mem,Z,6)),hex(q),cpu.c)
        ub.append(c0);us.append(c1)

        sx=s32(x);sy=s32(y)
        wr32(cpu.mem,X,x);wr32(cpu.mem,Y,y); bx=bytes(cpu.mem[X:X+4]);by=bytes(cpu.mem[Y:Y+4])
        c2=cpu.call(api['MATH_SMUL32'],100_000); sexp=(sx*sy)&MASK64
        if rd(cpu.mem,Z,8)!=sexp or cpu.c!=0 or bytes(cpu.mem[X:X+4])!=bx or bytes(cpu.mem[Y:Y+4])!=by:
            errors+=1
            if errors<=6: print('SMUL32 ERROR',profile,kind,hex(x),hex(y))
        wr32(cpu.mem,X,x);wr32(cpu.mem,Y,y)
        c3=cpu.call(api['MATH_SMUL32_SHR16'],100_000); sq=((sx*sy)>>16)&MASK48
        if rd(cpu.mem,Z,6)!=sq or cpu.c!=0 or c3!=c2+DELTA:
            errors+=1
            if errors<=6: print('SMUL32_SHR16 ERROR',profile,kind,hex(x),hex(y),c2,c3,hex(rd(cpu.mem,Z,6)),hex(sq),cpu.c)
        sb.append(c2);ss.append(c3)
    if errors: raise AssertionError(f'{profile} {kind}: {errors} errors')
    return {'cases':len(cases),'umul32':stats(ub),'umul32_shr16':stats(us),'smul32':stats(sb),'smul32_shr16':stats(ss),
            '_ub':ub,'_us':us,'_sb':sb,'_ss':ss}

def main():
    cases=corpus();res={}
    for p in PROFILES:
        res[p]={}
        for k in KINDS:
            r=run(p,k,cases);res[p][k]=r
            print(f"{p} {k} PASS {r['cases']} U={r['umul32']['mean_cycles']:.6f} U>>16={r['umul32_shr16']['mean_cycles']:.6f} "
                  f"S={r['smul32']['mean_cycles']:.6f} S>>16={r['smul32_shr16']['mean_cycles']:.6f}")
        for key in ('_ub','_us','_sb','_ss'):
            if res[p]['reference'][key]!=res[p]['alternate'][key]:
                raise AssertionError(f'{p}: reference/alternate {key} differs')
    # V5 inherits V1 unsigned implementation; signed family is also inherited.
    for key in ('_ub','_us','_sb','_ss'):
        if res['v1_balanced']['reference'][key]!=res['v5_hybrid_lowzp']['reference'][key]:
            raise AssertionError(f'V1/V5 family differs: {key}')
    clean={}
    for p in PROFILES:
        clean[p]={}
        for k in KINDS:
            r=res[p][k]
            clean[p][k]={'cases':r['cases'],'umul32':r['umul32'],'umul32_shr16':r['umul32_shr16'],
                         'smul32':r['smul32'],'smul32_shr16':r['smul32_shr16']}
    out=ROOT/'validation/multiply_refresh/MUL32_SHR16_ADAPTER_VALIDATION.json'
    out.write_text(json.dumps({
      'status':'PASS','seed':hex(SEED),'delta_cycles':DELTA,
      'basis':'2026-10-06 all-profile 32-bit fixed-point adapter corpus; both unsigned and signed SHR16 must equal base +63 cycles exactly; public entry cycles include RTS and exclude caller JSR/input stores',
      'results':clean},indent=2)+'\n')
    print('MUL32 SHR16 ADAPTER PASS')

if __name__=='__main__': main()
