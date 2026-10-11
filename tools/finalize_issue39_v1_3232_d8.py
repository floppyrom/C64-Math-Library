#!/usr/bin/env python3
"""Issue39 V1 D8 32/32 qualified release finalizer, post-full-profile audit."""
from pathlib import Path
import csv,json,hashlib
from common_corpus_ranking import load_common
from finalize_signed_core_reuse import rebuild_game_math_aggregate
R=Path(__file__).resolve().parents[1]
NAMES=('MATH_UDIV32_32','MATH_UMOD32_32')
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
V1_SHA='795cf2320f1fee8b097641bb87f3e2ff591b3c84329b700f35ec7d4ef9593387'
V5_SHA='9f59d7f8eb8d5cd78d0f01867418e77db5e867e06b9b43afe34df36ccea82dc2'
DOC='docs/ISSUE39_V1_3232_D8_DELEGATION_2026-10-11.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/'v1_balanced/resident/math_v1_balanced_game_math.prg')==V1_SHA
assert sha(R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg')==V5_SHA
proof=json.loads((R/'validation/review/ISSUE39_V1_32_32_D8_DELEGATION.json').read_text())
assert proof['status']=='PASS' and proof['paired_machine_calls']==51812
assert proof['candidate_sha256']==V1_SHA and proof['v5_resident_sha256_unchanged']==V5_SHA
common=load_common(R);assert common['total_calls']==136335
for op,mean,n in (('MATH_UDIV32_32',335.8255771344815,2729),
                  ('MATH_UMOD32_32',399.6768328445748,1705)):
 assert abs(proof['routines'][op]['canonical']['new_mean_cycles']-mean)<1e-9
 assert abs(common['routines'][op]['metrics']['v1_balanced']['mean_cycles']-mean)<1e-9
 assert common['routines'][op]['cases_per_profile']==n
 assert proof['routines'][op]['d8_uniform']['faster']==1024
 assert proof['routines'][op]['canonical']['worst_regression_cycles']<=14
all_unsigned=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
all_signed=json.loads((R/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
assert all_unsigned['status']=='PASS' and all_unsigned['summary']['machine_calls']==822050
assert all_signed['status']=='PASS' and all_signed['summary']['machine_calls']==364533
assert set(all_unsigned['profiles'])==set(PROFILES)
assert set(all_signed['profiles'])==set(PROFILES)
for name in ('ISSUE39_V1_UDIV24_BYTE8_PAIRED','ISSUE39_V1_UDIV24_NARROW_REJECTION',
             'UDIV32_ZERO_HIGH_BYPASS_PAIRED','ISSUE39_V5_32_32_NARROW_DELEGATION'):
 assert (R/'validation/review'/f'{name}.json').is_file(),name
p=R/'PERFORMANCE.md';lines=p.read_text().splitlines()
for op in NAMES:
 idx=[i for i,v in enumerate(lines) if v.startswith('| '+chr(96)+op+chr(96)+' |')]
 assert len(idx)==1,(op,idx)
 cells=lines[idx[0]].split('|')
 for i,profile in enumerate(PROFILES):
  cells[3+i]=f" {common['routines'][op]['metrics'][profile]['mean_cycles']:.6f} "
 lines[idx[0]]='|'.join(cells)
p.write_text('\n'.join(lines)+'\n')
def rewrite_csv(name, fn):
 p=R/name
 with p.open(newline='') as f:rs=list(csv.DictReader(f))
 fn(rs)
 with p.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n')
  writer.writeheader();writer.writerows(rs)
def v1_public(rs):
 for row in rs:
  k=row['operation'].upper()
  if k not in NAMES:continue
  x=all_unsigned['profiles']['v1_balanced'][k]
  assert int(row['cases'])==x['cases']
  row.update(avg_cycles=f"{x['mean_cycles']:.6f}",min_cycles=str(x['min_cycles']),
             max_cycles=str(x['max_cycles']),
             evidence='2026-10-11 issue39 V1 D8 guarded 32/32 public-core paired validation')
rewrite_csv('v1_balanced/PUBLIC_PERFORMANCE.csv',v1_public)
def v1_game(rs):
 for row in rs:
  op='MATH_'+row['routine'].upper()
  if op not in NAMES:continue
  x=all_unsigned['profiles']['v1_balanced'][op]
  row.update(cases=str(x['cases']),mean_cycles=f"{x['mean_cycles']:.6f}",
             min_cycles=str(x['min_cycles']),max_cycles=str(x['max_cycles']))
rewrite_csv('v1_balanced/PUBLIC_PERFORMANCE_GAME_MATH.csv',v1_game)
def v3_legacy(rs):
 for row in rs:
  op='MATH_'+row['operation'].upper()
  if op in NAMES:
   row['v1_balanced_cycles']=f"{all_unsigned['profiles']['v1_balanced'][op]['mean_cycles']:.6f}"
rewrite_csv('v3_reu_512k/PUBLIC_PERFORMANCE.csv',v3_legacy)
def hybrid(rs):
 for row in rs:
  op=row['routine']
  if op not in NAMES:continue
  a=common['routines'][op]['metrics']['v1_balanced']['mean_cycles']
  b=common['routines'][op]['metrics']['v5_hybrid_lowzp']['mean_cycles']
  row.update(v1_mean_cycles=f'{a:.6f}',v5_mean_cycles=f'{b:.6f}',
             improvement_percent=f'{(a-b)*100/a:.6f}',
             provenance='2026-10-11 issue39 V1 D8 32/32 paired benchmark; V5 byte-identical')
rewrite_csv('v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv',hybrid)
rebuild_game_math_aggregate()
marker='2026-10-11 ISSUE39 V1 GUARDED 32/32 D8 PUBLIC DIVMOD DELEGATE'
message=f'''{marker}
- Source-backed V1 32/32 narrow-D8 route at REG_LOW+$0D80, using existing V1 public UDIV32/16 for full-width quotient with R2/R3 cleared. Only reached after D!=0, N>D, D3=0 and guarded D2|D1=0; other inputs go through original shared 32/32 core. No normal ZP, stable input/output/carry API, unchanged resident PRG length.
- Exact merged PR61 SHA parent reconstruction; **51,812 paired historical old/new public 6502 executions**, mathematically correct, full remainder/carry/input preservation, zero slower calls among measured D8 inputs. Worst non-D8 guard penalty +14 cycles (explicitly not universal Pareto dominance). V1 same-input UDIV32_32 **358.009161→335.825577** (−6.2%), UMOD32_32 **435.224633→399.676833** (−8.2%).
- Dedicated D8 full-numerator samples 1943.200→1643.726 UDIV32_32, 1942.482→1643.277 UMOD32_32, 1024/1024 faster per API. D16/D24 denominators incur small +14-cycle guard overhead. An earlier wider-D16 V1 transplant was rejected for rare >400-cycle regressions.
- V5's existing faster D16 imported V2 producer is unchanged byte-for-byte: V5 builder validates, removes the V1 D8 island and restores the old dead high-zero selector before V5-specific narrow helper. Reference and alternate relocatable assemblies validated.
- V1 unsigned 164,410 + full-profile unsigned 822,050 and signed 364,533, common 136,335 and 51,812 paired V1 D8 calls passed. 160 real VICE old/new resident public-entry calls matched mathematical oracle. Previous PR57/PR60/PR61 certificates re-run on SHA-validated historical V1 parent, not the newer V1 live binary.
- Updated public numbers, routine catalogs, both changelogs, docs/manual, checksum package and CI. Unsigned DIV/MOD issue39 family remains open.
- Details: {DOC}
'''
for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 p=R/name
 if marker not in p.read_text():p.write_text(message+'\n'+p.read_text())
line=f'- Issue #39 source-backed V1 32/32 guarded narrow-D8 divider: {DOC}. The full unsigned DIV/MOD campaign remains open.'
for name in ('README.md','USER_MANUAL.md'):
 p=R/name
 if line not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+line+'\n')
p=R/'RELEASE_STATUS.json';j=json.loads(p.read_text())
j['date']='2026-10-11'
j['reference_prg_sha256']={name:sha(R/name/'resident'/f'math_{name}_game_math.prg') for name in PROFILES}
alternate={}
for name in PROFILES[:-1]:
 man=R/'build_source/alternate'/name/'source_build_manifest.json'
 alternate[name]=json.loads(man.read_text())['output_sha256']
alternate[PROFILES[-1]]=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
j['alternate_prg_sha256']=alternate
if isinstance(j.get('hybrid_v5'),dict):
 j['hybrid_v5']['reference_prg_sha256']=V5_SHA
 j['hybrid_v5']['alternate_prg_sha256']=alternate[PROFILES[-1]]
j['issue39_v1_32_32_guarded_d8_2026_10_11']={
 'status':'PASS','document':DOC,'unsigned_family_complete':False,
 'prior_v1_resident_sha256':proof['parent_sha256'],
 'v1_resident_sha256':V1_SHA,'v5_unchanged_sha256':V5_SHA,
 'public_abi_changed':False,'normal_zp_growth':0,'resident_prg_byte_growth':0,
 'paired_old_new_cpu_calls':51812,'max_guard_regression_cycles':14,
 'vice_full_resident_old_new_calls':160,
 'all_profile_unsigned_calls':822050,'all_profile_signed_calls':364533,
 'same_input_corpus_calls':136335,
 'paired_report_sha256':sha(R/'validation/review/ISSUE39_V1_32_32_D8_DELEGATION.json')}
if isinstance(j.get('issue39_unsigned_small_width_workloads_2026_10_11'),dict):
 j['issue39_unsigned_small_width_workloads_2026_10_11']['data_sha256']=sha(R/'validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json')
if isinstance(j.get('issue39_common_input_unsigned_divmod'),dict):
 j['issue39_common_input_unsigned_divmod']['benchmark_sha256']=sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
 j['issue39_common_input_unsigned_divmod']['arithmetic_binaries_changed']=True
if isinstance(j.get('documentation'),dict):
 manual=R/'USER_MANUAL.md'
 j['documentation'].update(user_manual_bytes=manual.stat().st_size,
    user_manual_lines=len(manual.read_text().splitlines()),
    user_manual_sha256=sha(manual))
p.write_text(json.dumps(j,indent=2)+'\n')
print('ISSUE39 V1 32/32 D8 RELEASE METADATA PASS')
