#!/usr/bin/env python3
"""Regenerate public benchmark/source indexes from profile manifests.

STANDALONE_RESULTS.csv is intentionally curated because its rows may use
external or specialized benchmark corpora. This tool refreshes its source
hashes, regenerates PUBLIC_PROFILE_RESULTS.csv, then rebuilds
routines/SOURCE_CATALOG.csv.
"""
from __future__ import annotations
import csv, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def read_csv(p:Path):
    with p.open(newline='') as f: return list(csv.DictReader(f))
def category(name:str)->str:
    for prefix,cat in [('mul_','multiply'),('div_','divide'),('mod_','modulo'),('recip_','fixed'),('sin_','trig'),('cos_','trig'),('sincos_','trig'),('atan2_','trig'),('isqrt_','root'),('normalize_','vector'),('dist_','game')]:
        if name.startswith(prefix): return cat
    return 'other'

def main():
    manifests={p:{r['legacy_api']:r for r in read_csv(ROOT/p/'standalone/MANIFEST.csv')} for p in PROFILES}
    public=read_csv(ROOT/'docs/CONSOLIDATED_ROUTINE_TABLE.csv')
    fields=list(public[0].keys())+['source_path','source_sha256']
    with (ROOT/'benchmarks/PUBLIC_PROFILE_RESULTS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\\n');w.writeheader()
        for r in public:
            m=manifests[r['profile']][r['routine']]
            sp=f"{r['profile']}/standalone/{m['file']}"
            rr=dict(r);rr['source_path']=sp;rr['source_sha256']=sha(ROOT/sp);w.writerow(rr)

    # One-row-per-canonical-routine convenience index: fastest shipped profile.
    published_rows=read_csv(ROOT/'benchmarks/PUBLIC_PROFILE_RESULTS.csv')
    best={}
    for r in published_rows:
        k=r['canonical_name']
        try: cyc=float(r['mean_cycles'])
        except Exception: continue
        if k not in best or cyc < float(best[k]['mean_cycles']):
            best[k]=r
    best_fields=['canonical_name','routine','profile','mean_cycles','min_cycles','max_cycles','zp_bytes','stack_page_reserved_bytes','cycle_basis','source_path','source_sha256']
    with (ROOT/'benchmarks/BEST_PROFILE_RESULTS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=best_fields,lineterminator='\\n');w.writeheader()
        for k in sorted(best):
            r=best[k];w.writerow({x:r.get(x,'') for x in best_fields})

    standalone_path=ROOT/'benchmarks/STANDALONE_RESULTS.csv'
    standalone=read_csv(standalone_path)
    sfields=list(standalone[0].keys())
    with standalone_path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=sfields,lineterminator='\\n');w.writeheader()
        for r in standalone:
            r=dict(r);r['source_sha256']=sha(ROOT/r['source_path']);w.writerow(r)

    pub_index={(r['profile'],r['routine']):r for r in public}
    catalog=[]
    for p in PROFILES:
        for api,m in manifests[p].items():
            pr=pub_index[(p,api)];sp=f"{p}/standalone/{m['file']}"
            catalog.append({
                'scope':'shipped-profile','category':category(m['canonical_name']),'profile':p,
                'legacy_api':api,'canonical_name':m['canonical_name'],'variant':'',
                'mean_cycles':pr['mean_cycles'],'zp_bytes':pr['zp_bytes'],
                'stack_page_reserved_bytes':pr['stack_page_reserved_bytes'],'source_path':sp,
                'source_sha256':sha(ROOT/sp),'validation_path':'benchmarks/PUBLIC_PROFILE_RESULTS.csv',
                'status':'shipped','notes':f"alias_of={m['alias_of']}" if m['alias_of'] else ''})
    for r in standalone:
        catalog.append({
            'scope':'standalone-alternative','category':r['category'],'profile':'','legacy_api':'',
            'canonical_name':r['canonical_name'],'variant':r['variant'],'mean_cycles':r['mean_cycles'],
            'zp_bytes':r['zp_bytes'],'stack_page_reserved_bytes':r['stack_page_reserved_bytes'],
            'source_path':r['source_path'],'source_sha256':sha(ROOT/r['source_path']),
            'validation_path':r['validation_path'],'status':r['status'],'notes':r['notes']})
    catalog.sort(key=lambda x:(x['category'],x['canonical_name'],x['scope'],x['profile'],x['variant']))
    cfields=['scope','category','profile','legacy_api','canonical_name','variant','mean_cycles','zp_bytes','stack_page_reserved_bytes','source_path','source_sha256','validation_path','status','notes']
    with (ROOT/'routines/SOURCE_CATALOG.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cfields,lineterminator='\\n');w.writeheader();w.writerows(catalog)
    print(f'PUBLIC INDEXES UPDATED: {len(public)} shipped rows, {len(standalone)} standalone alternatives, {len(catalog)} catalog rows')

if __name__=='__main__': main()
