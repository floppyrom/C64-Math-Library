#!/usr/bin/env python3
"""Issue39 source-backed V1 UDIV24/UMOD24 84->69 byte shared-subtraction screen."""
from pathlib import Path
import json,hashlib,random,sys,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler,CPU
from validate_unsigned_division import api,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus
from audit_issue39_unsigned_small_workloads import pairs,KINDS

PRG=ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg'
SOURCE=ROOT/'tools/candidates/issue39_v1_24by8_shared_subtraction.asm'
CURRENT_SHA='cae2afdf0271da338d110f2104a8530374214ef915d88a803c508bce9679bb4f'
original=PRG.read_bytes()
assert hashlib.sha256(original).hexdigest()==CURRENT_SHA,"Main V1 changed: rebaseline"
load=int.from_bytes(original[:2],'little'); assert load==0x1000
entry=0x1d00; off=2+entry-load
oldhex='ad10c08d18c0ad11c08d19c0ad12c08d1ac0a9008d1cc0a2180e18c02e19c02e1ac02e1cc0b014ad1cc0cd14c09018ed14c08d1cc0ee18c04c471dad1cc0ed14c08d1cc0ee18c0cad0cfa9008d1dc08d1ec01860'
assert original[off:off+84]==bytes.fromhex(oldhex),"V1 original loop drift"
assert original[2+0x7fa0-load:2+0x7fa8-load]==bytes.fromhex('ad15c0d0034c001d')
image,labels,_=Assembler().assemble(SOURCE.read_text())
assert len(image)==69 and labels['V1LAT_24_BY_8']==entry
assert set(image)==set(range(entry,entry+69))
assert bytes(image[i] for i in range(entry,entry+17))==original[off:off+17]
replacement=bytearray(original)
for addr,byte in image.items():replacement[2+addr-load]=byte
replacement[off+69:off+84]=bytes(15)
assert len(replacement)==len(original)
assert replacement[:off]==original[:off] and replacement[off+84:]==original[off+84:]
cpus=[]
for data in (original,replacement):
 m=bytearray(65536);m[load:load+len(data)-2]=data[2:]
 c=CPU(m);c.d=0;c.call(0x3280,2000000);cpus.append(c)
rng=random.Random(0x2438aa08)
stress=[((rng.randrange(1,256)<<16)|rng.randrange(65536),d)
        for d in range(1,256) for _ in range(16)]
wide=[(rng.randrange(1<<24),rng.randrange(256,1<<24)) for _ in range(2048)]
small=[(rng.randrange(1<<16),rng.randrange(1,256)) for _ in range(1024)]
other={k:pairs(24,k) for k in KINDS}
other.update(full_n24_d8=stress,wide_divisor_control=wide,n2_zero_control=small)
report={'status':'PASS','original_v1_sha256':CURRENT_SHA,
 'candidate_sha256':hashlib.sha256(replacement).hexdigest(),
 'public_abi_changed':False,'resident_file_size_growth':0,'normal_zp_growth':0,
 'old_core_bytes':84,'new_core_bytes':69,'source':str(SOURCE.relative_to(ROOT)),
 'machine_calls':0,'routines':{}}
API=api('v1_balanced')
for routine,count in (('MATH_UDIV24',4096),('MATH_UMOD24',1024)):
 groups={'canonical':[(n,d) for n,d,_ in corpus(routine,24,24,0,count)[1]],**other}
 report['routines'][routine]={}
 for name,tests in groups.items():
  before=after=faster=slower=equal=0;max_reg=0;max_gain=0
  for n,d in tests:
   got=[]
   for c in cpus:
    wr(c.mem,0xc010,n,3);wr(c.mem,0xc014,d,3)
    c.mem[0xc013]=0xa5;c.mem[0xc017]=0x5a
    c.c=1;sp=c.sp
    cy=c.call(api('v1_balanced')[routine],4000000)
    got.append((cy,rd(c.mem,0xc018,3),rd(c.mem,0xc01c,3),
                c.c,rd(c.mem,0xc010,3),rd(c.mem,0xc014,3),
                c.mem[0xc013],c.mem[0xc017],sp,c.sp))
   x,y=got;q,r,carry=expected(n,d,24,24)
   assert x[1:]==y[1:],(routine,name,hex(n),hex(d),'ABI disagreement',got)
   assert (y[1],y[2],y[3])==(q,r,carry),(routine,name,hex(n),hex(d),got)
   assert y[4:8]==(n,d,0xa5,0x5a) and all(z[-2]==z[-1] for z in got)
   a=y[0]-x[0];before+=x[0];after+=y[0]
   faster+=a<0;slower+=a>0;equal+=a==0
   max_reg=max(max_reg,a);max_gain=min(max_gain,a)
  result=dict(cases=len(tests),before_mean=before/len(tests),
              after_mean=after/len(tests),faster=faster,slower=slower,
              equal=equal,worst_regression=max_reg,best_gain=max_gain)
  assert not slower,(routine,name,result)
  print(routine,name,result,flush=True)
  report['routines'][routine][name]=result
  report['machine_calls']+=2*len(tests)
print('ISSUE39 V1 24/8 INNER LOOP SCREEN PASS',report['machine_calls'],flush=True)
p=argparse.ArgumentParser();p.add_argument('--out',type=Path);o=p.parse_args()
if o.out:o.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
