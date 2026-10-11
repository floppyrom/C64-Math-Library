#!/usr/bin/env python3
"""Issue39: paired archived PR60 V1 UDIV24/UMOD24 vs specialized 24/8 path.

The prior release is reconstructed from the new resident by undoing only
the old gate and the previously unused 128-byte low-memory island. A fixed
SHA-256 asserts byte-identical provenance. NO corpus or slow-tail exemptions.
"""
from pathlib import Path
import hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from validate_unsigned_division import api,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus
from audit_issue39_unsigned_small_workloads import pairs,KINDS
from issue39_v1_3232_d8_parent import restore_pr61
BASE_SHA='97c3e04112335e5958653ac656771b9e11d1d4fede0f5c824b9169aa49b1b564'
P=ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg'
OUT=ROOT/'validation/review/ISSUE39_V1_UDIV24_BYTE8_PAIRED.json'
new=restore_pr61(P.read_bytes());lo=int.from_bytes(new[:2],'little')
assert lo==0x1000 and new[2+0x7FA0-lo:2+0x7FA8-lo]==bytes.fromhex('ad15c0d0034c001d')
assert new[2+0x1D00-lo:2+0x1D03-lo]==bytes.fromhex('ad10c0')
prior=bytearray(new)
prior[2+0x7FA0-lo:2+0x7FB0-lo]=bytes.fromhex('ad15c0d008ec14c090034cb07f4c9672')
prior[2+0x1D00-lo:2+0x1D80-lo]=bytes(128)
assert hashlib.sha256(prior).hexdigest()==BASE_SHA,'exact archived resident reconstruction failed'
cpu=[]
for blob in (prior,new):
 m=bytearray(65536);m[lo:lo+len(blob)-2]=blob[2:]
 c=CPU(m);c.d=0;c.call(0x3280,2000000);cpu.append(c)
rng=random.Random(0x63924808)
stress=[((rng.randrange(1,256)<<16)|rng.randrange(65536),d)
        for d in range(1,256) for i in range(16)]
wide=[(rng.randrange(1<<24),rng.randrange(256,1<<24)) for _ in range(4096)]
small_n=[(rng.randrange(1<<16),rng.randrange(1,256)) for _ in range(1024)]
classes={k:pairs(24,k) for k in KINDS}
classes.update(full_d8_stress=stress,wide_divisor_no_change=wide,
               n2_zero_divisor_8bit=small_n)
report={'status':'PASS','parent_sha256':BASE_SHA,
 'candidate_sha256':hashlib.sha256(new).hexdigest(),
 'source':'source-backed 24/8, quotient in MATH_Q and 8-bit remainder in MATH_R',
 'normal_zp_growth_bytes':0,'public_abi_changed':False,
 'changed_profile':'v1_balanced','resident_byte_growth':0,
 'paired_machine_calls':0,'routines':{}}
for name,count in (('MATH_UDIV24',4096),('MATH_UMOD24',1024)):
 groups={'canonical':[(n,d) for n,d,_ in corpus(name,24,24,0,count)[1]],**classes}
 report['routines'][name]={}
 for group,vectors in groups.items():
  t0=t1=faster=slower=equal=0;max_delta=-100000;min_delta=100000
  for n,d in vectors:
   got=[]
   for c in cpu:
    wr(c.mem,0xC010,n,3);wr(c.mem,0xC014,d,3)
    c.mem[0xC013]=0xA5;c.mem[0xC017]=0x5A
    cycles=c.call(api('v1_balanced')[name],4000000)
    got.append((cycles,rd(c.mem,0xC018,3),rd(c.mem,0xC01C,3),
                c.c,rd(c.mem,0xC010,3),rd(c.mem,0xC014,3),
                c.mem[0xC013],c.mem[0xC017]))
   a,b=got;q,r,carry=expected(n,d,24,24)
   assert a[2:4]==b[2:4]==(r,carry),(name,group,n,d,got)
   if name=='MATH_UDIV24':assert a[1]==b[1]==q,(name,group,n,d,got)
   assert a[4:]==b[4:]==(n,d,0xA5,0x5A),(name,group,n,d,got)
   delta=b[0]-a[0];t0+=a[0];t1+=b[0]
   faster+=delta<0;slower+=delta>0;equal+=delta==0
   max_delta=max(max_delta,delta);min_delta=min(min_delta,delta)
  item={'cases':len(vectors),'parent_mean_cycles':t0/len(vectors),
    'candidate_mean_cycles':t1/len(vectors),'faster':faster,'slower':slower,
    'equal':equal,'best_delta_cycles':min_delta,'worst_delta_cycles':max_delta}
  assert not slower,(name,group,'regression veto',item)
  report['routines'][name][group]=item;report['paired_machine_calls']+=2*len(vectors)
  print(name,group,item,flush=True)
 assert report['routines'][name]['full_d8_stress']['faster']==4080
assert report['paired_machine_calls']==56580,report['paired_machine_calls']
OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print('ISSUE39 V1 24/8 PAIRED PASS',report['paired_machine_calls'])
