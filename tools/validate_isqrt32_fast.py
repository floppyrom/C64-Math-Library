#!/usr/bin/env python3
from pathlib import Path
import sys,json,math,random,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m']
PRGS={p:ROOT/p/'resident'/f'math_{p}_game_math.prg' for p in PROFILES}
REUS={
 'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu',
 'v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu',
}
PUB=0x5E30;INIT=0x3280;IO_N=0xC010;IO_Z=0xC008

def wr(c,a,v,n):
 for i in range(n):c.mem[a+i]=(v>>(8*i))&255

def rd(c,a,n):return sum(c.mem[a+i]<<(8*i) for i in range(n))

def load_prg(path):
 b=path.read_bytes();ld=b[0]|b[1]<<8;m=bytearray(65536);m[ld:ld+len(b)-2]=b[2:];return m

def cases():
 e=[0,1,2,3,4,7,8,9,15,16,17,24,25,26,255,256,257,65534,65535,65536,65537,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
 roots=[0,1,2,3,15,16,31,127,128,255,256,257,1023,4095,16383,32767,32768,65534,65535]
 for r in roots:
  q=r*r
  for d in (-2,-1,0,1,2):
   if 0<=q+d<=0xffffffff:e.append(q+d)
 rng=random.Random(0x495351525433325F);e += [rng.randrange(1<<32) for _ in range(5000)]
 return list(dict.fromkeys(e))

def main():
 cs=cases();res=[]
 for p in PROFILES:
  reu=bytearray(REUS[p].read_bytes()) if p in REUS else None
  c=CPU(load_prg(PRGS[p]),reu=reu);c.d=0;c.call(INIT,2_000_000);total=0;mn=10**9;mx=0
  for n in cs:
   wr(c,IO_N,n,4);before=bytes(c.mem[IO_N:IO_N+4]);cy=c.call(PUB,2_000_000);got=rd(c,IO_Z,2)
   assert got==math.isqrt(n),(p,hex(n),got,math.isqrt(n))
   assert bytes(c.mem[IO_N:IO_N+4])==before,(p,'input',hex(n))
   assert c.c==0,(p,'carry',hex(n))
   total+=cy;mn=min(mn,cy);mx=max(mx,cy)
  r={'profile':p,'status':'PASS','cases':len(cs),'mean_cycles':total/len(cs),'min_cycles':mn,'max_cycles':mx,'resident_prg_sha256':hashlib.sha256(PRGS[p].read_bytes()).hexdigest()};res.append(r);print(p,'PASS',len(cs),f'{r["mean_cycles"]:.6f}',mn,mx,flush=True)
 out={
  'status':'PASS',
  'algorithm':'hybrid exact ISQRT32: exact ISQRT16 high-byte seed plus eight restoring base-4 refinement steps',
  'proof_note':'For N=(H<<16)+L and r=floor(sqrt(H)), 256*r <= sqrt(N) < 256*(r+1), so r is exactly the high byte of floor(sqrt(N)). The residual H-r^2 seeds the remaining eight base-4 digits.',
  'contract':'floor(sqrt(N32)); N preserved; C=0',
  'case_design':'boundary values, values around representative perfect squares, 5,000 deterministic random 32-bit radicands',
  'profiles':res}
 d=ROOT/'validation/review';d.mkdir(parents=True,exist_ok=True);(d/'ISQRT32_FAST_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
