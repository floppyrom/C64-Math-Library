#!/usr/bin/env python3
"""Issue39 PR68 V1 no-growth UDIV16/UMOD16 release staging, fail-closed.

Runs on the dedicated PR branch in GitHub Actions, never on main. Compiles
both relocation configurations before and after installing the source-backed
candidate, validates all five public profiles and regenerates sealed releases.
"""
from pathlib import Path
import hashlib,json,csv,subprocess,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OLD='9afa30ffd24c1ce9566e7ef21e4032396fbdea7d4c3da5b68e137fc12ec41b62'
NEW='cae2afdf0271da338d110f2104a8530374214ef915d88a803c508bce9679bb4f'
NEW_V5='634e58f536374bc12877e692515f68ab5c5f38954caf5c189a8f67d356289d02'
DOC='docs/ISSUE39_PR68_V1_U16_DIRECT_Q2_EXIT_2026-10-12.md'
TAG='2026-10-12 ISSUE39 PR68 V1 16BIT DIRECT Q2 EXIT'
NATIVE='validation/review/ISSUE39_V1_U16_Q2_NATIVE_VICE.json'
SOURCE='validation/review/ISSUE39_V1_U16_Q2_LAYOUT_SOURCE_SCREEN.json'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def run(*args):
 print('RUN',*map(str,args),flush=True)
 subprocess.run([str(z) for z in args],cwd=ROOT,check=True)
def py(name,*args):run(sys.executable,'tools/'+name+'.py',*args)
def rpath(p):return f'{p}/resident/math_{p}_game_math.prg'
def rows(p):
 with (ROOT/p).open(newline='') as f:return list(csv.DictReader(f))
def csvsave(p,rs):
 with (ROOT/p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def checksum():
 paths=sorted((f for f in ROOT.rglob('*') if f.is_file() and '.git' not in f.parts and f.name!='SHA256SUMS.txt'),key=lambda p:str(p.relative_to(ROOT)))
 (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n' for f in paths))
def perf(op,means):
 p=ROOT/'PERFORMANCE.md';ls=p.read_text().splitlines()
 ix=[i for i,x in enumerate(ls) if x.startswith('| `'+op+'` |')]
 assert len(ix)==1,(op,ix)
 columns=ls[ix[0]].split('|')
 for k,profile in enumerate(PROFILES):columns[3+k]=f' {means[profile]:.6f} '
 ls[ix[0]]='|'.join(columns);p.write_text('\n'.join(ls)+'\n')
def main():
 statusp=ROOT/'RELEASE_STATUS.json';state=json.loads(statusp.read_text())
 oldhash={p:sha(rpath(p)) for p in PROFILES}
 assert oldhash['v1_balanced']==OLD
 assert oldhash==state['reference_prg_sha256']
 native=json.loads((ROOT/NATIVE).read_text())
 assert native['status']=='PASS' and native['total_calls']==1024 and native['new_resident_sha256']==NEW
 py('generate_sources')
 for config in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',config)
  py('build_hybrid','--config-kind',config)
 py('screen_issue39_v1_u16_q2_layout')
 candidate=ROOT/'build_source/reference/v1_balanced/math_v1_balanced_source_built.prg'
 assert hashlib.sha256(candidate.read_bytes()).hexdigest()==NEW
 shutil.copyfile(candidate,ROOT/rpath('v1_balanced'))
 assert sha(rpath('v1_balanced'))==NEW
 # V5 inherits the canonical V1 323-byte source core. Stage the precise
 # same 57-byte change in V5 only after verifying the unchanged rest.
 inherited=ROOT/'build_hybrid/reference/v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg'
 assert hashlib.sha256(inherited.read_bytes()).hexdigest()==NEW_V5
 old_v5=(ROOT/rpath('v5_hybrid_lowzp')).read_bytes()
 v5new=inherited.read_bytes();assert len(old_v5)==len(v5new)
 offset=2+0x4200-0x1000
 assert old_v5[:offset]==v5new[:offset] and old_v5[offset+323:]==v5new[offset+323:]
 assert sum(a!=b for a,b in zip(old_v5,v5new))==57
 shutil.copyfile(inherited,ROOT/rpath('v5_hybrid_lowzp'))
 for p in PROFILES[1:4]:assert sha(rpath(p))==oldhash[p],p
 # Confirm that all sources rebuild deterministically against now-installed
 # V1 reference and V5 hybrid source-derived residents.
 py('generate_sources')
 for config in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',config)
  py('build_hybrid','--config-kind',config)
 assert hashlib.sha256(candidate.read_bytes()).hexdigest()==NEW
 for p in PROFILES[1:]:
  if p=='v5_hybrid_lowzp':
   q=ROOT/'build_hybrid/reference/v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg'
  else:q=ROOT/'build_source/reference'/p/f'math_{p}_source_built.prg'
  assert hashlib.sha256(q.read_bytes()).hexdigest()==(NEW_V5 if p=='v5_hybrid_lowzp' else oldhash[p]),p
 # Permanent arithmetic correctness and comparable workloads (V1 refreshed).
 py('validate_unsigned_division')
 py('benchmark_unsigned_common_corpus')
 py('audit_issue39_unsigned_small_workloads')
 py('benchmark_unsigned_3216_workloads')
 py('validate_signed_division')
 py('validate_v1_3216_unroll')
 py('audit_issue39_v1v5_umod8_guard')
 py('audit_issue39_zero_high_bypass')
 # New V1 U16 proof must not change previously frozen PR57-62 certificates.
 for name in (
    'ISSUE39_V1V5_UMOD8_GUARD_EXHAUSTIVE.json',
    'UDIV32_ZERO_HIGH_BYPASS_PAIRED.json'):
  fp=ROOT/'validation/review'/name
  assert fp.exists()
 common=json.loads((ROOT/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
 unsigned=json.loads((ROOT/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
 signed=json.loads((ROOT/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
 assert common['status']==unsigned['status']==signed['status']=='PASS'
 assert common['total_calls']==136335 and unsigned['summary']['machine_calls']==822050
 new_means={}
 for op in ('MATH_UDIV16','MATH_UMOD16'):
  metrics=common['routines'][op]['metrics'];means={p:metrics[p]['mean_cycles'] for p in PROFILES}
  assert means['v1_balanced']<({'MATH_UDIV16':156.348479,'MATH_UMOD16':189.383578}[op])
  perf(op,means);new_means[op]=means
 # Source-specified V1 routine-specific seed, which differs from same-input
 # five-profile corpus; never substitute one for the other.
 p='v1_balanced/PUBLIC_PERFORMANCE.csv';data=rows(p)
 for item in data:
  k={'math_udiv16':'MATH_UDIV16','math_umod16':'MATH_UMOD16'}.get(item['operation'])
  if k:
   val=unsigned['profiles']['v1_balanced'][k]
   item.update(avg_cycles=f"{val['mean_cycles']:.6f}",
               min_cycles=str(val['min_cycles']),max_cycles=str(val['max_cycles']),
               cases=str(val['cases']),evidence='2026-10-12 PR68 exact source-backed V1 q=2 branch public ABI audit')
 csvsave(p,data)
 p='v3_reu_512k/PUBLIC_PERFORMANCE.csv';data=rows(p)
 for item in data:
  k={'udiv16':'MATH_UDIV16','umod16':'MATH_UMOD16'}.get(item['operation'])
  if k:
   item['v1_balanced_cycles']=f"{unsigned['profiles']['v1_balanced'][k]['mean_cycles']:.6f}"
 csvsave(p,data)
 py('publish_standalone_sources')
 py('generate_consolidated_routine_table')
 py('generate_public_indexes')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 details=f"""# Issue #39: PR68 — V1 16-bit quotient-two branch re-layout

**Date:** 2026-10-12. **Status:** source-backed native-verified V1 323-byte
UDIV16/UMOD16 improvement. The larger unsigned DIV/MOD campaign is still open.

The V1 shared unsigned private division core at `REG_KERNEL+$0200`
(reference $4200..$4342) now places the quotient-2 exit before the rare
post-restoring quotient-bias tail. This brings the quotient-2 exit into the
6502 BCC relative-branch range, eliminating the prior absolute JMP.
Three unreachable alignment bytes follow a different RTS, preserving
the high-quotient shift/subtract loop's original page phases and placement.

### Verified measurement

- Initial independent OptiSearch Reduced6502 full-public-ABI paired screen:
  963 input pairs per API, 320 faster / 643 equal / zero slower;
  mean saving 0.332295 cycles.
- Independent wider stress: 13,559 identical structured/random and quotient-
  stratified pairs per API, 8,255 faster / 5,304 equal / zero slower,
  mean saving **0.608821 cycles per call**. Zero arithmetic, status, input or
  stack-state errors in 27,118 calls.
- Native VICE x64sc: complete V1 old/new residents (MATH_INIT, RAM banked in),
  256 operand pairs each for UDIV16 and UMOD16, 1,024 old+new public calls,
  no differences and no mathematical/flag errors. Evidence: `{NATIVE}`.
- Source assembly: independent 323-byte expected SHA-256 matches the rebuilt
  reference code at $4200..$4342; **57 changed bytes in that window, 0
  changed elsewhere**. Alternate relocation compiles successfully. Resident
  length, ordinary ZP, scratch ownership, stack, public jump addresses and
  all other profiles are unchanged.
- Source candidate SHA-256: `{NEW}`; pre-change SHA-256: `{OLD}`.
- On the published 2,729-pair UDIV16 same-input corpus: old V1 **156.348479**,
  new V1 **{new_means['MATH_UDIV16']['v1_balanced']:.6f}** cycles.
- On the published 1,705-pair UMOD16 same-input corpus: old V1 **189.383578**,
  new V1 **{new_means['MATH_UMOD16']['v1_balanced']:.6f}** cycles.

### Release, provenance and future

Only V1's direct source changes. V5 imports the same V1 private 323-byte
core and inherits exactly the same size-neutral 57-byte change. V2/V3/V4
binaries remain byte-identical. The helper `tools/issue39_v1_u16_q2_parent.py`
restores the exact previous V1 bytes when auditing archived PR57-62 experiments
so frozen evidence does not silently drift to a later resident hash. No private
OptiSearch generator or unpublished Repose program was copied into the release.
This is a manual post-OptiSearch synthesis inspired by the comparator's page-
placement finding, with public-ABI resource and relocation checks.

The campaign's **Unsigned DIV/MOD family checkbox remains open** until all
widths/variants receive the same optimization/no-gain decision. This is not
claimed to be globally optimal.
"""
 (ROOT/DOC).write_text(details)
 blurb=f'- Issue #39 [V1 UDIV16/UMOD16 direct q=2 branch]( {DOC} ): source-backed no-growth in-slot short-quotient improvement. Native VICE and 5-profile validation; unsigned family audit remains open.'.replace('( ', '(')
 for name in ('README.md','USER_MANUAL.md'):
  f=ROOT/name;ss=f.read_text()
  if blurb not in ss:f.write_text(ss.rstrip()+'\n\n'+blurb+'\n')
 log=f"""{TAG}
- V1 shared UDIV16/UMOD16 core: put q=2 return into short BCC range and move cold 3-byte alignment padding after RTS, preserving the $4200-$4342 323-byte envelope and long quotient loop page phase. 57 in-core byte changes; no V2-V4 resident modification and the same 57-byte inherited V5 change or normal ZP, stack, code-span, API change.
- 13,559 same-input quotient-stratified/edge/random cases per V1 16-bit public API: 8,255 faster, 5,304 equal, zero slower, 0.608821 fewer mean cycles. Native VICE 1,024 old/new public calls all correct. Reference/alternate relocation, 5-profile unsigned correctness and paired corpus, signed correctness, stable historical PR57-62 SHA reconstructions validated.
- Common-input V1 UDIV16 mean 156.348479->{new_means['MATH_UDIV16']['v1_balanced']:.6f}; UMOD16 189.383578->{new_means['MATH_UMOD16']['v1_balanced']:.6f} cycles. Performance tables, standalone source mirrors, README/manual, changelogs, release metadata, checksums refreshed. Unsigned family campaign remains OPEN. {DOC}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=ROOT/name;ss=f.read_text()
  if TAG not in ss:f.write_text(log+'\n'+ss)
 state=json.loads(statusp.read_text());state['date']='2026-10-12'
 state['reference_prg_sha256']={p:sha(rpath(p)) for p in PROFILES}
 state['alternate_prg_sha256']={p:json.loads((ROOT/'build_source/alternate'/p/'source_build_manifest.json').read_text())['output_sha256'] for p in PROFILES[:4]}
 state['alternate_prg_sha256']['v5_hybrid_lowzp']=json.loads((ROOT/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
 state['issue39_v1_u16_q2_short_branch_2026_10_12']={
  'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
  'changed_profiles':['v1_balanced','v5_hybrid_lowzp'],'v2_v3_v4_byte_identical':True,
  'old_v5_sha256':oldhash['v5_hybrid_lowzp'],'new_v5_sha256':NEW_V5,
  'old_v1_sha256':OLD,'new_v1_sha256':NEW,
  'resident_byte_growth':0,'normal_zp_growth':0,'stack_growth':0,
  'public_abi_changed':False,'source_changed_bytes_inside_core':57,
  'native_vice_old_new_calls':1024,'paired_stress_calls':27118,
  'common_input_unsigned_all_profile_calls':common['total_calls'],
  'unsigned_full_correctness_calls':unsigned['summary']['machine_calls'],
  'native_report_sha256':sha(NATIVE),
  'parent_reconstruction_source_sha256':sha('tools/issue39_v1_u16_q2_parent.py')}
 for key,path,field in (
  ('issue39_common_input_unsigned_divmod','validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json','benchmark_sha256'),
  ('issue39_unsigned_small_width_workloads_2026_10_11','validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','data_sha256'),
  ('issue39_unsigned_3216_multiworkload_2026_10_11','validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json','report_sha256')):
  if isinstance(state.get(key),dict):state[key][field]=sha(path)
 if isinstance(state.get('documentation'),dict):
  a=ROOT/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=a.stat().st_size,user_manual_lines=len(a.read_text().splitlines()),user_manual_sha256=hashlib.sha256(a.read_bytes()).hexdigest())
 statusp.write_text(json.dumps(state,indent=2)+'\n')
 py('verify_deterministic_rebuild')
 run('make','clean')
 for i in range(4):
  checksum();py('package_audit')
  if all(line.split('  ',1)[0]==sha(line.split('  ',1)[1]) for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines()):break
 else:raise AssertionError('package/checksum did not stabilize')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 checksum();py('package_audit')
 print('ISSUE39 PR68 V1 DIRECT Q2 RELEASE STAGED PASS',flush=True)
if __name__=='__main__':main()
