#!/usr/bin/env python3
"""Issue39 V1 UDIV24/UMOD24 rejected selector expansion: paired negative proof.

The existing narrow-divisor latency gate requires N2 >= D0 if D1=D2=0.
Skipping that condition may improve some small-divisor calls, but makes many
others hundreds of cycles slower. Deliberately DO NOT patch shipped sources.
"""
from pathlib import Path
import json,hashlib,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from benchmark_unsigned_common_corpus import SPECS,corpus
from validate_unsigned_division import api,wr,rd,expected
from audit_issue39_unsigned_small_workloads import pairs
from issue39_v1_3232_d8_parent import restore_pr61
PATH=ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg'
OUT=ROOT/'validation/review/ISSUE39_V1_UDIV24_NARROW_REJECTION.json'
# This negative screen certifies a *historical* rejected dispatch experiment.
# Reconstruct the exact PR60 parent after the newer 24/8 specialization:
# old selector restored; formerly empty low 128-byte island zeroed.
current=restore_pr61(PATH.read_bytes());lo=current[0]|current[1]<<8
assert current[2+0x7FA0-lo:2+0x7FA8-lo]==bytes.fromhex('ad15c0d0034c001d')
prior=bytearray(current)
prior[2+0x7FA0-lo:2+0x7FA0-lo+16]=bytes.fromhex('ad15c0d008ec14c090034cb07f4c9672')
prior[2+0x1D00-lo:2+0x1D80-lo]=bytes(0x80)
prg=bytes(prior)
assert hashlib.sha256(prg).hexdigest()=='97c3e04112335e5958653ac656771b9e11d1d4fede0f5c824b9169aa49b1b564'
m=bytearray(65536);m[lo:lo+len(prg)-2]=prg[2:]
assert m[0x7fa8:0x7faa]==bytes.fromhex('90 03'),'unexpected shipped gate'
candidate=m.copy();candidate[0x7fa8:0x7faa]=bytes.fromhex('ea ea')
cpus=(CPU(m),CPU(candidate))
for cpu in cpus:cpu.d=0;cpu.call(0x3280,2_000_000)
assert bytes(cpus[0].mem[0x7fa8:0x7faa])==bytes.fromhex('90 03')
assert bytes(cpus[1].mem[0x7fa8:0x7faa])==bytes.fromhex('ea ea')
report={'status':'REJECT','base_sha256':hashlib.sha256(prg).hexdigest(),
 'change':'skip V1LAT_GATE CPX/D0 BCC legacy, extend delegate to narrow N2<D0',
 'no_source_changes':True,'cases_checked':0,'machine_calls':0,'routines':{}}
rng=random.Random(0xC6392424)
extra=[(n<<16 | rng.randrange(65536),d) for d in range(1,256) for n in range(1,min(d,8))]
for name in ('MATH_UDIV24','MATH_UMOD24'):
 spec=next(x for x in SPECS if x[0]==name)
 groups={'canonical':[(n,d) for n,d,_ in corpus(name,spec[1],spec[2],spec[5],spec[7])[1]],
         'small_divisor':pairs(24,'small_divisor'),
         'power_of_two':pairs(24,'power_of_two'),
         'narrow_corner':extra}
 report['routines'][name]={}
 for group,inputs in groups.items():
    before=after=faster=equal=slower=0;min_delta=10**9;max_delta=-10**9
    for n,d in inputs:
        measurements=[]
        for cpu in cpus:
            wr(cpu.mem,0xc010,n,3);wr(cpu.mem,0xc014,d,3)
            cy=cpu.call(api('v1_balanced')[name],4_000_000)
            measurements.append((cy,rd(cpu.mem,0xc018,3),rd(cpu.mem,0xc01c,3),cpu.c,
                     rd(cpu.mem,0xc010,3),rd(cpu.mem,0xc014,3)))
        a,b=measurements;q,r,c=expected(n,d,24,24)
        assert a[2:]==b[2:]==(r,c,n,d),(name,group,hex(n),hex(d),measurements)
        if name=='MATH_UDIV24':assert a[1]==b[1]==q
        delta=b[0]-a[0]
        faster+=delta<0;equal+=delta==0;slower+=delta>0
        min_delta=min(min_delta,delta);max_delta=max(max_delta,delta)
        before+=a[0];after+=b[0]
    entry={'cases':len(inputs),'before_mean_cycles':before/len(inputs),
       'candidate_mean_cycles':after/len(inputs),'faster':faster,'equal':equal,
       'slower':slower,'largest_speedup_cycles':-min_delta,
       'worst_regression_cycles':max_delta}
    report['routines'][name][group]=entry
    report['cases_checked']+=len(inputs);report['machine_calls']+=2*len(inputs)
    print(name,group,entry,flush=True)
 assert report['routines'][name]['canonical']['worst_regression_cycles']>=2
 assert report['routines'][name]['narrow_corner']['slower']>report['routines'][name]['narrow_corner']['faster']
 assert report['routines'][name]['narrow_corner']['worst_regression_cycles']>=400
assert m[0x7fa8:0x7faa]==bytes.fromhex('90 03')
OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print('ISSUE39 V1 UDIV24/UMOD24 SELECTOR EXPANSION REJECTED',report['machine_calls'],'paired CPU executions')
