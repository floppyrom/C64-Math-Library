#!/usr/bin/env python3
from pathlib import Path
import json,math,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

PROFILE='v4_reu_16m'
PUB=0x5E30; INIT=0x3280; IO_N=0xC010; IO_Z=0xC008; MASK32=(1<<32)-1

def splitmix64(x):
 x=(x+0x9E3779B97F4A7C15)&((1<<64)-1);z=x
 z=(z^(z>>30))*0xBF58476D1CE4E5B9&((1<<64)-1)
 z=(z^(z>>27))*0x94D049BB133111EB&((1<<64)-1)
 return x,(z^(z>>31))&((1<<64)-1)

def pairs(count,seed):
 x=seed
 for _ in range(count):
  x,a=splitmix64(x);x,b=splitmix64(x);yield a&0xffffffff,b&0xffffffff

edge=[0,1,2,3,7,15,16,31,127,128,255,256,257,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffff,0x800000,0xffffff,0x1000000,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
CASES=[a for a,b in pairs(4096,0x5A7E3200)]+edge+[x*x&MASK32 for x in [0,1,2,3,255,256,257,65535]]
assert len(CASES)==4130

def parse_api(path):
 out={}
 for line in path.read_text().splitlines():
  m=re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
  if m:out[m.group(1)]=int(m.group(2),16)
 return out

def load_prg(path):
 b=path.read_bytes();lo=b[0]|b[1]<<8;m=bytearray(65536);m[lo:lo+len(b)-2]=b[2:];return m

def load(kind):
 if kind=='baseline':
  prg=ROOT/'v4_reu_16m/resident/math_v4_reu_16m_game_math.prg'
  reu=ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'
  api={'MATH_INIT':INIT,'MATH_ISQRT32':PUB,'MATH_N':IO_N,'MATH_Z':IO_Z}
 else:
  d=ROOT/'build_source'/kind/PROFILE
  prg=d/f'math_{PROFILE}_source_built.prg'
  reu=d/f'c64_math_{PROFILE}_source_built.reu'
  api=parse_api(d/'math_api.inc')
 c=CPU(load_prg(prg),reu=bytearray(reu.read_bytes()));c.d=0;c.call(api['MATH_INIT'],3_000_000)
 return c,api

def wr(c,a,v,n):
 for i in range(n):c.mem[a+i]=(v>>(8*i))&255

def rd(c,a,n):return sum(c.mem[a+i]<<(8*i) for i in range(n))

def run(kind):
 c,A=load(kind);vec=[];err=0
 io_n=A['MATH_N'];io_z=A['MATH_Z']
 for n in CASES:
  wr(c,io_n,n,4);before=bytes(c.mem[io_n:io_n+4])
  cy=c.call(A['MATH_ISQRT32'],2_000_000);got=rd(c,io_z,2)
  if got!=math.isqrt(n) or bytes(c.mem[io_n:io_n+4])!=before or c.c!=0:
   err+=1
   if err<=5:print('ERROR',kind,hex(n),got,math.isqrt(n),c.c)
  vec.append(cy)
 return {'cases':len(vec),'errors':err,'mean_cycles':sum(vec)/len(vec),'min_cycles':min(vec),'max_cycles':max(vec),'cycles':vec}

base=run('baseline');ref=run('reference');alt=run('alternate')
if base['errors'] or ref['errors'] or alt['errors']:raise AssertionError((base,ref,alt))
print('baseline',base['mean_cycles'],base['min_cycles'],base['max_cycles'])
print('reference',ref['mean_cycles'],ref['min_cycles'],ref['max_cycles'],'delta',ref['mean_cycles']-base['mean_cycles'])
print('alternate',alt['mean_cycles'],alt['min_cycles'],alt['max_cycles'],'delta',alt['mean_cycles']-base['mean_cycles'])
out={'status':'PASS','corpus':'same 4,130-case deterministic ISQRT32 corpus',
     'baseline':{k:v for k,v in base.items() if k!='cycles'},
     'reference':{k:v for k,v in ref.items() if k!='cycles'},
     'alternate':{k:v for k,v in alt.items() if k!='cycles'}}
path=ROOT/'validation/review/ISQRT32_REU_PREFIX_AB.json'
path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n')
print('ISQRT32 REU PREFIX A/B PASS')
