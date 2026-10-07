#!/usr/bin/env python3
"""Paired validation for the integrated direct UDIV32/16 source candidate.

Compares each V2/V3/V4 source-built reference image with the current shipped
resident image on the same deterministic inputs.  Also exercises alternate-map
source builds for arithmetic/input-preservation correctness.
"""
from pathlib import Path
import json,random,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from validate_unsigned_division import load as load_resident,wr,rd,expected,edge

PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')
BUILD=ROOT/'build_u3216'

def unhx(v):
    return int(v[1:],16) if isinstance(v,str) and v.startswith('$') else int(v)

def load_source(profile,kind):
    d=BUILD/kind/profile
    man=json.loads((d/'source_build_manifest.json').read_text())
    p=d/man['output_prg']; b=p.read_bytes(); lo=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[lo:lo+len(b)-2]=b[2:]
    reu=None
    ri=man.get('reu_image')
    if ri and ri.get('path'):
        rp=d/Path(ri['path']).name
        if not rp.exists(): rp=d/ri['path']
        reu=bytearray(rp.read_bytes())
    cpu=CPU(mem,reu=reu);cpu.d=0
    api={k:unhx(v) for k,v in man['public_entries'].items()}
    cpu.call(unhx(man['math_init']),2_000_000)
    return cpu,api

def vectors():
    out=[(n,d) for n in edge(32) for d in edge(16)]
    r=random.Random(0x3216A11)
    out += [(r.getrandbits(32),r.randrange(1,65536)) for _ in range(40000)]
    out += [(r.getrandbits(32),r.randrange(1,256)) for _ in range(20000)]
    out += [(r.getrandbits(32),0) for _ in range(128)]
    for d in list(range(1,33))+[63,127,128,129,254,255,256,257,511,512,1023,4095,16383,32767,65535]:
        for q in [0,1,2,3,7,15,31,127,255,256,257,65535,65536,0xffffff,0xffffffff]:
            for z in (-1,0,1):
                n=d*q+z
                if 0<=n<=0xffffffff: out.append((n,d))
        for n in [0,1,d-1,d,d+1,0xffff,0xffffff,0x7fffffff,0xffffffff,max(0,0xffffffff-d)]:
            if 0<=n<=0xffffffff: out.append((n,d))
    return list(dict.fromkeys(out))

def one(cpu,entry,n,d):
    N,D,Q,R=0xc010,0xc014,0xc018,0xc01c
    wr(cpu.mem,N,n,4);wr(cpu.mem,D,d,2)
    bn=bytes(cpu.mem[N:N+4]);bd=bytes(cpu.mem[D:D+2])
    cy=cpu.call(entry,4_000_000)
    eq,er,ec=expected(n,d,32,16)
    got=(rd(cpu.mem,Q,4),rd(cpu.mem,R,2),cpu.c)
    ok=got==(eq,er,ec) and bytes(cpu.mem[N:N+4])==bn and bytes(cpu.mem[D:D+2])==bd
    return cy,ok,got,(eq,er,ec)

def stats(c):
    return {'mean_cycles':sum(c)/len(c),'min_cycles':min(c),'max_cycles':max(c),'cases':len(c)}

def run():
    vec=vectors(); result={'status':'PASS','cases':len(vec),'profiles':{}}
    for p in PROFILES:
        old,Aold=load_resident(p)
        new,Anew=load_source(p,'reference')
        alt,Aalt=load_source(p,'alternate')
        oc=[];nc=[];d8o=[];d8n=[];errs=[]
        for n,d in vec:
            a,ok1,g1,e=one(old,Aold['MATH_UDIV32_16'],n,d)
            b,ok2,g2,_=one(new,Anew['MATH_UDIV32_16'],n,d)
            _,ok3,g3,_=one(alt,Aalt['MATH_UDIV32_16'],n,d)
            if not(ok1 and ok2 and ok3):
                errs.append({'n':hex(n),'d':hex(d),'old':g1,'new':g2,'alt':g3,'exp':e})
                if len(errs)>=8: break
            oc.append(a);nc.append(b)
            if 0<d<256:d8o.append(a);d8n.append(b)
        if errs: raise AssertionError((p,errs))
        delta=[a-b for a,b in zip(oc,nc)]
        d8delta=[a-b for a,b in zip(d8o,d8n)]
        result['profiles'][p]={
            'old':stats(oc),'new':stats(nc),
            'saved_mean_cycles':sum(delta)/len(delta),
            'min_saved_cycles':min(delta),'max_saved_cycles':max(delta),
            'slower_cases':sum(x<0 for x in delta),'equal_cases':sum(x==0 for x in delta),
            'd8':{
              'old':stats(d8o),'new':stats(d8n),
              'saved_mean_cycles':sum(d8delta)/len(d8delta),
              'slower_cases':sum(x<0 for x in d8delta)
            },
            'alternate_map_exact':True
        }
        print(p,json.dumps(result['profiles'][p],sort_keys=True),flush=True)
    out=ROOT/'validation/research/UDIV32_16_INTEGRATED.json'
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print('UDIV32/16 INTEGRATED PASS',len(vec),'cases/profile')
if __name__=='__main__':run()
