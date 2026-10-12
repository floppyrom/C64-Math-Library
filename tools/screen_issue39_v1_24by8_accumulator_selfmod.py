#!/usr/bin/env python3
"""Issue39: exact public ABI old/new screen for 68-byte self-modifying accumulator 24÷8 engine.

Runs on current post-PR78 main WITHOUT modifying any release image or API.
"""
from pathlib import Path
import argparse, hashlib, json, random, sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from mini6502 import Assembler,CPU
from validate_unsigned_division import api,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus
from audit_issue39_unsigned_small_workloads import pairs,KINDS

OLD_SHA='28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0'
PRG=R/'v1_balanced/resident/math_v1_balanced_game_math.prg'
SOURCE=R/'tools/candidates/issue39_v1_24by8_accumulator_selfmod.asm'
b=PRG.read_bytes()
assert hashlib.sha256(b).hexdigest()==OLD_SHA, 'unexpected PR78 base'
load=int.from_bytes(b[:2], 'little')
assert load==0x1000
entry=0x1d00;off=2+entry-load
old=bytes(b[off:off+84]);assert old[69:]==bytes(15), 'old island not fully zeroed'
candidate,labels,_=Assembler().assemble(SOURCE.read_text())
assert labels['V1LAT_24_BY_8']==entry and len(candidate)==68
assert sorted(candidate)==list(range(entry,entry+68))
assert old[:17]==bytes(candidate[i] for i in range(entry,entry+17)), 'entry/state setup has unexpectedly changed'
patched=bytearray(b)
for addr,byte in candidate.items():patched[2+addr-load]=byte
patched[off+68:off+84]=bytes(16)
assert len(b)==len(patched) and patched[:off]==b[:off] and patched[off+84:]==b[off+84:]
cpus=[]
for raw in (b,patched):
 m=bytearray(65536)
 m[load:load+len(raw)-2]=raw[2:]
 c=CPU(m);c.d=0;c.call(0x3280,2_000_000);cpus.append(c)
A=api('v1_balanced')
rng=random.Random(0x2469dcad)
stress=[((rng.randrange(1,256)<<16)|rng.randrange(65536),d) for d in range(1,256) for _ in range(16)]
wide=[(rng.randrange(1<<24),rng.randrange(256,1<<24)) for _ in range(2048)]
small=[(rng.randrange(1<<16),rng.randrange(1,256)) for _ in range(1024)]
other={k:pairs(24,k) for k in KINDS}
other.update(full_n24_d8=stress,wide_divisor_control=wide,n2_zero_control=small)
report={'status':'PASS','original_v1_sha256':OLD_SHA,'new_v1_sha256':hashlib.sha256(patched).hexdigest(),
 'source':'tools/candidates/issue39_v1_24by8_accumulator_selfmod.asm','scope':'RAM-only, self-modifying in-memory candidate; NOT shipped, NOT ROM-safe',
 'old_core_bytes':69,'new_core_bytes':68,'normal_zp_growth':0,'stack_growth':0,'abi_changed':False,
 'paired_machine_calls':0,'regressions':0,'routines':{}}
for routine,count in (('MATH_UDIV24',4096),('MATH_UMOD24',1024)):
 groups={'canonical':[(n,d) for n,d,_ in corpus(routine,24,24,0,count)[1]],**other}
 report['routines'][routine]={}
 for name,tests in groups.items():
  before=after=faster=slower=equal=0;best=0;worst=0
  for n,d in tests:
   got=[]
   for c in cpus:
    wr(c.mem,0xc010,n,3);wr(c.mem,0xc014,d,3)
    c.mem[0xc013]=0xa5;c.mem[0xc017]=0x5a;c.mem[0xc01f]=0xd7
    c.c=1;c.d=0;sp=c.sp
    cy=c.call(A[routine],4_000_000)
    got.append((cy,rd(c.mem,0xc018,3),rd(c.mem,0xc01c,3),c.c,rd(c.mem,0xc010,3),rd(c.mem,0xc014,3),c.mem[0xc013],c.mem[0xc017],c.mem[0xc01f],sp,c.sp))
   x,y=got;q,r,carry=expected(n,d,24,24)
   assert x[1:]==y[1:],(routine,name,hex(n),hex(d),'ABI disagreement',got)
   assert y[1:]==(q,r,carry,n,d,0xa5,0x5a,0xd7,y[9],y[10]),(routine,name,hex(n),hex(d),got)
   assert x[9]==x[10] and y[9]==y[10]
   delta=y[0]-x[0];before+=x[0];after+=y[0]
   faster+=delta<0;slower+=delta>0;equal+=delta==0
   best=min(best,delta);worst=max(worst,delta)
  assert slower==0,(routine,name,slower)
  report['routines'][routine][name]=dict(cases=len(tests),before_mean=before/len(tests),after_mean=after/len(tests),faster=faster,equal=equal,slower=slower,best_delta=best,worst_delta=worst)
  report['paired_machine_calls']+=len(tests)*2
  report['regressions']+=slower
  print(routine,name,len(tests),f'{before/len(tests):.6f}->{after/len(tests):.6f}','faster',faster,'tied',equal,'slower',slower,flush=True)
print('ISSUE39 V1 ACCUMULATOR SELFMOD SCREEN PASS',report['paired_machine_calls'],'old/new calls',flush=True)
a=argparse.ArgumentParser();a.add_argument('--out',type=Path);args=a.parse_args()
if args.out:args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
