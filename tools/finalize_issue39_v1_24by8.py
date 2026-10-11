#!/usr/bin/env python3
"""Seal V1 exact 24/8 deployment after all-profile validation and full rebuild."""
from pathlib import Path
import csv,hashlib,json
from common_corpus_ranking import load_common
from finalize_signed_core_reuse import rebuild_game_math_aggregate
R=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
NAMES=('MATH_UDIV24','MATH_UMOD24')
DOC='docs/ISSUE39_V1_UDIV24_BYTE8_2026-10-11.md'
V1_SHA='67d709a3006e5529d49b579be20747b292f466679ea42ac24fd5384e4d71879e'
V5_SHA='9f59d7f8eb8d5cd78d0f01867418e77db5e867e06b9b43afe34df36ccea82dc2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v1=R/'v1_balanced/resident/math_v1_balanced_game_math.prg'
v5=R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg'
assert sha(v1)==V1_SHA,(sha(v1),V1_SHA)
assert sha(v5)==V5_SHA,(sha(v5),V5_SHA)
paired=json.loads((R/'validation/review/ISSUE39_V1_UDIV24_BYTE8_PAIRED.json').read_text())
assert paired['status']=='PASS' and paired['paired_machine_calls']==56580
for op,prev,new in (('MATH_UDIV24',177.7420576478014,170.72669892699346),
                    ('MATH_UMOD24',269.7881519639408,248.31745009658724)):
 g=paired['routines'][op]['canonical']
 assert g['slower']==0 and abs(g['parent_mean_cycles']-prev)<1e-9
 assert abs(g['candidate_mean_cycles']-new)<1e-9
 assert paired['routines'][op]['full_d8_stress']['faster']==4080
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
assert neg['status']=='REJECT' and neg['base_sha256']==paired['parent_sha256']
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
    max_cycles=str(a['max_cycles']),evidence='2026-10-11 issue39 V1 exact 24/8 source and full machine-code validation')
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
            provenance='2026-10-11 issue39 exact same-input V1 24/8 proof; V5 unchanged V2-derived core')
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
rebuild_game_math_aggregate()
marker='2026-10-11 ISSUE39 V1 BALANCED 24/8 EXACT NARROW-DIVISOR DIVMOD'
msg=f'''{marker}
- Source-backed 84-byte exact V1 24/8 restoring core at REG_LOW+$0D00, fed by an N2>0,D2=D1=0 bounded selector for UDIV24 and shared UMOD24. Quotient shifted into public MATH_Q; 8-bit remainder with ninth carry held in MATH_R. Zero new normal ZP and stack, stable ABI and PRG length.
- 56,580 same-input old/new public machine-code executions across canonical, seven profile workloads, 4,080 narrow stress, 4,096 wide controls and 1,024 N2=0 controls per API: no wrong outputs or slower calls. Canonical means V1 UDIV24 177.742058→170.726699, UMOD24 269.788152→248.317450 cycles. Independent full-N2/small-D means 1724.909314→1221.545098 (4,080/4,080 faster per API); maximum individual saving 893 cycles.
- Historical PR60 rejected V1 selector remains reproducible via source-anchored old parent SHA; the negative certificate is not mislabeled as a failure of the new algorithm.
- V5's imported V2 24-bit cores stay unchanged. V5 build reclaims the V1-only 24/8 island and restores its inherited unreachable selector; **V5 reference resident remains byte-for-byte identical**. Reference/alternate source maps and mixed-call ABI rechecked.
- V1 164,410 unsigned and all-profile 822,050 unsigned + 364,533 signed + 136,335 common + 53,760 seven-class calls validated. Genuine VICE full-resident 80 old and 80 new calls matched both public APIs. No claim that a private OptiSearch native timing beat the public ABI.
- Published performance tables, sources, documentation, both changelogs, release/checksums, and CI. Unsigned DIV/MOD campaign remains open.
- Details: {DOC}
'''
for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 p=R/fn
 if marker not in p.read_text():p.write_text(msg+'\n'+p.read_text())
link=f'- Issue #39 V1 Balanced exact unsigned 24/8 narrow-division fast path: {DOC}. The wider unsigned DIV/MOD campaign remains open.'
for fn in ('README.md','USER_MANUAL.md'):
 p=R/fn
 if link not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+link+'\n')
statefile=R/'RELEASE_STATUS.json';state=json.loads(statefile.read_text())
state['date']='2026-10-11'
state['reference_prg_sha256']={p:sha(R/p/'resident'/f'math_{p}_game_math.prg') for p in PROFILES}
alt={}
for p in PROFILES[:4]:
 alt[p]=json.loads((R/'build_source/alternate'/p/'source_build_manifest.json').read_text())['output_sha256']
alt[PROFILES[-1]]=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
state['alternate_prg_sha256']=alt
if isinstance(state.get('hybrid_v5'),dict):
 state['hybrid_v5']['reference_prg_sha256']=V5_SHA
 state['hybrid_v5']['alternate_prg_sha256']=alt[PROFILES[-1]]
state['issue39_v1_unsigned_24_by_8_2026_10_11']={
 'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
 'v1_resident_sha256':V1_SHA,'v5_resident_sha256_unchanged':V5_SHA,
 'normal_zp_growth':0,'new_low_code_bytes':84,
 'public_abi_changed':False,'resident_prg_byte_growth':0,
 'paired_old_new_calls':56580,'paired_regressions':0,
 'native_vice_old_new_calls':160,'all_profile_unsigned_calls':822050,
 'all_profile_signed_calls':364533,'common_input_calls':136335,
 'seven_workload_calls':53760,
 'v1_old_new_cycles':{x:{'old':paired['routines'][x]['canonical']['parent_mean_cycles'],
 'new':paired['routines'][x]['canonical']['candidate_mean_cycles']} for x in NAMES},
 'paired_report_sha256':sha(R/'validation/review/ISSUE39_V1_UDIV24_BYTE8_PAIRED.json')}
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
