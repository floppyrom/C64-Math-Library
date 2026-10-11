#!/usr/bin/env python3
"""Paired, source-executed V5 32/32 narrow-denominator optimization certificate."""
from pathlib import Path
import hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from validate_unsigned_division import wr,rd,expected,api
from issue39_umod8_guard_parent import restore_umod8_parent
from benchmark_unsigned_common_corpus import SPECS,corpus
PROFILE='v5_hybrid_lowzp'
OLD_SHA='6255f93fdfcd35c2aa27085915e32dca86e3f641af96a1160cd38cf951f70d51'
NAMES=('MATH_UDIV32_32','MATH_UMOD32_32')
prg=restore_umod8_parent(PROFILE,(ROOT/PROFILE/'resident'/f'math_{PROFILE}_game_math.prg').read_bytes())
lo=prg[0]|prg[1]<<8
candidate=bytearray(65536);candidate[lo:lo+len(prg)-2]=prg[2:]
original=candidate.copy()
assert candidate[0x6859:0x685c]==bytes.fromhex('4c 00 1d')
assert candidate[0x1d00:0x1d03]==bytes.fromhex('ad 16 c0')
original[0x6859:0x685c]=bytes.fromhex('4c 00 c1')
original[0x1d00:0x1d15]=bytes(21)
baseline=bytes((lo&255,lo>>8))+bytes(original[lo:lo+len(prg)-2])
assert hashlib.sha256(baseline).hexdigest()==OLD_SHA
cpus=[CPU(original),CPU(candidate)]
for c in cpus:
 c.d=0
 c.call(0x3280,2_000_000)
assert bytes(cpus[0].mem[0x1d00:0x1d15])==bytes(21)
assert bytes(cpus[1].mem[0x1d00:0x1d03])==bytes.fromhex('ad 16 c0')
out={'status':'PASS','baseline_sha256':OLD_SHA,'candidate_sha256':hashlib.sha256(prg).hexdigest(),
 'normal_zp_growth':0,'resident_prg_growth':0,
 'method':'paired exact public 6502 cycles, quotient/remainder/carry and N/D preservation',
 'routines':{},'paired_inputs':0,'machine_calls':0}
for name in NAMES:
 spec=next(z for z in SPECS if z[0]==name)
 scenarios=[('canonical',[(n,d) for n,d,_ in corpus(name,spec[1],spec[2],spec[5],spec[7])[1]])]
 for group,count in [('narrow_16bit_divisor',1024),('middle_24bit_divisor',1024),('wide_32bit_divisor',1024),('divide_by_zero',64)]:
  rng=random.Random(0xC6393232+sum(map(ord,name))+sum(map(ord,{'narrow_16bit_divisor':'narrow_divisor','middle_24bit_divisor':'middle_divisor','wide_32bit_divisor':'wide_divisor','divide_by_zero':'zero_divisor'}[group])))
  if group=='narrow_16bit_divisor':cases=[(rng.getrandbits(32),rng.randrange(1,65536)) for _ in range(count)]
  elif group=='middle_24bit_divisor':cases=[(rng.getrandbits(32),rng.randrange(65536,1<<24)) for _ in range(count)]
  elif group=='wide_32bit_divisor':cases=[(rng.getrandbits(32),rng.randrange(1<<24,1<<32)) for _ in range(count)]
  else:cases=[(rng.getrandbits(32),0) for _ in range(count)]
  scenarios.append((group,cases))
 out['routines'][name]={}
 for group,pairs in scenarios:
  old_total=new_total=0
  hist={}
  for n,d in pairs:
   records=[]
   for cpu in cpus:
    wr(cpu.mem,0xc010,n,4);wr(cpu.mem,0xc014,d,4)
    cy=cpu.call(api(PROFILE)[name],4_000_000)
    q,r=rd(cpu.mem,0xc018,4),rd(cpu.mem,0xc01c,4)
    records.append((cy,q,r,cpu.c,rd(cpu.mem,0xc010,4),rd(cpu.mem,0xc014,4)))
   a,b=records
   exp=expected(n,d,32,32)
   assert a[1:]==b[1:],(name,group,hex(n),hex(d),a,b)
   assert (b[2],b[3],b[4],b[5])==(exp[1],exp[2],n,d)
   if name=='MATH_UDIV32_32':assert b[1]==exp[0]
   old_total+=a[0];new_total+=b[0]
   delta=b[0]-a[0];hist[delta]=hist.get(delta,0)+1
  item={'cases':len(pairs),'before_mean_cycles':old_total/len(pairs),
   'after_mean_cycles':new_total/len(pairs),
   'faster':sum(v for k,v in hist.items() if k<0),
   'equal':hist.get(0,0),'slower':sum(v for k,v in hist.items() if k>0),
   'worst_regression_cycles':max(0,max(hist)), 'maximum_saving_cycles':max(0,-min(hist)),
   'case_sha256':hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()}
  out['routines'][name][group]=item
  out['paired_inputs']+=len(pairs);out['machine_calls']+=2*len(pairs)
  print(name,group,f"{item['before_mean_cycles']:.3f}->{item['after_mean_cycles']:.3f}",
        'faster/equal/slower',item['faster'],item['equal'],item['slower'],flush=True)
expected_means={'MATH_UDIV32_32':(358.00916086478566,275.01319164529133),
 'MATH_UMOD32_32':(435.22463343108507,302.35307917888565)}
for name,(parent,new) in expected_means.items():
 z=out['routines'][name]['canonical']
 assert abs(z['before_mean_cycles']-parent)<1e-8
 assert abs(z['after_mean_cycles']-new)<1e-8
 assert z['worst_regression_cycles']==10
 assert not out['routines'][name]['narrow_16bit_divisor']['slower']
 assert out['routines'][name]['middle_24bit_divisor']['worst_regression_cycles']==10
assert out['paired_inputs']==10706 and out['machine_calls']==21412
dest=ROOT/'validation/review/ISSUE39_V5_32_32_NARROW_DELEGATION.json'
dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('ISSUE39 V5 32/32 NARROW DELEGATE PASS',out['machine_calls'],'paired machine calls')
