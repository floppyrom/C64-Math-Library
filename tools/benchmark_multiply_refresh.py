#!/usr/bin/env python3
"""Benchmark and validate the shipped multiply surface after the 2026-09 refresh.

The corpus is identical across all five profiles.  Timings are public-entry CPU
cycles including RTS and excluding caller JSR/input stores.  The script also
checks arithmetic, Carry, and public input preservation.
"""
from __future__ import annotations
from pathlib import Path
import argparse, json, random, re, sys, time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
REU={
 'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu',
 'v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu',
}
MASK=lambda b:(1<<b)-1

def si(v,b): return v-(1<<b) if v&(1<<(b-1)) else v

def wr(mem,a,v,n):
    for i in range(n): mem[a+i]=(v>>(8*i))&255

def rd(mem,a,n): return sum(mem[a+i]<<(8*i) for i in range(n))

def api(path):
    out={}
    for line in path.read_text().splitlines():
        m=re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
        if m: out[m.group(1)]=int(m.group(2),16)
    return out

def load(profile):
    resident=ROOT/profile/'resident'
    p=resident/f'math_{profile}_game_math.prg'; b=p.read_bytes(); ld=b[0]|b[1]<<8
    mem=bytearray(65536); mem[ld:ld+len(b)-2]=b[2:]
    reu=bytearray(REU[profile].read_bytes()) if profile in REU else None
    c=CPU(mem,reu=reu); c.d=0; P=api(resident/'math_api.inc')
    c.call(0x3280,2_000_000)
    return c,P

def edge(bits):
    m=MASK(bits); s=1<<(bits-1)
    return list(dict.fromkeys(x&m for x in [0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))

def corpus(bits,random_count,seed):
    e=edge(bits); out=[(x,y) for x in e for y in e]
    r=random.Random(seed)
    out += [(r.randrange(1<<bits),r.randrange(1<<bits)) for _ in range(random_count)]
    return out

CORPORA={
  8:[(x,y) for x in range(256) for y in range(256)],
  16:corpus(16,4096,0x4D554C10),
  24:corpus(24,2048,0x4D554C18),
  32:corpus(32,2048,0x4D554C20),
  'ready32':[(lambda r:(r.randrange(1<<32),r.randrange(1<<32)))(random.Random(0))],
}
# Build READY and shift corpora explicitly without stateful comprehension tricks.
r=random.Random(0x52454144); CORPORA['ready32']=[(r.randrange(1<<32),r.randrange(1<<32)) for _ in range(1024)]
CORPORA['shift16']=corpus(16,4000,0x53485208)
CORPORA['shift32']=corpus(32,4000,0x53485210)

def run_full(c,P,name,bits,pairs,signed=False,ready=False):
    X=0xC000;Y=X+4;Z=X+8;n=bits//8; total=0;mn=None;mx=None;errors=0
    for x,y in pairs:
        wr(c.mem,X,x,n);wr(c.mem,Y,y,n);bx=bytes(c.mem[X:X+n]);by=bytes(c.mem[Y:Y+n])
        cy=c.call(P[name],2_000_000)
        a=si(x,bits) if signed else x; b=si(y,bits) if signed else y
        exp=(a*b)&MASK(bits*2); got=rd(c.mem,Z,n*2)
        if got!=exp or c.c!=0 or bytes(c.mem[X:X+n])!=bx or bytes(c.mem[Y:Y+n])!=by:
            errors+=1
            if errors<4: print('ERROR',name,hex(x),hex(y),hex(got),hex(exp),c.c,file=sys.stderr)
        total+=cy; mn=cy if mn is None else min(mn,cy); mx=cy if mx is None else max(mx,cy)
    if errors: raise AssertionError((name,errors))
    return {'mean_cycles':total/len(pairs),'min_cycles':mn,'max_cycles':mx,'cases':len(pairs),'errors':0}

def run_shift(c,P,name,bits,shift,outbytes,pairs,signed=False):
    X=0xC000;Y=X+4;Z=X+8;n=bits//8;total=0;mn=None;mx=None;errors=0
    for x,y in pairs:
        wr(c.mem,X,x,n);wr(c.mem,Y,y,n);bx=bytes(c.mem[X:X+n]);by=bytes(c.mem[Y:Y+n])
        cy=c.call(P[name],2_000_000)
        a=si(x,bits) if signed else x; b=si(y,bits) if signed else y
        exp=((a*b)>>shift)&MASK(outbytes*8);got=rd(c.mem,Z,outbytes)
        if got!=exp or c.c!=0 or bytes(c.mem[X:X+n])!=bx or bytes(c.mem[Y:Y+n])!=by:
            errors+=1
            if errors<4: print('ERROR',name,hex(x),hex(y),hex(got),hex(exp),c.c,file=sys.stderr)
        total+=cy;mn=cy if mn is None else min(mn,cy);mx=cy if mx is None else max(mx,cy)
    if errors: raise AssertionError((name,errors))
    return {'mean_cycles':total/len(pairs),'min_cycles':mn,'max_cycles':mx,'cases':len(pairs),'errors':0}

def benchmark_profile(p):
    c,P=load(p); d={}
    # Direct SMUL8 is small enough to certify exhaustively in every profile.
    d['MATH_SMUL8']=run_full(c,P,'MATH_SMUL8',8,CORPORA[8],True)
    if p in ('v1_balanced','v5_hybrid_lowzp'):
        d['MATH_UMUL24']=run_full(c,P,'MATH_UMUL24',24,CORPORA[24],False)
    d['MATH_UMUL32']=run_full(c,P,'MATH_UMUL32',32,CORPORA[32],False)
    d['MATH_UMUL32_READY']=run_full(c,P,'MATH_UMUL32_READY',32,CORPORA['ready32'],False,True)
    d['MATH_UMUL32_SHR16']=run_shift(c,P,'MATH_UMUL32_SHR16',32,16,6,CORPORA['shift32'],False)
    # Signed producers are covered by the larger signed validator; benchmark
    # fixed-point derivatives here because their cycle rows change when the
    # underlying producer changes.
    d['MATH_SMUL16_SHR8']=run_shift(c,P,'MATH_SMUL16_SHR8',16,8,3,CORPORA['shift16'],True)
    d['MATH_SMUL32_SHR16']=run_shift(c,P,'MATH_SMUL32_SHR16',32,16,6,CORPORA['shift32'],True)
    return d

def write_merged(profiles,start):
    out={
      'status':'PASS','date':'2026-09-20',
      'timing_convention':'public entry through RTS; caller JSR and input stores excluded',
      'corpus':'identical deterministic bit-pattern corpus across profiles; SMUL8 exhaustive 65,536; 24/32-bit 2,409; READY32 1,024; fixed-shift 4,361. Wider signed producer rows use validation/review/SIGNED_MULTIPLY_VALIDATION.json.',
      'profiles':profiles,
      'summary':{'profiles':len(profiles),'machine_calls':sum(v['cases'] for d in profiles.values() for v in d.values()),'elapsed_seconds':round(time.time()-start,2)}
    }
    path=ROOT/'validation/multiply_refresh/MULTIPLY_REFRESH_BENCHMARK.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n')
    return path,out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--profile',choices=PROFILES);ap.add_argument('--merge',action='store_true');a=ap.parse_args();start=time.time()
    droot=ROOT/'validation/multiply_refresh';droot.mkdir(parents=True,exist_ok=True)
    if a.merge:
        profiles={}
        for p in PROFILES:
            q=droot/f'{p}.json'
            if not q.exists(): raise SystemExit(f'missing {q}')
            profiles[p]=json.loads(q.read_text())['results']
        path,out=write_merged(profiles,start);print('MULTIPLY REFRESH MERGED',out['summary']['machine_calls'],'calls ->',path.relative_to(ROOT));return
    ps=[a.profile] if a.profile else PROFILES;profiles={}
    for p in ps:
        d=benchmark_profile(p);profiles[p]=d
        (droot/f'{p}.json').write_text(json.dumps({'status':'PASS','profile':p,'results':d},indent=2)+'\n')
        print(p,'PASS',sum(v['cases'] for v in d.values()),'refresh-sensitive calls',flush=True)
    path,out=write_merged(profiles,start)
    print('MULTIPLY REFRESH PASS',out['summary']['machine_calls'],'calls ->',path.relative_to(ROOT))
if __name__=='__main__':main()

