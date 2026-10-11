#!/usr/bin/env python3
"""Source-backed publication of issue #39 V1/V5 zero-high-byte legacy bypass."""
from pathlib import Path
import csv,hashlib,json
from common_corpus_ranking import load_common
from finalize_signed_core_reuse import rebuild_game_math_aggregate
R=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
CHANGED=('v1_balanced','v5_hybrid_lowzp')
OPS=('MATH_UDIV32_32','MATH_UMOD32_32')
DOC='docs/ISSUE39_UDIV32_ZERO_HIGH_BYPASS_2026-10-11.md'
REF_V1='5fb24ad166ecb0f8a3897d8523ce8224dfce947a0d0c5320f287dcefc98f4e6a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/'v1_balanced/resident/math_v1_balanced_game_math.prg')==REF_V1
hm=json.loads((R/'build_hybrid/reference/v5_hybrid_lowzp/source_build_manifest.json').read_text())
v5ref=R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg'
assert sha(v5ref)==hm['output_sha256'],(sha(v5ref),hm['output_sha256'])
for reportname,total in (('UNSIGNED_DIVISION_VALIDATION',822050),('SIGNED_DIVISION_VALIDATION',364533)):
    d=json.loads((R/'validation/review'/f'{reportname}.json').read_text())
    assert d['status']=='PASS' and d['summary']['machine_calls']==total
    assert len(d['profiles'])==5 and all(not x['errors'] for p in d['profiles'].values() for x in p.values())
unsigned=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
shared=load_common(R)
paired=json.loads((R/'validation/review/UDIV32_ZERO_HIGH_BYPASS_PAIRED.json').read_text())
assert paired['status']=='PASS' and paired['matched_calls']==8868
assert all(not x['slower'] and x['max_delta']==0 and x['min_delta']==-12 for p in paired['profiles'].values() for x in p['routines'].values())
assert shared['total_calls']==136335 and len(shared['routines'])==11
expected={'MATH_UDIV32_32':(358.00916086478566,2729,359.0776841333822),
          'MATH_UMOD32_32':(435.22463343108507,1705,436.899706744868)}
for name,(mean,count,before) in expected.items():
    rec=shared['routines'][name]
    assert rec['cases_per_profile']==count
    assert abs(rec['metrics']['v1_balanced']['mean_cycles']-mean)<1e-10
    assert abs(rec['metrics']['v5_hybrid_lowzp']['mean_cycles']-mean)<1e-10
    for p in PROFILES[1:4]:
        assert rec['metrics'][p]['mean_cycles'] < mean,(name,p)
# Legacy V1 GAME_MATH CSV uses a separate 6,801-call validator corpus.
# Preserve that corpus's cases, and never mislabel same-input means as its result.
p=R/'v1_balanced/PUBLIC_PERFORMANCE_GAME_MATH.csv'
with p.open(newline='') as f:rows=list(csv.DictReader(f))
found=set()
for row in rows:
    k=row['routine']
    if k not in ('UDIV32_32','UMOD32_32'):continue
    name='MATH_'+k
    # The legacy UMOD CSV was previously an alias to the UDIV validation mean.
    # Replace with its own independently validated remainder-only public mean.
    z=unsigned['profiles']['v1_balanced'][name]
    row['cases']=str(z['cases'])
    row['mean_cycles']=f"{z['mean_cycles']:.6f}"
    row['min_cycles']=str(z['min_cycles'])
    row['max_cycles']=str(z['max_cycles'])
    # Preserve the published shared-core alias; per-API corpora differ.
    found.add(k)
assert found=={'UDIV32_32','UMOD32_32'},found
with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader();w.writerows(rows)
rebuild_game_math_aggregate()
# Refresh all unsigned rows using one fixed input distribution per routine.
p=R/'PERFORMANCE.md';lines=p.read_text().splitlines()
for name,r in shared['routines'].items():
    i=[i for i,l in enumerate(lines) if l.startswith('| '+chr(96)+name+chr(96)+' |')]
    assert len(i)==1,(name,i)
    cells=lines[i[0]].split('|')
    for j,prof in enumerate(PROFILES):
        cells[j+3]=f" {r['metrics'][prof]['mean_cycles']:.6f} "
    lines[i[0]]='|'.join(cells)
p.write_text('\n'.join(lines)+'\n')
# V5 comparative table must describe the same corpus for V1 and V5.
p=R/'v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv'
with p.open(newline='') as f:rows=list(csv.DictReader(f))
matched=set()
for row in rows:
    if row['routine'] not in OPS:continue
    name=row['routine']
    val=shared['routines'][name]['metrics']
    a=val['v1_balanced']['mean_cycles']
    b=val['v5_hybrid_lowzp']['mean_cycles']
    row['v1_mean_cycles']=f'{a:.6f}'
    row['v5_mean_cycles']=f'{b:.6f}'
    row['improvement_percent']=f'{(a-b)*100/a:.6f}'
    row['provenance']='2026-10-11 issue39 identical-input source audit of shared V1/V5 q2q3 shortcut'
    matched.add(name)
# V5 hybrid file might not include 32_32 in its original sampled table;
# adding a line would break curated schema assumptions. Preserve that absence.
with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader();w.writerows(rows)
marker='2026-10-11 ISSUE39 V1/V5 32/32 ZERO-HIGH FALLBACK BYPASS'
msg=f"""{marker}
- Post-PR56: divisor high byte zero skips the provably impossible q2/q3 gate and jumps directly from qone to the original legacy divider. Three resident byte changes, no ZP/ABI/PRG span growth.
- Same-input V1/V5: UDIV32_32 359.077684→358.009161 cycles (2,729 calls/profile); UMOD32_32 436.899707→435.224633 (1,705/profile); 243 + 238 faster inputs/profile, exactly 12 cycles saved, no regressions among 8,868 paired calls.
- Five-profile 822,050 unsigned, 364,533 signed, 136,335 common corpus, 30,720 workloads; source relocation, V5 hybrid and full-resident VICE validated. Generated sources, both changelogs and hashes republished; unsigned DIV/MOD family remains open.
- Details: {DOC}
"""
for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
    p=R/name
    if marker not in p.read_text():p.write_text(msg+'\n'+p.read_text())
link=f'- Issue #39 zero-high-byte V1/V5 32/32 fallback bypass: {DOC}. Other unsigned architecture audits remain open.'
for name in ('README.md','USER_MANUAL.md'):
    p=R/name
    if link not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+link+'\n')
p=R/'RELEASE_STATUS.json';d=json.loads(p.read_text());d['date']='2026-10-11'
d['reference_prg_sha256']={q:sha(R/q/'resident'/f'math_{q}_game_math.prg') for q in PROFILES}
alts={}
for q in PROFILES[:-1]:
    m=json.loads((R/'build_source/alternate'/q/'source_build_manifest.json').read_text())
    alts[q]=m['output_sha256']
alts['v5_hybrid_lowzp']=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
d['alternate_prg_sha256']=alts
if isinstance(d.get('hybrid_v5'),dict):
    d['hybrid_v5']['reference_prg_sha256']=sha(v5ref)
    d['hybrid_v5']['alternate_prg_sha256']=alts['v5_hybrid_lowzp']
d['issue39_common_input_unsigned_divmod']['benchmark_sha256']=sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
d['issue39_common_input_unsigned_divmod']['arithmetic_binaries_changed']=True
d['issue39_v1_v5_32_32_zero_high_bypass_2026_10_11']={
 'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
 'pr56_parent':'eb2153b4dfd64c64437e0c89dda1db5dbf89bbdb',
 'v1_reference_sha256':REF_V1,'v5_reference_sha256':sha(v5ref),
 'normal_zp_growth_bytes':0,'resident_size_growth_bytes':0,'public_abi_changed':False,
 'executable_byte_deltas':3,'paired_calls':paired['matched_calls'],
 'paired_mismatches':0,'paired_slowdowns':0,'max_case_speedup_cycles':12,
 'v1_v5_common_input_cycles':{n:shared['routines'][n]['metrics']['v1_balanced']['mean_cycles'] for n in OPS},
 'all_profile_unsigned_calls':822050,'all_profile_signed_calls':364533,
 'common_input_calls':136335,'workload_calls':30720,'native_vice_full_resident_calls':320}
if isinstance(d.get('documentation'),dict):
    u=R/'USER_MANUAL.md'
    d['documentation'].update(user_manual_bytes=u.stat().st_size,
        user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=sha(u))
p.write_text(json.dumps(d,indent=2)+'\n')
print('ISSUE39 V1/V5 ZERO-HIGH DIVIDER BYPASS PUBLICATION PASS')
