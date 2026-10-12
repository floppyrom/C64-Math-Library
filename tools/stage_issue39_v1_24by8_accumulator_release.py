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
PR78='28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0'
V5='5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222'
DOC='docs/ISSUE39_V1_UDIV24_ACCUMULATOR_RELEASE_2026-10-12.md'
MARK='2026-10-12 ISSUE39 V1 ACCUMULATOR-REMAINDER 61-BYTE 24/8 DIVMOD RELEASE'
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
 candidate,l,_=Assembler().assemble((ROOT/'tools/candidates/issue39_v1_24by8_accumulator.asm').read_text())
 assert len(candidate)==61 and l['V1LAT_24_BY_8']==0x1d00
 lo=int.from_bytes(old[:2],'little');assert lo==0x1000
 off=2+0x1d00-lo
 expected=bytearray(old)
 for a,b in candidate.items():expected[2+a-lo]=b
 expected[off+61:off+84]=bytes(23)
 assert restore_pr78(bytes(expected))==old
 newhash=hashlib.sha256(expected).hexdigest()
 print('EXPECTED V1 RESIDENT SHA',newhash,flush=True)

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
 assert abs(means['MATH_UDIV24']['v1_balanced']-166.190196)<0.00001,means
 assert abs(means['MATH_UMOD24']['v1_balanced']-234.433355)<0.00001,means

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

 details=f"""# Issue #39: integrated V1 61-byte accumulator-resident 24÷8 DIV/MOD

**2026-10-12. Source-backed release.** The V1 bounded 24÷8 engine now keeps the
partial 8-bit remainder in A during 24 shift/subtract steps and writes R0 once
on completion. Exactly **69→61 executable bytes**, while the original 84-byte
source-owned island stays reserved with 23 trailing zero bytes. The new engine
uses zero additional ZP or stack, leaves N/D unchanged, and preserves stable
public addresses, output flags and full resident size.

Source: `relocatable_source/v1_balanced/udiv24_latency_escape_balanced.inc`;
candidate: `tools/candidates/issue39_v1_24by8_accumulator.asm`.
Release resident SHA256: `{newhash}`; previous PR78 V1 SHA: `{PR78}`.
V5 SHA remains `{V5}`; V2/V3/V4 unchanged.

### Same-input complete-public-entry comparison

| API | PR78 baseline | Installed accumulator | Difference |
|---|---:|---:|---:|
| UDIV24 (4,753 samples) | 170.238165 | {means['MATH_UDIV24']['v1_balanced']:.6f} | {means['MATH_UDIV24']['v1_balanced']-170.238165:+.6f} |
| UMOD24 (1,553 samples) | 246.822279 | {means['MATH_UMOD24']['v1_balanced']:.6f} | {means['MATH_UMOD24']['v1_balanced']-246.822279:+.6f} |

The standalone research screen checked **48,388 paired prior/new full public
6502 calls**, with zero wrong Q/R/C, no input/stack clobber, and no slower
calls. The D8 4,080-case stress mean went 1202.660784→976.350000.
A separate native VICE x64sc old/new **isolated** kernel test passed 128
calls; do not misrepresent this as native full-resident coverage or timing.
Current resident source builds at reference/alternate maps, full five-profile
{u['summary']['machine_calls']} unsigned and {s['summary']['machine_calls']}
signed calls, and {common['total_calls']} same-input profile calls all pass.
The previous PR78 84→69-byte historical test is SHA-reconstructed and retains
its original certificate, rather than claiming its old metrics are the new ones.

This release is **part of** issue #39; the family-wide audit/no-gain review
and later ISQRT/UMUL/SMUL/etc campaign remain open.
"""
 (ROOT/DOC).write_text(details)
 link='- Issue #39 V1 accumulator 61-byte 24/8 shared DIV/MOD release: '+DOC+'. The unsigned campaign remains open.'
 for fn in ('README.md','USER_MANUAL.md'):
  p=ROOT/fn
  if link not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+link+'\n')
 log=f"""{MARK}
- V1 shared UDIV24/UMOD24 short-divisor kernel: keep partial R in A across all 24 iterations, 69→61 bytes, 23 padded bytes in the original 84-byte owned island. Zero new normal ZP/stack, stable API/addresses and resident size, V2–V5 byte-identical.
- 48,388 paired prior/new complete public CPU calls, no ABI errors or slower pairs; canonical same-input UDIV24 170.238165→{means['MATH_UDIV24']['v1_balanced']:.6f}, UMOD24 246.822279→{means['MATH_UMOD24']['v1_balanced']:.6f}. Native x64sc 128 isolated source-kernel correctness calls; full-resident native not claimed.
- Five-profile unsigned 822,050 and signed 364,533 calls; 136,335 same-input and 53,760 small-workload calls; historical parent reproducibility, reference/alternate source relocation, V5 isolation. Standalone mirrors, performance tables, release/checksums and docs refreshed. Campaign #39 remains OPEN. {DOC}
"""
 for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  p=ROOT/fn
  if MARK not in p.read_text():p.write_text(log+'\n'+p.read_text())
 state['date']='2026-10-12'
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
 state['issue39_v1_24by8_accumulator_release_2026_10_12']={
  'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
  'prior_v1_sha256':PR78,'new_v1_sha256':newhash,'unchanged_v5_sha256':V5,
  'public_abi_changed':False,'code_bytes_old':69,'code_bytes_new':61,
  'normal_zp_growth':0,'stack_growth':0,'resident_prg_growth':0,
  'paired_old_new_calls':48388,'paired_regressions':0,'native_isolated_calls':128,
  'native_full_resident_calls':None,
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
 print('ACCUMULATOR 61-BYTE RELEASE STAGED',newhash,flush=True)
if __name__=='__main__':main()
