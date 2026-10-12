#!/usr/bin/env python3
"""Issue39 V1 UMOD16: reject apparent remainder-only q=0 generator advantage.

Screen a *hand-written* public-address q=0 front end in RAM, never modify the
shipped resident or source. Compare loose R-only behavior with exact V1
UDIV16/UMOD16-alias behavior including Q output, carry, N/D, sentinel storage.
The purpose is a reproducible ABI-qualified *negative* result, not a release.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from validate_unsigned_division import load,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus,band
from audit_issue39_unsigned_small_workloads import pairs,KINDS
OLD_SHA='cae2afdf0271da338d110f2104a8530374214ef915d88a803c508bce9679bb4f'
MOD_API=0x3220
DIV_API=0x3140
GATE=0x1E80
# Both original experimental layout variants come from a manual branch design,
# not an OptiSearch binary. Both skip the core for q=0 and tail-jump to the
# original V1 quotient-producing core for q>=1. In the loose case Q is OMITTED.
LOOSE=bytes.fromhex(
 'af11c0 cd15c0 9010 d00b ad10c0 cd14c0 9006 4c1c42 4c5242'
 ' ad10c0 8d1cc0 8e1dc0 60'
)
STRICT=bytes.fromhex(
 'af11c0 cd15c0 9010 d00b ad10c0 cd14c0 9006 4c1c42 4c5242'
 ' ad10c0 8d1cc0 8e1dc0 a900 8d18c0 8d19c0 60'
)
assert len(LOOSE)==34 and len(STRICT)==42
N,D,Q,R=0xC010,0xC014,0xC018,0xC01C
P=ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg'
OUT=ROOT/'validation/review/ISSUE39_V1_UMOD16_Q0_FASTPATH_REJECTED.json'

def sha(x):return hashlib.sha256(x).hexdigest()
def make_machines():
 raw=P.read_bytes()
 assert sha(raw)==OLD_SHA,('baseline moved; rerun investigation',sha(raw))
 base,entries=load('v1_balanced')
 assert entries['MATH_UMOD16']==MOD_API and entries['MATH_UDIV16']==DIV_API
 assert bytes(base.mem[MOD_API:MOD_API+3])==bytes.fromhex('4c0042')
 assert bytes(base.mem[GATE:GATE+42])==bytes(42),'candidate code island not unused'
 result=[base]
 for code in (LOOSE,STRICT):
  m=bytearray(base.mem)
  m[MOD_API:MOD_API+3]=bytes.fromhex('4c801e')
  m[GATE:GATE+len(code)]=code
  c=CPU(m);c.d=0;result.append(c)
 return result

def main():
 cpus=make_machines()
 _,official=corpus('MATH_UMOD16',16,16,0,1024)
 assert len(official)==1705
 groups={'official_shared_1705':[(n,d) for n,d,_ in official]}
 for kind in KINDS:groups[kind]=pairs(16,kind)
 assert all(len(groups[k])==256 for k in KINDS)
 result={'status':'REJECT','date':'2026-10-12','profile':'v1_balanced',
  'operation':'MATH_UMOD16','resident_sha256':OLD_SHA,
  'candidate_kind':'hand-written, in-memory low-quotient bypass inspired by Repose UMOD16; not a copied OptiSearch binary',
  'loose_bytes':len(LOOSE),'strict_bytes':len(STRICT),
  'affected_public_entry':'0x3220','ephemeral_code_origin':'0x1e80',
  'resident_files_modified':False,'stable_api_changed':False,
  'rationale':'V1 UMOD16 historically aliases UDIV16 and writes both Q16 and R16; a bare remainder-only fast path loses the Q16 side effect',
  'workloads':{},'paired_input_sets':{},'total_calls':0}
 miss_total=0
 for title,inputs in groups.items():
  metrics={name:{'diff':[],'by_band':defaultdict(list),'q_mismatch':0,'r_c_errors':0,
                 'input_errors':0,'exact_q_r_c_errors':0} for name in ('loose','strict')}
  old_mean=0
  for n,d in inputs:
   expected_q,expected_r,expected_c=expected(n,d,16,16)
   observations=[]
   for cpu in cpus:
    wr(cpu.mem,N,n,2);wr(cpu.mem,D,d,2)
    wr(cpu.mem,Q,0x5BA5,2);wr(cpu.mem,R,0x7C62,2)
    cpu.mem[0xC030]=0xA5
    cycles=cpu.call(MOD_API,4000000)
    observations.append({'q':rd(cpu.mem,Q,2),'r':rd(cpu.mem,R,2),
       'carry':cpu.c,'n':rd(cpu.mem,N,2),'d':rd(cpu.mem,D,2),
       'sentinel':cpu.mem[0xC030],'cycles':cycles})
   baseline=observations[0]
   assert (baseline['q'],baseline['r'],baseline['carry'])==(expected_q,expected_r,expected_c)
   assert baseline['n']==n and baseline['d']==d and baseline['sentinel']==0xA5
   old_mean+=baseline['cycles']
   label=band(n,d,0)
   for name,obj in zip(('loose','strict'),observations[1:]):
    z=metrics[name]
    if (obj['r'],obj['carry'])!=(expected_r,expected_c):z['r_c_errors']+=1
    if (obj['n'],obj['d'],obj['sentinel'])!=(n,d,0xA5):z['input_errors']+=1
    if (obj['q'],obj['r'],obj['carry'])!=(expected_q,expected_r,expected_c):z['exact_q_r_c_errors']+=1
    if obj['q']!=expected_q:z['q_mismatch']+=1
    delta=obj['cycles']-baseline['cycles']
    z['diff'].append(delta);z['by_band'][label].append(delta)
  row={'cases':len(inputs),'baseline_mean_cycles':old_mean/len(inputs),'candidate':{}}
  for name,z in metrics.items():
   vec=z['diff'];f=Counter('faster' if k<0 else 'equal' if k==0 else 'slower' for k in vec)
   row['candidate'][name]={'mean_delta_cycles':sum(vec)/len(vec),
    'faster':f['faster'],'equal':f['equal'],'slower':f['slower'],
    'worst_slowdown':max(vec),'max_speedup':-min(vec),
    'q_mismatches':z['q_mismatch'],'r_c_errors':z['r_c_errors'],
    'input_errors':z['input_errors'],'exact_q_r_c_errors':z['exact_q_r_c_errors'],
    'classes':{k:{'cases':len(v),'mean_delta':sum(v)/len(v),
       'max_slowdown':max(v),'best_saving':-min(v)} for k,v in z['by_band'].items()}}
  assert row['candidate']['strict']['exact_q_r_c_errors']==0
  assert row['candidate']['strict']['input_errors']==0
  assert row['candidate']['loose']['r_c_errors']==0
  assert row['candidate']['loose']['input_errors']==0
  miss_total+=row['candidate']['loose']['q_mismatches']
  result['workloads'][title]=row;result['total_calls']+=len(inputs)*3
  print(title,'baseline',f"{row['baseline_mean_cycles']:.6f}",
   'loose',f"{row['candidate']['loose']['mean_delta_cycles']:+.6f}",
   'strict',f"{row['candidate']['strict']['mean_delta_cycles']:+.6f}",
   'loose Q mismatch',row['candidate']['loose']['q_mismatches'],flush=True)
 assert result['total_calls']==(1705+len(KINDS)*256)*3
 assert miss_total>0,'remainder-only candidate unexpectedly preserves documented quotient'
 assert result['workloads']['official_shared_1705']['candidate']['strict']['mean_delta_cycles']>0,'strict candidate unexpectedly wins: investigate'
 # UDIV16 entry is untouched. In-memory probe both code maps for a fixed
 # structured operand sample; output Q/R/status/input must be identical.
 divchecks=0
 for n,d in groups['official_shared_1705'][:256]:
  values=[]
  for cpu in cpus:
   wr(cpu.mem,N,n,2);wr(cpu.mem,D,d,2)
   cy=cpu.call(DIV_API,4000000)
   values.append((cy,rd(cpu.mem,Q,2),rd(cpu.mem,R,2),cpu.c,rd(cpu.mem,N,2),rd(cpu.mem,D,2)))
  assert values[0]==values[1]==values[2],('UDIV16 changed unexpectedly',n,d,values)
  divchecks+=3
 result['udiv16_unchanged_calls']=divchecks
 result['total_calls']+=divchecks
 result['conclusion']='Do not promote: loose remainder-only ABI mismatch; strict full-Q alternative slows current common corpus and consumes additional code.'
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('V1 UMOD16 Q0 OPTISEARCH INSPIRED CANDIDATE: REJECT',result['total_calls'],'calls',flush=True)
if __name__=='__main__':main()
