#!/usr/bin/env python3
"""Source-backed release publication for Issue39 V5 32/32 narrow delegation."""
from pathlib import Path
import csv,hashlib,json
from common_corpus_ranking import load_common
from finalize_signed_core_reuse import rebuild_game_math_aggregate
R=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV32_32','MATH_UMOD32_32')
DOC='docs/ISSUE39_V5_3232_NARROW_DELEGATION_2026-10-11.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg'
assert sha(p)=='9f59d7f8eb8d5cd78d0f01867418e77db5e867e06b9b43afe34df36ccea82dc2'
paired=json.loads((R/'validation/review/ISSUE39_V5_32_32_NARROW_DELEGATION.json').read_text())
assert paired['status']=='PASS' and paired['machine_calls']==21412
assert paired['candidate_sha256']==sha(p)
common=load_common(R)
assert common['total_calls']==136335
target={'MATH_UDIV32_32':(358.00916086478566,275.01319164529133,2729),
        'MATH_UMOD32_32':(435.22463343108507,302.35307917888565,1705)}
for op,(v1,v5,count) in target.items():
 row=common['routines'][op]
 assert row['cases_per_profile']==count
 assert abs(row['metrics']['v1_balanced']['mean_cycles']-v1)<1e-8
 assert abs(row['metrics']['v5_hybrid_lowzp']['mean_cycles']-v5)<1e-8
 assert abs(paired['routines'][op]['canonical']['after_mean_cycles']-v5)<1e-8
for f,required in [('UNSIGNED_DIVISION_VALIDATION',822050),('SIGNED_DIVISION_VALIDATION',364533)]:
 val=json.loads((R/'validation/review'/f'{f}.json').read_text())
 assert val['status']=='PASS' and val['summary']['machine_calls']==required
 assert len(val['profiles'])==5 and not any(z['errors'] for row in val['profiles'].values() for z in row.values())
# Only V5 changes. Keep V1/V2/V3/V4 means byte-identical.
path=R/'PERFORMANCE.md';lines=path.read_text().splitlines()
for op in OPS:
 row=[i for i,line in enumerate(lines) if line.startswith('| '+chr(96)+op+chr(96)+' |')]
 assert len(row)==1,(op,row)
 cells=lines[row[0]].split('|')
 cells[7]=f" {common['routines'][op]['metrics']['v5_hybrid_lowzp']['mean_cycles']:.6f} "
 lines[row[0]]='|'.join(cells)
path.write_text('\n'.join(lines)+'\n')
path=R/'v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv'
with path.open(newline='') as f:rows=list(csv.DictReader(f))
typed={'MATH_UDIV32_32':'div_u32_u32_u32_32','MATH_UMOD32_32':'mod_u32_u32_u32'}
for op in OPS:
 metrics=common['routines'][op]['metrics'];v1=metrics['v1_balanced']['mean_cycles'];v5=metrics['v5_hybrid_lowzp']['mean_cycles']
 row={'routine':op,'canonical_name':typed[op],'v1_mean_cycles':f'{v1:.6f}','v5_mean_cycles':f'{v5:.6f}',
      'improvement_percent':f'{(v1-v5)*100/v1:.6f}',
      'provenance':'Issue39 2026-10-11 V5 narrow-divisor 32/16 reuse; explicit +10 cycle middle-divisor guard'}
 existing=[r for r in rows if r['routine']==op]
 if existing:existing[0].update(row)
 else:rows.append(row)
with path.open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['routine','canonical_name','v1_mean_cycles','v5_mean_cycles','improvement_percent','provenance'],lineterminator='\n')
 writer.writeheader();writer.writerows(rows)
rebuild_game_math_aggregate()
marker='2026-10-11 ISSUE39 V5 32/32 NARROW-DIVISOR DELEGATION'
msg=f"""\{marker}
- V5-only shared UDIV32_32/UMOD32_32 route when D3=D2=0 reuses the already imported V2-derived 32/16 quotient engine; direct 21-byte helper at REG_LOW+$0D00, 0 new ZP, no public ABI or resident PRG size change. V1 stays untouched (its candidate suffered up to +403 cycles).
- Same-input V5 UDIV32_32 358.009161→275.013192 cycles (2,729 pairs, 234 faster, 2,486 equal, 9 slower); UMOD32_32 435.224633→302.353079 (1,705 pairs, 234 faster, 1,467 equal, 4 slower). Narrow 16-bit divisor class saves ~934 cycles on average; 17–24-bit divisors pay +10 guard cycles in most cases. Results workload-dependent.
- Paired 21,412 CPU calls, V5 unsigned 164,410 and signed 36,273 calls, real VICE 80 old+80 new calls and hybrid mixed-call validation; all-profile 822,050 unsigned/364,533 signed, 136,335 common corpus. Earlier PR57 zero-high certificate is reconstructed from the historical PR58 V5 parent image and remains valid.
- Regenerated hybrid source/binaries, standalone mirrors, public and consolidated indexes, both changelogs and checksums. OptiSearch private; this is a manual architecture reuse, not an optimizer-native record. Issue39 unsigned campaign remains unchecked.
- Details: {DOC}
""".replace('\\{marker}','{marker}')
for f in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 path=R/f
 if marker not in path.read_text():path.write_text(msg+'\n'+path.read_text())
link=f'- V5 32/32 narrow-divisor shared fast-32/16 path: {DOC}; the unsigned DIV/MOD family campaign remains open.'
for f in ('README.md','USER_MANUAL.md'):
 path=R/f
 if link not in path.read_text():path.write_text(path.read_text().rstrip()+'\n\n'+link+'\n')
r=R/'RELEASE_STATUS.json';j=json.loads(r.read_text())
j['reference_prg_sha256']={q:sha(R/q/'resident'/f'math_{q}_game_math.prg') for q in PROFILES}
alts={q:json.loads((R/'build_source/alternate'/q/'source_build_manifest.json').read_text())['output_sha256'] for q in PROFILES[:4]}
alts['v5_hybrid_lowzp']=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
j['alternate_prg_sha256']=alts
if isinstance(j.get('hybrid_v5'),dict):
 j['hybrid_v5']['reference_prg_sha256']=sha(p)
 j['hybrid_v5']['alternate_prg_sha256']=alts['v5_hybrid_lowzp']
if isinstance(j.get('issue39_common_input_unsigned_divmod'),dict):
 j['issue39_common_input_unsigned_divmod']['benchmark_sha256']=sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
 j['issue39_common_input_unsigned_divmod']['arithmetic_binaries_changed']=True
j['issue39_v5_32_32_narrow_delegate_2026_10_11']={
 'status':'PASS','documentation':DOC,'unsigned_family_complete':False,'v5_reference_sha256':sha(p),
 'v5_alternate_sha256':alts['v5_hybrid_lowzp'],'normal_zp_growth_bytes':0,
 'new_private_code_bytes':21,'prg_file_growth_bytes':0,'public_abi_changed':False,
 'paired_old_new_calls':21412,'canonical_udiv32_32_mean_cycles':target['MATH_UDIV32_32'][1],
 'canonical_umod32_32_mean_cycles':target['MATH_UMOD32_32'][1],
 'max_guard_regression_cycles':10,'all_profile_unsigned_calls':822050,
 'all_profile_signed_calls':364533,'same_input_calls':136335,'native_vice_calls_per_version':80}
if isinstance(j.get('documentation'),dict):
 u=R/'USER_MANUAL.md'
 j['documentation'].update(user_manual_bytes=u.stat().st_size,user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=sha(u))
r.write_text(json.dumps(j,indent=2)+'\n')
print('ISSUE39 V5 32/32 NARROW DELEGATE PUBLICATION PASS')
