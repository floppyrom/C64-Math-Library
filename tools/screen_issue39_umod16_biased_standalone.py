#!/usr/bin/env python3
"""Issue39: screen Repose biased UMOD16 under current V2-V5 complete public ABI.

RAM-only research. No resident replacement, no stable-source edits, no REU
cycle claim. The V1 UMOD16 alias has a different Q-producing contract.
"""
from pathlib import Path
import argparse,collections,hashlib,json,re,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import load,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus

SOURCE=R/'routines/standalone_lab/portable/mod_u16_biased_carry.asm'
MAPS={'aligned_e000':(0xe000,0xe400),
      'unaligned_e108':(0xe108,0xe500)}
PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
TESTS=[(n,d,k) for n,d,k in corpus('MATH_UMOD16',16,16,0,1024)[1]]
assert len(TESTS)==1705,len(TESTS)

def donor_source(kern,adapt):
 s=SOURCE.read_text()
 for k,v in {'KERNEL_CODE':kern,'KERNEL_ADAPTER':adapt,
             'INPUT_NUM':0xc010,'INPUT_DIV':0xc014,
             'OUTPUT_QUOT':0xc018,'OUTPUT_REM':0xc01c,
             'TEMP_ZP':0x70}.items():
  old_line=next(line for line in s.splitlines() if line.startswith(k+' = $'))
  s=s.replace(old_line,k+' = $'+format(v,'04X'))
  assert k+' = $'+format(v,'04X') in s,k
 return s

def run_case(cpu,entry,n,d):
 mem=cpu.mem
 wr(mem,0xc010,n,2);wr(mem,0xc014,d,2)
 mem[0xc013]=0xac;mem[0xc017]=0xdb
 mem[0xc018:0xc01c]=bytes((0x55,0x66,0x77,0x88))
 mem[0xc01c:0xc020]=bytes((0x99,0xaa,0xbb,0xcc))
 cpu.d=0;cpu.c=1
 sp=cpu.sp
 cyc=cpu.call(entry,4_000_000)
 got={'cycles':cyc,'q':rd(mem,0xc018,2),'r':rd(mem,0xc01c,2),
      'carry':cpu.c,'n':rd(mem,0xc010,2),'d':rd(mem,0xc014,2),
      'N3':mem[0xc013],'D3':mem[0xc017],
      'Q_high':bytes(mem[0xc01a:0xc01c]).hex(),
      'R_high':bytes(mem[0xc01e:0xc020]).hex(),
      'stack_balanced':cpu.sp==sp}
 assert got['r']==(n%d if d else 0) and got['carry']==int(d==0),(n,d,got)
 assert got['n']==n and got['d']==d and got['N3']==0xac and got['D3']==0xdb
 assert got['stack_balanced']
 return got

def screen():
 data={'status':'PASS','method':'identical input complete-call NMOS 6502 emulator cycles',
       'candidate_source':str(SOURCE.relative_to(R)),'corpus_size_per_profile':len(TESTS),
       'resident_changes':False,'extra_zp_bytes':2,'nested_jsr_stack_bytes':2,
       'external_code_ram_required':262,'profiles':{},'total_calls':0}
 for map_name,(kern,adapt) in MAPS.items():
  src=donor_source(kern,adapt)
  image,labels,_=Assembler().assemble(src)
  assert len(image)==262 and labels['FAST_UMOD16_PUBLIC']==adapt+15
  assert set(image).isdisjoint(range(0x1000,0xd000)) # resident unchanged
  assert set(image).isdisjoint(range(0xd000,0xe000)) # avoid I/O
  for profile in PROFILES:
   base,api=load(profile);donor,_=load(profile)
   for adr,byte in image.items():donor.mem[adr]=byte
   before=after=faster=tied=slower=0
   q_deltas=0
   classes=collections.defaultdict(lambda:[0,0,0])
   for n,d,k in TESTS:
    a=run_case(base,api['MATH_UMOD16'],n,d)
    b=run_case(donor,labels['FAST_UMOD16_PUBLIC'],n,d)
    if a['q']!=b['q']:q_deltas+=1
    delta=b['cycles']-a['cycles']
    before+=a['cycles'];after+=b['cycles']
    faster+=delta<0;tied+=delta==0;slower+=delta>0
    classes[str(k)][0]+=1
    classes[str(k)][1]+=a['cycles']
    classes[str(k)][2]+=b['cycles']
   metrics={'cases':len(TESTS),'resident_mean':before/len(TESTS),
            'standalone_mean':after/len(TESTS),
            'delta_mean':(after-before)/len(TESTS),
            'faster':faster,'equal':tied,'slower':slower,
            'Q16_output_different_cases':q_deltas,
            'class_means':{k:{'count':v[0],'resident_mean':v[1]/v[0],
                            'standalone_mean':v[2]/v[0]} for k,v in sorted(classes.items())}}
   data['profiles'].setdefault(profile,{})[map_name]=metrics
   data['total_calls']+=len(TESTS)*2
   print(profile,map_name,f"{metrics['resident_mean']:.6f}->{metrics['standalone_mean']:.6f}",
         'Q differences',q_deltas,'slower',slower,flush=True)
 assert data['total_calls']==len(TESTS)*2*len(PROFILES)*len(MAPS)
 print('ISSUE39 UMOD16 BIASED SCREEN PASS',data['total_calls'],'calls',flush=True)
 return data
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);args=parser.parse_args()
 report=screen()
 if args.out:args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')

  s,count=re.subn(regex,k+' = $'+format(v,'04X'),s)
  assert count==1,(k,count)
 return s

def run_case(cpu,entry,n,d):
 mem=cpu.mem
 wr(mem,0xc010,n,2);wr(mem,0xc014,d,2)
 mem[0xc013]=0xac;mem[0xc017]=0xdb
 mem[0xc018:0xc01c]=bytes((0x55,0x66,0x77,0x88))
 mem[0xc01c:0xc020]=bytes((0x99,0xaa,0xbb,0xcc))
 cpu.d=0;cpu.c=1
 sp=cpu.sp
 cyc=cpu.call(entry,4_000_000)
 got={'cycles':cyc,'q':rd(mem,0xc018,2),'r':rd(mem,0xc01c,2),
      'carry':cpu.c,'n':rd(mem,0xc010,2),'d':rd(mem,0xc014,2),
      'N3':mem[0xc013],'D3':mem[0xc017],
      'Q_high':bytes(mem[0xc01a:0xc01c]).hex(),
      'R_high':bytes(mem[0xc01e:0xc020]).hex(),
      'stack_balanced':cpu.sp==sp}
 assert got['r']==(n%d if d else 0) and got['carry']==int(d==0),(n,d,got)
 assert got['n']==n and got['d']==d and got['N3']==0xac and got['D3']==0xdb
 assert got['stack_balanced']
 return got

def screen():
 data={'status':'PASS','method':'identical input complete-call NMOS 6502 emulator cycles',
       'candidate_source':str(SOURCE.relative_to(R)),'corpus_size_per_profile':len(TESTS),
       'resident_changes':False,'extra_zp_bytes':2,'nested_jsr_stack_bytes':2,
       'external_code_ram_required':262,'profiles':{},'total_calls':0}
 for map_name,(kern,adapt) in MAPS.items():
  src=donor_source(kern,adapt)
  image,labels,_=Assembler().assemble(src)
  assert len(image)==262 and labels['FAST_UMOD16_PUBLIC']==adapt+15
  assert set(image).isdisjoint(range(0x1000,0xd000)) # resident unchanged
  assert set(image).isdisjoint(range(0xd000,0xe000)) # avoid I/O
  for profile in PROFILES:
   base,api=load(profile);donor,_=load(profile)
   for adr,byte in image.items():donor.mem[adr]=byte
   before=after=faster=tied=slower=0
   q_deltas=0
   classes=collections.defaultdict(lambda:[0,0,0])
   for n,d,k in TESTS:
    a=run_case(base,api['MATH_UMOD16'],n,d)
    b=run_case(donor,labels['FAST_UMOD16_PUBLIC'],n,d)
    if a['q']!=b['q']:q_deltas+=1
    delta=b['cycles']-a['cycles']
    before+=a['cycles'];after+=b['cycles']
    faster+=delta<0;tied+=delta==0;slower+=delta>0
    classes[str(k)][0]+=1
    classes[str(k)][1]+=a['cycles']
    classes[str(k)][2]+=b['cycles']
   metrics={'cases':len(TESTS),'resident_mean':before/len(TESTS),
            'standalone_mean':after/len(TESTS),
            'delta_mean':(after-before)/len(TESTS),
            'faster':faster,'equal':tied,'slower':slower,
            'Q16_output_different_cases':q_deltas,
            'class_means':{k:{'count':v[0],'resident_mean':v[1]/v[0],
                            'standalone_mean':v[2]/v[0]} for k,v in sorted(classes.items())}}
   data['profiles'].setdefault(profile,{})[map_name]=metrics
   data['total_calls']+=len(TESTS)*2
   print(profile,map_name,f"{metrics['resident_mean']:.6f}->{metrics['standalone_mean']:.6f}",
         'Q differences',q_deltas,'slower',slower,flush=True)
 assert data['total_calls']==len(TESTS)*2*len(PROFILES)*len(MAPS)
 print('ISSUE39 UMOD16 BIASED SCREEN PASS',data['total_calls'],'calls',flush=True)
 return data
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);args=parser.parse_args()
 report=screen()
 if args.out:args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
