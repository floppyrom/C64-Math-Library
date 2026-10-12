#!/usr/bin/env python3
"""Exhaustive K8 versus exact released 8x8 public UDIV8: every N and D."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load
from screen_issue39_u8_prefix_source_sweep import generate,run_one,MAPS
def run(profile=None,map_name=None):
 ps=[profile] if profile else PROFILES
 maps={k:v for k,v in MAPS.items() if map_name is None or map_name==k}
 status=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 out={'status':'PASS_EXHAUSTIVE_PUBLIC_ABI_K8_SOURCE','variants':{},'paired_inputs':0,'cpu_calls':0,
      'native_vice_calls':0,'code_origin_maps':list(maps),'production_changed':False,'candidate_extra_zp_bytes':1}
 for p in ps:
  file=ROOT/p/'resident'/f'math_{p}_game_math.prg'
  sha=hashlib.sha256(file.read_bytes()).hexdigest()
  assert status['reference_prg_sha256'][p]==sha
  result={'resident_sha256':sha,'maps':{}}
  for label,origin in maps.items():
   code,labels,_=Assembler().assemble(generate(8,origin))
   assert len(code)==229 and labels['CANDIDATE_UDIV8_PUBLIC']==origin
   old,api=load(p);cand,entries=load(p)
   assert entries==api and all(cand.mem[a]==0 for a in code)
   for a,v in code.items():cand.mem[a]=v
   totals=[0,0];fast=slow=equal=0;worst=-10**9;best=0;vec_sha=hashlib.sha256()
   class_sums={}
   for n in range(256):
    for d in range(256):
     t0=run_one(old,api['MATH_UDIV8'],n,d)
     t1=run_one(cand,origin,n,d)
     delta=t1-t0
     totals[0]+=t0;totals[1]+=t1
     fast+=delta<0;slow+=delta>0;equal+=delta==0
     worst=max(worst,delta);best=max(best,-delta)
     vec_sha.update(t0.to_bytes(4,'little')+t1.to_bytes(4,'little'))
     k='div_zero' if d==0 else ('small_d1to15' if d<=15 else ('medium_d16to127' if d<=127 else 'large_d128to255'))
     g=class_sums.setdefault(k,{'count':0,'old_sum':0,'cand_sum':0,'faster':0,'slower':0})
     g['count']+=1;g['old_sum']+=t0;g['cand_sum']+=t1
     g['faster']+=delta<0;g['slower']+=delta>0
     out['paired_inputs']+=1;out['cpu_calls']+=2
   for a in class_sums.values():
    a['delta_mean']=(a['cand_sum']-a['old_sum'])/a['count']
    a['old_mean']=a['old_sum']/a['count'];a['candidate_mean']=a['cand_sum']/a['count']
   result['maps'][label]={'cases':65536,'current_mean':totals[0]/65536,
    'K8_mean':totals[1]/65536,'delta_mean':(totals[1]-totals[0])/65536,
    'faster':fast,'slower':slow,'equal':equal,'worst_regression':worst,
    'best_speedup':best,'code_bytes':len(code),'extra_ZP':1,
    'cycle_pair_sha256':vec_sha.hexdigest(),'classes':class_sums}
   print('UDIV8 65536',p,label,'public',round(totals[0]/65536,6),
         'K8',round(totals[1]/65536,6),'delta',round((totals[1]-totals[0])/65536,6),
         'faster',fast,'slower',slow,flush=True)
  out['variants'][p]=result
 assert out['paired_inputs']==65536*len(ps)*len(maps)
 return out
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--profile',choices=PROFILES)
 ap.add_argument('--map',choices=list(MAPS))
 ap.add_argument('--out',type=Path)
 a=ap.parse_args()
 result=run(a.profile,a.map)
 if a.out:
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 U8 K8 EXHAUSTIVE',result['paired_inputs'],result['cpu_calls'],flush=True)
if __name__=='__main__':main()
