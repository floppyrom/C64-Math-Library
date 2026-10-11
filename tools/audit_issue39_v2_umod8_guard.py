#!/usr/bin/env python3
"""Exact full-domain old/new V2 UMOD8 public ABI and cycle certificate.

All 65,536 N,D pairs; 131,072 calls, mathematical oracle + preserved Q,
input bytes and high sentinels. Parent SHA must be exactly merged PR63 V2.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from mini6502 import CPU
from validate_unsigned_division import expected,api
OLD_SHA='e1e828a2748099b6f05b224b98ca26960d120f8ba886c4906e8b52bdb8b4fbcd'
NEW_SHA='2df096598ae5f046272472f08add0ade079a8a16ab43dc7b6cdd41aea7e80dad'
V5_SHA='bed1ee986857d045d452036d78d0d6cbdc078dbc3407f8a860a8fd54f8395fa2'
P=R/'v2_pareto_fast/resident/math_v2_pareto_fast_game_math.prg'
OUT=R/'validation/review/ISSUE39_V2_UMOD8_D32_EXHAUSTIVE.json'
image=P.read_bytes();lo=int.from_bytes(image[:2],'little')
assert lo==0x1000 and len(image)==49042
assert hashlib.sha256(image).hexdigest()==NEW_SHA
o=lambda x:2+x-lo
assert image[o(0x3200):o(0x3203)]==bytes.fromhex('4c001e')
assert image[o(0x1e00):o(0x1e05)]==bytes.fromhex('ad14c0c920')
assert image[o(0x1e4d):o(0x1e80)]==bytes(0x80-0x4d)
prior=bytearray(image)
prior[o(0x3200):o(0x3203)]=bytes.fromhex('ad10c0')
prior[o(0x1e00):o(0x1e80)]=bytes(0x80)
assert hashlib.sha256(prior).hexdigest()==OLD_SHA
assert hashlib.sha256((R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg').read_bytes()).hexdigest()==V5_SHA
cpus=[]
for blob in (prior,image):
 mem=bytearray(65536);mem[lo:lo+len(blob)-2]=blob[2:]
 cpu=CPU(mem);cpu.d=0;cpu.call(0x3280,2000000);cpus.append(cpu)
j={'status':'PASS','profile':'v2_pareto_fast','guard_minimum_divisor':32,
 'new_code_bytes':77,'normal_zp_growth':0,'public_abi_changed':False,
 'v5_resident_sha256_unchanged':V5_SHA,'parent_sha256':OLD_SHA,
 'candidate_sha256':NEW_SHA,'input_pairs':0,'paired_cpu_calls':0,
 'old_total_cycles':0,'new_total_cycles':0,'faster':0,'equal':0,'slower':0,
 'qualified_slower':0,'fallback_slower':0,'worst_regression_cycles':0,
 'worst_speedup_cycles':0,'cycle_sha256_old':'','cycle_sha256_new':''}
hashes=[hashlib.sha256(),hashlib.sha256()];entry=api('v2_pareto_fast')['MATH_UMOD8']
for n in range(256):
 for d in range(256):
  observations=[]
  for i,cpu in enumerate(cpus):
   m=cpu.mem;m[0xc010]=n;m[0xc014]=d
   m[0xc011]=0xB5;m[0xc015]=0xA9
   m[0xc018:0xc01c]=bytes.fromhex('a65b7cd2')
   m[0xc01d:0xc020]=bytes.fromhex('3e4f71')
   cycles=cpu.call(entry,100000)
   hashes[i].update(cycles.to_bytes(2,'little'))
   observations.append((cycles,m[0xc01c],cpu.c,tuple(m[0xc018:0xc01c]),
                        tuple(m[0xc01d:0xc020]),tuple(m[0xc010:0xc012]),
                        tuple(m[0xc014:0xc016])))
  _,r,c=expected(n,d,8,8)
  want=(r,c,(0xa6,0x5b,0x7c,0xd2),(0x3e,0x4f,0x71),(n,0xb5),(d,0xa9))
  assert observations[0][1:]==observations[1][1:]==want,(n,d,observations,want)
  delta=observations[1][0]-observations[0][0]
  j['input_pairs']+=1;j['paired_cpu_calls']+=2
  j['old_total_cycles']+=observations[0][0];j['new_total_cycles']+=observations[1][0]
  j['faster' if delta<0 else 'equal' if delta==0 else 'slower']+=1
  j['worst_regression_cycles']=max(j['worst_regression_cycles'],delta)
  j['worst_speedup_cycles']=max(j['worst_speedup_cycles'],-delta)
  if d>=32:
   j['qualified_slower']+=delta>0
   assert delta<=0,(n,d,delta)
  else:
   j['fallback_slower']+=delta>0
   assert delta==14,(n,d,delta)
assert j['input_pairs']==65536 and j['paired_cpu_calls']==131072
assert (j['faster'],j['equal'],j['slower'])==(57060,284,8192),j
assert (j['qualified_slower'],j['fallback_slower'],j['worst_regression_cycles'])==(0,8192,14)
assert (j['old_total_cycles'],j['new_total_cycles'])==(4247988,3462647)
j['old_mean_cycles']=j['old_total_cycles']/65536
j['new_mean_cycles']=j['new_total_cycles']/65536
j['cycle_sha256_old'],j['cycle_sha256_new']=(z.hexdigest() for z in hashes)
OUT.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
print('V2 UMOD8 GUARDED EXHAUSTIVE PASS',j['paired_cpu_calls'],j['old_mean_cycles'],j['new_mean_cycles'])
