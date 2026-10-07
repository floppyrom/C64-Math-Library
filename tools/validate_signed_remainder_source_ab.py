#!/usr/bin/env python3
from pathlib import Path
import json,random,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILES=['v2_pareto_fast','v3_reu_512k','v4_reu_16m']
ROUTINES=[('MATH_SMOD16',16,2),('MATH_SMOD24',24,3)]
N=0xC010;D=0xC014;R=0xC01C

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
  if profile.startswith('v3_'): reup=ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu'
  elif profile.startswith('v4_'): reup=ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'
  else: reup=Path('/nonexistent')
 else:
  d=ROOT/'build_source'/kind/profile
  prg=d/f'math_{profile}_source_built.prg';inc=d/'math_api.inc'
  reup=d/f'c64_math_{profile}_source_built.reu'
 reu=bytearray(reup.read_bytes()) if reup.exists() else None
 c=CPU(load_prg(prg),reu=reu);c.d=0;A=api(inc);c.call(A['MATH_INIT'],3_000_000);return c,A

def enc(x,bits):return x&((1<<bits)-1)
def dec(x,bits):
 sign=1<<(bits-1);return x-(1<<bits) if x&sign else x
def wr(m,a,v,n):
 for i in range(n):m[a+i]=(v>>(8*i))&255
def rd(m,a,n):return sum(m[a+i]<<(8*i) for i in range(n))

def edges(bits):
 lo=-(1<<(bits-1));hi=(1<<(bits-1))-1
 return list(dict.fromkeys([lo,lo+1,-32768 if bits>=16 else lo,-257,-256,-255,-128,-127,-16,-3,-2,-1,0,1,2,3,15,16,127,128,255,256,257,hi-1,hi]))

def cases(bits,seed):
 e=[x for x in edges(bits) if -(1<<(bits-1))<=x<(1<<(bits-1))]
 out=[(n,d) for n in e for d in e]
 rng=random.Random(seed);lo=-(1<<(bits-1));hi=1<<(bits-1)
 out += [(rng.randrange(lo,hi),rng.randrange(lo,hi)) for _ in range(16000)]
 # explicit q=0/q=1 distributions by magnitude
 for _ in range(4000):
  dmag=rng.randrange(1,1<<(bits-1))
  q=rng.randrange(2)
  rem=rng.randrange(dmag)
  nmag=q*dmag+rem
  if nmag < (1<<(bits-1)):
   n=nmag if rng.randrange(2)==0 else -nmag
   d=dmag if rng.randrange(2)==0 else -dmag
   out.append((n,d))
 out += [(rng.randrange(lo,hi),0) for _ in range(256)]
 return out

def expected(n,d):
 if d==0:return 0,1
 mag=abs(n)%abs(d);return (-mag if n<0 else mag),0

def run(c,entry,cs,bits,nbytes):
 tot=0;mn=10**9;mx=0;err=0
 for n,d in cs:
  un=enc(n,bits);ud=enc(d,bits);wr(c.mem,N,un,nbytes);wr(c.mem,D,ud,nbytes)
  bn=bytes(c.mem[N:N+nbytes]);bd=bytes(c.mem[D:D+nbytes])
  cy=c.call(entry,5_000_000);got=dec(rd(c.mem,R,nbytes),bits);exp,ec=expected(n,d)
  if got!=exp or c.c!=ec or bytes(c.mem[N:N+nbytes])!=bn or bytes(c.mem[D:D+nbytes])!=bd:
   err+=1
   if err<=4:print('ERROR',hex(entry),n,d,'got',got,c.c,'exp',exp,ec)
  tot+=cy;mn=min(mn,cy);mx=max(mx,cy)
 return dict(cases=len(cs),errors=err,mean_cycles=tot/len(cs),min_cycles=mn,max_cycles=mx)

out={'status':'PASS','profiles':{}}
for pi,p in enumerate(PROFILES):
 base,BA=cpu_for(p,'baseline');ref,RA=cpu_for(p,'reference');alt,AA=cpu_for(p,'alternate');pr={}
 for ri,(name,bits,nbytes) in enumerate(ROUTINES):
  cs=cases(bits,0x534D0000+pi*0x1000+ri)
  b=run(base,BA[name],cs,bits,nbytes);n=run(ref,RA[name],cs,bits,nbytes);a=run(alt,AA[name],cs,bits,nbytes)
  if b['errors'] or n['errors'] or a['errors']:raise AssertionError((p,name,b,n,a))
  n['delta_vs_baseline']=n['mean_cycles']-b['mean_cycles'];a['delta_vs_baseline']=a['mean_cycles']-b['mean_cycles']
  pr[name]={'baseline':b,'reference':n,'alternate':a}
  print(p,name,'PASS',len(cs),f"baseline={b['mean_cycles']:.6f}",f"new={n['mean_cycles']:.6f}",f"delta={n['delta_vs_baseline']:.6f}",f"range={n['min_cycles']}-{n['max_cycles']}",flush=True)
 out['profiles'][p]=pr
path=ROOT/'validation/review/SIGNED_REMAINDER_SOURCE_AB.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n')
print('SIGNED REMAINDER SOURCE A/B PASS')
