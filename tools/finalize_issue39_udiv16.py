#!/usr/bin/env python3
"""Publish issue #39 shared UDIV16/UMOD16 conditional branch simplification."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
EXPECT={
'v2_pareto_fast':'016b620bf3f4228238f0377e4b3128c2cc1ec4211a1f69f560f7f2d4bbc520fb',
'v3_reu_512k':'77c39d522c7a58856179f4a45187871fcbd940967c055095bc614a065da98425',
'v4_reu_16m':'7488a1f93a3237190be40626ac9945801620e86bc7cfeba76fd41fd06f196b70',
'v5_hybrid_lowzp':'7a843a703a51f402ec51a6e66f589cff020725784fff9f9cc0d9ef7b9bfbe91b'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
doc='docs/ISSUE39_UDIV16_BRANCH_TRANSPLANT_2026-10-11.md'
u=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
s=json.loads((R/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
for report in (u,s):
 assert report['status']=='PASS' and len(report['profiles'])==5
 assert all(z['errors']==0 for pr in report['profiles'].values() for z in pr.values())
assert u['summary']['machine_calls']==822050
for p,h in EXPECT.items():
 pr=R/p/'resident'/f'math_{p}_game_math.prg'
 assert sha(pr)==h,(p,sha(pr))
 q=u['profiles'][p]
 assert q['MATH_UDIV16']['cases']==4753 and q['MATH_UMOD16']['cases']==1553
baseline={
 'v2_pareto_fast':(127.754891647,195.931101095),
 'v3_reu_512k':(125.408794446,196.392788152),
 'v4_reu_16m':(125.605512308,195.511912428),
 'v5_hybrid_lowzp':(126.362297496,199.898261429)}
for p,(div,mod) in baseline.items():
 q=u['profiles'][p]
 assert abs(q['MATH_UDIV16']['mean_cycles']-div)<0.0000006,(p,'div',q['MATH_UDIV16']['mean_cycles'])
 assert abs(q['MATH_UMOD16']['mean_cycles']-mod)<0.0000006,(p,'mod',q['MATH_UMOD16']['mean_cycles'])
perf=R/'PERFORMANCE.md';lines=perf.read_text().splitlines()
for name in ('MATH_UDIV16','MATH_UMOD16'):
 selected=[i for i,s in enumerate(lines) if s.startswith('| '+chr(96)+name+chr(96)+' |')]
 assert len(selected)==1,(name,selected)
 i=selected[0];parts=lines[i].split('|')
 for j,p in enumerate(PROFILES):parts[j+3]=' '+f"{u['profiles'][p][name]['mean_cycles']:.6f}"+' '
 lines[i]='|'.join(parts)
perf.write_text('\n'.join(lines)+'\n')
marker='2026-10-11 ISSUE39 UDIV16/UMOD16 SHARED CONDITIONAL TRANSPLANT'
entry=f"""{marker}
- Removed an unreachable BCC after SEC in V2/V3/V4 UDIV16 shared producer; V5 inherits the source-level patch from V2.
- V2/V3/V4/V5 UDIV16 mean cycles: 127.754892 / 125.408794 / 125.605512 / 126.362297.
- V2/V3/V4/V5 UMOD16 mean cycles: 195.931101 / 196.392788 / 195.511912 / 199.898261.
- 25,224 deterministic paired calls: zero mismatches, zero regressions; 2 cycles saved on 248 calls across the eight public-entry corpora. No PRG span, stable ABI, ZP or stack-page change. V1 retained.
- Reference/alternate source rebuilt, all-profile unsigned and signed validators requalified, standalone source mirrors/catalog, benchmark tables, release-status/checksums regenerated.
- Private OptiSearch P40 supplied a constrained search candidate; this is a human-guided transformation, not a large generic OptiSearch discovery. The unsigned DIV/MOD campaign in issue #39 remains unchecked.
- Detail: {doc}
"""
for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 f=R/fn
 if marker not in f.read_text():f.write_text(entry+'\n'+f.read_text())
for fn in ('README.md','USER_MANUAL.md'):
 f=R/fn
 n='Issue #39 shared UDIV16/UMOD16 branch transplant'
 if n not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+f'- {n}: {doc}; unsigned family audit remains open.\n')
release=R/'RELEASE_STATUS.json';d=json.loads(release.read_text())
d['date']='2026-10-11'
d['reference_prg_sha256']={p:sha(R/p/'resident'/f'math_{p}_game_math.prg') for p in PROFILES}
d['alternate_prg_sha256']={}
for p in PROFILES[:4]:
 m=json.loads((R/'build_source/alternate'/p/'source_build_manifest.json').read_text())
 d['alternate_prg_sha256'][p]=m['output_sha256']
m=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())
d['alternate_prg_sha256']['v5_hybrid_lowzp']=m['output_sha256']
d.setdefault('hybrid_v5',{})['reference_prg_sha256']=EXPECT['v5_hybrid_lowzp']
d['hybrid_v5']['alternate_prg_sha256']=m['output_sha256']
d['issue39_udiv16_shared_branch_2026_10_11']={
 'status':'PASS','documentation':doc,'unsigned_family_complete':False,
 'paired_calls':25224,'paired_mismatches':0,'paired_slowdowns':0,
 'all_profile_unsigned_calls':u['summary']['machine_calls'],
 'all_profile_signed_calls':s['summary']['machine_calls'],
 'changed_prg_sha256':EXPECT,
 'new_mean_cycles':{p:{n:u['profiles'][p][n]['mean_cycles'] for n in ('MATH_UDIV16','MATH_UMOD16')} for p in EXPECT},
 'normal_zp_growth_bytes':0,'stack_page_reserved_growth_bytes':0}
if isinstance(d.get('documentation'),dict):
 m=R/'USER_MANUAL.md';d['documentation'].update(user_manual_bytes=m.stat().st_size,user_manual_lines=len(m.read_text().splitlines()),user_manual_sha256=sha(m))
release.write_text(json.dumps(d,indent=2)+'\n')
print('ISSUE39 UDIV16 publication metadata PASS')
