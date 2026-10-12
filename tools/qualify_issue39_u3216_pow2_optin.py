#!/usr/bin/env python3
"""Issue39: SHA-pinned five-profile 32/16 power-of-two caller-opt-in A/B.

This specialist has a strict D=2^k, 0<=k<=15 precondition, and never
patches a public entry or resident. Both UDIV32/16 and UMOD32/16 produce
the same Q32/R16/C result. Cycle figures exclude REU/VIC contention.
"""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,wr,rd,expected
SRC=ROOT/'routines/standalone_lab/library_dependent/div_u32_u16_pow2_optin.asm'
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
MAPS=(0x0800,0x0B00)
def corpus():
 rng=random.Random(0xC6392A22)
 groups=defaultdict(list)
 for x in range(16):
  d=1<<x
  for n in (0,1,2,3,d-1,d,d+1,2*d-1,2*d,2*d+1,65535,65536,65537,
            0xfffffe,0xffffff,0x1000000,0x7fffffff,0x80000000,0xffffffff):
   groups[f'exp_{x:02d}_edge'].append((n&0xffffffff,d))
  for _ in range(128):
   groups[f'exp_{x:02d}_uniform'].append((rng.getrandbits(32),d))
  for _ in range(64):
   groups[f'exp_{x:02d}_n16'].append((rng.getrandbits(16),d))
 return groups
def call(cpu,entry,n,d):
 m=cpu.mem
 wr(m,0xc010,n,4);wr(m,0xc014,d,2)
 m[0xc016]=0xa7;m[0xc017]=0x39;m[0xc020]=0x42
 wr(m,0xc018,0x4ca9d178,4);wr(m,0xc01c,0x67bcfd91,4)
 cpu.d=0;cpu.c=1;sp=cpu.sp
 ticks=cpu.call(entry,4_000_000)
 q,r,c=expected(n,d,32,16)
 state=(rd(m,0xc018,4),rd(m,0xc01c,4),cpu.c,rd(m,0xc010,4),
       rd(m,0xc014,2),m[0xc016],m[0xc017],m[0xc020],cpu.sp)
 assert state[0]==q and state[1]&65535==r and state[2]==c,(hex(entry),n,d,state,(q,r,c))
 assert state[3:]==(n,d,0xa7,0x39,0x42,sp),(n,d,state,'state corruption')
 return ticks,state
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);args=p.parse_args()
 published=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 groups=corpus();count=sum(len(v) for v in groups.values())
 assert count==3376
 report={'status':'PASS_OPTIN_NOT_DEFAULT','source':str(SRC.relative_to(ROOT)),
   'reproducer':'tools/qualify_issue39_u3216_pow2_optin.py',
   'precondition':'D16 is exactly 2^k for k in 0..15; no divide-by-zero coverage',
   'profile_count':5,'resident_changed':False,'public_entries_patched':False,
   'native_vice_calls':0,'normal_zp_growth':0,'nested_stack_growth':0,
   'cycle_basis':'6502 instruction cycles, excludes real VIC/REU contention',
   'origin_maps':['0x800','0xb00'],'pairs':0,'cpu_calls':0,'profiles':{}}
 for profile in PROFILES:
  path=ROOT/profile/'resident'/f'math_{profile}_game_math.prg'
  sha=hashlib.sha256(path.read_bytes()).hexdigest()
  assert published['reference_prg_sha256'][profile]==sha,(profile,'wrong resident SHA')
  entry={'resident_sha256':sha,'maps':{}}
  for location in MAPS:
   source=SRC.read_text().replace('* = $0800','* = $'+format(location,'04X'))
   code,labels,_=Assembler().assemble(source)
   assert len(code)==114 and labels['U3216_POW2_OPTIN']==location
   old,old_api=load(profile);new,new_api=load(profile)
   assert old_api==new_api
   assert all(new.mem[address]==0 for address in code),(profile,location,'occupied RAM')
   for address,value in code.items():new.mem[address]=value
   data={}
   for op in OPS:
    by_group={};tot=[]
    for group,vec in groups.items():
     deltas=[];pairs=hashlib.sha256();times=hashlib.sha256()
     for n,d in vec:
      pairs.update(n.to_bytes(4,'little')+d.to_bytes(2,'little'))
      t0,o0=call(old,old_api[op],n,d)
      t1,o1=call(new,location,n,d)
      assert o0==o1,(profile,location,op,group,n,d,o0,o1)
      deltas.append(t1-t0);tot.append(t1-t0)
      times.update(t0.to_bytes(4,'little')+t1.to_bytes(4,'little'))
      report['pairs']+=1;report['cpu_calls']+=2
     by_group[group]={'cases':len(deltas),'delta_mean':sum(deltas)/len(deltas),
       'faster':sum(x<0 for x in deltas),'slower':sum(x>0 for x in deltas),
       'equal':sum(x==0 for x in deltas),'max_regression':max(deltas),
       'max_gain':-min(deltas),'pair_sha256':pairs.hexdigest(),
       'cycle_pair_sha256':times.hexdigest()}
    data[op]={'groups':by_group,'summary':{'cases':len(tot),
      'delta_mean':sum(tot)/len(tot),'faster':sum(x<0 for x in tot),
      'slower':sum(x>0 for x in tot),'equal':sum(x==0 for x in tot),
      'max_regression':max(tot),'max_gain':-min(tot)}}
   entry['maps'][hex(location)]=data
   report['code_bytes']=len(code)
   print(profile,hex(location),*[round(data[op]['summary']['delta_mean'],3) for op in OPS],flush=True)
  assert entry['maps']['0x800']==entry['maps']['0xb00'],('location changed cycles',profile)
  report['profiles'][profile]=entry
 assert report['pairs']==67520 and report['cpu_calls']==135040
 assert report['code_bytes']==114
 if args.out:
  args.out.parent.mkdir(parents=True,exist_ok=True)
  args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('ISSUE39 POW2 OPT-IN PASS',report['pairs'],report['cpu_calls'],flush=True)
if __name__=='__main__':main()
