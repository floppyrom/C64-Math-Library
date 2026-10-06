#!/usr/bin/env python3
"""Validate direct-output public SMUL24 across all five fixed profiles."""
from pathlib import Path
import json, random, re, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
KINDS=('reference','alternate')
BUILD=ROOT/'build_source'
HYBRID=ROOT/'build_hybrid'
SEED=0x52424D18
MASK24=(1<<24)-1
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
    mem=bytearray(65536)
    mem[lo:lo+len(prg)-2]=prg[2:]
    reu=bytearray((d/man['reu_image']['file']).read_bytes()) if man.get('reu_image') else None
    api=parse_inc(d/'math_api.inc')
    cpu=CPU(mem,reu=reu)
    cpu.d=0
    cpu.call(api['MATH_INIT'],2_000_000)
    return cpu,api

def s24(v):
    v &= MASK24
    return v-(1<<24) if v&(1<<23) else v

def enc24(v):
    return v&MASK24

def corpus():
    edges=(-8388608,-8388607,-65536,-32768,-257,-256,-129,-128,-3,-2,-1,
           0,1,2,3,127,128,255,256,257,32767,32768,65535,65536,8388606,8388607)
    out=[(x,y) for x in edges for y in edges]
    rng=random.Random(SEED)
    for _ in range(10_000):
        x=rng.randrange(-(1<<23),1<<23)
        y=rng.randrange(-(1<<23),1<<23)
        out.append((x,y))
    return out

def run(profile,kind,cases):
    cpu,api=load(profile,kind)
    X=api['MATH_X'];Y=api['MATH_Y'];Z=api['MATH_Z']
    vec=[];errors=0
    quad={'pp':[0,0],'pn':[0,0],'np':[0,0],'nn':[0,0]}
    for x,y in cases:
        ex=enc24(x);ey=enc24(y)
        for i in range(3):
            cpu.mem[X+i]=(ex>>(8*i))&255
            cpu.mem[Y+i]=(ey>>(8*i))&255
        cy=cpu.call(api['MATH_SMUL24'],30_000)
        got=sum(cpu.mem[Z+i]<<(8*i) for i in range(6))
        exp=(x*y)&MASK48
        if got!=exp or cpu.c!=0:
            errors+=1
            if errors<=8:
                print('ERROR',profile,kind,x,y,hex(got),hex(exp),cpu.c)
        q=('n' if x<0 else 'p')+('n' if y<0 else 'p')
        quad[q][0]+=1;quad[q][1]+=cy
        vec.append(cy)
    if errors: raise AssertionError(f'{profile} {kind}: {errors} errors')
    return {
        'cases':len(cases),'mean_cycles':sum(vec)/len(vec),
        'min_cycles':min(vec),'max_cycles':max(vec),
        'quadrant_counts':{k:v[0] for k,v in quad.items()},
        'quadrant_means':{k:v[1]/v[0] for k,v in quad.items()},
        'cycles':vec,
    }

def main():
    cases=corpus();results={}
    for p in PROFILES:
        results[p]={}
        for k in KINDS:
            r=run(p,k,cases);results[p][k]=r
            print(f"{p} {k} PASS {r['cases']} {r['mean_cycles']:.6f} {r['min_cycles']}-{r['max_cycles']} "
                  f"quadrants={r['quadrant_counts']}")
        if results[p]['reference']['cycles']!=results[p]['alternate']['cycles']:
            raise AssertionError(f'{p}: reference/alternate cycle vectors differ')
    v2=results['v2_pareto_fast']['reference']['cycles']
    for p in ('v3_reu_512k','v4_reu_16m'):
        if results[p]['reference']['cycles']!=v2:
            raise AssertionError(f'{p}: cycle vector differs from V2')
    if results['v5_hybrid_lowzp']['reference']['cycles']!=results['v1_balanced']['reference']['cycles']:
        raise AssertionError('V5 SMUL24 cycle vector differs from inherited V1 path')

    fast=results['v2_pareto_fast']['reference']['mean_cycles']
    low=results['v1_balanced']['reference']['mean_cycles']
    if not fast < 475:
        raise AssertionError(f'optimized V2-V4 SMUL24 unexpectedly slow: {fast}')
    if not low < 520:
        raise AssertionError(f'optimized V1/V5 SMUL24 unexpectedly slow: {low}')

    clean={}
    for p in PROFILES:
        clean[p]={}
        for k in KINDS:
            r=results[p][k]
            clean[p][k]={x:r[x] for x in (
                'cases','mean_cycles','min_cycles','max_cycles',
                'quadrant_counts','quadrant_means')}
    out=ROOT/'validation/multiply_refresh/SMUL24_DIRECTOUT_VALIDATION.json'
    out.write_text(json.dumps({
        'status':'PASS','seed':hex(SEED),
        'basis':'2026-10-06 SMUL24 direct-output deterministic signed edge+random corpus; public entry cycles include RTS and exclude caller JSR/input stores',
        'results':clean},indent=2)+'\n')
    print('SMUL24 DIRECT-OUTPUT PASS')

if __name__=='__main__': main()
