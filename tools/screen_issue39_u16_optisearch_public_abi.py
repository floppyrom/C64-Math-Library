#!/usr/bin/env python3
"""Issue 39: replay already-published OptiSearch U16 sources against V1-V5.

D16 donor provides quotient and remainder. Zero-ZP U16 remainder donor
is valid only for public remainder-only contracts (V2-V5), not V1's
quotient-producing UMOD16 alias. No permanent resident/code/ZP changes.
"""
from pathlib import Path
import argparse,hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'routines/standalone_lab/portable'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,expected,load,rd,wr
from benchmark_unsigned_common_corpus import corpus
from verify import render
N,D,Q,R=0xc010,0xc014,0xc018,0xc01c
OPS=('MATH_UDIV16','MATH_UMOD16')
DONORS={
 'biased_2zp':('div_u16_biased.asm','FAST_UDIV16_BIASED',323,2,False),
 'direct_mod_0zp':('mod_u16_direct_zerozp.asm','FAST_UMOD16_DIRECT_PUBLIC',976,0,True),
}
MAPS={
 'ram_0800':dict(KERNEL_CODE=0x0800,KERNEL_TABLE=0x0c00,KERNEL_ADAPTER=0x0d00,
   INPUT_NUM=N,INPUT_DIV=D,OUTPUT_QUOT=Q,OUTPUT_REM=R,TEMP_ZP=0x70,TEMP_RAM=0x0400),
 'ram_0851':dict(KERNEL_CODE=0x0851,KERNEL_TABLE=0x0d10,KERNEL_ADAPTER=0x0d60,
   INPUT_NUM=N,INPUT_DIV=D,OUTPUT_QUOT=Q,OUTPUT_REM=R,TEMP_ZP=0x70,TEMP_RAM=0x0420)
}
def workloads(op):
 count=2048 if op==OPS[0] else 1024
 official=[(n,d) for n,d,_ in corpus(op,16,16,0,count)[1]]
 rng=random.Random(0xC6391601 if op==OPS[0] else 0xC6391602)
 groups={
  'official':official,
  'uniform16':[(rng.randrange(65536),rng.randrange(1,65536)) for _ in range(128)],
  'narrow_d8':[(rng.randrange(65536),rng.randrange(1,256)) for _ in range(128)],
  'tiny_d4':[(rng.randrange(65536),rng.randrange(1,16)) for _ in range(128)],
  'qzero':[(d-1,d) for d in (rng.randrange(2,65536) for _ in range(128))],
  'qone':[(d+rng.randrange(d),d) for d in (rng.randrange(1,32768) for _ in range(128))],
  'q2to7':[(q*d+rng.randrange(d),d) for q,d in ((rng.randrange(2,8),rng.randrange(1,8192)) for _ in range(128))],
  'powers2':[(rng.randrange(65536),1<<rng.randrange(16)) for _ in range(128)],
  'd0':[(rng.randrange(65536),0) for _ in range(128)],
 }
 return groups
def full_call(cpu,entry,n,d,is_remainder):
 mem=cpu.mem
 wr(mem,N,n,2);wr(mem,D,d,2)
 mem[0xc012]=0x4a;mem[0xc013]=0x52
 mem[0xc016]=0xa5;mem[0xc017]=0x39
 wr(mem,Q,0xA7BC519D,4);wr(mem,R,0xE57B9013,4)
 mem[0x0440]=0x62;mem[0x0441]=0xB9
 cpu.d=0;cpu.c=1;sp=cpu.sp
 cycles=cpu.call(entry,2_000_000)
 eq,er,ec=expected(n,d,16,16)
 state=(rd(mem,Q,2),rd(mem,R,2),cpu.c,rd(mem,N,2),rd(mem,D,2),
        mem[0xc012],mem[0xc013],mem[0xc016],mem[0xc017],
        bytes(mem[0xc01a:0xc01c]).hex(),
        bytes(mem[0xc01e:0xc020]).hex(),
        mem[0x0440],mem[0x0441],cpu.sp)
 assert (state[1],state[2])==(er,ec),(n,d,hex(entry),'R/C',state,(eq,er,ec))
 assert is_remainder or state[0]==eq,(n,d,hex(entry),'Q',state,eq)
 assert state[3:]==(n,d,0x4a,0x52,0xa5,0x39,
                    bytes.fromhex('bca7').hex(),bytes.fromhex('7be5').hex(),
                    0x62,0xb9,sp),(n,d,hex(entry),'ownership',state)
 return cycles,state
def run(profile=None,donor=None,location=None):
 ps=[profile] if profile else PROFILES
 ds={k:v for k,v in DONORS.items() if donor is None or k==donor}
 maps={k:v for k,v in MAPS.items() if location is None or k==location}
 cases={op:workloads(op) for op in OPS}
 state=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 result={'status':'PASS_SOURCE_BACKED_PUBLIC_ABI_NO_DEFAULT_PROMOTION',
   'cycle_basis':'full public 6502 instruction cycles, no VIC/REU bus cost',
   'resident_changed':False,'public_entries_patched':False,'native_vice_calls':0,
   'profiles':{},'donors':{},'input_classes':{},'paired_inputs':0,'cpu_calls':0,
   'ram_maps':list(maps)}
 for donor,(filename,_,bytes_,zp,_) in ds.items():
  path=ROOT/'routines/standalone_lab/portable'/filename
  result['donors'][donor]={'source':str(path.relative_to(ROOT)),
    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'code_and_data_bytes':bytes_,'extra_zero_page_bytes':zp,
    'scratch_ram_bytes':2 if zp==0 else 0}
 for op,groups in cases.items():
  result['input_classes'][op]={k:{'cases':len(v),
    'sha256':hashlib.sha256(b''.join(n.to_bytes(2,'little')+d.to_bytes(2,'little') for n,d in v)).hexdigest()}
    for k,v in groups.items()}
 for p in ps:
  path=ROOT/p/'resident'/f'math_{p}_game_math.prg'
  sha=hashlib.sha256(path.read_bytes()).hexdigest()
  assert sha==state['reference_prg_sha256'][p],('resident mismatched SHA',p)
  pr={'resident_sha256':sha,'donors':{}}
  for donor,(filename,symbol,nbytes,zp,mod_only) in ds.items():
   if p=='v1_balanced' and mod_only:
    pr['donors'][donor]={'skipped':'V1 UMOD16 quotient output is promised: remainder-only donor incompatible'}
    continue
   pr['donors'][donor]={}
   for mapname,mp in maps.items():
    code,labels,_=Assembler().assemble(render(filename,mp))
    assert len(code)==nbytes,(donor,mapname,len(code),nbytes)
    assert all(0x0800<=a<0x1000 for a in code),(donor,mapname,'outside code RAM')
    old,entries=load(p);new,entries2=load(p)
    assert entries==entries2 and all(new.mem[a]==0 for a in code),(p,donor,mapname,'occupied RAM')
    for a,v in code.items():new.mem[a]=v
    rec={'source_bytes':nbytes,'extra_zp':zp,'scratch_ram':2 if zp==0 else 0,
         'requires_caller_owned_code_ram':True,'operations':{}}
    for op in ((OPS[1],) if mod_only else OPS):
     rec['operations'][op]={}
     for group,inputs in cases[op].items():
      sums=[0,0];fast=slow=equal=qside=0;largest_regression=-10**9
      digest=hashlib.sha256()
      for n,d in inputs:
       old_cycles,oa=full_call(old,entries[op],n,d,op==OPS[1] and p!='v1_balanced')
       new_cycles,na=full_call(new,labels[symbol],n,d,op==OPS[1] and p!='v1_balanced')
       assert oa[1:]==na[1:],(p,donor,mapname,op,group,n,d,oa,na)
       if op==OPS[0] or p=='v1_balanced':
        assert oa[0]==na[0],(p,donor,mapname,op,group,n,d,oa[0],na[0])
       qside+=oa[0]!=na[0]
       sums[0]+=old_cycles;sums[1]+=new_cycles
       delta=new_cycles-old_cycles
       fast+=delta<0;slow+=delta>0;equal+=delta==0
       largest_regression=max(largest_regression,delta)
       digest.update(old_cycles.to_bytes(4,'little')+new_cycles.to_bytes(4,'little'))
       result['paired_inputs']+=1;result['cpu_calls']+=2
      rec['operations'][op][group]={
       'cases':len(inputs),'mean_resident':sums[0]/len(inputs),
       'mean_donor':sums[1]/len(inputs),'delta_mean':(sums[1]-sums[0])/len(inputs),
       'faster':fast,'slower':slow,'equal':equal,
       'quotient_side_effect_differences':qside,
       'worst_regression_cycles':largest_regression,'cycle_pair_sha256':digest.hexdigest()}
     print(p,donor,mapname,op,
       'official',round(rec['operations'][op]['official']['delta_mean'],3),
       'uniform',round(rec['operations'][op]['uniform16']['delta_mean'],3),
       'narrow',round(rec['operations'][op]['narrow_d8']['delta_mean'],3),flush=True)
    pr['donors'][donor][mapname]=rec
  result['profiles'][p]=pr
 assert result['paired_inputs']>0 and result['cpu_calls']==2*result['paired_inputs']
 return result
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--profile',choices=PROFILES)
 ap.add_argument('--donor',choices=list(DONORS))
 ap.add_argument('--map',choices=list(MAPS))
 ap.add_argument('--out',type=Path)
 a=ap.parse_args()
 report=run(a.profile,a.donor,a.map)
 if a.out:
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 U16 OPTISEARCH PUBLIC ABI PASS',report['paired_inputs'],report['cpu_calls'],flush=True)
if __name__=='__main__':main()
