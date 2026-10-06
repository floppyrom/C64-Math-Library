#!/usr/bin/env python3
"""Validate the optimized V2/V3/V4 public UMUL16 producer and SHR8 composition."""
from pathlib import Path
import json, random, re, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')
KINDS=('reference','alternate')
BUILD=ROOT/'build_source'
SEED=0x16160016

def parse_inc(path):
    out={}
    for line in path.read_text().splitlines():
        m=re.match(r'\s*([A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
        if m: out[m.group(1)]=int(m.group(2),16)
    return out

def load(profile,kind):
    d=BUILD/kind/profile
    man=json.loads((d/'source_build_manifest.json').read_text())
    prg=(d/man['output_prg']).read_bytes()
    lo=prg[0]|(prg[1]<<8)
    mem=bytearray(65536)
    mem[lo:lo+len(prg)-2]=prg[2:]
    reu=None
    if man.get('reu_image'):
        reu=bytearray((d/man['reu_image']['file']).read_bytes())
    api=parse_inc(d/'math_api.inc')
    cpu=CPU(mem,reu=reu)
    cpu.d=0
    cpu.call(api['MATH_INIT'],2_000_000)
    return cpu,api

def corpus():
    edges=(0,1,2,3,0x7f,0x80,0xff,0x100,0x101,0x7fff,0x8000,0xfffe,0xffff)
    out=[(x,y) for x in edges for y in edges]
    rng=random.Random(SEED)
    out.extend((rng.randrange(65536),rng.randrange(65536)) for _ in range(10_000))
    return out

def run(profile,kind,cases):
    cpu,api=load(profile,kind)
    X=api['MATH_X'];Y=api['MATH_Y'];Z=api['MATH_Z']
    vec=[];shr_vec=[];errors=0
    for x,y in cases:
        cpu.mem[X]=x&255;cpu.mem[X+1]=x>>8
        cpu.mem[Y]=y&255;cpu.mem[Y+1]=y>>8
        cy=cpu.call(api['MATH_UMUL16'],10_000)
        got=sum(cpu.mem[Z+i]<<(8*i) for i in range(4))
        exp=(x*y)&0xffffffff
        if got!=exp or cpu.c!=0:
            errors+=1
            if errors<=8: print('UMUL16 ERROR',profile,kind,hex(x),hex(y),hex(got),hex(exp),cpu.c)
        vec.append(cy)

        cpu.mem[X]=x&255;cpu.mem[X+1]=x>>8
        cpu.mem[Y]=y&255;cpu.mem[Y+1]=y>>8
        scy=cpu.call(api['MATH_UMUL16_SHR8'],10_000)
        sgot=sum(cpu.mem[Z+i]<<(8*i) for i in range(3))
        sexp=((x*y)>>8)&0xffffff
        if sgot!=sexp or cpu.c!=0:
            errors+=1
            if errors<=8: print('SHR8 ERROR',profile,kind,hex(x),hex(y),hex(sgot),hex(sexp),cpu.c)
        if scy!=cy+27:
            errors+=1
            if errors<=8: print('CYCLE COMPOSE ERROR',profile,kind,x,y,cy,scy)
        shr_vec.append(scy)
    if errors: raise AssertionError(f'{profile} {kind}: {errors} errors')
    return {
        'profile':profile,'kind':kind,'cases':len(cases),
        'mean_cycles':sum(vec)/len(vec),'min_cycles':min(vec),'max_cycles':max(vec),
        'shr8_mean_cycles':sum(shr_vec)/len(shr_vec),
        'shr8_min_cycles':min(shr_vec),'shr8_max_cycles':max(shr_vec),
        'cycles':vec,'shr8_cycles':shr_vec,
    }

def main():
    cases=corpus()
    results={}
    for p in PROFILES:
        results[p]={}
        for k in KINDS:
            r=run(p,k,cases);results[p][k]=r
            print(f"{p} {k} PASS {r['cases']} UMUL16 {r['mean_cycles']:.6f} "
                  f"{r['min_cycles']}-{r['max_cycles']} SHR8 {r['shr8_mean_cycles']:.6f}")
        if results[p]['reference']['cycles']!=results[p]['alternate']['cycles']:
            raise AssertionError(f'{p}: reference/alternate UMUL16 cycle vectors differ')
        if results[p]['reference']['shr8_cycles']!=results[p]['alternate']['shr8_cycles']:
            raise AssertionError(f'{p}: reference/alternate SHR8 cycle vectors differ')
    base=results[PROFILES[0]]['reference']['cycles']
    for p in PROFILES[1:]:
        if results[p]['reference']['cycles']!=base:
            raise AssertionError(f'{p}: fixed-profile UMUL16 cycle vector differs from V2')
    mean=results['v2_pareto_fast']['reference']['mean_cycles']
    if not mean < 218:
        raise AssertionError(f'optimized UMUL16 unexpectedly slow: {mean}')
    print('UMUL16 DIRECT-OUTPUT PASS')
    clean={}
    for p in PROFILES:
        clean[p]={}
        for k in KINDS:
            r=results[p][k]
            clean[p][k]={x:r[x] for x in ('cases','mean_cycles','min_cycles','max_cycles','shr8_mean_cycles','shr8_min_cycles','shr8_max_cycles')}
    out=ROOT/'validation/multiply_refresh/UMUL16_DIRECTOUT_VALIDATION.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({'status':'PASS','seed':hex(SEED),'basis':'2026-10-06 UMUL16 direct-output + V2-V4 SHR8 register-return deterministic edge+random corpus; public entry cycles include RTS and exclude caller JSR/input stores','results':clean},indent=2)+'\n')

if __name__=='__main__': main()
