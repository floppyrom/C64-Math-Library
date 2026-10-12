#!/usr/bin/env python3
"""Issue39: V2-V4 UMOD32_32 late-zero-check 54-byte in-place layout.

The active gate is in the resident machine image at $5472, not the
non-included historical udiv32_32_early_gate.inc. Build public-ABI paired
comparisons against the actual shipped residents. --stage-images regenerates
canonical source/ref/alternate from patched residents within an isolated CI
checkout. No private OptiSearch binaries are copied.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json,random,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import load,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus,band
PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')
UNCHANGED=('v1_balanced','v5_hybrid_lowzp')
OLD={
 'v2_pareto_fast':'83f78f48f34b19d605b131ec54cfa5c89af11e0cc9bff0b73787de53664e8138',
 'v3_reu_512k':'d65979b93be27710b4688e0ad7ed86d4ef539692601d446a922ecf04d2573bad',
 'v4_reu_16m':'5a5dca8e9023db7f3e23e3cfde54d419ea44d4c6212f2f4ff49496c84b3ea66e'}
GATE=0x5472
LENGTH=54
OLD_GUARD=bytes.fromhex('ad14c00d15c00d16c00d17c0f052')
OUT=ROOT/'validation/review/ISSUE39_V234_32_32_LATEZERO_PAIRED.json'
def sha(data):return hashlib.sha256(data).hexdigest()
def res(p):return ROOT/p/'resident'/f'math_{p}_game_math.prg'
def patch(raw):
 assert len(raw)==49042 and int.from_bytes(raw[:2],'little')==0x1000
 start=GATE-0x1000+2
 old=raw[start:start+LENGTH];assert old[:14]==OLD_GUARD
 comp=bytearray(old[14:54])
 for idx in range(4):
  k=idx*10
  assert comp[k]==0xAD and comp[k+3]==0xCD and comp[k+6]==0x90 and comp[k+8]==0xD0,(idx,comp[k:k+10].hex())
  assert comp[k+7]+14<128 and comp[k+9]+14<128
  comp[k+7]+=14;comp[k+9]+=14
 guard=OLD_GUARD[:-1]+bytes((0x2A,))
 b=bytearray(raw);b[start:start+LENGTH]=comp+guard
 changes=[i for i,(x,y) in enumerate(zip(b,raw)) if x!=y]
 assert changes and all(start<=i<start+LENGTH for i in changes)
 assert len(changes)==50,('gate change count',len(changes))
 return bytes(b),len(changes)
def machine_probe(profile,old,new):
 a,apis=load(profile);b,newapis=load(profile)
 assert apis==newapis
 b.mem[0x1000:0x1000+len(new)-2]=new[2:]
 report={}
 for name,count in (('MATH_UDIV32_32',2048),('MATH_UMOD32_32',1024)):
  _,cc=corpus(name,32,32,0,count)
  assert len(cc)==(2729 if count==2048 else 1705)
  cases=[(n,d,'official') for n,d,_ in cc]
  seed=0x39003232 + PROFILES.index(profile)*65537 + count
  rng=random.Random(seed)
  for n in (0,1,2,0xff,0xffff,0x80000000,0xffffffff):
   cases.append((n,0,'zero_divisor'))
  for n in (0,1,2,3,7,0xff,0x100,0xffff,0x7fffffff,0x80000000,0xffffffff):
   cases.append((n,n,'equality'))
  for _ in range(256):
   n=rng.randrange(1<<32);d=rng.randrange(1<<32)
   cases.append((n,d,'random'))
   cases.append((d,d,'equality'))
   cases.append((n,0,'zero_divisor'))
  delta=[];bands=defaultdict(list);count_out=Counter()
  for n,d,kind in cases:
   q,r,c=expected(n,d,32,32);seen=[]
   for cpu in (a,b):
    wr(cpu.mem,0xC010,n,4);wr(cpu.mem,0xC014,d,4)
    wr(cpu.mem,0xC018,0x5BA5B3C7,4)
    wr(cpu.mem,0xC01C,0x62D48C70,4)
    cpu.mem[0xC030]=0xA5
    cy=cpu.call(apis[name],4_000_000)
    v=(rd(cpu.mem,0xC018,4),rd(cpu.mem,0xC01C,4),cpu.c,
      rd(cpu.mem,0xC010,4),rd(cpu.mem,0xC014,4),cpu.mem[0xC030])
    seen.append((cy,v))
   first,second=seen
   if name=='MATH_UDIV32_32':
    assert first[1]==second[1]==(q,r,c,n,d,0xA5),(profile,name,hex(n),hex(d),seen)
   else:
    # Modulo promises R32/C and input preservation; the Q32 side effect
    # remains exactly identical to the original even when unspecified.
    want=(r,c,n,d,0xA5)
    assert first[1][1:]==second[1][1:]==want,(profile,name,hex(n),hex(d),seen,want)
    assert first[1][0]==second[1][0],(profile,name,'unexpected Q side effect')
   diff=second[0]-first[0]
   delta.append(diff)
   bands[band(n,d,0)].append(diff);count_out['faster' if diff<0 else 'tie' if diff==0 else 'slower']+=1
  if name=='MATH_UDIV32_32':assert not any(delta),('UDIV path changed',profile)
  else:assert sum(delta)<0,(profile,'no aggregate gain',sum(delta))
  report[name]={'case_count':len(cases),'official_case_count':len(cc),
   'mean_delta_cycles':sum(delta)/len(delta),'faster':count_out['faster'],
   'equal':count_out['tie'],'slower':count_out['slower'],
   'minimum_delta':min(delta),'maximum_delta':max(delta),
   'classes':{k:{'cases':len(v),'mean_delta':sum(v)/len(v),'max_slowdown':max(v)} for k,v in bands.items()},
   'arithmetic_or_abi_errors':0}
  print('ISSUE39 V234 32bit',profile,name,len(cases),'delta',f'{sum(delta)/len(delta):.6f}',
   'fast/tie/slow',count_out['faster'],count_out['tie'],count_out['slower'],flush=True)
 return report
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--stage-images',action='store_true')
 args=ap.parse_args()
 existing={p:sha(res(p).read_bytes()) for p in (*PROFILES,*UNCHANGED)}
 result={'status':'PASS','scope':'paired old/new complete 6502 public resident images including zero-divisor and quotient classes',
  'candidate':'sink 14-byte divide-by-zero OR gate into n=d branch by 54-byte fixed-address instruction permutation',
  'changed_profiles':list(PROFILES),'unchanged_profiles':list(UNCHANGED),'old_source_sha256':OLD,
  'profiles':{},'resident_prg_growth':0,'normal_zero_page_growth':0,'public_abi_changed':False,
  'native_vice_checked':False,'source_reference_alternate_checked':False,'total_old_new_calls':0}
 patched={}
 for p in PROFILES:
  old=res(p).read_bytes();assert sha(old)==OLD[p],('incorrect baseline',p,sha(old))
  new,changes=patch(old);patched[p]=new
  # The production include (remainder_fast_v2.inc) must compile to the
  # precise fixed-address patch, rather than a coincidentally identical
  # experimental resident. Independently assemble alternate maps too.
  built=ROOT/'build_source/reference'/p/f'math_{p}_source_built.prg'
  assert built.read_bytes()==new,('source did not reproduce exact 54-byte patch',p,sha(built.read_bytes()),sha(new))
  alternate=ROOT/'build_source/alternate'/p/f'math_{p}_source_built.prg'
  assert alternate.exists() and alternate.stat().st_size==len(new),('alternate source not built',p)
  probe=machine_probe(p,old,new)
  result['profiles'][p]={'old_sha256':sha(old),'new_sha256':sha(new),'changed_bytes':changes,
   'in_place_code_window':'$5472-$54A7','operations':probe}
  result['total_old_new_calls']+=2*sum(x['case_count'] for x in probe.values())
 assert result['total_old_new_calls']>20000
 result['source_reference_alternate_checked']=True
 if args.stage_images:
  for p in PROFILES:res(p).write_bytes(patched[p])
  def run(*argv):
   print('RUN',*argv,flush=True)
   subprocess.run([sys.executable,*argv],cwd=ROOT,check=True)
  run('tools/generate_sources.py')
  for kind in ('reference','alternate'):
   run('tools/assemble_sources.py','--profile','all','--config-kind',kind)
   run('tools/build_hybrid.py','--config-kind',kind)
  for p in PROFILES:
   built=ROOT/'build_source/reference'/p/f'math_{p}_source_built.prg'
   assert built.read_bytes()==patched[p],('source reproduction failure',p,sha(built.read_bytes()),sha(patched[p]))
  for p in UNCHANGED:assert sha(res(p).read_bytes())==existing[p],('other resident changed',p)
  hybrid=ROOT/'build_hybrid/reference/v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg'
  assert sha(hybrid.read_bytes())==existing['v5_hybrid_lowzp'],'V5 unexpected donor inheritance'
  result['native_vice_checked']=False
  result['source_reference_alternate_checked']=True
  result['status']='PASS_SOURCE_BUILT'
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('ISSUE39 V2-V4 UMOD32_32 LATE ZERO PUBLIC-ABI QUALIFIED',result['total_old_new_calls'],'calls',flush=True)
if __name__=='__main__':main()
