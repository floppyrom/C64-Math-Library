#!/usr/bin/env python3
"""Issue39: full-resident UDIV24/UMOD24 vs existing 24/8 RAM-SMC opt-in.

Strict input precondition: N2>0, D1=D2=0, 1<=D0<=255.
Self-modifying RAM code is caller-owned, non-reentrant and not ROM-safe.
No public entry or resident source is modified; 6502 instruction cycles only.
"""
from pathlib import Path
import argparse,hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'routines/standalone_lab/portable'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,wr,rd,expected
from verify import render
SOURCE=ROOT/'routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm'
OPS=('MATH_UDIV24','MATH_UMOD24')
MAPS={'ram_0800':0x0800,'ram_0851':0x0851}
N,D,Q,R=0xc010,0xc014,0xc018,0xc01c
def cases():
 rng=random.Random(0xC6392483)
 groups={
  'uniform_24_d8':[(rng.randrange(1<<16,1<<24),rng.randrange(1,256)) for _ in range(2048)],
  'tiny_d1to7':[(rng.randrange(1<<16,1<<24),rng.randrange(1,8)) for _ in range(256)],
  'pow2_d8':[(rng.randrange(1<<16,1<<24),1<<rng.randrange(8)) for _ in range(256)],
  'n_high_ff':[(rng.randrange(0xff0000,1<<24),rng.randrange(1,256)) for _ in range(256)],
  'd255':[(rng.randrange(1<<16,1<<24),255) for _ in range(256)]}
 edges=[]
 for d in (1,2,3,4,7,15,16,31,63,64,127,128,255):
  for n in (0x10000,0x10001,0x100ff,0x10100,0x1ffff,0x20000,0x3ffff,
            0x7ffff,0xfffff,0x100000,0x7fffff,0x800000,0xfffffe,0xffffff):
   edges.append((n,d))
 groups['structured_edges']=edges
 assert all(0x10000<=n<=0xffffff and 1<=d<=255 for g in groups.values() for n,d in g)
 return groups
def call(cpu,entry,n,d,rem_only):
 m=cpu.mem
 wr(m,N,n,3);wr(m,D,d,3)
 m[0xc013]=0x4a;m[0xc017]=0x5a
 wr(m,Q,0xA7CB5913,4);wr(m,R,0xE56A9284,4)
 m[0xc022]=0xac;m[0x0430]=0x61
 cpu.d=0;cpu.c=1;sp=cpu.sp
 cycles=cpu.call(entry,4_000_000)
 q,r,c=expected(n,d,24,24)
 state=(rd(m,Q,3),rd(m,R,3),cpu.c,rd(m,N,3),rd(m,D,3),
        m[0xc013],m[0xc017],m[0xc01b],m[0xc01f],m[0xc022],m[0x0430],cpu.sp)
 assert (state[1],state[2])==(r,c),(hex(entry),hex(n),d,'R/C',state,(q,r,c))
 assert rem_only or state[0]==q,(hex(entry),hex(n),d,'Q',state,q)
 assert state[3:]==(n,d,0x4a,0x5a,0xa7,0xe5,0xac,0x61,sp),(hex(entry),hex(n),d,'ABI',state)
 return cycles,state
def run(profile=None,location=None):
 ps=[profile] if profile else PROFILES
 maps={k:v for k,v in MAPS.items() if location is None or k==location}
 groups=cases()
 status=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 r={'status':'PASS_OPTIN_ONLY','source':str(SOURCE.relative_to(ROOT)),
    'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'precondition':'N24>=65536; D24=1..255 (high divisor bytes zero)',
    'caller_owns_ram_and_smc':True,'public_entries_patched':False,
    'resident_changed':False,'native_vice_calls':0,
    'paired_cases':0,'cpu_calls':0,
    'profiles':{},'classes':{k:{'cases':len(v),
       'operand_sha256':hashlib.sha256(b''.join(n.to_bytes(3,'little')+d.to_bytes(3,'little') for n,d in v)).hexdigest()}
       for k,v in groups.items()}}
 for p in ps:
  path=ROOT/p/'resident'/f'math_{p}_game_math.prg'
  sha=hashlib.sha256(path.read_bytes()).hexdigest()
  assert sha==status['reference_prg_sha256'][p],(p,sha,'resident mismatch')
  out={'resident_sha256':sha,'maps':{}}
  for map_name,origin in maps.items():
   asm=render(SOURCE.name,{'KERNEL_CODE':origin})
   code,labels,_=Assembler().assemble(asm)
   assert len(code)<96 and labels['FAST_UDIV24_BY8_RAM_SMC']==origin
   assert all(0x0800<=adr<0x1000 for adr in code)
   old,entries=load(p);new,entries2=load(p)
   assert entries==entries2 and all(new.mem[adr]==0 for adr in code)
   for adr,value in code.items():new.mem[adr]=value
   mr={'code_bytes':len(code),'normal_zp_bytes':0,'self_modifying_code_bytes':2,
       'maps_require_writable_executable_ram':True,'operations':{}}
   for op in OPS:
    mr['operations'][op]={}
    for kind,inputs in groups.items():
     total0=total1=fast=slow=eq=qdif=0;max_slow=-10**9
     digest=hashlib.sha256()
     for n,d in inputs:
      t0,a=call(old,entries[op],n,d,op=='MATH_UMOD24' and p!='v1_balanced')
      t1,b=call(new,origin,n,d,op=='MATH_UMOD24' and p!='v1_balanced')
      assert a[1:]==b[1:],(p,op,map_name,n,d,a,b)
      if op=='MATH_UDIV24' or p=='v1_balanced':
       assert a[0]==b[0],(p,op,map_name,n,d,a[0],b[0])
      qdif+=a[0]!=b[0]
      total0+=t0;total1+=t1
      delta=t1-t0
      fast+=delta<0;slow+=delta>0;eq+=delta==0;max_slow=max(max_slow,delta)
      digest.update(t0.to_bytes(4,'little')+t1.to_bytes(4,'little'))
      r['paired_cases']+=1;r['cpu_calls']+=2
     mr['operations'][op][kind]={
       'cases':len(inputs),'public_mean':total0/len(inputs),
       'optin_mean':total1/len(inputs),'mean_delta':(total1-total0)/len(inputs),
       'faster':fast,'slower':slow,'equal':eq,'worst_regression':max_slow,
       'q_side_effect_differences':qdif,'paired_cycle_sha256':digest.hexdigest()}
    print(p,map_name,op,'uniform delta',round(mr['operations'][op]['uniform_24_d8']['mean_delta'],3),
          'small D1..7 delta',round(mr['operations'][op]['tiny_d1to7']['mean_delta'],3),flush=True)
   out['maps'][map_name]=mr
  r['profiles'][p]=out
 assert r['paired_cases']>0 and r['cpu_calls']==2*r['paired_cases']
 return r
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--profile',choices=PROFILES)
 ap.add_argument('--map',choices=list(MAPS))
 ap.add_argument('--out',type=Path)
 a=ap.parse_args()
 data=run(a.profile,a.map)
 if a.out:
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 24BY8 SMC CURRENT RESIDENT OPTIN PASS',data['paired_cases'],data['cpu_calls'],flush=True)
if __name__=='__main__':main()
