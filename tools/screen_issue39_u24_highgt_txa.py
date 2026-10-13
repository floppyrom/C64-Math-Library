#!/usr/bin/env python3
"""Issue #39: source-reassemble a register-lifetime optimization in generic 24-bit DIV.

Test TXA for the high limb of N-D on the N2>D2 path. LAX N2 earlier
defines X, and no intervening instruction in the high_gt predecessor clobbers X.
The only source mutation is one high_gt 'LDA MATH_N+2' -> 'TXA' per V1/V2.
Neither canonical production source nor resident binaries are changed.
"""
from pathlib import Path
import argparse,hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler,CPU
import assemble_sources as asm
from validate_unsigned_division import expected,wr,rd,load,api
from benchmark_unsigned_common_corpus import corpus
PROFILES=('v1_balanced','v2_pareto_fast')
OPS=('MATH_UDIV24','MATH_UMOD24')
N,D,Q,R=0xc010,0xc014,0xc018,0xc01c
def compile_pair(p):
 src=ROOT/'relocatable_source'/p/'math_relocatable.asm'
 cfg=ROOT/'relocatable_source'/p/'math_config_reference.inc'
 text=asm.preprocess(src,cfg)
 name='DU24B' if p=='v1_balanced' else 'DU24F'
 needle=(name+'_high_gt:\n lda MATH_N+0\n sec\n sbc MATH_D+0\n'
         ' sta MATH_R+0\n lda MATH_N+1\n sbc MATH_D+1\n'
         ' sta MATH_R+1\n lda MATH_N+2\n sbc MATH_D+2\n ldx #0')
 replace=needle.replace(' lda MATH_N+2\n sbc MATH_D+2\n ldx #0',
                        ' txa\n sbc MATH_D+2\n ldx #0')
 assert text.count(needle)==1,(p,'high_gt source not unique')
 candidate=text.replace(needle,replace)
 original,old_labels,_=Assembler().assemble(text)
 updated,new_labels,_=Assembler().assemble(candidate)
 before,entries=load(p)
 # Compare every source-defined byte against current resident image. 
 assert all(before.mem[a]==v for a,v in original.items()),(p,'canonical assembler differs from resident')
 patched=bytearray(65536)
 for a,v in updated.items():patched[a]=v
 new=CPU(patched);new.d=0;new.call(entries['MATH_INIT'],2_000_000)
 # Report exactly what changed (many private offsets may shift).
 different=sum(before.mem[a]!=new.mem[a] for a in set(original)|set(updated))
 return before,new,entries,{
  'old_source_sha256':hashlib.sha256(text.encode()).hexdigest(),
  'candidate_source_sha256':hashlib.sha256(candidate.encode()).hexdigest(),
  'high_gt_old_address':old_labels[name+'_high_gt'],
  'high_gt_new_address':new_labels[name+'_high_gt'],
  'changed_code_bytes':different,'source_edit':'high_gt LDA N2 -> TXA',
  'extra_zero_page_bytes':0,'api_addresses_changed':False}
def inputs(op):
 nbits=24
 count=2048 if op==OPS[0] else 1024
 _meta,official=corpus(op,nbits,nbits,0,count)
 rng=random.Random(0xC6392417+(op==OPS[1]))
 edge=(0,1,2,7,255,256,65535,65536,65537,0xfffffe,0xffffff)
 groups={
  'official_common':[(n,d) for n,d,_ in official],
  'n2_greater_d2':[],
  'n2_equal_d2':[],
  'n2_less_d2':[],
  'd8_with_n2':[],
  'fullwidth_random':[],
  'edge_pairs':[(n,d) for n in edge for d in edge],
  'divisor_zero':[(rng.randrange(1<<24),0) for _ in range(128)]
 }
 for _ in range(1024):
  dh=rng.randrange(0,255);nh=rng.randrange(dh+1,256)
  groups['n2_greater_d2'].append((nh<<16|rng.randrange(65536),dh<<16|rng.randrange(65536)))
  dh=rng.randrange(256)
  groups['n2_equal_d2'].append((dh<<16|rng.randrange(65536),dh<<16|rng.randrange(65536)))
  nh=rng.randrange(255);dh=rng.randrange(nh+1,256)
  groups['n2_less_d2'].append((nh<<16|rng.randrange(65536),dh<<16|rng.randrange(65536)))
  groups['d8_with_n2'].append((rng.randrange(65536,1<<24),rng.randrange(1,256)))
  groups['fullwidth_random'].append((rng.randrange(1<<24),rng.randrange(1,1<<24)))
 return groups
def call(cpu,entry,n,d,quotient):
 m=cpu.mem
 wr(m,N,n,3);wr(m,D,d,3)
 wr(m,Q,0xa13b582c,4);wr(m,R,0xe74b9026,4)
 m[0xc020]=0x38
 cpu.d=0;cpu.c=1;sp=cpu.sp
 ticks=cpu.call(entry,4_000_000)
 eq,er,ec=expected(n,d,24,24)
 got=(rd(m,Q,3),rd(m,R,3),cpu.c,rd(m,N,3),rd(m,D,3),m[Q+3],m[R+3],m[0xc020],cpu.sp)
 assert (got[1],got[2])==(er,ec),(hex(entry),n,d,'R/C',got,eq,er,ec)
 assert (not quotient or got[0]==eq),(hex(entry),n,d,'Q',got,eq)
 assert got[3:5]==(n,d) and got[6:]==(0xe7,0x38,sp),(hex(entry),n,d,'preservation',got)
 return ticks,got
def run(profile=None):
 chosen=[profile] if profile else PROFILES
 result={'status':'PASS_SOURCE_BACKED_HIGHGT_LIVE_X_RESEARCH',
  'profiles':{},'paired_inputs':0,'cpu_calls':0,
  'resident_changed':False,'public_api_changed':False,
  'normal_zp_growth':0,'native_vice_calls':0}
 released=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 for p in chosen:
  old,new,entries,metadata=compile_pair(p)
  resident=ROOT/p/'resident'/('math_'+p+'_game_math.prg')
  digest=hashlib.sha256(resident.read_bytes()).hexdigest()
  assert digest==released['reference_prg_sha256'][p]
  pr={'resident_sha256':digest,'code':metadata,'routines':{}}
  for op in OPS:
   rec={}
   for kind,pairs in inputs(op).items():
    oldsum=newsum=fast=slow=eq=qside=q3side=0
    trace=hashlib.sha256();maximum=-10**9
    for n,d in pairs:
     # V1 UMOD24 quotient-producing alias; V2 remainder-only by contract.
     quotient=(op==OPS[0] or p=='v1_balanced')
     t0,o0=call(old,entries[op],n,d,quotient)
     t1,o1=call(new,entries[op],n,d,quotient)
     assert o0[1:5]+o0[6:]==o1[1:5]+o1[6:],(p,op,kind,n,d,'R/C and ABI',o0,o1)
     if quotient: assert o0[0]==o1[0],(p,op,kind,n,d,'Q',o0,o1)
     qside+=o0[0]!=o1[0]
     q3side+=o0[5]!=o1[5]
     delta=t1-t0
     oldsum+=t0;newsum+=t1
     fast+=delta<0;slow+=delta>0;eq+=delta==0
     maximum=max(maximum,delta)
     trace.update(t0.to_bytes(4,'little')+t1.to_bytes(4,'little'))
     result['paired_inputs']+=1;result['cpu_calls']+=2
    rec[kind]={'cases':len(pairs),'old_mean':oldsum/len(pairs),
       'candidate_mean':newsum/len(pairs),
       'delta_mean':(newsum-oldsum)/len(pairs),'faster':fast,
       'slower':slow,'equal':eq,'max_regression':maximum,
       'Q_side_effect_differences':qside,
       'Q3_extra_byte_differences':q3side,'cycle_pair_sha256':trace.hexdigest(),
       'input_sha256':hashlib.sha256(b''.join(n.to_bytes(3,'little')+d.to_bytes(3,'little') for n,d in pairs)).hexdigest()}
   pr['routines'][op]=rec
   print(p,op,
     'official',round(rec['official_common']['delta_mean'],6),
     'highgt',round(rec['n2_greater_d2']['delta_mean'],6),
     'faster',rec['official_common']['faster'],
     'slower',rec['official_common']['slower'],flush=True)
  result['profiles'][p]=pr
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('--profile',choices=PROFILES)
 ap.add_argument('--out',type=Path)
 a=ap.parse_args()
 report=run(a.profile)
 if a.out:
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 GENERIC UDIV24 HIGHGT TXA SCREEN',report['paired_inputs'],report['cpu_calls'],flush=True)
