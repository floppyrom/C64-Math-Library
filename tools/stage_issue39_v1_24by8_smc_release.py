#!/usr/bin/env python3
"""Stage the source-backed PR79 61-byte V1 24/8 core as an auditable release.

Runs ONLY on the isolated issue39 release branch through a write-enabled
GitHub Actions job. Does not touch user-provided OptiSearch source.
"""
from pathlib import Path
import csv,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from finalize_signed_core_reuse import rebuild_game_math_aggregate
from issue39_v1_24by8_accumulator_parent import restore_pr78
PROFILE=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV24','MATH_UMOD24')
PR78='cdc2ca502d664055f896d7ad1601e8dd994b61be33e24bde3e25fc0dcbee1cdd'
NEW_SHA='d6e013740a8c1ac8f35fa895b69afb8bf6226cde99f491a470b4518a7c6dfa9a'
V5='5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222'
DOC='docs/ISSUE39_V1_24BY8_SMC_INTEGRATED_RELEASE_2026-10-12.md'
MARK='2026-10-12 ISSUE39 V1 68-BYTE RAM SMC 24/8 DIVMOD RELEASE'
def path(p):return ROOT/p/'resident'/('math_'+p+'_game_math.prg')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def execute(*args):
 print('RUN',*args,flush=True)
 subprocess.run([str(x) for x in args],cwd=ROOT,check=True)
def py(cmd,*args):execute(sys.executable,ROOT/'tools'/(cmd+'.py'),*args)
def csv_load(p):
 with (ROOT/p).open(newline='') as f:return list(csv.DictReader(f))
def csv_save(p,rows):
 with (ROOT/p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def checksum():
 paths=sorted((p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts
               and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
               key=lambda p:str(p.relative_to(ROOT)))
 (ROOT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(ROOT))+'\n' for p in paths))
def main():
 state=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 before={p:sha(path(p)) for p in PROFILE}
 assert before['v1_balanced']==PR78 and before['v5_hybrid_lowzp']==V5, before
 assert before==state['reference_prg_sha256'],'source snapshot must match release status'
 old=path('v1_balanced').read_bytes()
 candidate,l,_=Assembler().assemble((ROOT/'tools/candidates/issue39_v1_24by8_accumulator_selfmod.asm').read_text())
 assert len(candidate)==68 and l['V1LAT_24_BY_8']==0x1d00
 lo=int.from_bytes(old[:2],'little');assert lo==0x1000
 off=2+0x1d00-lo
 expected=bytearray(old)
 for a,b in candidate.items():expected[2+a-lo]=b
 expected[off+68:off+84]=bytes(16)
 assert restore_pr78(bytes(expected))==restore_pr78(old)
 newhash=hashlib.sha256(expected).hexdigest()
 assert newhash==NEW_SHA,(newhash,NEW_SHA)
 print('EXPECTED V1 RESIDENT SHA',newhash,flush=True)

 py('screen_issue39_v1_24by8_accumulator_selfmod','--out','/tmp/issue39_smc_vs61.json')
 s1=json.loads(Path('/tmp/issue39_smc_vs61.json').read_text())
 assert s1['status']=='PASS' and s1['regressions']==0 and s1['paired_machine_calls']==48388 and s1['new_v1_sha256']==NEW_SHA
 py('verify_issue39_v1_24by8_accumulator_selfmod_portable','--out','/tmp/issue39_smc_portable.json')
 assert json.loads(Path('/tmp/issue39_smc_portable.json').read_text())['full_calls']==6344
 # Before overwriting the shipped resident, prove the source overlay compiles
 # to exactly the 61-byte candidate and that V5 is byte-identical.
 py('screen_issue39_v1_24by8_accumulator')
 py('generate_sources')
 for cfg in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',cfg)
  py('build_hybrid','--config-kind',cfg)
 built=ROOT/'build_source/reference/v1_balanced/math_v1_balanced_source_built.prg'
 assert built.read_bytes()==bytes(expected),('source build differs from proven candidate',sha(built),newhash)
 hybrid=ROOT/'build_hybrid/reference/v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg'
 assert sha(hybrid)==V5,'candidate may not modify V5; investigate overlap'
 for p in PROFILE[1:4]:assert sha(path(p))==before[p]
 path('v1_balanced').write_bytes(built.read_bytes())
 assert sha(path('v1_balanced'))==newhash

 # Source must remain reproducible once the new resident becomes canonical.
 py('generate_sources')
 for cfg in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',cfg)
  py('build_hybrid','--config-kind',cfg)
 assert sha(built)==newhash
 assert sha(hybrid)==V5
 assert path('v1_balanced').read_bytes()==built.read_bytes()
 for p in PROFILE[1:]:assert sha(path(p))==before[p],p

 # Both live current-candidate and all historical paired proofs must replay.
 py('screen_issue39_v1_24by8_accumulator')
 py('screen_issue39_v1_24by8_shared_subtraction')
 py('screen_issue39_v1_24by8_accumulator_selfmod')
 py('validate_unsigned_division')
 py('validate_signed_division')
 py('benchmark_unsigned_common_corpus')
 py('audit_issue39_unsigned_small_workloads')
 py('benchmark_unsigned_3216_workloads')
 py('validate_v1_3216_unroll')
 py('audit_issue39_v1v5_umod8_guard')
 py('audit_issue39_zero_high_bypass')
 u=json.loads((ROOT/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
 s=json.loads((ROOT/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
 common=json.loads((ROOT/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
 assert u['status']==s['status']==common['status']=='PASS'
 assert u['summary']['machine_calls']==822050 and s['summary']['machine_calls']==364533
 assert common['total_calls']==136335
 means={op:{p:common['routines'][op]['metrics'][p]['mean_cycles'] for p in PROFILE} for op in OPS}
 assert abs(means['MATH_UDIV24']['v1_balanced']-165.228277)<0.00001,means
 assert abs(means['MATH_UMOD24']['v1_balanced']-231.489375)<0.00001,means

 # Profile-specific independent-seed and all-profile same-input numbers
 # intentionally remain distinct in the published tables.
 rows=csv_load('v1_balanced/PUBLIC_PERFORMANCE.csv')
 for row in rows:
  name=row['operation'].upper()
  if name not in OPS:continue
  x=u['profiles']['v1_balanced'][name]
  row.update(avg_cycles=f"{x['mean_cycles']:.6f}",min_cycles=str(x['min_cycles']),
             max_cycles=str(x['max_cycles']),evidence='2026-10-12 issue39 61-byte accumulator 24/8 source-built resident')
 csv_save('v1_balanced/PUBLIC_PERFORMANCE.csv',rows)
 rows=csv_load('v1_balanced/PUBLIC_PERFORMANCE_GAME_MATH.csv')
 for row in rows:
  name='MATH_'+row['routine'].upper()
  if name not in OPS:continue
  x=u['profiles']['v1_balanced'][name]
  row.update(cases=str(x['cases']),mean_cycles=f"{x['mean_cycles']:.6f}",
             min_cycles=str(x['min_cycles']),max_cycles=str(x['max_cycles']))
 csv_save('v1_balanced/PUBLIC_PERFORMANCE_GAME_MATH.csv',rows)
 rows=csv_load('v3_reu_512k/PUBLIC_PERFORMANCE.csv')
 for row in rows:
  name='MATH_'+row['operation'].upper()
  if name in OPS:row['v1_balanced_cycles']=f"{u['profiles']['v1_balanced'][name]['mean_cycles']:.6f}"
 csv_save('v3_reu_512k/PUBLIC_PERFORMANCE.csv',rows)
 rows=csv_load('v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv')
 for row in rows:
  name=row['routine']
  if name not in OPS:continue
  a=means[name]['v1_balanced'];b=means[name]['v5_hybrid_lowzp']
  row.update(v1_mean_cycles=f'{a:.6f}',v5_mean_cycles=f'{b:.6f}',
             improvement_percent=f'{(a-b)*100/a:.6f}',
             provenance='2026-10-12 exact same-input V1 accumulator 24/8; V5 byte-identical')
 csv_save('v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv',rows)
 lines=(ROOT/'PERFORMANCE.md').read_text().splitlines()
 for op in OPS:
  hit=[i for i,v in enumerate(lines) if v.startswith('| `'+op+'` |')]
  assert len(hit)==1,(op,hit)
  cells=lines[hit[0]].split('|')
  for j,p in enumerate(PROFILE):cells[3+j]=f' {means[op][p]:.6f} '
  lines[hit[0]]='|'.join(cells)
 (ROOT/'PERFORMANCE.md').write_text('\n'.join(lines)+'\n')
 rebuild_game_math_aggregate()
 py('publish_standalone_sources')
 py('generate_consolidated_routine_table')
 py('generate_public_indexes')
 py('validate_public_catalog')
 py('validate_standalone_sources')

 details=f"""# Issue #39: V1 68-byte RAM self-modifying shared 24/8 DIV/MOD release

12 October 2026. Replaces ONLY the previous 61-byte short-divisor V1
producer with a 68-byte writable-RAM-only SMC kernel within the original
84-byte fixed code island. Modifies the immediate operands of CMP and SBC.
The existing library is sequential/non-reentrant; this routine MUST execute
from writable RAM, and cannot be invoked concurrently or from ROM.
The source-only previous 61-byte fallback remains separately available.

Prior V1 binary SHA256: {PR78}; source-built current: {newhash}.
V2–V5 binaries remain byte-identical. API and zero-page/stack unchanged.
Native VICE full resident comparison 384 public calls with zero correctness,
flags, input preservation or stack errors; no native cycle timing is claimed.
Paired 48,388 old/new public calls and 6,344 independently relocatable
standalone calls pass. 822,050 unsigned, 364,533 signed multi-profile calls
and 136,335 common same-input profile calls; reference/alternate builds pass.

| API | 61-byte before | 68-byte after |
|---|---:|---:|
| UDIV24 | 166.190196 | {means['MATH_UDIV24']['v1_balanced']:.6f} |
| UMOD24 | 234.433355 | {means['MATH_UMOD24']['v1_balanced']:.6f} |
| 24/8 special stress | 976.350000 | 927.934314 |

Standalone SMC: routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm
Non-SMC historical portable source: tools/candidates/issue39_v1_24by8_accumulator.asm
Native evidence: validation/review/ISSUE39_V1_24BY8_68SMC_FULL_RESIDENT_NATIVE_VICE.json
Issue #39 remains open; other DIV/MOD widths and profiles still unaudited.
"""
 (ROOT/DOC).write_text(details)
 link='- Issue #39 V1 RAM SMC 68-byte shared 24/8 release: '+DOC+'. Requires writable RAM and non-reentrant execution; 61-byte fallback is retained; family-wide audit remains open.'
 for fn in ('README.md','USER_MANUAL.md'):
  p=ROOT/fn
  if link not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+link+'\n')
 native=json.loads((ROOT/'validation/review/ISSUE39_V1_24BY8_68SMC_FULL_RESIDENT_NATIVE_VICE.json').read_text())
 assert native['status']=='PASS' and native['sha_before']==PR78 and native['sha_after']==newhash
 assert native['total_public_resident_calls']==384 and not native['native_cycles_measured']
 log=f"""{MARK}
- V1 bounded 24/8 DIV/MOD producer 61→68 executable bytes, fits existing 84-byte island. Writable executable RAM, no reentrancy/ROM support; prior 61-byte fallback retained. V2–V5 unchanged, no public ABI/ZP/stack/resident-size growth.
- Paired same-input UDIV24 166.190196→{means['MATH_UDIV24']['v1_balanced']:.6f}, UMOD24 234.433355→{means['MATH_UMOD24']['v1_balanced']:.6f}; D8 stress 976.350000→927.934314. 48,388 paired public calls, zero regressions; 6,344 portable two-map calls, 384 native VICE full-resident calls (not cycle timings).
- Complete five-profile unsigned/signed, common benchmark, reference/alternate relocation and binary isolation; both changelogs, performance tables, release metadata, and SHA checksums rebuilt. #39 remains OPEN. {DOC}
"""
 for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  p=ROOT/fn
  if MARK not in p.read_text():p.write_text(log+'\n'+p.read_text())
 state['date']='2026-10-12'
 state['issue39_v1_24by8_ram_smc_specialist_2026_10_12']['status']='PASS_PROMOTED_V1_RAM_ONLY'
 state['issue39_v1_24by8_ram_smc_specialist_2026_10_12']['installed_binary_changed']=True
 state['reference_prg_sha256']={p:sha(path(p)) for p in PROFILE}
 alt={}
 for p in PROFILE[:4]:
  q=ROOT/'build_source/alternate'/p/'source_build_manifest.json'
  alt[p]=json.loads(q.read_text())['output_sha256']
 alt['v5_hybrid_lowzp']=json.loads((ROOT/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
 state['alternate_prg_sha256']=alt
 if isinstance(state.get('hybrid_v5'),dict):
  state['hybrid_v5']['reference_prg_sha256']=V5
  state['hybrid_v5']['alternate_prg_sha256']=alt['v5_hybrid_lowzp']
 state['issue39_v1_24by8_smc_integrated_release_2026_10_12']={
  'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
  'prior_v1_sha256':PR78,'new_v1_sha256':newhash,'unchanged_v5_sha256':V5,
  'public_abi_changed':False,'code_bytes_old':61,'code_bytes_new':68,
  'normal_zp_growth':0,'stack_growth':0,'resident_prg_growth':0,
  'paired_old_new_calls':48388,'paired_regressions':0,'native_isolated_calls':128,
  'native_full_resident_calls':384,'requires_writable_ram':True,'reentrant':False,
  'five_profile_unsigned_calls':u['summary']['machine_calls'],
  'five_profile_signed_calls':s['summary']['machine_calls'],
  'common_input_calls':common['total_calls'],
  'official_means':means}
 for key,p,field in (
  ('issue39_common_input_unsigned_divmod','validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json','benchmark_sha256'),
  ('issue39_unsigned_small_width_workloads_2026_10_11','validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','data_sha256'),
  ('issue39_unsigned_3216_multiworkload_2026_10_11','validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json','report_sha256')):
  if isinstance(state.get(key),dict):state[key][field]=sha(ROOT/p)
 if isinstance(state.get('documentation'),dict):
  f=ROOT/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=f.stat().st_size,
   user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 (ROOT/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 # The CI package gate requires exact per-file SHA manifests. Generated
 # source_build/ dirs MUST be removed before sealing the lean release.
 execute('make','clean')
 for i in range(3):
  checksum();py('package_audit')
 # Ensure the sealed JSON itself is current, not merely a successful script run.
 py('validate_public_catalog')
 print('ISSUE39 V1 68-BYTE RAM SMC RELEASE STAGED',newhash,flush=True)
if __name__=='__main__':main()
