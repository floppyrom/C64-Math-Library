#!/usr/bin/env python3
"""Issue39 V1–V5: current-public-ABI A/B of already-public OptiSearch U32 donors.

No resident mutation, no native VICE cycle timing, no candidate promotion.
Research-owned RAM and four-byte ZP option are NOT default profile resources.
"""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'routines/standalone_lab/portable'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus
from verify import render
N,D,Q,R=0xc010,0xc014,0xc018,0xc01c
OPS=('MATH_UDIV32_32','MATH_UMOD32_32')
DONORS={
 'aligned_0zp':('div_u32_aligned_nozp.asm','FAST_UDIV32_PUBLIC',576,0,False),
 'zptail_4zp':('div_u32_zptail.asm','FAST_UDIV32_PUBLIC',544,4,False),
 'mod_aligned_0zp':('mod_u32_aligned_carry.asm','FAST_UMOD32_ALIGNED_PUBLIC',496,0,True),
}
MAPS={
 'ram_0800':dict(KERNEL_CODE=0x0800,KERNEL_AUX=0x0c00,KERNEL_ADAPTER=0x0f00,INPUT_NUM=N,INPUT_DIV=D,OUTPUT_QUOT=Q,OUTPUT_REM=R,TEMP_ZP=0x70,TEMP_RAM=0x0400),
 'ram_0851':dict(KERNEL_CODE=0x0851,KERNEL_AUX=0x0d13,KERNEL_ADAPTER=0x0f51,INPUT_NUM=N,INPUT_DIV=D,OUTPUT_QUOT=Q,OUTPUT_REM=R,TEMP_ZP=0x70,TEMP_RAM=0x0420),
}
def inputs(op):
 count=2048 if op==OPS[0] else 1024
 common=[(n,d) for n,d,k in corpus(op,32,32,0,count)[1]]
 rng=random.Random(0xC6393232 if op==OPS[0] else 0xC6393233)
 groups={
 'official_common':common,
 'uniform_32':[(rng.getrandbits(32),rng.randrange(1,1<<32)) for _ in range(64)],
 'divisor_8bit':[(rng.getrandbits(32),rng.randrange(1,256)) for _ in range(64)],
 'divisor_16bit':[(rng.getrandbits(32),rng.randrange(256,65536)) for _ in range(64)],
 'divisor_24bit':[(rng.getrandbits(32),rng.randrange(65536,1<<24)) for _ in range(64)],
 'quotient_0':[(d-1,d) for d in (rng.randrange(2,1<<32) for _ in range(64))],
 'quotient_1':[(d+rng.randrange(d),d) for d in (rng.randrange(1,1<<31) for _ in range(64))],
 'high_quotient':[(rng.randrange(1<<30,1<<32),rng.randrange(1,256)) for _ in range(64)],
 'divisor_zero':[(rng.getrandbits(32),0) for _ in range(64)]}
 return groups
def call(cpu,entry,n,d,remainder_only):
 mem=cpu.mem
 wr(mem,N,n,4);wr(mem,D,d,4)
 wr(mem,Q,0xe5a95c67,4);wr(mem,R,0x3b127cd4,4)
 mem[0xc024]=0xa6;mem[0xc025]=0x49;mem[0x0430]=0x53;mem[0x0431]=0xc7
 cpu.d=0;cpu.c=1;sp=cpu.sp
 ticks=cpu.call(entry,4_000_000)
 eq,er,ec=expected(n,d,32,32)
 got=(rd(mem,Q,4),rd(mem,R,4),cpu.c,rd(mem,N,4),rd(mem,D,4),
      mem[0xc024],mem[0xc025],mem[0x0430],mem[0x0431],cpu.sp)
 assert (got[1],got[2])==(er,ec),(entry,n,d,'R/C',got,(eq,er,ec))
 assert remainder_only or got[0]==eq,(entry,n,d,'Q',got,(eq,er,ec))
 assert got[3:]==(n,d,0xa6,0x49,0x53,0xc7,sp),(entry,n,d,'ABI/SP',got)
 return ticks,got
def run(profile=None,donor=None,location=None):
 state=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 ps=[profile] if profile else PROFILES
 ds={k:v for k,v in DONORS.items() if donor is None or donor==k}
 ms={k:v for k,v in MAPS.items() if location is None or location==k}
 workloads={op:inputs(op) for op in OPS}
 out={'status':'PASS_PUBLIC_OPTISEARCH_ABI_REPLAY_NO_PROMOTION',
      'resident_changed':False,'public_entries_patched':False,'native_vice_calls':0,
      'cycles':'full 6502 public call instruction cycles; excludes VIC/REU DMA contention',
      'candidate_sources':{},'inputs':{},'profiles':{},'maps':list(ms),
      'paired_cases':0,'cpu_calls':0,'errors':0}
 for k,(file,_,_,_,_) in ds.items():
  out['candidate_sources'][k]={'path':'routines/standalone_lab/portable/'+file,
    'sha256':hashlib.sha256((ROOT/'routines/standalone_lab/portable'/file).read_bytes()).hexdigest()}
 for op,groups in workloads.items():
  out['inputs'][op]={name:{'cases':len(v),'sha256':hashlib.sha256(b''.join(n.to_bytes(4,'little')+d.to_bytes(4,'little') for n,d in v)).hexdigest()} for name,v in groups.items()}
 for p in ps:
  f=ROOT/p/'resident'/f'math_{p}_game_math.prg'
  sha=hashlib.sha256(f.read_bytes()).hexdigest()
  assert state['reference_prg_sha256'][p]==sha,(p,'resident pin mismatch',sha)
  rec={'resident_sha256':sha,'donors':{}}
  for label,(filename,symbol,code_bytes,zp,mod_only) in ds.items():
   rec['donors'][label]={}
   for map_name,mp in ms.items():
    src=render(filename,mp)
    code,syms,_=Assembler().assemble(src)
    assert len(code)==code_bytes,(label,map_name,len(code),code_bytes)
    assert all(0x0800<=addr<0x1000 for addr in code),(label,map_name,'outside caller RAM')
    base,apis=load(p);cand,apis2=load(p)
    assert apis==apis2 and all(cand.mem[a]==0 for a in code),(p,label,map_name,'RAM collision')
    for a,v in code.items():cand.mem[a]=v
    mr={'code_bytes':code_bytes,'extra_zp_bytes':zp,'scratch_ram_bytes':4 if zp==0 else 0,
        'caller_owned_ram_required':True,'operations':{}}
    for op in ((OPS[1],) if mod_only else OPS):
     mr['operations'][op]={}
     for kind,vec in workloads[op].items():
      before=after=fast=slow=tied=0;peak_slow=-1000000;peak_gain=-1000000
      q_differences=0;cyhash=hashlib.sha256()
      for n,d in vec:
       old,oa=call(base,apis[op],n,d,op==OPS[1])
       new,na=call(cand,syms[symbol],n,d,op==OPS[1])
       assert oa[1:]==na[1:],(p,label,map_name,op,kind,hex(n),hex(d),oa,na)
       if op==OPS[0]:assert oa[0]==na[0]
       q_differences+=oa[0]!=na[0]
       before+=old;after+=new
       delta=new-old
       fast+=delta<0;slow+=delta>0;tied+=delta==0
       peak_slow=max(peak_slow,delta);peak_gain=max(peak_gain,-delta)
       cyhash.update(old.to_bytes(4,'little')+new.to_bytes(4,'little'))
       out['paired_cases']+=1;out['cpu_calls']+=2
      mr['operations'][op][kind]={'cases':len(vec),
       'before_mean':before/len(vec),'after_mean':after/len(vec),
       'delta_mean':(after-before)/len(vec),'faster':fast,'slower':slow,'equal':tied,
       'worst_regression':peak_slow,'best_gain':peak_gain,
       'mod_quotient_side_effect_differences':q_differences,
       'cycles_pair_sha256':cyhash.hexdigest()}
     print(p,label,map_name,op,
       'official delta',round(mr['operations'][op]['official_common']['delta_mean'],3),
       'uniform delta',round(mr['operations'][op]['uniform_32']['delta_mean'],3),flush=True)
    rec['donors'][label][map_name]=mr
  out['profiles'][p]=rec
 assert out['paired_cases']>0 and out['cpu_calls']==2*out['paired_cases']
 return out
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--profile',choices=PROFILES)
 ap.add_argument('--donor',choices=list(DONORS))
 ap.add_argument('--map',choices=list(MAPS))
 ap.add_argument('--out',type=Path)
 a=ap.parse_args()
 result=run(a.profile,a.donor,a.map)
 if a.out:
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 U3232 OPTISEARCH PUBLIC ABI REPLAY PASS',result['paired_cases'],result['cpu_calls'],flush=True)
if __name__=='__main__':main()
