#!/usr/bin/env python3
"""Release metadata and public benchmark publication for guarded V1/V5 UMOD8."""
from pathlib import Path
import csv,json,hashlib
from common_corpus_ranking import load_common
from finalize_signed_core_reuse import rebuild_game_math_aggregate

R=Path(__file__).resolve().parents[1]
V1_SHA='9afa30ffd24c1ce9566e7ef21e4032396fbdea7d4c3da5b68e137fc12ec41b62'
V5_SHA='bed1ee986857d045d452036d78d0d6cbdc078dbc3407f8a860a8fd54f8395fa2'
PARENT_V1_SHA='795cf2320f1fee8b097641bb87f3e2ff591b3c84329b700f35ec7d4ef9593387'
PARENT_V5_SHA='9f59d7f8eb8d5cd78d0f01867418e77db5e867e06b9b43afe34df36ccea82dc2'
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OP='MATH_UMOD8'
DOC='docs/ISSUE39_V1V5_UMOD8_GUARDED_REMAINDER_2026-10-11.md'
AUDIT=R/'validation/review/ISSUE39_V1V5_UMOD8_GUARD_EXHAUSTIVE.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/'v1_balanced/resident/math_v1_balanced_game_math.prg')==V1_SHA
assert sha(R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg')==V5_SHA
proof=json.loads(AUDIT.read_text())
assert proof['status']=='PASS' and proof['paired_public_cpu_calls']==262144
assert proof['bytes_of_new_code']==77 and proof['guard_minimum_divisor']==32
for name,old_sha,new_sha,old_mean,new_mean in (
    ('v1_balanced',PARENT_V1_SHA,V1_SHA,65.28515625,53.14067077636719),
    ('v5_hybrid_lowzp',PARENT_V5_SHA,V5_SHA,64.81915283203125,52.83580017089844)):
    m=proof['profiles'][name]
    assert m['old_resident_sha256']==old_sha and m['new_resident_sha256']==new_sha
    assert m['cases']==65536 and m['max_regression_cycles']==14
    assert m['qualified_d32_slower']==0 and m['fallback_d_lt32_slower']==8192
    assert abs(m['old_mean_cycles']-old_mean)<1e-10
    assert abs(m['new_mean_cycles']-new_mean)<1e-10
full=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
signed=json.loads((R/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
assert full['status']==signed['status']=='PASS'
assert full['summary']['machine_calls']==822050
assert signed['summary']['machine_calls']==364533
assert set(full['profiles'])==set(PROFILES)
assert set(signed['profiles'])==set(PROFILES)
for name,rootkey,total in [
    ('ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','total_calls',53760),
    ('ISSUE39_V1_UDIV24_BYTE8_PAIRED.json','paired_machine_calls',56580),
    ('ISSUE39_V1_32_32_D8_DELEGATION.json','paired_machine_calls',51812),
    ('ISSUE39_V5_32_32_NARROW_DELEGATION.json','paired_machine_calls',21412)]:
    j=json.loads((R/'validation/review'/name).read_text())
    assert j['status']=='PASS' and j[rootkey]==total,(name,j.get(rootkey))
common=load_common(R)
assert common['total_calls']==136335
assert common['routines'][OP]['cases_per_profile']==2465
assert abs(common['routines'][OP]['metrics']['v1_balanced']['mean_cycles']-58.43975659229209)<1e-10
assert abs(common['routines'][OP]['metrics']['v5_hybrid_lowzp']['mean_cycles']-58.129411764705885)<1e-10

# One public row, all five means derived from one exact same-input corpus.
p=R/'PERFORMANCE.md'
lines=p.read_text().splitlines()
indices=[i for i,s in enumerate(lines) if s.startswith('| '+chr(96)+OP+chr(96)+' |')]
assert len(indices)==1,indices
cols=lines[indices[0]].split('|')
for index,name in enumerate(PROFILES):
    cols[3+index]=f" {common['routines'][OP]['metrics'][name]['mean_cycles']:.6f} "
lines[indices[0]]='|'.join(cols)
p.write_text('\n'.join(lines)+'\n')

def change_csv(path,func):
    p=R/path
    with p.open(newline='') as f:rows=list(csv.DictReader(f))
    func(rows)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)

def v1(rows):
    selected=[row for row in rows if row['operation'].lower()=='math_umod8']
    assert len(selected)==1
    row=selected[0];m=full['profiles']['v1_balanced'][OP]
    assert int(row['cases'])==m['cases']
    row.update(avg_cycles=f"{m['mean_cycles']:.6f}",min_cycles=str(m['min_cycles']),
               max_cycles=str(m['max_cycles']),
               evidence='2026-10-11 issue39 guarded remainder UMOD8, 65536 full-domain pairs and full public ABI',
               notes='Source-backed V1 77-byte D>=32 remainder-only path, D<32 original fallback; preserves Q')
change_csv('v1_balanced/PUBLIC_PERFORMANCE.csv',v1)

def v3summary(rows):
    selected=[row for row in rows if row['operation'].lower()=='umod8']
    assert len(selected)==1
    selected[0]['v1_balanced_cycles']=f"{full['profiles']['v1_balanced'][OP]['mean_cycles']:.6f}"
change_csv('v3_reu_512k/PUBLIC_PERFORMANCE.csv',v3summary)

def hybrid(rows):
    selected=[row for row in rows if row['routine']==OP]
    assert len(selected)==1
    row=selected[0]
    a=common['routines'][OP]['metrics']['v1_balanced']['mean_cycles']
    b=common['routines'][OP]['metrics']['v5_hybrid_lowzp']['mean_cycles']
    row.update(v1_mean_cycles=f'{a:.6f}',v5_mean_cycles=f'{b:.6f}',
         improvement_percent=f'{(a-b)*100/a:.6f}',
         provenance='2026-10-11 issue39 exact same-input guarded remainder UMOD8: 65536 per profile, no added ZP')
change_csv('v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv',hybrid)

# Rebuild game-math aggregate without rewriting unrelated measured rows.
rebuild_game_math_aggregate()
marker='2026-10-11 ISSUE39 V1/V5 77-BYTE GUARDED REMAINDER-ONLY UMOD8'
msg=f'''{marker}
- V1 Balanced and V5 Hybrid gain a source-backed 77-byte non-ZP UMOD8 remainder-only guard at REG_LOW+$0E00. For D>=32, quotient<=7 and at most seven inline subtract-and-compare stages produce R without ever altering MATH_Q; D<32 reuses the existing V1 or imported V2/V5 public wrapper at MATH_UMOD8+3. Inputs and carry preserved, no new zero page, stack or resident PRG span.
- **262,144 complete paired historical-old/new 6502 calls**, 65,536 exhaustive input pairs per profile, no output/ABI errors. V1 exhaustive mean **65.285156→53.140671** (−18.60%), V5 **64.819153→52.835800** (−18.49%). Same-input common corpus V1 **67.294523→58.439757** (−13.16%), V5 **66.848276→58.129412** (−13.04%).
- All 57,344 D>=32 calls per profile are faster or equal, with zero qualified slowdowns. All 8,192 D<32 fallback calls per profile incur exactly +14 cycles; this deliberate bounded trade-off is not universal Pareto dominance. The smaller-divisor original path avoids hundreds-of-cycles worst tails of an unrestricted repetition engine.
- **320 native VICE x64sc full-resident old/new public calls** passed across V1 and V5, preserving Q0, N/D and carry. Private OptiSearch native candidate timing is not misrepresented as a public-ABI win.
- Prior PR #57/#59/#60/#61/#62 historical proof reports remain reconstructed from their original SHA-qualified parent residents via the new UMOD8 parent capsule, avoiding false provenance or rerunning old tests against new features.
- All-profile unsigned 822,050 and signed 364,533 public calls, 136,335 common-input, 53,760 workload-specific, 262,144 paired new, source reference+alternate relocation and hybrid mixed-call validation form the release gate. Updated source, performance tables/catalogs, both changelogs, docs, README/manual, checksums and CI. Overall unsigned DIV/MOD issue39 family remains open.
- Details: {DOC}
'''
for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
    p=R/fn
    if marker not in p.read_text():p.write_text(msg+'\n'+p.read_text())
link=f'- Issue #39 V1/V5 source-backed 77-byte guarded remainder-only UMOD8: {DOC}; exhaustive old/new V1/V5 validation and no ZP growth.'
for fn in ('README.md','USER_MANUAL.md'):
    p=R/fn
    if link not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+link+'\n')

statefile=R/'RELEASE_STATUS.json';state=json.loads(statefile.read_text())
state['date']='2026-10-11'
state['reference_prg_sha256']={name:sha(R/name/'resident'/f'math_{name}_game_math.prg') for name in PROFILES}
alt={}
for name in PROFILES[:-1]:
    alt[name]=json.loads((R/'build_source/alternate'/name/'source_build_manifest.json').read_text())['output_sha256']
alt['v5_hybrid_lowzp']=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
state['alternate_prg_sha256']=alt
if isinstance(state.get('hybrid_v5'),dict):
    state['hybrid_v5']['reference_prg_sha256']=V5_SHA
    state['hybrid_v5']['alternate_prg_sha256']=alt['v5_hybrid_lowzp']
state['issue39_v1v5_guarded_umod8_2026_10_11']={
 'status':'PASS','document':DOC,'unsigned_family_complete':False,
 'previous_v1_sha256':PARENT_V1_SHA,'v1_resident_sha256':V1_SHA,
 'previous_v5_sha256':PARENT_V5_SHA,'v5_resident_sha256':V5_SHA,
 'public_abi_changed':False,'new_normal_zp_bytes':0,'resident_prg_byte_growth':0,
 'new_code_bytes_in_prior_zero_island':77,
 'guard_minimum_divisor':32,'max_fallback_penalty_cycles':14,
 'old_new_paired_cpu_calls':262144,'native_vice_old_new_calls':320,
 'all_profile_unsigned_calls':822050,'all_profile_signed_calls':364533,
 'common_input_calls':136335,'new_certificate_sha256':sha(AUDIT)}
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
print('ISSUE39 V1/V5 UMOD8 RELEASE METADATA PASS')
