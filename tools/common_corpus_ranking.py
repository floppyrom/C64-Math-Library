"""Stable, audited cross-profile unsigned ranking basis.

Shipped PUBLIC_PROFILE_RESULTS remain historical per-profile validation
statistics. BEST_PROFILE_RESULTS must never compare those different seeds.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json

REPORT='validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json'
EXPECTED={
 'MATH_UDIV8','MATH_UMOD8','MATH_UDIV16','MATH_UMOD16',
 'MATH_UDIV24','MATH_UMOD24','MATH_UDIV32_16','MATH_UMOD32_16',
 'MATH_UDIV32_32','MATH_UMOD32_32','MATH_UDIV16_SHL8'
}
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')

def load_common(root:Path)->dict:
    f=root/REPORT
    if not f.is_file():raise AssertionError(f'missing common-input ranking proof: {REPORT}')
    data=json.loads(f.read_text())
    assert data.get('status')=='PASS' and set(data['routines'])==EXPECTED,'unsigned common-corpus family coverage incomplete'
    assert data['profile_order']==list(PROFILES),'benchmark profile layout changed'
    for p in PROFILES:
        binary=root/p/'resident'/f'math_{p}_game_math.prg'
        got=hashlib.sha256(binary.read_bytes()).hexdigest()
        assert data['sources'][p]['resident_sha256']==got,(p,'stale common-corpus proof',got)
    for name,x in data['routines'].items():
        assert x['status']=='PASS' and x['total_calls']==x['cases_per_profile']*len(PROFILES)
        assert x['cases_per_profile']>1000
        assert set(x['metrics'])==set(PROFILES)
        for p,m in x['metrics'].items():
            assert m['mean_cycles']>0 and m['max_cycles']>=m['min_cycles']>0,(name,p)
    return data

def rank_public(row:dict,common:dict)->dict:
    """Return a copy with comparable cycles for covered unsigned routines.

    Source/ZP metadata is preserved from the profile's published source row.
    """
    r=dict(row)
    name=r['routine']
    if name in common['routines']:
        q=common['routines'][name]
        z=q['metrics'][r['profile']]
        r.update(mean_cycles=f"{z['mean_cycles']:.6f}",
                 min_cycles=str(z['min_cycles']),max_cycles=str(z['max_cycles']),
                 cycle_basis=f"Issue39 identical-input corpus {q['cases_per_profile']} calls; {REPORT}")
    return r
