#!/usr/bin/env python3
"""Issue #39: exhaustive exact same-input V2 UMOD8 guard D>=24 threshold sweep.

Evaluate BOTH validated routes for every n,d using the exact released V2
resident, then reconstruct candidate thresholds by dispatch decision. Because
the cutoff changes only CMP #imm, no code layout or per-route cycles change.
Research-only; NOT a default source change or proof of global optimality.
"""
from pathlib import Path
import hashlib,json,sys,argparse
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from validate_unsigned_division import load
PRG=R/'v2_pareto_fast/resident/math_v2_pareto_fast_game_math.prg'
GUARD=0x5323
CMP_OPERAND=GUARD+4
ENTRY=0x3200
DSET=(24,25,26,28,30,31,32,33,34,36,40,48,64,80,96,128,160,192,224,255)
EXPECTED_SHA='0510d469e1ff3bf136395e49b2e5055b9ab485fd87c4741ab5d0cbfc8fdf013d'
def cpu_with_cutoff(v):
 c,api=load('v2_pareto_fast')
 assert api['MATH_UMOD8']==ENTRY
 assert bytes(c.mem[GUARD:GUARD+5])==bytes((0xad,0x14,0xc0,0xc9,0x18))
 c.mem[CMP_OPERAND]=v
 return c
def invoke(c,n,d):
 m=c.mem
 m[0xc010:0xc012]=bytes((n,0xb5))
 m[0xc014:0xc016]=bytes((d,0xa9))
 m[0xc018:0xc01c]=bytes((0xc3,0x5c,0x2b,0x97))
 m[0xc01c:0xc020]=bytes((0xd2,0x52,0x76,0x19))
 c.d=0;sp=c.sp
 cycles=c.call(ENTRY,200000)
 out=(m[0xc01c],c.c,bytes(m[0xc018:0xc01c]),
       bytes(m[0xc01d:0xc020]),bytes(m[0xc010:0xc012]),
       bytes(m[0xc014:0xc016]),sp==c.sp)
 expect=(n%d if d else 0,int(d==0),
         bytes((0xc3,0x5c,0x2b,0x97)),bytes((0x52,0x76,0x19)),
         bytes((n,0xb5)),bytes((d,0xa9)),True)
 assert out==expect,(n,d,out,expect)
 return cycles
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);opts=p.parse_args()
 blob=PRG.read_bytes();sha=hashlib.sha256(blob).hexdigest()
 assert sha==EXPECTED_SHA,(sha,EXPECTED_SHA)
 baseline=cpu_with_cutoff(24)
 fallback=cpu_with_cutoff(255)
 choices={v:{'cycles':0,'faster':0,'slower':0,'equal':0,'worst_regression':0,'maximum_saving':0} for v in DSET}
 bands=[{'from':24,'to':31},{'from':32,'to':47},{'from':48,'to':63},
        {'from':64,'to':127},{'from':128,'to':254}]
 for v in DSET:choices[v]['strata']={f"D_{b['from']}_{b['to']}":{'before':0,'after':0,'cases':0} for b in bands}
 cases=0;both_routes=0;fallback_only=0
 inputhash=hashlib.sha256();base_trace=hashlib.sha256()
 for d in range(256):
  for n in range(256):
   inputhash.update(bytes((n,d)))
   actual=invoke(baseline,n,d)
   if 24<=d<=254:
    alternative=invoke(fallback,n,d)
    both_routes+=1
   else:
    alternative=actual
    fallback_only+=d<24
   base_trace.update(actual.to_bytes(2,'little'))
   for cutoff,t in choices.items():
    new=actual if d>=cutoff or d<24 else alternative
    # For cutoff=255 and d=255 actual is still the fast path.
    diff=new-actual
    t['cycles']+=new
    t['faster']+=diff<0;t['slower']+=diff>0;t['equal']+=diff==0
    t['worst_regression']=max(t['worst_regression'],diff)
    t['maximum_saving']=max(t['maximum_saving'],-diff)
    for band in bands:
     if band['from']<=d<=band['to']:
      b=t['strata'][f"D_{band['from']}_{band['to']}"]
      b['before']+=actual;b['after']+=new;b['cases']+=1
   cases+=1
  if d%32==31:print('screened divisor high',d,'of 255',flush=True)
 assert cases==65536 and both_routes==231*256 and fallback_only==24*256
 prior=choices[24]
 assert prior['faster']==prior['slower']==0 and prior['equal']==65536
 for cutoff,row in choices.items():
  row['mean_cycles']=row['cycles']/cases
  row['delta_cycles_per_call']=(row['cycles']-prior['cycles'])/cases
  row['total_delta_cycles']=row['cycles']-prior['cycles']
  for name,v in row['strata'].items():
   v['before_mean']=v['before']/v['cases']
   v['after_mean']=v['after']/v['cases']
  print('D>=',cutoff,'mean',format(row['mean_cycles'],'.6f'),
        'delta',format(row['delta_cycles_per_call'],'+.6f'),
        'faster',row['faster'],'slower',row['slower'],flush=True)
 assert abs(prior['mean_cycles']-52.20445251464844)<1e-6,(prior['mean_cycles'],'legacy V2 65k anchor')
 # Confirm mathematical routing equivalence with real patched CPUs at
 # disjoint thresholds and edge-heavy deterministic probes.
 spotcases=[(n,d) for d in (0,1,23,24,25,26,28,31,32,47,48,63,64,95,96,127,128,191,192,223,224,254,255)
            for n in (0,1,2,3,7,15,31,63,127,128,255)]
 for cutoff in (25,31,32,48,64,96,128,192,255):
  direct=cpu_with_cutoff(cutoff)
  compare_base=cpu_with_cutoff(24)
  compare_fallback=cpu_with_cutoff(255)
  for n,d in spotcases:
   seen=invoke(direct,n,d)
   inferred=(invoke(compare_base,n,d) if d>=cutoff or d<24 else invoke(compare_fallback,n,d))
   assert seen==inferred,(cutoff,n,d,seen,inferred)
 res={'status':'PASS','source':'tools/screen_issue39_v2_umod8_guard_thresholds.py',
  'resident_sha256':sha,'baseline_guard_cutoff':24,'source_offset':hex(CMP_OPERAND),
  'input_sha256':inputhash.hexdigest(),'baseline_cycle_vector_sha256':base_trace.hexdigest(),
  'sample_count':cases,'dual_route_pairs':both_routes,
  'fully_real_direct_threshold_spot_checks':len(spotcases)*9,
  'basis':'6502 complete current resident public API cycles; no physical bus/REU timing',
  'code_resource_changes':0,'decision':'candidate research only; per-call regressions and workload sensitivity must be considered',
  'thresholds':{str(k):v for k,v in choices.items()}}
 if opts.out:
  opts.out.parent.mkdir(parents=True,exist_ok=True)
  opts.out.write_text(json.dumps(res,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 V2 UMOD8 GUARD EXHAUSTIVE PASS',cases,'cases',flush=True)
if __name__=='__main__':main()
