#!/usr/bin/env python3
"""Issue #39: same-input profile audit for the six 8/16/24-bit unsigned APIs.

Sealed selection evidence, *not* certification of arithmetic optimality.
The seven workloads independently target divisors, quotient magnitude and zero.
Resident 6502 instruction cycles do not count physical REU/DMA transfer time.
"""
from pathlib import Path
import csv, hashlib, json, random, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import PROFILES,load,wr,rd,expected
WIDTHS=(8,16,24)
KINDS=('uniform','small_divisor','quotient_zero','quotient_one','quotient_2_to_7','power_of_two','divide_by_zero')
COUNT=256
N,D,Q,R=0xC010,0xC014,0xC018,0xC01C
OUT=ROOT/'validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json'
CSV=ROOT/'benchmarks/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.csv'

def pairs(bits,kind):
    mask=(1<<bits)-1
    rng=random.Random(0x63901011+bits*10000+KINDS.index(kind)*257)
    out=[]
    for _ in range(COUNT):
        if kind=='uniform':n,d=rng.randrange(mask+1),rng.randrange(mask+1)
        elif kind=='small_divisor':n,d=rng.randrange(mask+1),rng.randrange(1,min(256,mask+1))
        elif kind=='quotient_zero':
            d=rng.randrange(1,mask+1);n=rng.randrange(d)
        elif kind=='quotient_one':
            d=rng.randrange(1,mask+1);n=d+rng.randrange(min(d,mask-d+1))
        elif kind=='quotient_2_to_7':
            d=rng.randrange(1,max(2,mask//8+1));q=rng.randrange(2,8)
            n=q*d+rng.randrange(d)
        elif kind=='power_of_two':n,d=rng.randrange(mask+1),1<<rng.randrange(bits)
        elif kind=='divide_by_zero':n,d=rng.randrange(mask+1),0
        else:raise AssertionError(kind)
        assert 0<=n<=mask and 0<=d<=mask
        out.append((n,d))
    return out

def audit():
    cpus={};entries={};resident={}
    for p in PROFILES:
        cpus[p],entries[p]=load(p)
        resident[p]=hashlib.sha256((ROOT/p/'resident'/f'math_{p}_game_math.prg').read_bytes()).hexdigest()
    report={'status':'PASS','sample_count_per_workload':COUNT,'workloads':list(KINDS),
        'profiles':list(PROFILES),'basis':'public entry NMOS6502 instruction cycles, not REU bus wall time',
        'resident_sha256':resident,'total_calls':0,'results':{}}
    rows=[]
    for bits in WIDTHS:
        for op in ('UDIV','UMOD'):
            name=f'MATH_{op}{bits}'
            report['results'][name]={}
            for kind in KINDS:
                cases=pairs(bits,kind)
                traces={}
                case_sha=hashlib.sha256(json.dumps(cases,separators=(',',':')).encode()).hexdigest()
                for profile in PROFILES:
                    c=cpus[profile];entry=entries[profile][name];trace=[]
                    for n,d in cases:
                        wr(c.mem,N,n,bits//8);wr(c.mem,D,d,bits//8)
                        cycles=c.call(entry,4_000_000)
                        q,r,carry=expected(n,d,bits,bits)
                        assert (rd(c.mem,R,bits//8),c.c)==(r,carry),(name,kind,profile,n,d)
                        if op=='UDIV':assert rd(c.mem,Q,bits//8)==q,(name,kind,profile,n,d)
                        assert (rd(c.mem,N,bits//8),rd(c.mem,D,bits//8))==(n,d)
                        trace.append(cycles)
                    traces[profile]=trace
                    report['total_calls']+=len(trace)
                details={}
                for profile,trace in traces.items():
                    ordered=sorted(trace)
                    item={'mean_cycles':sum(trace)/len(trace),
                          'median_cycles':ordered[(COUNT-1)//2],
                          'p95_cycles':ordered[int((COUNT-1)*0.95)],
                          'max_cycles':ordered[-1],'min_cycles':ordered[0],
                          'cycles_sha256':hashlib.sha256(json.dumps(trace,separators=(',',':')).encode()).hexdigest()}
                    details[profile]=item
                    rows.append({'routine':name,'width':bits,'workload':kind,'profile':profile,
                         'cases':COUNT,'mean_cycles':f'{item["mean_cycles"]:.6f}',
                         'p95_cycles':item['p95_cycles'],'max_cycles':item['max_cycles'],
                         'case_sha256':case_sha,'resident_sha256':resident[profile]})
                report['results'][name][kind]={'cases_sha256':case_sha,'per_profile':details}
                print(name,kind,' '.join(f'{p.split("_")[0]}={details[p]["mean_cycles"]:.3f}' for p in PROFILES),flush=True)
    assert report['total_calls']==len(WIDTHS)*2*len(KINDS)*COUNT*len(PROFILES)==53760
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    with CSV.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    print('ISSUE39 SMALL-WIDTH WORKLOADS PASS',report['total_calls'])
if __name__=='__main__':audit()
