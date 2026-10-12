#!/usr/bin/env python3
"""Publish source-verified V2/V3/V4 UMOD32_32 D=0 equality gate, without ABI or size growth.

GitHub Actions PR-branch only. Never commit candidate until full five-profile
regressions, source/alternate relocations and package seal pass.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
ALL=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
CHANGED=ALL[1:4]
DOC='docs/ISSUE39_V234_UMOD32_LATE_ZERO_2026-10-12.md'
PROOF='validation/review/ISSUE39_V234_32_32_LATEZERO_PAIRED.json'
VICE='validation/review/ISSUE39_V234_UMOD32_LATEZERO_NATIVE_VICE.json'
TAG='2026-10-12 ISSUE39 V2-V4 UMOD32 LATE ZERO CHECK'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def path(p):return f'{p}/resident/math_{p}_game_math.prg'
def run(*xs):
 print('RUN',*map(str,xs),flush=True);subprocess.run([str(x) for x in xs],cwd=ROOT,check=True)
def py(script,*args):run(sys.executable,'tools/'+script+'.py',*args)
def checksum():
 fs=sorted((p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='SHA256SUMS.txt'),key=lambda p:str(p.relative_to(ROOT)))
 (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in fs))
def perf(op,stats):
 dest=ROOT/'PERFORMANCE.md';ls=dest.read_text().splitlines()
 inds=[i for i,s in enumerate(ls) if s.startswith('| `'+op+'` |')]
 assert len(inds)==1
 cols=ls[inds[0]].split('|')
 for k,profile in enumerate(ALL):cols[3+k]=f' {stats[profile]:.6f} '
 ls[inds[0]]='|'.join(cols)
 dest.write_text('\n'.join(ls)+'\n')
def main():
 status=ROOT/'RELEASE_STATUS.json';state=json.loads(status.read_text())
 old={p:digest(path(p)) for p in ALL}
 assert old==state['reference_prg_sha256'],('baseline release SHA mismatch',old)
 native=json.loads((ROOT/VICE).read_text())
 assert native['status']=='PASS' and native['total_calls']==1536
 for p in CHANGED:assert native['profiles'][p]['old_sha256']==old[p]
 # Build the actual active remainder_fast_v2.inc source at reference and alternate.
 py('generate_sources')
 for kind in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',kind)
  py('build_hybrid','--config-kind',kind)
 py('screen_issue39_v234_32_32_latezero')
 proof=json.loads((ROOT/PROOF).read_text())
 assert proof['status']=='PASS' and proof['total_old_new_calls']==36036
 for p in CHANGED:
  f=ROOT/'build_source/reference'/p/f'math_{p}_source_built.prg'
  assert digest(f.relative_to(ROOT))==native['profiles'][p]['new_sha256']
  assert proof['profiles'][p]['changed_bytes']==50
  assert proof['profiles'][p]['new_sha256']==digest(f.relative_to(ROOT))
  shutil.copyfile(f,ROOT/path(p))
 for p in (ALL[0],ALL[-1]):assert digest(path(p))==old[p]
 # Exactly rebuild everything from installed residents; this is required so
 # next release's generated source matches source-of-truth after publication.
 py('generate_sources')
 for kind in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',kind)
  py('build_hybrid','--config-kind',kind)
 for p in ALL:
  q=(ROOT/'build_hybrid/reference/v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg') if p==ALL[-1] else ROOT/'build_source/reference'/p/f'math_{p}_source_built.prg'
  assert hashlib.sha256(q.read_bytes()).hexdigest()==digest(path(p)),('not deterministic',p)
 # Validate all profiles, not only the three affected residents.
 py('validate_unsigned_division')
 py('benchmark_unsigned_common_corpus')
 py('audit_issue39_unsigned_small_workloads')
 py('benchmark_unsigned_3216_workloads')
 py('validate_signed_division')
 common=json.loads((ROOT/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
 unsigned=json.loads((ROOT/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
 signed=json.loads((ROOT/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
 assert common['status']==unsigned['status']==signed['status']=='PASS'
 assert common['total_calls']==136335
 assert unsigned['summary']['machine_calls']==822050
 previous={'v2_pareto_fast':295.997654,'v3_reu_512k':295.997654,'v4_reu_16m':295.997654}
 changed_means={p:common['routines']['MATH_UMOD32_32']['metrics'][p]['mean_cycles'] for p in ALL}
 for p in CHANGED:assert changed_means[p]<previous[p] and changed_means[p]>0,(p,changed_means[p])
 perf('MATH_UMOD32_32',changed_means)
 # Also refresh signed/public standalone source and consolidated catalog.
 py('publish_standalone_sources')
 py('generate_consolidated_routine_table')
 py('generate_public_indexes')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 rows=[]
 for p in CHANGED:
  z=proof['profiles'][p]['operations']['MATH_UMOD32_32']
  rows.append(f"| {p} | {z['case_count']:,} | {-z['mean_delta_cycles']:.6f} | {z['faster']:,} | {z['equal']:,} | {z['slower']:,} | {changed_means[p]:.6f} |")
 document=f"""# Issue39: V2–V4 unsigned 32/32 modulo delayed-zero guard

**2026-10-12** · Source-qualified, native x64sc verified, complete resident-size-neutral
improvement. **Unsigned DIV/MOD campaign remains open.**

## Mechanism

Only the V2/V3/V4 source-owned remainder-only `RM3232U_ENTRY` gate in
`relocatable_source/division/remainder_fast_v2.inc` changes. The canonical
54-byte gate starts at $5472. Its existing 14-byte divisor-zero OR/test
precedes the high-to-low unsigned N/D comparison. Relocate that same
14-byte OR/test to the **N=D branch** (the only comparison outcome where
both might be zero). N<D proves divisor nonzero; N>D continues to the
original public divider with its own D=0 guard. Four branch offsets adjust
to preserve identical targets. **Exactly 50 code bytes change in each of
V2, V3, V4 and no other resident bytes change.** Total resident, normal ZP,
table/REU contents, public API, and source-relocation contract unchanged.
V1 and V5 remain byte-identical.

## Performance and verification

The candidate was compared at unchanged public entry $5E03 on identical
operand pairs, including zero divisor, equality, high quotient and random.
The same corpus also called UDIV32/32 at $5E00.

| Profile | Modulo sampled input pairs | Mean cycles saved | Faster | Tied | Slower | New official common-input mean |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

- The **36,036** old/new public 6502 calls across V2/V3/V4 passed. For
  UDIV32/32, all **3,515 cases per profile** have exact cycle parity and
  identical quotient/remainder/flags. For UMOD32/32, all **2,491 pairs
  per profile** produce identical remainder, carry, preserved N/D, external
  sentinel, and even original Q side effects. A few D=0 cases are slower;
  aggregate means reflect the explicit corpus, not universal dominance.
- Native x64sc full-resident old/new public ABI report: **1,536 calls**;
  all Q/R/status observations match, no mathematical errors. This is not
  a native hardware cycle report. `{VICE}`.
- Exact reference binaries rebuilt from source and alternate relocations
  compiled successfully. The generated canonical sources reproduce the
  exact published reference residents. This change is *not* editing a
  dormant udiv32_32_early_gate.inc; that historical fragment is unused in
  the current V2–V4 source build.
- The full unsigned division validator (**{unsigned['summary']['machine_calls']:,}**
  public calls) and full signed division validator passed on all five
  profiles. All five common-input unsigned routines recomputed using the
  same benchmark specification (**{common['total_calls']:,} calls total**).
- Repose's standalone generators have not been copied. This is a manual
  in-core rearrangement of the library's own remainder frontend.
- Results and proof: `{PROOF}`. Executable check:
  `tools/screen_issue39_v234_32_32_latezero.py`.

The remainder of issue #39's entire unsigned DIV/MOD family still requires
its own production/no-gain decisions; **do not mark the campaign item complete**.
"""
 (ROOT/DOC).write_text(document)
 blurb=f'- Issue #39 V2/V3/V4 UMOD32/32 equality-only divide-by-zero test: [source/VICE/public-ABI proof]({DOC}); size and ZP unchanged, family campaign open.'
 for p in ('README.md','USER_MANUAL.md'):
  f=ROOT/p;s=f.read_text()
  if blurb not in s:f.write_text(s.rstrip()+'\n\n'+blurb+'\n')
 log=f"""{TAG}
- Improved V2/V3/V4 MATH_UMOD32_32: move 14-byte divisor-zero check from entry to N=D equality branch. 54-byte fixed-size active remainder frontend at $5472; exactly 50 changed bytes per resident, no resident/ZP/stack/API or REU growth. V1/V5 unmodified. UDIV32_32 cycles and outputs unchanged.
- Same-input 2,491-pair profile screens: savings V2=13.599358, V3=13.594540, V4=13.599358 cycles per public call; 36,036 total old/new 6502 calls, zero ABI errors. Native VICE 1,536 old/new calls also correct (not a timing claim). Full five-profile unsigned and signed validation, sources, alternate build, docs, checksums sealed. See {DOC}. Unsigned family still OPEN.
"""
 for p in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=ROOT/p;s=f.read_text()
  if TAG not in s:f.write_text(log+'\n'+s)
 state=json.loads(status.read_text())
 state['date']='2026-10-12'
 state['reference_prg_sha256']={p:digest(path(p)) for p in ALL}
 state['alternate_prg_sha256']={p:json.loads((ROOT/'build_source/alternate'/p/'source_build_manifest.json').read_text())['output_sha256'] for p in ALL[:4]}
 state['alternate_prg_sha256'][ALL[-1]]=json.loads((ROOT/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
 state['issue39_v234_umod32_latezero_2026_10_12']={
  'status':'PASS','document':DOC,'unsigned_family_complete':False,
  'changed_profiles':list(CHANGED),'unchanged_profiles':[ALL[0],ALL[-1]],
  'old_reference_sha256':{p:old[p] for p in CHANGED},
  'new_reference_sha256':{p:digest(path(p)) for p in CHANGED},
  'changed_bytes_per_profile':50,'resident_growth':0,'normal_zp_growth':0,
  'public_abi_changed':False,'public_old_new_emulated_calls':proof['total_old_new_calls'],
  'native_x64sc_old_new_calls':native['total_calls'],
  'native_report_sha256':digest(VICE),
  'paired_report_sha256':digest(PROOF),
  'same_input_all_unsigned_calls':common['total_calls'],
  'unsigned_correctness_calls':unsigned['summary']['machine_calls'],
  'signed_correctness_profiles':len(signed['profiles']),
  'new_official_umod3232_means':{p:changed_means[p] for p in CHANGED}}
 for k,p,field in (
  ('issue39_common_input_unsigned_divmod','validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json','benchmark_sha256'),
  ('issue39_unsigned_small_width_workloads_2026_10_11','validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','data_sha256'),
  ('issue39_unsigned_3216_multiworkload_2026_10_11','validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json','report_sha256')):
  if isinstance(state.get(k),dict):state[k][field]=digest(p)
 if isinstance(state.get('documentation'),dict):
  p=ROOT/'USER_MANUAL.md';state['documentation'].update(
   user_manual_bytes=p.stat().st_size,user_manual_lines=len(p.read_text().splitlines()),
   user_manual_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 status.write_text(json.dumps(state,indent=2)+'\n')
 py('verify_deterministic_rebuild')
 run('make','clean')
 for i in range(4):
  checksum();py('package_audit')
  if all(row.split('  ',1)[0]==digest(row.split('  ',1)[1]) for row in (ROOT/'SHA256SUMS.txt').read_text().splitlines()):break
 else:raise AssertionError('failed stable checksum/package seal')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 checksum();py('package_audit')
 print('ISSUE39 V2-V4 UMOD32/32 NATIVE QUALIFIED RELEASE STAGED PASS',flush=True)
if __name__=='__main__':main()
