#!/usr/bin/env python3
"""Issue144 C: four-profile unrestricted ISQRT32 highword direct-seed same-input screen."""
from __future__ import annotations
from pathlib import Path
import sys,math,json,hashlib,statistics
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from issue144_isqrt32_highword_direct_experiment import build,PROFILES
from validate_unsigned_division import load,wr,rd

MASK=(1<<64)-1

def splitmix64(x):
 x=(x+0x9E3779B97F4A7C15)&MASK;z=x;z=(z^(z>>30))*0xBF58476D1CE4E5B9&MASK;z=(z^(z>>27))*0x94D049BB133111EB&MASK
 return x,(z^(z>>31))&MASK

def corpus():
 x=0x5A7E3200;data=[]
 for _ in range(4096):
  x,a=splitmix64(x);x,b=splitmix64(x);data.append(a&0xffffffff)
 data += [0,1,2,3,7,15,16,31,127,128,255,256,257,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffff,0x800000,0xffffff,0x1000000,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
 data += [(v*v)&0xffffffff for v in (0,1,2,3,255,256,257,65535)]
 assert len(data)==4130
 return data

def metrics(a):
 b=sorted(a);return {'mean_cycles':statistics.mean(a),'median_cycles':statistics.median(a),'p95_cycles':b[int((len(b)-1)*.95)],'minimum':b[0],'maximum':b[-1],'cycle_vector_sha256':hashlib.sha256(b''.join(int(x).to_bytes(4,'little',signed=True) for x in a)).hexdigest()}

def model(p,values):
 asm,code=build(p)
 baseline,api=load(p);special,_=load(p)
 orig_entry=bytes(special.mem[0x5e30:0x5e33]);assert orig_entry[0]==0x4c
 for k,v in code.items():
  assert special.mem[k]==0
  special.mem[k]=v
 special.mem[0x5e31:0x5e33]=b'\x00\x0c'
 old=[];new=[];xy=[]
 for i,n in enumerate(values):
  for cpu in (baseline,special):wr(cpu.mem,0xC010,n,4)
  cycles_old=baseline.call(api['MATH_ISQRT32'],1000000)
  cycles_new=special.call(api['MATH_ISQRT32'],1000000)
  target=math.isqrt(n)
  assert rd(baseline.mem,0xc008,2)==rd(special.mem,0xc008,2)==target,(p,i,'root')
  assert baseline.c==special.c==0,(p,i,'carry')
  assert rd(special.mem,0xc010,4)==rd(baseline.mem,0xc010,4)==n,(p,i,'input')
  assert baseline.sp==special.sp,(p,i,'sp')
  assert baseline.x==special.x and baseline.y==special.y,(p,i,'xy',baseline.x,special.x,baseline.y,special.y)
  old.append(cycles_old);new.append(cycles_new)
  if i%193==0:
   # Interleave another public API with current initialized resident tables.
   q=(n+0x1edcba)&0xffff
   for cpu in (baseline,special):
    wr(cpu.mem,0xC010,q,4)
    cycles=cpu.call(api['MATH_ISQRT16'],100000)
    assert rd(cpu.mem,0xC008,2)==math.isqrt(q)
 assert all(a>b for a,b in zip(old,new))
 gains=[a-b for a,b in zip(old,new)]
 special.mem[0x5e30:0x5e33]=orig_entry
 for n in values[:48]:
  wr(special.mem,0xC010,n,4)
  special.call(api['MATH_ISQRT32'],1000000)
  assert rd(special.mem,0xC008,2)==math.isqrt(n)
 return {'status':'PASS_PUBLIC_ENTRY_ALL_DOMAIN_INPUT_CARRY_X_Y_SP', 'cases':len(values), 'stock':metrics(old),'specialist':metrics(new),'paired_savings':metrics(gains),'program_bytes':len(code),'source_sha256':hashlib.sha256(asm.encode()).hexdigest(),'mixed_ISQRT16_interleaved':True,'original_public_entry_restored':True}

def main():
 values=corpus();result={'status':'PASS_UNRESTRICTED_ISQRT32_DIRECT_HIGHWORD_SEED_CPU_MODEL','cases_per_profile':4130,'corpus_sha256':hashlib.sha256(b''.join(n.to_bytes(4,'little') for n in values)).hexdigest(),'profiles':{},'regular_PRG_REU_modified':False}
 for p in PROFILES:
  item=model(p,values);result['profiles'][p]=item
  print('DIRECT ISQRT32',p,'saved',item['paired_savings']['mean_cycles'],'PASS',flush=True)
 dest=ROOT/'validation/review/ISSUE144_ISQRT32_DIRECT_HIGHWORD_SEED_MODEL.json';dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('PASS',4130*len(PROFILES))
if __name__=='__main__':main()
