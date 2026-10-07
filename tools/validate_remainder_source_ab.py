#!/usr/bin/env python3
from pathlib import Path
import json,random,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=['v2_pareto_fast','v3_reu_512k','v4_reu_16m']
ROUTINES=[
 ('MATH_UMOD16',16,16,2),
 ('MATH_UMOD24',24,24,3),
 ('MATH_UMOD32_32',32,32,4),
]
def api(path):
 out={}
 for line in path.read_text().splitlines():
  m=re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
  if m:out[m.group(1)]=int(m.group(2),16)
 return out

def load_prg(path):
 b=path.read_bytes();lo=b[0]|b[1]<<8;m=bytearray(65536);m[lo:lo+len(b)-2]=b[2:];return m

def cpu_for(profile,kind):
 if kind=='baseline':
  prg=ROOT/profile/'resident'/f'math_{profile}_game_math.prg'
  inc=ROOT/profile/'resident/math_api.inc'
  reup=ROOT/profile/'reu'/f'c64_math_{profile.replace("_reu_512k","_512k").replace("_reu_16m","_16m")}_game_math.reu'
  # actual names differ only by profile; fall back through directory listing
  if profile.startswith('v3_'): reup=ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu'
  elif profile.startswith('v4_'): reup=ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'
 else:
  d=ROOT/'build_source'/kind/profile
  prg=d/f'math_{profile}_source_built.prg'
  inc=d/'math_api.inc'
  reup=d/f'c64_math_{profile}_source_built.reu'
 reu=bytearray(reup.read_bytes()) if reup.exists() else None
 c=CPU(load_prg(prg),reu=reu);c.d=0
 A=api(inc);c.call(A['MATH_INIT'],3_000_000)
 return c,A

def wr(m,a,v,n):
 for i in range(n):m[a+i]=(v>>(8*i))&255

def rd(m,a,n):return sum(m[a+i]<<(8*i) for i in range(n))

def edges(bits):
 M=(1<<bits)-1;h=1<<(bits-1)
 return list(dict.fromkeys(x&M for x in [0,1,2,3,4,5,7,15,16,31,63,127,128,255,256,257,511,1023,h-1,h,h+1,M-2,M-1,M]))

def cases(bits,seed):
 e=edges(bits);out=[(n,d) for n in e for d in e]
 rng=random.Random(seed)
 out += [(rng.randrange(1<<bits),rng.randrange(1<<bits)) for _ in range(12000)]
 # quotient-focused distributions: q=0/1/small/hard plus divide-by-zero
 for _ in range(3000):
  d=rng.randrange(1,1<<bits)
  q=rng.randrange(0,6)
  rem=rng.randrange(d)
  n=q*d+rem
  if n < (1<<bits):out.append((n,d))
 out += [(rng.randrange(1<<bits),0) for _ in range(256)]
 return out

def run(c,A,entry,cs,nbytes):
 N=A['MATH_N'];D=A['MATH_D'];R=A['MATH_R']
 tot=0;mn=10**9;mx=0;err=0
 for n,d in cs:
  wr(c.mem,N,n,nbytes);wr(c.mem,D,d,nbytes)
  bn=bytes(c.mem[N:N+nbytes]);bd=bytes(c.mem[D:D+nbytes])
  cy=c.call(entry,5_000_000);got=rd(c.mem,R,nbytes)
  exp=0 if d==0 else n%d;ec=1 if d==0 else 0
  if got!=exp or c.c!=ec or bytes(c.mem[N:N+nbytes])!=bn or bytes(c.mem[D:D+nbytes])!=bd:
   err+=1
   if err<=3:print('ERROR',hex(entry),hex(n),hex(d),hex(got),c.c,hex(exp),ec)
  tot+=cy;mn=min(mn,cy);mx=max(mx,cy)
 return dict(cases=len(cs),errors=err,mean_cycles=tot/len(cs),min_cycles=mn,max_cycles=mx)

out={'status':'PASS','profiles':{}}
for pi,p in enumerate(PROFILES):
 base,BA=cpu_for(p,'baseline')
 ref,RA=cpu_for(p,'reference')
 alt,AA=cpu_for(p,'alternate')
 pr={}
 for ri,(name,nb,db,nbytes) in enumerate(ROUTINES):
  cs=cases(nb,0x524D0000+pi*0x1000+ri)
  b=run(base,BA,BA[name],cs,nbytes)
  n=run(ref,RA,RA[name],cs,nbytes)
  a=run(alt,AA,AA[name],cs,nbytes)
  if b['errors'] or n['errors'] or a['errors']:raise AssertionError((p,name,b,n,a))
  n['delta_vs_baseline']=n['mean_cycles']-b['mean_cycles']
  a['delta_vs_baseline']=a['mean_cycles']-b['mean_cycles']
  pr[name]={'baseline':b,'reference':n,'alternate':a}
  print(p,name,'PASS',len(cs),
        f"baseline={b['mean_cycles']:.6f}",
        f"new={n['mean_cycles']:.6f}",
        f"delta={n['delta_vs_baseline']:.6f}",
        f"range={n['min_cycles']}-{n['max_cycles']}",flush=True)
 out['profiles'][p]=pr
path=ROOT/'validation/review/REMAINDER_ONLY_SOURCE_AB.json'
path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n')
print('REMAINDER SOURCE A/B PASS')
