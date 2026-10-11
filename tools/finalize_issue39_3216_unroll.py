#!/usr/bin/env python3
"""Publish fully validated Issue39 V1 32/16 two-loop unroll and performance."""
from pathlib import Path
import csv,hashlib,json
from common_corpus_ranking import load_common
from finalize_signed_core_reuse import rebuild_game_math_aggregate
R=Path(__file__).resolve().parents[1]
P=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
N=('MATH_UDIV32_16','MATH_UMOD32_16')
DOC='docs/ISSUE39_V1_UDIV32_16_DUAL_LOOP_UNROLL_2026-10-11.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v1=R/'v1_balanced/resident/math_v1_balanced_game_math.prg'
assert sha(v1)=='97c3e04112335e5958653ac656771b9e11d1d4fede0f5c824b9169aa49b1b564'
v5=R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg'
assert sha(v5)==json.loads((R/'build_hybrid/reference/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
paired=json.loads((R/'validation/review/V1_UDIV32_16_DUAL_UNROLL.json').read_text())
assert paired['status']=='PASS' and paired['paired_inputs']==10578 and paired['paired_calls']==21156
assert all(not x['slower'] for rec in paired['routines'].values() for x in rec.values())
shared=load_common(R)
assert shared['total_calls']==136335
targets={'MATH_UDIV32_16':(825.8739465005497,2729,896.0615610113595),
         'MATH_UMOD32_16':(843.6299120234604,1705,916.2803519061583)}
for name,(after,count,before) in targets.items():
 r=shared['routines'][name];q=paired['routines'][name]['common']
 assert r['cases_per_profile']==count
 assert abs(r['metrics']['v1_balanced']['mean_cycles']-after)<1e-8
 assert abs(q['mean_parent_cycles']-before)<1e-8 and abs(q['mean_candidate_cycles']-after)<1e-8
for name,calls in (('UNSIGNED_DIVISION_VALIDATION',822050),('SIGNED_DIVISION_VALIDATION',364533)):
 d=json.loads((R/'validation/review'/f'{name}.json').read_text())
 assert d['status']=='PASS' and d['summary']['machine_calls']==calls
 assert len(d['profiles'])==5 and all(not z['errors'] for v in d['profiles'].values() for z in v.values())
w=json.loads((R/'validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json').read_text())
assert w['status']=='PASS' and w['total_calls']==30720
path=R/'PERFORMANCE.md';lines=path.read_text().splitlines()
for name in N:
 ix=[i for i,l in enumerate(lines) if l.startswith('| '+chr(96)+name+chr(96)+' |')]
 assert len(ix)==1,(name,ix)
 cells=lines[ix[0]].split('|')
 cells[3]=f" {shared['routines'][name]['metrics']['v1_balanced']['mean_cycles']:.6f} "
 lines[ix[0]]='|'.join(cells)
path.write_text('\n'.join(lines)+'\n')
path=R/'v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv'
with path.open(newline='') as f:rows=list(csv.DictReader(f))
for row in rows:
 if row['routine'] not in N:continue
 r=shared['routines'][row['routine']]['metrics'];a=r['v1_balanced']['mean_cycles'];b=r['v5_hybrid_lowzp']['mean_cycles']
 row.update(v1_mean_cycles=f'{a:.6f}',v5_mean_cycles=f'{b:.6f}',
            improvement_percent=f'{(a-b)*100/a:.6f}',
            provenance='Issue39 same-input V1 dual-loop unroll; V5 keeps V2-derived 32/16 core')
with path.open('w',newline='') as f:
 cw=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');cw.writeheader();cw.writerows(rows)
rebuild_game_math_aggregate()
marker='2026-10-11 ISSUE39 V1 32/16 DUAL LOOP UNROLL'
msg=f"""{marker}
- Two V1 32/16 quotient loops unrolled into $1900-$1CF7 (1,016 occupied bytes); 0 additional ZP, no public ABI or resident PRG span growth. Relative branch targets and X=0 at exit preserved.
- Same-input public UDIV32_16 mean 896.061561→825.873947 (2,729 pairs; 2,578 faster, 151 equal, 0 slower); UMOD32_16 916.280352→843.629912 (1,705 pairs; 1,554 faster, 151 equal, 0 slower). Six independent 512-pair workload classes also show no new regressions, up to 136 cycles saved.
- 21,156 paired source-executed calls, native full-resident VICE old/new 80+80 calls, V1 unsigned 164,410, signed 97,329, and all-profile 822,050 unsigned, 364,533 signed, 136,335 common and 30,720 workloads pass. Reference/alternate source, V5 hybrid, catalog and checksum publication regenerated.
- V5 keeps its V2-derived 32/16 core. Earlier table island rejected for V5 ATAN2 overlap. Private OptiSearch is not published; unsigned family campaign remains open.
- Details: {DOC}
"""
for file in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 path=R/file
 if marker not in path.read_text():path.write_text(msg+'\n'+path.read_text())
link=f'- Issue #39 V1 32/16 dual-loop quotient unroll: {DOC}. The unsigned DIV/MOD campaign remains open.'
for file in ('README.md','USER_MANUAL.md'):
 path=R/file
 if link not in path.read_text():path.write_text(path.read_text().rstrip()+'\n\n'+link+'\n')
path=R/'RELEASE_STATUS.json';j=json.loads(path.read_text())
j['reference_prg_sha256']={q:sha(R/q/'resident'/f'math_{q}_game_math.prg') for q in P}
alts={q:json.loads((R/'build_source/alternate'/q/'source_build_manifest.json').read_text())['output_sha256'] for q in P[:4]}
alts['v5_hybrid_lowzp']=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
j['alternate_prg_sha256']=alts
if isinstance(j.get('hybrid_v5'),dict):
 j['hybrid_v5']['reference_prg_sha256']=sha(v5)
 j['hybrid_v5']['alternate_prg_sha256']=alts['v5_hybrid_lowzp']
j['issue39_v1_32_16_dual_unroll_2026_10_11']={
 'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
 'v1_reference_sha256':sha(v1),'v5_reference_sha256':sha(v5),
 'unroll_code_bytes':1016,'normal_zp_growth':0,'resident_prg_byte_growth':0,
 'public_abi_changed':False,'paired_inputs':10578,'paired_executions':21156,'paired_regressions':0,
 'all_profile_unsigned_calls':822050,'all_profile_signed_calls':364533,
 'common_input_calls':136335,'workload_calls':30720,'native_vice_old_new_calls':160,
 'v1_common_cycles':{n:shared['routines'][n]['metrics']['v1_balanced']['mean_cycles'] for n in N}}
if isinstance(j.get('documentation'),dict):
 u=R/'USER_MANUAL.md';j['documentation'].update(user_manual_bytes=u.stat().st_size,
  user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=sha(u))
if isinstance(j.get('issue39_common_input_unsigned_divmod'),dict):
 j['issue39_common_input_unsigned_divmod']['benchmark_sha256']=sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
 j['issue39_common_input_unsigned_divmod']['arithmetic_binaries_changed']=True
path.write_text(json.dumps(j,indent=2)+'\n')
print('ISSUE39 V1 32/16 DUAL UNROLL PUBLICATION PASS')
