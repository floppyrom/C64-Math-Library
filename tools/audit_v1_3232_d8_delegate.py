#!/usr/bin/env python3
"""Issue #39: paired public-ABI V1 32/32 D8 donor with bounded guard penalty.

Old resident reconstructed byte-exactly from the new one; checks both UDIV
and UMOD, including N/D preservation, carry and full-width remainder.
"""
from pathlib import Path
import hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from validate_unsigned_division import wr,rd,expected,api
from benchmark_unsigned_common_corpus import SPECS,corpus
from issue39_v1_3232_d8_parent import restore_pr61,PR61_SHA
from issue39_umod8_guard_parent import restore_umod8_parent
p=ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg'
new=restore_umod8_parent('v1_balanced',p.read_bytes());old=restore_pr61(new)
V5_SHA='9f59d7f8eb8d5cd78d0f01867418e77db5e867e06b9b43afe34df36ccea82dc2'
assert hashlib.sha256(restore_umod8_parent('v5_hybrid_lowzp',(ROOT/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg').read_bytes())).hexdigest()==V5_SHA
start=int.from_bytes(new[:2],'little');assert start==0x1000
cpus=[]
for image in (old,new):
    m=bytearray(65536);m[start:start+len(image)-2]=image[2:]
    cpu=CPU(m);cpu.d=0;cpu.call(0x3280,2000000);cpus.append(cpu)
rng=random.Random(0x39323208)
report={'status':'PASS','parent_sha256':PR61_SHA,
        'candidate_sha256':hashlib.sha256(new).hexdigest(),
        'v5_resident_sha256_unchanged':V5_SHA,'normal_zp_growth':0,
        'resident_prg_byte_growth':0,'max_allowed_non_d8_guard_penalty':14,
        'paired_machine_calls':0,'routines':{}}
for name in ('MATH_UDIV32_32','MATH_UMOD32_32'):
    spec=next(z for z in SPECS if z[0]==name)
    groups={'canonical':[(n,d) for n,d,_ in corpus(name,32,32,0,spec[7])[1]]}
    for width in (8,16,24,32):
        groups[f'd{width}_uniform']=[(rng.randrange(1<<32),rng.randrange(1,1<<width)) for _ in range(1024)]
    groups['d8_smallnumerator']=[(rng.randrange(1<<16),rng.randrange(1,256)) for _ in range(1024)]
    groups['d8_highnumerator']=[(rng.randrange(1<<31,1<<32),rng.randrange(1,256)) for _ in range(1024)]
    groups['d8_quota_edges']=[(min((1<<32)-1,max(0,d*q+r)),d)
        for d in range(1,256) for q in (0,1,2,3,7,127,65535,1<<24)
        for r in (0,min(d-1,3))]
    groups['zero_divisor']=[(rng.randrange(1<<32),0) for _ in range(512)]
    report['routines'][name]={}
    for group,pairs in groups.items():
        prev=now=fast=equal=slow=worst=0
        for n,d in pairs:
            observations=[]
            for cpu in cpus:
                wr(cpu.mem,0xc010,n,4);wr(cpu.mem,0xc014,d,4)
                cpu.mem[0xc030]=0xa5
                cy=cpu.call(api('v1_balanced')[name],4000000)
                observations.append((cy,rd(cpu.mem,0xc018,4),rd(cpu.mem,0xc01c,4),cpu.c,
                    rd(cpu.mem,0xc010,4),rd(cpu.mem,0xc014,4),cpu.mem[0xc030]))
            before,after=observations;q,r,c=expected(n,d,32,32)
            assert before[2:]==after[2:]==(r,c,n,d,0xa5),(name,group,n,d,observations)
            if name=='MATH_UDIV32_32':assert before[1]==after[1]==q,(name,group,n,d,observations)
            delta=after[0]-before[0]
            assert delta<=14,(name,group,hex(n),hex(d),delta,'excessive regression')
            assert not (0<d<256 and delta>0),(name,group,hex(n),hex(d),delta,'D8 regression')
            prev+=before[0];now+=after[0]
            fast+=delta<0;equal+=delta==0;slow+=delta>0;worst=max(worst,delta)
        report['paired_machine_calls']+=len(pairs)*2
        item={'cases':len(pairs),'old_mean_cycles':prev/len(pairs),
             'new_mean_cycles':now/len(pairs),'faster':fast,'equal':equal,
             'slower':slow,'worst_regression_cycles':worst}
        report['routines'][name][group]=item
        print(name,group,item,flush=True)
assert report['paired_machine_calls']==51812,report['paired_machine_calls']
out=ROOT/'validation/review/ISSUE39_V1_32_32_D8_DELEGATION.json'
out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print('ISSUE39 V1 32/32 D8 DONOR PASS',report['paired_machine_calls'],'paired machine calls')
