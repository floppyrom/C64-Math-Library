#!/usr/bin/env python3
"""Validate the V2/V3/V4 direct-output public UMUL24 producer."""
from pathlib import Path
import json, random, re, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')
KINDS=('reference','alternate')
BUILD=ROOT/'build_source'
SEED=0x24240024

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
    mem=bytearray(65536); mem[lo:lo+len(prg)-2]=prg[2:]
    reu=bytearray((d/man['reu_image']['file']).read_bytes()) if man.get('reu_image') else None
    api=parse_inc(d/'math_api.inc')
    cpu=CPU(mem,reu=reu); cpu.d=0; cpu.call(api['MATH_INIT'],2_000_000)
    return cpu,api

def corpus():
    edges=(0,1,2,3,0x7f,0x80,0xff,0x100,0x101,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffff,0x800000,0xfffffe,0xffffff)
    out=[(x,y) for x in edges for y in edges]
    rng=random.Random(SEED)
    out.extend((rng.randrange(1<<24),rng.randrange(1<<24)) for _ in range(10_000))
    return out

def run(profile,kind,cases):
    cpu,api=load(profile,kind)
    X=api['MATH_X'];Y=api['MATH_Y'];Z=api['MATH_Z']
    vec=[];errors=0
    for x,y in cases:
        for i in range(3):
            cpu.mem[X+i]=(x>>(8*i))&255
            cpu.mem[Y+i]=(y>>(8*i))&255
        cy=cpu.call(api['MATH_UMUL24'],20_000)
        got=sum(cpu.mem[Z+i]<<(8*i) for i in range(6))
        exp=(x*y)&((1<<48)-1)
        if got!=exp or cpu.c!=0:
            errors+=1
            if errors<=8:
                print('ERROR',profile,kind,hex(x),hex(y),hex(got),hex(exp),cpu.c)
        vec.append(cy)
    if errors: raise AssertionError(f'{profile} {kind}: {errors} errors')
    return {'cases':len(cases),'mean_cycles':sum(vec)/len(vec),
            'min_cycles':min(vec),'max_cycles':max(vec),'cycles':vec}

def main():
    cases=corpus(); results={}
    for p in PROFILES:
        results[p]={}
        for k in KINDS:
            r=run(p,k,cases);results[p][k]=r
            print(f"{p} {k} PASS {r['cases']} {r['mean_cycles']:.6f} {r['min_cycles']}-{r['max_cycles']}")
        if results[p]['reference']['cycles']!=results[p]['alternate']['cycles']:
            raise AssertionError(f'{p}: reference/alternate cycle vectors differ')
    base=results[PROFILES[0]]['reference']['cycles']
    for p in PROFILES[1:]:
        if results[p]['reference']['cycles']!=base:
            raise AssertionError(f'{p}: cycle vector differs from V2')
    mean=results['v2_pareto_fast']['reference']['mean_cycles']
    if not mean < 442:
        raise AssertionError(f'optimized UMUL24 unexpectedly slow: {mean}')
    clean={}
    for p in PROFILES:
        clean[p]={}
        for k in KINDS:
            r=results[p][k]
            clean[p][k]={x:r[x] for x in ('cases','mean_cycles','min_cycles','max_cycles')}
    out=ROOT/'validation/multiply_refresh/UMUL24_DIRECTOUT_VALIDATION.json'
    out.write_text(json.dumps({
        'status':'PASS','seed':hex(SEED),
        'basis':'2026-10-06 UMUL24 direct-output deterministic edge+random corpus; public entry cycles include RTS and exclude caller JSR/input stores',
        'results':clean},indent=2)+'\n')
    print('UMUL24 DIRECT-OUTPUT PASS')

if __name__=='__main__': main()
