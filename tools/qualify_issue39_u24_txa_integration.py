#!/usr/bin/env python3
"""Current-shipped versus source-built general U24 TXA profile integration proof.

Strict source-build SHA, stable 56 API addresses/reference and alternate
memory maps, paired public-ABI quotient/remainder/carry & sentinel checks.
Do not install a candidate merely because this runs: full native VICE
and official per-operation benchmark release still separately required.
"""
from pathlib import Path
import argparse,hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from validate_unsigned_division import PROFILES,load,expected,wr,rd,edge
from benchmark_unsigned_common_corpus import corpus
OPS=('MATH_UDIV24','MATH_UMOD24')
REF_REU={'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu',
         'v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'}
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def candidate(profile,kind):
 root=(ROOT/'build_hybrid' if profile=='v5_hybrid_lowzp' else ROOT/'build_source')/kind/profile
 man=json.loads((root/'source_build_manifest.json').read_text())
 binary=root/man['output_prg']
 assert man['output_sha256']==digest(binary)
 blob=binary.read_bytes();start=int.from_bytes(blob[:2],'little')
 m=bytearray(65536);m[start:start+len(blob)-2]=blob[2:]
 if profile in REF_REU:
  reu_desc=man['reu_image']
  assert reu_desc and reu_desc['sha256']==digest(root/reu_desc['file'])
  reu=bytearray((root/reu_desc['file']).read_bytes())
 else:reu=None
 cpu=CPU(m,reu=reu);cpu.d=0
 entry=int(man['math_init'][1:],16)
 cpu.call(entry,2_000_000)
 io=int(man['public_io'][1:5],16)
 apis={k:int(v[1:],16) for k,v in man['public_entries'].items()}
 return cpu,apis,io,man,binary
def vectors(op):
 _,sample=corpus(op,24,24,0,4096 if op==OPS[0] else 1024)
 rng=random.Random(0xC639241E+(op==OPS[1]))
 out={'official':[(n,d) for n,d,_ in sample],
  'n2_gt_d2':[],'n2_eq_d2':[],'n2_lt_d2':[],
  'random_d8':[],'random_full24':[],'zero_divisor':[]}
 for _ in range(256):
  dh=rng.randrange(0,255);nh=rng.randrange(dh+1,256)
  out['n2_gt_d2'].append((nh<<16|rng.randrange(65536),dh<<16|rng.randrange(65536)))
  dh=rng.randrange(256)
  out['n2_eq_d2'].append((dh<<16|rng.randrange(65536),dh<<16|rng.randrange(65536)))
  nh=rng.randrange(255);dh=rng.randrange(nh+1,256)
  out['n2_lt_d2'].append((nh<<16|rng.randrange(65536),dh<<16|rng.randrange(65536)))
  out['random_d8'].append((rng.randrange(65536,1<<24),rng.randrange(1,256)))
  out['random_full24'].append((rng.randrange(1<<24),rng.randrange(1,1<<24)))
  out['zero_divisor'].append((rng.randrange(1<<24),0))
 return out
def call(cpu,entry,io,n,d,check_q):
 m=cpu.mem;N,D,Q,R=io+16,io+20,io+24,io+28
 wr(m,N,n,3);wr(m,D,d,3)
 wr(m,Q,0xa1594e2b,4);wr(m,R,0xe7b31c6f,4)
 # $C020–$C023 may be owned by the REU mechanism; preserve unrelated RAM
 # sufficiently beyond the 32-byte public I/O region.
 guard=io+0x2c
 m[guard]=0x59
 cpu.c=1;cpu.d=0;sp=cpu.sp
 cycles=cpu.call(entry,4_000_000)
 q,r,c=expected(n,d,24,24)
 observed=(rd(m,Q,3),rd(m,R,3),cpu.c,rd(m,N,3),rd(m,D,3),
           m[Q+3],m[R+3],m[guard],cpu.sp)
 assert (observed[1],observed[2])==(r,c),(hex(entry),hex(n),hex(d),'RC',observed,r,c)
 assert not check_q or observed[0]==q,(hex(entry),hex(n),hex(d),'Q',observed,q)
 assert (observed[3],observed[4],observed[6],observed[7],observed[8])==(n,d,0xe7,0x59,sp),('ABI',observed)
 return cycles,observed
def test_one(p,kind,status):
 a,public,io,man,binary=candidate(p,kind)
 refmap=kind=='reference'
 before=None
 if refmap:
  old,oldentry=load(p);old_io=0xc000
  assert public=={k:v for k,v in public.items()} # public aliases from source map
  for name in OPS:assert public[name]==oldentry[name],(p,name)
  before=old,oldentry,old_io
 else:
  # The reference and alternate public maps need not share address,
  # but must expose the complete same API namespace.
  assert len(public)>=56,(p,len(public))
 assert len(public)>=56 and len(man['public_entries'])>=56
 r={'source_prg_sha256':man['output_sha256'],
    'source_bytes':binary.stat().st_size,
    'resident_baseline_sha256':status['reference_prg_sha256'][p],
    'public_API_entries':len(public),'source_reu_sha256':man.get('reu_image',{}).get('sha256') if man.get('reu_image') else None,
    'operations':{}}
 for name in OPS:
  by={}
  for class_name,cases in vectors(name).items():
   oc=nc=fast=slow=same=q3_effects=q_side_effects=0
   ticks=hashlib.sha256()
   for n,d in cases:
    quotient=(name==OPS[0] or p=='v1_balanced')
    t1,one=call(a,public[name],io,n,d,quotient)
    if before:
     t0,zero=call(before[0],before[1][name],before[2],n,d,quotient)
     assert one[1:5]==zero[1:5] and one[6:]==zero[6:],('paired ABI',p,name,kind,class_name,n,d,zero,one)
     if quotient:assert one[0]==zero[0]
     q3_effects+=one[5]!=zero[5]
     q_side_effects+=one[0]!=zero[0]
     dt=t1-t0;oc+=t0;nc+=t1;fast+=dt<0;slow+=dt>0;same+=dt==0
     ticks.update(t0.to_bytes(4,'little')+t1.to_bytes(4,'little'))
    else:
     nc+=t1;ticks.update(t1.to_bytes(4,'little'))
   by[class_name]={'cases':len(cases),
     'source_mean':nc/len(cases),
     'shipped_mean':oc/len(cases) if before else None,
     'mean_delta':(nc-oc)/len(cases) if before else None,
     'faster':fast,'slower':slow,'equal':same,
     'Q3_side_effect_differences':q3_effects,
     'Q24_side_effect_differences':q_side_effects,
     'cycles_sha256':ticks.hexdigest(),
     'operand_sha256':hashlib.sha256(b''.join(n.to_bytes(3,'little')+d.to_bytes(3,'little') for n,d in cases)).hexdigest()}
  r['operations'][name]=by
  print('CANDIDATE',p,kind,name,'official',by['official']['cases'],
     'mean',round(by['official']['source_mean'],5),
     'delta',None if not refmap else round(by['official']['mean_delta'],5),
     'faster',by['official']['faster'],'slower',by['official']['slower'],flush=True)
 return r
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--profile',choices=PROFILES)
 ap.add_argument('--map',choices=['reference','alternate'])
 ap.add_argument('--out',type=Path)
 args=ap.parse_args()
 status=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 selected=[args.profile] if args.profile else PROFILES
 kinds=[args.map] if args.map else ['reference','alternate']
 out={'status':'PASS_CANDIDATE_SOURCE_MAPS_NO_INSTALL',
  'profiles':{},'public_residents_changed':False,'native_vice_calls':0,
  'intent':'qualify actual V1–V5 assembled canonical source, including V5 imported V2',
  'maps':kinds}
 for p in selected:
  out['profiles'][p]={}
  for kind in kinds:
   out['profiles'][p][kind]=test_one(p,kind,status)
 if args.out:
  args.out.parent.mkdir(parents=True,exist_ok=True)
  args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 U24 TXA FULL PROFILE SOURCE CANDIDATE ORACLE PASS',flush=True)
if __name__=='__main__':main()
