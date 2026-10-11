#!/usr/bin/env python3
"""Source-backed publication of issue #39 V1/V5 high-byte bounded 32/32 q=2/3."""
from pathlib import Path
import csv,hashlib,json
from common_corpus_ranking import load_common
from finalize_signed_core_reuse import rebuild_game_math_aggregate
R=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
CHANGED=('v1_balanced','v5_hybrid_lowzp')
OPS=('MATH_UDIV32_32','MATH_UMOD32_32')
DOC='docs/ISSUE39_UDIV32_32_HIGH_Q23_V1V5_2026-10-11.md'
REF_V1='45bf4a6a75462983dbfed1cb03b670cacc4299ed25d45865e34a353640c94d9f'
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
assert shared['total_calls']==136335 and len(shared['routines'])==11
expected={'MATH_UDIV32_32':(359.0776841333822,2729,370.5720043972151),
          'MATH_UMOD32_32':(436.899706744868,1705,444.6521994134897)}
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
marker='2026-10-11 ISSUE39 V1/V5 32/32 PROVEN QUOTIENT-2/3'
msg=f"""{marker}
- 131-byte bounded quotient-two/three fast path added after the existing V1/V5 q=1 32/32 guard. D3 in $40–$7F and N3>2*D3+1 proves 2D<=N<4D; compute R=N−2D, conditionally subtract D, and emit Q=2 or 3. DEY loop preserves SBC carry. All nonqualifying inputs use the original core.
- Common-input V1 and V5: UDIV32_32 370.572004→359.077684 cycles (−3.10%, 2,729 operands/profile), UMOD32_32 444.652199→436.899707 (−1.74%, 1,705/profile). Max one-call speedup 388 cycles; max slowdown 22. Uniform 32×32 inputs improve 21.442 cycles/call, while narrow-divisor inputs incur about +12; explicit Pareto trade-off.
- Zero additional normal ZP; unchanged 56-entry API and resident PRG length. New source island $6860–$68E2. Full 822,050 unsigned, 364,533 signed, 136,335 common-corpus, 30,720 workload calls, reference/alternate source builds, V5 hybrid, catalogs, dual changelogs and checksums republished. Native x64sc old/new 48-case proof passed.
- Manual high-byte range proof, not an OptiSearch-generated native record. Issue #39 unsigned family remains open.
- Details: {DOC}
"""
for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
    p=R/name
    if marker not in p.read_text():p.write_text(msg+'\n'+p.read_text())
link=f'- Issue #39 bounded-high-byte 32/32 V1/V5 q=2/3 optimization: {DOC}. Other unsigned architecture audits remain open.'
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
d['issue39_v1_v5_32_32_q23_high_2026_10_11']={
 'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
 'v1_reference_sha256':REF_V1,'v5_reference_sha256':sha(v5ref),
 'source_extra_executable_bytes':131,'normal_zp_growth_bytes':0,
 'resident_size_growth_bytes':0,'public_abi_changed':False,
 'paired_calls':8868,'paired_errors':0,'paired_nonzero_slowdowns':(633+453)*2,
 'max_regression_cycles':22,
 'v1_v5_common_input_cycles':{n:shared['routines'][n]['metrics']['v1_balanced']['mean_cycles'] for n in OPS},
 'all_profile_unsigned_calls':822050,'all_profile_signed_calls':364533,
 'common_input_calls':136335}
if isinstance(d.get('documentation'),dict):
    u=R/'USER_MANUAL.md'
    d['documentation'].update(user_manual_bytes=u.stat().st_size,
        user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=sha(u))
p.write_text(json.dumps(d,indent=2)+'\n')
print('ISSUE39 V1/V5 32/32 BOUNDED Q2/Q3 PUBLICATION PASS')
