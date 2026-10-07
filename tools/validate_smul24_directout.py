#!/usr/bin/env python3
"""Validate direct-output public SMUL24 across all five fixed profiles."""
from pathlib import Path
import json, random, re, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from generate_consolidated_routine_table import trace

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
    config_profile='v1_balanced' if profile=='v5_hybrid_lowzp' else profile
    cfg=parse_inc(ROOT/'relocatable_source'/config_profile/f'math_config_{kind}.inc')
    zp=cfg['ZP_MAIN']+(7 if profile in ('v1_balanced','v5_hybrid_lowzp') else 0x1f)
    code,_,_=trace(cpu.mem,api['MATH_SMUL24'])
    allowed=code|set(range(zp,zp+24))|set(range(Z,Z+6))|set(range(0x1f8,0x1fe))
    write=cpu.wr
    def guarded_write(address,value):
        if address not in allowed:
            raise AssertionError((profile,kind,'unexpected SMUL24 write',hex(address)))
        write(address,value)
    cpu.wr=guarded_write
    vec=[];errors=0
    quad={'pp':[0,0],'pn':[0,0],'np':[0,0],'nn':[0,0]}
    for index,(x,y) in enumerate(cases):
        ex=enc24(x);ey=enc24(y)
        for i in range(3):
            cpu.mem[X+i]=(ex>>(8*i))&255
            cpu.mem[Y+i]=(ey>>(8*i))&255
        before_x=bytes(cpu.mem[X:X+3]);before_y=bytes(cpu.mem[Y:Y+3])
        # CPY must establish its own carry, independent of the caller's flags.
        cpu.c=index&1
        cpu.a=(index*17)&255;cpu.x=(index*31)&255;cpu.y=index&255
        cy=cpu.call(api['MATH_SMUL24'],30_000)
        got=sum(cpu.mem[Z+i]<<(8*i) for i in range(6))
        exp=(x*y)&MASK48
        if (got!=exp or cpu.c!=0 or cpu.sp!=0xfd
                or bytes(cpu.mem[X:X+3])!=before_x or bytes(cpu.mem[Y:Y+3])!=before_y):
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

def mixed_calls(profile,kind):
    """Exercise the pointer-low scratch reuse between other public operations."""
    cpu,api=load(profile,kind)
    rng=random.Random(0x24CA771)
    calls=0
    for index in range(256):
        for bits,signed in ((16,False),(24,False),(32,False),(16,True),(32,True)):
            x=rng.getrandbits(bits);y=rng.getrandbits(bits)
            for value,addr in ((x,api['MATH_X']),(y,api['MATH_Y'])):
                for i in range(bits//8):cpu.mem[addr+i]=(value>>(8*i))&255
            entry=api[f'MATH_{"S" if signed else "U"}MUL{bits}']
            cpu.call(entry)
            sx=x-(1<<bits) if signed and x&(1<<(bits-1)) else x
            sy=y-(1<<bits) if signed and y&(1<<(bits-1)) else y
            got=int.from_bytes(cpu.mem[api['MATH_Z']:api['MATH_Z']+bits//4],'little')
            assert got==(sx*sy)&((1<<(2*bits))-1),(profile,kind,bits,signed)
            assert cpu.c==0
            calls+=1
            # Immediately reuse shared scratch for SMUL24, then let the next
            # wider multiply check that its persistent pointer highs survived.
            x=rng.getrandbits(24);y=rng.getrandbits(24)
            cpu.mem[api['MATH_X']:api['MATH_X']+3]=x.to_bytes(3,'little')
            cpu.mem[api['MATH_Y']:api['MATH_Y']+3]=y.to_bytes(3,'little')
            cpu.c=index&1
            cpu.call(api['MATH_SMUL24'])
            got=int.from_bytes(cpu.mem[api['MATH_Z']:api['MATH_Z']+6],'little')
            assert got==(s24(x)*s24(y))&MASK48,(profile,kind,'mixed SMUL24')
            assert cpu.c==0
            calls+=1
    return calls

def main():
    cases=corpus();results={}
    for p in PROFILES:
        results[p]={}
        for k in KINDS:
            r=run(p,k,cases);results[p][k]=r
            r['mixed_calls']=mixed_calls(p,k)
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
    if not fast < 470:
        raise AssertionError(f'optimized V2-V4 SMUL24 unexpectedly slow: {fast}')
    if not low < 515:
        raise AssertionError(f'optimized V1/V5 SMUL24 unexpectedly slow: {low}')

    clean={}
    for p in PROFILES:
        clean[p]={}
        for k in KINDS:
            r=results[p][k]
            clean[p][k]={x:r[x] for x in (
                'cases','mean_cycles','min_cycles','max_cycles',
                'quadrant_counts','quadrant_means','mixed_calls')}
    out=ROOT/'validation/multiply_refresh/SMUL24_DIRECTOUT_VALIDATION.json'
    out.write_text(json.dumps({
        'status':'PASS','seed':hex(SEED),
        'basis':'2026-10-07 SMUL24 carry-prime/direct-output deterministic signed edge+random corpus; public entry cycles include RTS and exclude caller JSR/input stores',
        'abi_checks':'input preservation, incoming carry alternation, C=0 result, balanced stack, guarded writes within existing code/24-ZP/result/transient stack, interleaved signed/unsigned multiplies',
        'results':clean},indent=2)+'\n')
    print('SMUL24 DIRECT-OUTPUT PASS')

if __name__=='__main__': main()
