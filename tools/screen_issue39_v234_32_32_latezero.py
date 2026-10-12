#!/usr/bin/env python3
"""Issue39: paired old/new V2–V4 UDIV32_32 and UMOD32_32 late-zero guard.

Complete residents + REU-loaded CPU; modifies only an ephemeral candidate
memory image. Every call sees the exact public ABI, including Q/R/C and N/D.
Do not publish changed binaries from this screen.
"""
from __future__ import annotations
from pathlib import Path
import json,hashlib,random,sys
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import load,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus,band
PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')
OPS=(('MATH_UDIV32_32',2048),('MATH_UMOD32_32',1024))
OLD_PROLOGUE=bytes.fromhex('ad14c00d15c00d16c00d17c0f0')
NEW_PROLOGUE=bytes.fromhex('ad13c0cd17c090')
OUT=ROOT/'validation/review/ISSUE39_V234_32_32_LATEZERO_PAIRED.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 result={'status':'PASS','scope':'research source-generated V2-V4 reference images, not shipped',
   'idea':'defer 32-bit divisor-zero OR gate until the n=d equality path; n<d proves nonzero d',
   'profiles':{},'total_public_old_new_calls':0,
   'reference_and_alternate_builds_required':True,
   'excluded_profiles':['v1_balanced','v5_hybrid_lowzp']}
 for p in PROFILES:
  path=ROOT/p/'resident'/f'math_{p}_game_math.prg'
  old=path.read_bytes()
  source=ROOT/'build_source/reference'/p/f'math_{p}_source_built.prg'
  candidate=source.read_bytes()
  assert old[:2]==candidate[:2] and len(old)==len(candidate)
  a=old.find(OLD_PROLOGUE);b=candidate.find(NEW_PROLOGUE)
  assert a>=0 and b>=0,(p,'unexpected source prologue')
  start_old=a-2+int.from_bytes(old[:2],'little')
  start_new=b-2+int.from_bytes(candidate[:2],'little')
  assert start_old==start_new,(p,'gate changed position',start_old,start_new)
  lo=int.from_bytes(old[:2],'little')
  diff=[i for i,(x,y) in enumerate(zip(old,candidate)) if x!=y]
  assert all(a<=i<a+160 for i in diff),(p,'unexpected binary changes outside gate',
    [(hex(i-2+lo),old[i],candidate[i]) for i in diff if not a<=i<a+160][:15])
  assert diff,('expected binary change',p)
  alt=ROOT/'build_source/alternate'/p/f'math_{p}_source_built.prg'
  assert alt.exists() and alt.stat().st_size>10000,(p,'alternate source')
  oldcpu,entry=load(p);newcpu,newentry=load(p)
  assert entry==newentry
  newcpu.mem[lo:lo+len(candidate)-2]=candidate[2:]
  pro={'old_resident_sha256':sha(old),'candidate_source_sha256':sha(candidate),
    'old_gate_address':hex(start_old),'new_gate_address':hex(start_new),
    'changed_binary_bytes':len(diff),'resident_size_growth':0,
    'normal_zp_growth':0,'public_entry_points_unchanged':True,'routines':{}}
  for op,count in OPS:
   _,common=corpus(op,32,32,0,count)
   cases=[(n,d) for n,d,_ in common]
   rng=random.Random(0x39000000+PROFILES.index(p)*257+count)
   # D=0 with both n=0 and n!=0, q=1, q>=256, q0 near D boundary.
   # Additional deterministic quotient and divide-by-zero boundary cases.
   cases.extend((x,0) for x in [0,1,2,255,65535,0x80000000,0xffffffff])
   cases.extend((d,d) for d in [0,1,2,3,7,255,256,65535,0x7fffffff,0x80000000,0xffffffff])
   for _ in range(256):
    d=rng.randrange(1<<32)
    cases.append((d,d))
    n=rng.randrange(1<<32)
    cases.append((n,d))
   cycles=[0,0];groups=defaultdict(list);stats=Counter();mismatches=[]
   for n,d in cases:
    q,r,c=expected(n,d,32,32)
    obs=[]
    for cpu in (oldcpu,newcpu):
     wr(cpu.mem,0xC010,n,4);wr(cpu.mem,0xC014,d,4)
     cpu.mem[0xC030]=0xA5
     cc=cpu.call(entry[op],4_000_000)
     z=(rd(cpu.mem,0xC018,4),rd(cpu.mem,0xC01C,4),cpu.c,rd(cpu.mem,0xC010,4),rd(cpu.mem,0xC014,4),cpu.mem[0xC030])
     obs.append((cc,z))
    expected_state=(q,r,c,n,d,0xA5)
    if obs[0][1]!=expected_state or obs[1][1]!=expected_state:
     if len(mismatches)<5:mismatches.append({'n':hex(n),'d':hex(d),'expected':expected_state,'before':obs[0],'after':obs[1]})
    dt=obs[1][0]-obs[0][0]
    cycles[0]+=obs[0][0];cycles[1]+=obs[1][0]
    stats['faster' if dt<0 else 'equal' if dt==0 else 'slower']+=1
    groups[band(n,d,0)].append(dt)
   assert not mismatches,(p,op,mismatches)
   m=len(cases)
   pro['routines'][op]={
    'paired_cases':m,'official_case_count':len(common),
    'mean_old':cycles[0]/m,'mean_candidate':cycles[1]/m,
    'mean_saving':(cycles[0]-cycles[1])/m,
    'faster':stats['faster'],'equal':stats['equal'],'slower':stats['slower'],
    'classes':{k:{'cases':len(v),'mean_saving':-sum(v)/len(v),'worst_regression':max(v)} for k,v in groups.items()},
    'arithmetic_or_abi_failures':0}
   result['total_public_old_new_calls']+=2*m
   print(p,op,m,'old',f'{cycles[0]/m:.3f}','new',f'{cycles[1]/m:.3f}',
    'fast/tie/slow',stats['faster'],stats['equal'],stats['slower'],flush=True)
  result['profiles'][p]=pro
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('ISSUE39 32/32 V2-V4 LATE DZERO SOURCE SCREEN PASS',result['total_public_old_new_calls'])
if __name__=='__main__':main()
