#!/usr/bin/env python3
"""PR67 V5-donor, all-profile public ABI and cycle-screen (research, no publication).

Must be called after generate_sources and both full reference/alternate
source assemblies. Resident swaps are temporary within an Actions checkout.
Only if the donor/hybrid proof passes do we evaluate all five new profiles.
Every resident is restored in finally, even if tests fail.
"""
from pathlib import Path
import subprocess,shutil,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
P=ROOT/'validation/review/ISSUE39_U16_PR67_HYBRID_ALLPROFILES_SCREEN.json'
OPS=('MATH_UDIV16','MATH_UMOD16','MATH_SDIV16','MATH_SMOD16')
def sha(b):return hashlib.sha256(b).hexdigest()
def run(*args):
 print('RUN',*args,flush=True)
 subprocess.run(args,cwd=ROOT,check=True)
def path(p):return ROOT/p/'resident'/f'math_{p}_game_math.prg'
def candidate(p):
 if p=='v5_hybrid_lowzp':return ROOT/'build_hybrid/reference/v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg'
 return ROOT/'build_source/reference'/p/f'math_{p}_source_built.prg'

def correct_diff(old,new,tag):
 assert old[:2]==new[:2] and len(old)==len(new),(tag,'resident shape changed')
 sites=[]
 assert old!=new,(tag,'expected strict gain but image unchanged')
 changes={i for i,(a,b) in enumerate(zip(old,new)) if a!=b}
 for i in sorted(changes):
  x=old[i:i+5];y=new[i:i+5]
  if x[0] in (0x90,0xb0) and x[1:3]==bytes.fromhex('034c') and y==bytes((0x4c,x[3],x[4],0xea,0xea)):
   sites.append(i)
 assert len(sites)==6,(tag,'expected six patch locations',[(hex(i-2+0x1000),old[i:i+5].hex(),new[i:i+5].hex()) for i in sites],len(changes))
 allowed={i+j for i in sites for j in range(5)}
 assert changes==allowed,(tag,'unintended changed bytes',[(hex(i-2+0x1000),f'{old[i]:02x}',f'{new[i]:02x}') for i in changes-allowed][:24])
 return [{'resident_address':hex(i-2+0x1000),'old':old[i:i+5].hex(),'new':new[i:i+5].hex()} for i in sites]

def main():
 old={p:path(p).read_bytes() for p in PROFILES}
 result={'status':'PASS','description':'full resident exact-diff source-built V2-V5 incl V5 imported donor; common corpus correctness/performance. Not yet VICE or release.', 'profiles':{}}
 try:
  for p in PROFILES[1:4]:
   cp=candidate(p).read_bytes()
   proof=correct_diff(old[p],cp,p)
   result['profiles'][p]={'old_sha256':sha(old[p]),'new_sha256':sha(cp),'sites':proof}
   path(p).write_bytes(cp)
  print('BUILD V5 with modified V2 donor',flush=True)
  run(sys.executable,'tools/build_hybrid.py','--config-kind','reference')
  v5=candidate('v5_hybrid_lowzp').read_bytes()
  proof=correct_diff(old['v5_hybrid_lowzp'],v5,'V5')
  result['profiles']['v5_hybrid_lowzp']={'old_sha256':sha(old['v5_hybrid_lowzp']),'new_sha256':sha(v5),'sites':proof}
  path('v5_hybrid_lowzp').write_bytes(v5)
  # The unchanged V1 must keep byte identity.
  assert path('v1_balanced').read_bytes()==old['v1_balanced']
  from sys import path as sp
  sp.insert(0,str(ROOT/'tools'))
  from validate_unsigned_division import load,expected,wr,rd
  from benchmark_unsigned_common_corpus import corpus
  from validate_signed_division import div_expected,load_profile
  results={}
  for p in PROFILES:
   cpu,entry=load(p);signed_cpu,signed_entry=load_profile(p)
   for op in OPS:
    is_signed=op[5]=='S'
    if is_signed:
     # Use identical signed operand pairs across all profiles.
     from audit_issue39_signed16_common import cases
     pairs=cases()
     # bounded 1000-case screen; the full paired script follows
     pairs=pairs[:1200]
     machine=signed_cpu;entrypoint=signed_entry[op]
    else:
     spec=(16,16,0,1024 if op=='MATH_UMOD16' else 2048)
     _,v=corpus(op,*spec)
     pairs=[(n,d) for n,d,_ in v]
     machine=cpu;entrypoint=entry[op]
    cycles=0;num=0
    for n,d in pairs:
     wr(machine.mem,0xc010,n,2);wr(machine.mem,0xc014,d,2)
     if is_signed:eq,er,carry=div_expected(n,16,d,16,16,16)
     else:eq,er,carry=expected(n,d,16,16,0)
     delta=machine.call(entrypoint,4_000_000)
     got=(rd(machine.mem,0xc018,2),rd(machine.mem,0xc01c,2),machine.c)
     if op.endswith('MOD16'):
      assert got[1:]==(er,carry),(p,op,hex(n),hex(d),got,(eq,er,carry))
     else:
      assert got==(eq,er,carry),(p,op,hex(n),hex(d),got,(eq,er,carry))
     assert rd(machine.mem,0xc010,2)==n and rd(machine.mem,0xc014,2)==d,(p,op,'mutated input')
     cycles+=delta;num+=1
    results[p+':'+op]={'calls':num,'mean_cycles':cycles/num}
    print(p,op,num,f'{cycles/num:.6f}',flush=True)
  result['paired_mean_cycles']=results
  P.parent.mkdir(parents=True,exist_ok=True);P.write_text(json.dumps(result,indent=2)+'\n')
  print('ISSUE39 PR67 V5 HYBRID + ALL5 PUBLIC ABI PROOF PASS',sum(v['calls'] for v in results.values()),flush=True)
 finally:
  for p in PROFILES: path(p).write_bytes(old[p])
if __name__=='__main__':main()
