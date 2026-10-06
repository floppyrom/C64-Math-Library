#!/usr/bin/env python3
"""Exhaustively validate the source-built V3/V4 hybrid REU UDIV8 path."""
from pathlib import Path
import json,re,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=('v3_reu_512k','v4_reu_16m')
BUILD=ROOT/'build_source/reference'
V2_MEAN=59.383011

def parse_inc(path):
    out={}
    for line in path.read_text().splitlines():
        m=re.match(r'\s*([A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
        if m:
            out[m.group(1)]=int(m.group(2),16)
    return out

def load(profile):
    d=BUILD/profile
    man=json.loads((d/'source_build_manifest.json').read_text())
    prg=(d/man['output_prg']).read_bytes()
    lo=prg[0]|(prg[1]<<8)
    mem=bytearray(65536)
    mem[lo:lo+len(prg)-2]=prg[2:]
    reu_info=man['reu_image']
    reu=bytearray((d/reu_info['file']).read_bytes())
    api=parse_inc(d/'math_api.inc')
    cpu=CPU(mem,reu=reu)
    cpu.d=0
    cpu.call(api['MATH_INIT'],2_000_000)
    return cpu,api

def run(profile):
    cpu,api=load(profile)
    N,D,Q,R=0xC010,0xC014,0xC018,0xC01C
    total=0
    mn=None
    mx=None
    errors=0
    classes={}
    for n in range(256):
        for d in range(256):
            cpu.mem[N]=n
            cpu.mem[D]=d
            before_n=cpu.mem[N]
            before_d=cpu.mem[D]
            cy=cpu.call(api['MATH_UDIV8'],10000)
            eq=0 if d==0 else n//d
            er=0 if d==0 else n%d
            ec=1 if d==0 else 0
            got=(cpu.mem[Q],cpu.mem[R],cpu.c)
            if got!=(eq,er,ec) or cpu.mem[N]!=before_n or cpu.mem[D]!=before_d:
                errors+=1
                if errors<=8:
                    print('ERROR',profile,n,d,'got',got,'expected',(eq,er,ec))
            total+=cy
            mn=cy if mn is None else min(mn,cy)
            mx=cy if mx is None else max(mx,cy)
            key='d0' if d==0 else ('q0' if eq==0 else 'q1' if eq==1 else 'q2' if eq==2 else 'q3' if eq==3 else 'q4+')
            z=classes.setdefault(key,[0,0])
            z[0]+=1
            z[1]+=cy
    mean=total/65536
    summary={
        'profile':profile,
        'cases':65536,
        'errors':errors,
        'mean_cycles':mean,
        'min_cycles':mn,
        'max_cycles':mx,
        'class_means':{k:v[1]/v[0] for k,v in sorted(classes.items())},
        'class_counts':{k:v[0] for k,v in sorted(classes.items())},
    }
    if errors:
        raise AssertionError(summary)
    if not mean < V2_MEAN:
        raise AssertionError(f'{profile}: hybrid REU UDIV8 {mean:.9f} does not beat V2 {V2_MEAN:.9f}')
    print(json.dumps(summary,sort_keys=True))
    return summary

if __name__=='__main__':
    out=[run(p) for p in PROFILES]
    if abs(out[0]['mean_cycles']-out[1]['mean_cycles'])>1e-12:
        raise AssertionError('V3/V4 hybrid UDIV8 cycle means diverged')
    print('REU UDIV8 HYBRID PASS')
