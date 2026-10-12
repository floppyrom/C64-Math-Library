#!/usr/bin/env python3
"""Seal V1 exact 24/8 deployment after all-profile validation and full rebuild."""
from pathlib import Path
import csv,hashlib,json
from common_corpus_ranking import load_common
from finalize_signed_core_reuse import rebuild_game_math_aggregate
R=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
NAMES=('MATH_UDIV24','MATH_UMOD24')
DOC='docs/ISSUE39_V1_UDIV24_SHARED_SUBTRACTION_RELEASE_2026-10-12.md'
V1_SHA='28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0'
V5_SHA='5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v1=R/'v1_balanced/resident/math_v1_balanced_game_math.prg'
v5=R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg'
assert sha(v1)==V1_SHA,(sha(v1),V1_SHA)
assert sha(v5)==V5_SHA,(sha(v5),V5_SHA)
paired=json.loads((R/'validation/review/ISSUE39_V1_24BY8_SHARED_SUBTRACTION_PAIRED.json').read_text())
assert paired['status']=='PASS' and paired['machine_calls']==48388
assert paired['candidate_sha256']==V1_SHA
paired['paired_machine_calls']=paired['machine_calls']
for op,groups in paired['routines'].items():
 for g in groups.values():
  g['parent_mean_cycles']=g['before_mean']
  g['candidate_mean_cycles']=g['after_mean']
 groups['full_d8_stress']=groups['full_n24_d8']

for op,prev,new in (('MATH_UDIV24',170.72669892699346,170.23816536924048),
                    ('MATH_UMOD24',248.31745009658724,246.8222794591114)):
 g=paired['routines'][op]['canonical']
 assert g['slower']==0 and abs(g['parent_mean_cycles']-prev)<1e-9
 assert abs(g['candidate_mean_cycles']-new)<1e-9
 assert paired['routines'][op]['full_d8_stress']['faster']==3779
for name,count in (('UNSIGNED_DIVISION_VALIDATION',822050),
                   ('SIGNED_DIVISION_VALIDATION',364533)):
 j=json.loads((R/'validation/review'/f'{name}.json').read_text())
 assert j['status']=='PASS' and j['summary']['machine_calls']==count
 assert set(j['profiles'])==set(PROFILES)
 assert all(not z['errors'] for p in j['profiles'].values() for z in p.values())
common=load_common(R);assert common['total_calls']==136335
for op in NAMES:
 assert abs(common['routines'][op]['metrics']['v1_balanced']['mean_cycles']-paired['routines'][op]['canonical']['candidate_mean_cycles'])<1e-9
s=json.loads((R/'validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json').read_text())
assert s['status']=='PASS' and s['total_calls']==53760
neg=json.loads((R/'validation/review/ISSUE39_V1_UDIV24_NARROW_REJECTION.json').read_text())
assert neg['status']=='REJECT'  # historical negative certificate; parent is older than PR68
# Complete public same-input leaderboard. Every other profile remains unchanged.
p=R/'PERFORMANCE.md';lines=p.read_text().splitlines()
for name in NAMES:
 found=[i for i,row in enumerate(lines) if row.startswith('| '+chr(96)+name+chr(96)+' |')]
 assert len(found)==1,(name,found)
 cells=lines[found[0]].split('|')
 for ix,prof in enumerate(PROFILES):
  cells[3+ix]=f" {common['routines'][name]['metrics'][prof]['mean_cycles']:.6f} "
 lines[found[0]]='|'.join(cells)
p.write_text('\n'.join(lines)+'\n')
# Independent seeded correctness validator has a different input distribution.
full=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
p=R/'v1_balanced/PUBLIC_PERFORMANCE.csv'
with p.open(newline='') as f:rows=list(csv.DictReader(f))
for row in rows:
 k=row['operation'].upper()
 if k not in ('MATH_UDIV24','MATH_UMOD24'):continue
 a=full['profiles']['v1_balanced'][k]
 assert int(row['cases'])==a['cases']
 row.update(avg_cycles=f"{a['mean_cycles']:.6f}",min_cycles=str(a['min_cycles']),
    max_cycles=str(a['max_cycles']),evidence='2026-10-12 issue39 V1 shared-subtraction 69-byte source/public-ABI validation')
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
p=R/'v1_balanced/PUBLIC_PERFORMANCE_GAME_MATH.csv'
with p.open(newline='') as f:rows=list(csv.DictReader(f))
for row in rows:
 name='MATH_'+row['routine'].upper()
 if name not in NAMES:continue
 a=full['profiles']['v1_balanced'][name]
 row.update(cases=str(a['cases']),mean_cycles=f"{a['mean_cycles']:.6f}",
            min_cycles=str(a['min_cycles']),max_cycles=str(a['max_cycles']))
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
p=R/'v3_reu_512k/PUBLIC_PERFORMANCE.csv'
with p.open(newline='') as f:rows=list(csv.DictReader(f))
for row in rows:
 name='MATH_'+row['operation'].upper()
 if name in NAMES:row['v1_balanced_cycles']=f"{full['profiles']['v1_balanced'][name]['mean_cycles']:.6f}"
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
p=R/'v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv'
with p.open(newline='') as f:rows=list(csv.DictReader(f))
for row in rows:
 op=row['routine']
 if op not in NAMES:continue
 a=common['routines'][op]['metrics']['v1_balanced']['mean_cycles']
 b=common['routines'][op]['metrics']['v5_hybrid_lowzp']['mean_cycles']
 row.update(v1_mean_cycles=f'{a:.6f}',v5_mean_cycles=f'{b:.6f}',
            improvement_percent=f'{(a-b)*100/a:.6f}',
            provenance='2026-10-12 issue39 exact same-input V1 shared-subtract 24/8 proof; V5 unchanged')
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
rebuild_game_math_aggregate()
marker='2026-10-12 ISSUE39 V1 24/8 SHARED-SUBTRACTION DIVMOD CORE 69 BYTES'
msg=f'''{marker}
- Source-backed V1 UDIV24/UMOD24 shared 24÷8 producer: 84->69 bytes; merged carry-aware subtraction path and cleared the 15 freed trailing bytes. No extra ZP/stack or change to ABI, public addresses, resident PRG length, or V2-V5 binaries.
- 48,388 paired prior/live full-public-entry machine calls, zero arithmetic or carry failures and zero slower cases. Canonical UDIV24 170.726699->170.238165, UMOD24 248.317450->246.822279 cycles; 4,080 N2/D8 targeted cases 1220.796->1202.297 with 3,779 faster, none slower per operation.
- Independent native VICE x64sc 256 old/new resident calls verify Q/R/C and preserved inputs against mathematical oracle; not native cycle timing. All-profile unsigned 822,050, signed 364,533, common 136,335 and seven-class 53,760 machine-code tests pass.
- Generated reference/alternate sources, stable executable mirrors, public rankings, docs, release metadata and checksums synchronized. V5 reference remains byte-identical at SHA256 {V5_SHA}. Issue39 overall unsigned DIV/MOD campaign stays OPEN.
- Details: {DOC}
'''
for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 p=R/fn
 if marker not in p.read_text():p.write_text(msg+'\n'+p.read_text())
link=f'- Issue #39 V1 Balanced 69-byte 24/8 shared-subtraction DIV/MOD release: {DOC}. The unsigned campaign remains open.'
for fn in ('README.md','USER_MANUAL.md'):
 p=R/fn
 if link not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+link+'\n')
statefile=R/'RELEASE_STATUS.json';state=json.loads(statefile.read_text())
state['date']='2026-10-12'
state['reference_prg_sha256']={p:sha(R/p/'resident'/f'math_{p}_game_math.prg') for p in PROFILES}
alt={}
for p in PROFILES[:4]:
 alt[p]=json.loads((R/'build_source/alternate'/p/'source_build_manifest.json').read_text())['output_sha256']
alt[PROFILES[-1]]=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
state['alternate_prg_sha256']=alt
if isinstance(state.get('hybrid_v5'),dict):
 state['hybrid_v5']['reference_prg_sha256']=V5_SHA
 state['hybrid_v5']['alternate_prg_sha256']=alt[PROFILES[-1]]
state['issue39_v1_24by8_shared_subtraction_2026_10_12']={
 'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
 'v1_resident_sha256':V1_SHA,'v5_resident_sha256_unchanged':V5_SHA,
 'normal_zp_growth':0,'new_low_code_bytes':69,
 'public_abi_changed':False,'resident_prg_byte_growth':0,
 'paired_old_new_calls':48388,'paired_regressions':0,
 'native_vice_old_new_calls':256,'all_profile_unsigned_calls':822050,
 'all_profile_signed_calls':364533,'common_input_calls':136335,
 'seven_workload_calls':53760,
 'v1_old_new_cycles':{x:{'old':paired['routines'][x]['canonical']['parent_mean_cycles'],
 'new':paired['routines'][x]['canonical']['candidate_mean_cycles']} for x in NAMES},
 'paired_report_sha256':sha(R/'validation/review/ISSUE39_V1_24BY8_SHARED_SUBTRACTION_PAIRED.json')}
if isinstance(state.get('issue39_unsigned_small_width_workloads_2026_10_11'),dict):
 state['issue39_unsigned_small_width_workloads_2026_10_11']['data_sha256']=sha(R/'validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json')
if isinstance(state.get('issue39_common_input_unsigned_divmod'),dict):
 state['issue39_common_input_unsigned_divmod']['benchmark_sha256']=sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
 state['issue39_common_input_unsigned_divmod']['arithmetic_binaries_changed']=True
if isinstance(state.get('documentation'),dict):
 u=R/'USER_MANUAL.md'
 state['documentation'].update(user_manual_bytes=u.stat().st_size,
  user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=sha(u))
statefile.write_text(json.dumps(state,indent=2)+'\n')
print('ISSUE39 V1 24/8 RELEASE METADATA PASS')
