#!/usr/bin/env python3
"""Compare all five shipped UDIV32/16 and UMOD32/16 profiles on fixed scenario workloads.

This *supplements* the canonical broad same-input ranking; it does not revise
its weighted mean or replace wider varied-seed correctness tests.
"""
from __future__ import annotations
from pathlib import Path
import csv, hashlib, json, random, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import PROFILES, expected, load, rd, wr

ROUTINES=('MATH_UDIV32_16','MATH_UMOD32_16')
WORKLOADS=('uniform_32x16','numerator_24bit','numerator_16bit',
           'small_divisors','power_of_two_divisors','quotient_zero_or_one')
COUNT=512
SEED=0xC6393216
N,D,Q,R=0xC010,0xC014,0xC018,0xC01C
OUT_JSON=ROOT/'validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json'
OUT_CSV=ROOT/'benchmarks/UNSIGNED_3216_WORKLOAD_AUDIT.csv'

def pairs(name):
    rng=random.Random(SEED+WORKLOADS.index(name)*0x10001)
    v=[]
    for _ in range(COUNT):
        if name=='uniform_32x16': n,d=rng.getrandbits(32),rng.getrandbits(16)
        elif name=='numerator_24bit': n,d=rng.getrandbits(24),rng.getrandbits(16)
        elif name=='numerator_16bit': n,d=rng.getrandbits(16),rng.getrandbits(16)
        elif name=='small_divisors': n,d=rng.getrandbits(32),rng.randrange(1,256)
        elif name=='power_of_two_divisors': n,d=rng.getrandbits(32),1<<rng.randrange(16)
        elif name=='quotient_zero_or_one':
            d=rng.randrange(1,65536)
            n=rng.randrange(0,d) if rng.getrandbits(1)==0 else d+rng.randrange(0,d)
        else: raise ValueError(name)
        v.append((n,d))
    return v

def pct(sorted_cycles,p):return sorted_cycles[int((len(sorted_cycles)-1)*p)]

def audit():
    result={'status':'PASS','basis':'machine-code 6502 instruction cycles including public entry/RTS; not REU bus wall time',
            'seed':SEED,'samples_per_workload':COUNT,'profiles':list(PROFILES),
            'routines':list(ROUTINES),'workloads':{},'total_calls':0,
            'profile_resident_sha256':{}}
    cpus={};entries={}
    for profile in PROFILES:
        c,e=load(profile);cpus[profile]=c;entries[profile]=e
        p=ROOT/profile/'resident'/f'math_{profile}_game_math.prg'
        result['profile_resident_sha256'][profile]=hashlib.sha256(p.read_bytes()).hexdigest()
    rows=[]
    for name in WORKLOADS:
        case_list=pairs(name)
        rec={'case_sha256':hashlib.sha256(json.dumps(case_list,separators=(',',':')).encode()).hexdigest(),
             'cases':len(case_list),'routines':{}}
        for routine in ROUTINES:
            rec['routines'][routine]={}
            donor_cycle_trace=None
            for profile in PROFILES:
                cpu=cpus[profile];entry=entries[profile][routine]
                timings=[]
                for n,d in case_list:
                    wr(cpu.mem,N,n,4);wr(cpu.mem,D,d,2)
                    cycles=cpu.call(entry,4_000_000)
                    exp_q,exp_r,exp_c=expected(n,d,32,16)
                    ret_r,ret_c=rd(cpu.mem,R,2),cpu.c
                    assert (ret_r,ret_c)==(exp_r,exp_c),(name,routine,profile,n,d,ret_r,ret_c)
                    if routine=='MATH_UDIV32_16':
                        assert rd(cpu.mem,Q,4)==exp_q,(name,routine,profile,n,d)
                    assert (rd(cpu.mem,N,4),rd(cpu.mem,D,2))==(n,d),('input altered',routine,profile,n,d)
                    timings.append(cycles)
                if profile=='v2_pareto_fast':donor_cycle_trace=timings
                if profile in ('v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp'):
                    assert timings==donor_cycle_trace,('donor 32/16 cycle drift',name,routine,profile)
                avg=sum(timings)/len(timings);ordered=sorted(timings)
                dat={'cases':len(timings),'mean_cycles':avg,'median_cycles':pct(ordered,.5),
                     'p95_cycles':pct(ordered,.95),'min_cycles':ordered[0],
                     'max_cycles':ordered[-1],
                     'cycles_sha256':hashlib.sha256(json.dumps(timings,separators=(',',':')).encode()).hexdigest()}
                rec['routines'][routine][profile]=dat
                rows.append({'workload':name,'routine':routine,'profile':profile,
                             'cases':len(timings),'mean_cycles':f'{avg:.6f}',
                             'median_cycles':dat['median_cycles'],'p95_cycles':dat['p95_cycles'],
                             'min_cycles':dat['min_cycles'],'max_cycles':dat['max_cycles'],
                             'case_sha256':rec['case_sha256'],
                             'resident_sha256':result['profile_resident_sha256'][profile]})
                result['total_calls']+=len(timings)
        result['workloads'][name]=rec
        print(f'{name}: '+', '.join(f'{r}: '+', '.join(f'{p[:2]}={rec["routines"][r][p]["mean_cycles"]:.3f}' for p in ('v1_balanced','v2_pareto_fast')) for r in ROUTINES),flush=True)
    assert result['total_calls']==len(PROFILES)*len(ROUTINES)*len(WORKLOADS)*COUNT==30720
    OUT_JSON.parent.mkdir(parents=True,exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True,exist_ok=True)
    OUT_JSON.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    with OUT_CSV.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print('UNSIGNED 32/16 MULTI-WORKLOAD PASS',result['total_calls'],'validated public calls')
if __name__=='__main__':audit()