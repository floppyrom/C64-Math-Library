#!/usr/bin/env python3
"""Paired same-input performance/ABI audit for unsigned DIV/MOD across public profiles.

This report is suitable for *cross-profile* comparisons, unlike the larger
varied-seed correctness validator. Never derive an all-purpose profile ranking
from one weighted mean: record workload classes and worst cases separately.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, random, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import PROFILES, edge, expected, load, rd, wr

# The same fixed list is passed to all five profiles for each API. The list is
# generated independently from the per-profile correctness-suite seeds.
SPECS=[
 ('MATH_UDIV8',8,8,8,8,0,False,2048),
 ('MATH_UMOD8',8,8,8,8,0,True,2048),
 ('MATH_UDIV16',16,16,16,16,0,False,2048),
 ('MATH_UMOD16',16,16,16,16,0,True,1024),
 ('MATH_UDIV24',24,24,24,24,0,False,4096),
 ('MATH_UMOD24',24,24,24,24,0,True,1024),
 ('MATH_UDIV32_16',32,16,32,16,0,False,2048),
 ('MATH_UMOD32_16',32,16,32,16,0,True,1024),
 ('MATH_UDIV32_32',32,32,32,32,0,False,2048),
 ('MATH_UMOD32_32',32,32,32,32,0,True,1024),
 ('MATH_UDIV16_SHL8',16,16,24,16,8,False,2048),
]
N,D,Q,R=0xc010,0xc014,0xc018,0xc01c

def corpus(name,nb,db,shift,random_count):
    # Preserve the originally investigated UDIV24/UMOD24 corpora exactly.
    if name=='MATH_UDIV24': seed=0x12345872
    elif name=='MATH_UMOD24': seed=0x19840713
    else: seed=0xC6390000+sum((i+1)*ord(c) for i,c in enumerate(name))
    rng=random.Random(seed)
    pairs=[(n,d,'edges') for n in edge(nb) for d in edge(db)]
    pairs.extend((rng.randrange(1<<nb),rng.randrange(1<<db),'random') for _ in range(random_count))
    if not name=='MATH_UMOD24':
        pairs.extend((rng.randrange(1<<nb),0,'zero') for _ in range(128))
    # Deliberate quotient-stress *shared inputs*. Not applied to DIV24 because
    # its historical identical-corpus measurements are a useful frozen anchor.
    if nb>8 and nb!=24:
        for d in (1,2,3,7,15,255,256,65535):
            if d<(1<<db):
                for n in ((1<<nb)-1,(1<<(nb-1))-1,((1<<nb)-1)//2):
                    pairs.append((n,d,'stress'))
    return seed,pairs

def band(n,d,shift):
    if d==0:return 'divisor_zero'
    q=(n<<shift)//d
    if q==0:return 'quotient_0'
    if q==1:return 'quotient_1'
    if q<=9:return 'quotient_2_to_9'
    if q<=255:return 'quotient_10_to_255'
    return 'quotient_256_plus'

def percentile(v,p):
    a=sorted(v)
    return a[min(len(a)-1,int((len(a)-1)*p))]

def run_bench(names=None):
    chosen=[x for x in SPECS if names is None or x[0] in names]
    cpus,entries={},{}
    for p in PROFILES: cpus[p],entries[p]=load(p)
    report={'status':'PASS','contract':'identical deterministic operand pairs across V1-V5; independent varied-seed correctness regression retained',
            'method':'6502 machine-code instruction cycles from public API call including RTS; no DMA bus-cycle claim',
            'profile_order':PROFILES,'sources':{},'routines':{},'cautions':[
                'Each operation has a separate input distribution; never rank unlike operations using unweighted row averages',
                'Structured edge cases overrepresent small divisors relative to uniformly random 24/32-bit inputs',
                'The existing varied-seed correctness validator has separately seeded operands and must not be used to rank profiles',
                'Do not compare REU physical bus-time, physical hardware wait states or Turbo overlays using instruction counts']}
    for p in PROFILES:
        path=ROOT/p/'resident'/f'math_{p}_game_math.prg'
        report['sources'][p]={'resident_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    for name,nb,db,qb,rb,shift,rem_only,count in chosen:
        seed,pairs=corpus(name,nb,db,shift,count)
        stats={p:[] for p in PROFILES}
        by_band={p:defaultdict(list) for p in PROFILES}
        by_kind={p:defaultdict(list) for p in PROFILES}
        exact={p:True for p in PROFILES}
        means_by_case=[]
        for n,d,kind in pairs:
            eq,er,ec=expected(n,d,qb,rb,shift)
            mark=band(n,d,shift);samples={}
            for p in PROFILES:
                cpu=cpus[p]
                wr(cpu.mem,N,n,(nb+7)//8);wr(cpu.mem,D,d,(db+7)//8)
                cy=cpu.call(entries[p][name],4_000_000)
                q=rd(cpu.mem,Q,(qb+7)//8);r=rd(cpu.mem,R,(rb+7)//8)
                ok=(r,cpu.c)==(er,ec) if rem_only else (q,r,cpu.c)==(eq,er,ec)
                if not ok or rd(cpu.mem,N,(nb+7)//8)!=n or rd(cpu.mem,D,(db+7)//8)!=d:
                    raise AssertionError((name,p,hex(n),hex(d),cy,(q,r,cpu.c),(eq,er,ec)))
                stats[p].append(cy);by_band[p][mark].append(cy);by_kind[p][kind].append(cy);samples[p]=cy
            baseline=samples[PROFILES[1]]
            for p in PROFILES:
                if samples[p]!=baseline: exact[p]=False
        metrics={}
        for p in PROFILES:
            a=stats[p]
            metrics[p]={'mean_cycles':sum(a)/len(a),'min_cycles':min(a),'p95_cycles':percentile(a,.95),
                        'max_cycles':max(a),'class_means':{k:sum(v)/len(v) for k,v in sorted(by_band[p].items())},
                        'selection_means':{k:sum(v)/len(v) for k,v in sorted(by_kind[p].items())}}
        report['routines'][name]={'status':'PASS','random_seed':hex(seed),'cases_per_profile':len(pairs),
             'total_calls':len(pairs)*len(PROFILES),'same_cases_sha256':hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest(),
             'metrics':metrics,'exact_per_call_cycles_equal_to_v2':exact}
        print(name,len(pairs),' '.join(f'{p.split("_")[0]}={metrics[p]["mean_cycles"]:.3f}' for p in PROFILES),flush=True)
    report['total_calls']=sum(x['total_calls'] for x in report['routines'].values())
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--only',nargs='*',choices=[x[0] for x in SPECS])
    ap.add_argument('--out',type=Path,default=ROOT/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
    args=ap.parse_args()
    report=run_bench(set(args.only) if args.only else None)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    # Same-input table used to audit rankings; historical per-profile validation
    # means are kept as separate coverage evidence.
    from common_corpus_ranking import REPORT
    if args.out.resolve()==(ROOT/REPORT).resolve():
        table=ROOT/'benchmarks/UNSIGNED_COMMON_PROFILE_RESULTS.csv'
        fields=['routine','profile','mean_cycles','min_cycles','p95_cycles','max_cycles',
                'cases','resident_sha256','same_cases_sha256','cycle_basis']
        with table.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
            for routine,z in sorted(report['routines'].items()):
                for profile in PROFILES:
                    v=z['metrics'][profile]
                    w.writerow({'routine':routine,'profile':profile,
                        'mean_cycles':f"{v['mean_cycles']:.6f}",
                        'min_cycles':v['min_cycles'],'p95_cycles':v['p95_cycles'],
                        'max_cycles':v['max_cycles'],'cases':z['cases_per_profile'],
                        'resident_sha256':report['sources'][profile]['resident_sha256'],
                        'same_cases_sha256':z['same_cases_sha256'],
                        'cycle_basis':'same-input deterministic source-executed 6502 instruction cycles'})
    print('COMMON CORPUS PASS',report['total_calls'],'paired machine-code calls')
if __name__=='__main__':main()
