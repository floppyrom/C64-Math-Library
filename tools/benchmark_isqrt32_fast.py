#!/usr/bin/env python3
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m']
PRGS={p:ROOT/p/'resident'/f'math_{p}_game_math.prg' for p in PROFILES}
REUS={
 'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu',
 'v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu',
}
PUB=0x5E30;INIT=0x3280;IO_N=0xC010;IO_Z=0xC008;MASK32=(1<<32)-1

def splitmix64(x):
 x=(x+0x9E3779B97F4A7C15)&((1<<64)-1);z=x;z=(z^(z>>30))*0xBF58476D1CE4E5B9&((1<<64)-1);z=(z^(z>>27))*0x94D049BB133111EB&((1<<64)-1);return x,(z^(z>>31))&((1<<64)-1)
def pairs(count,seed):
 x=seed
 for _ in range(count):
  x,a=splitmix64(x);x,b=splitmix64(x);yield a&0xffffffff,b&0xffffffff
def wr(c,a,v,n):
 for i in range(n):c.mem[a+i]=(v>>(8*i))&255
def rd(c,a,n):return sum(c.mem[a+i]<<(8*i) for i in range(n))
def load(p):
 b=PRGS[p].read_bytes();ld=b[0]|b[1]<<8;m=bytearray(65536);m[ld:ld+len(b)-2]=b[2:]
 reu=bytearray(REUS[p].read_bytes()) if p in REUS else None
 c=CPU(m,reu=reu);c.d=0;c.call(INIT,2_000_000);return c
edge32=[0,1,2,3,7,15,16,31,127,128,255,256,257,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffff,0x800000,0xffffff,0x1000000,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
CASES=[a for a,b in pairs(4096,0x5A7E3200)]+edge32+[x*x&MASK32 for x in [0,1,2,3,255,256,257,65535]]
assert len(CASES)==4130
res=[]
for p in PROFILES:
 c=load(p);tot=0;mn=10**9;mx=0;errors=0
 for n in CASES:
  wr(c,IO_N,n,4);before=bytes(c.mem[IO_N:IO_N+4]);cy=c.call(PUB,2_000_000);got=rd(c,IO_Z,2)
  if got!=math.isqrt(n) or bytes(c.mem[IO_N:IO_N+4])!=before or c.c!=0:errors+=1
  tot+=cy;mn=min(mn,cy);mx=max(mx,cy)
 r={'profile':p,'cases':len(CASES),'mean_cycles':tot/len(CASES),'min_cycles':mn,'max_cycles':mx,'errors':errors};res.append(r);print(p,r,flush=True)
 assert errors==0
out={'status':'PASS','corpus':'same 4,130-case deterministic ISQRT32 corpus used by the prior GAME_MATH performance table','algorithm':'ISQRT16 high-word seed + eight restoring base-4 refinement steps','profiles':res}
(ROOT/'validation/review/ISQRT32_FAST_PERFORMANCE_4130.json').write_text(json.dumps(out,indent=2)+'\n')
