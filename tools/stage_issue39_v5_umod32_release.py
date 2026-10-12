#!/usr/bin/env python3
"""Issue39 PR71 V5 Q-preserving 32/32 modulo release staging.

Only to be used on the dedicated PR branch. The native-verified in-resident
V5 front end is installed only after SHA-pinned source and Q/R/C comparison
proofs; all five-profile correct + mixed call benchmarks rerun before seal.
"""
from pathlib import Path
import hashlib,json,subprocess,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
ALL=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OLD='634e58f536374bc12877e692515f68ab5c5f38954caf5c189a8f67d356289d02'
NEW='5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222'
PRF='validation/review/ISSUE39_V5_UMOD3232_REORDERED_SHARED_GATE_SCREEN.json'
SRC='validation/review/ISSUE39_V5_UMOD32_SOURCE_QUALIFIED.json'
VICE='validation/review/ISSUE39_V5_UMOD32_NATIVE_VICE.json'
DOC='docs/ISSUE39_V5_UMOD32_QPRESERVING_REORDERED_2026-10-12.md'
TAG='2026-10-12 ISSUE39 V5 UMOD32 QUOTIENT-PRESERVING SOURCE FRONTEND'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def prg(p):return f'{p}/resident/math_{p}_game_math.prg'
def py(name,*args):
 print('RUN',name,*args,flush=True)
 subprocess.run([sys.executable,'tools/'+name+'.py',*args],cwd=ROOT,check=True)
def cmd(*args):
 print('RUN',*args,flush=True);subprocess.run(args,cwd=ROOT,check=True)
def checksum():
 files=sorted((f for f in ROOT.rglob('*') if f.is_file() and '.git' not in f.parts and f.name!='SHA256SUMS.txt'),key=lambda x:str(x.relative_to(ROOT)))
 (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n' for f in files))
def perf(op,stats):
 p=ROOT/'PERFORMANCE.md';lines=p.read_text().splitlines()
 ids=[i for i,row in enumerate(lines) if row.startswith('| `'+op+'` |')]
 assert len(ids)==1,ids
 cols=lines[ids[0]].split('|')
 for i,profile in enumerate(ALL):cols[3+i]=f' {stats[profile]:.6f} '
 lines[ids[0]]='|'.join(cols);p.write_text('\n'.join(lines)+'\n')
def main():
 statep=ROOT/'RELEASE_STATUS.json';state=json.loads(statep.read_text())
 old={p:sha(prg(p)) for p in ALL}
 assert state['reference_prg_sha256']==old,(old,state['reference_prg_sha256'])
 assert old[ALL[-1]]==OLD
 native=json.loads((ROOT/VICE).read_text())
 assert native['status']=='PASS' and native['old_new_calls']==512
 assert native['old_resident_sha256']==OLD and native['new_resident_sha256']==NEW
 # Screen all three V5 architecture candidates prior to installing new PRG.
 py('screen_issue39_v5_umod32_qpreserving')
 py('screen_issue39_v5_umod32_highbyte')
 py('screen_issue39_v5_umod32_reordered')
 screen=json.loads((ROOT/PRF).read_text())
 assert screen['status']=='PASS' and screen['errors']==0 and screen['tested_cases']==4314
 assert screen['corpus_means']['official']['cases']==1705
 assert screen['corpus_means']['official']['mean_delta']<0
 # Compile all reference and independently relocated alternate layouts.
 py('generate_sources')
 for config in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',config)
  py('build_hybrid','--config-kind',config)
 py('screen_issue39_v5_umod32_source')
 proof=json.loads((ROOT/SRC).read_text())
 assert proof['status']=='PASS' and proof['native_candidate_sha256']==NEW
 candidate=ROOT/'build_hybrid/reference/v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg'
 assert hashlib.sha256(candidate.read_bytes()).hexdigest()==NEW
 shutil.copyfile(candidate,ROOT/prg(ALL[-1]))
 assert sha(prg(ALL[-1]))==NEW
 for p in ALL[:-1]:assert sha(prg(p))==old[p],p
 # Rebuild from public shipped source after replacement and require byte parity.
 py('generate_sources')
 for config in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',config)
  py('build_hybrid','--config-kind',config)
 assert hashlib.sha256(candidate.read_bytes()).hexdigest()==NEW
 for p in ALL[:-1]:
  f=ROOT/'build_source/reference'/p/f'math_{p}_source_built.prg'
  assert hashlib.sha256(f.read_bytes()).hexdigest()==old[p],p
 # Full correctness and independent same-input benchmarking; no profile skipped.
 py('validate_unsigned_division')
 py('benchmark_unsigned_common_corpus')
 py('audit_issue39_unsigned_small_workloads')
 py('benchmark_unsigned_3216_workloads')
 py('validate_signed_division')
 py('validate_v5_umod16_frontend')
 # With PR70 V2 source now published, the historical replay helpers accept only
 # SHA-qualified image restorations; never label a newer release as old.
 # Preserve the exact historical report bytes through SHA-qualified parent
 # reconstruction. The current V5 includes a new independent 147-byte island.
 frozen=sha('validation/review/ISSUE39_V1V5_UMOD8_GUARD_EXHAUSTIVE.json')
 py('audit_issue39_v1v5_umod8_guard')
 assert sha('validation/review/ISSUE39_V1V5_UMOD8_GUARD_EXHAUSTIVE.json')==frozen
 py('audit_issue39_zero_high_bypass')
 common=json.loads((ROOT/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
 unsigned=json.loads((ROOT/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
 signed=json.loads((ROOT/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
 assert common['status']==unsigned['status']==signed['status']=='PASS'
 assert common['total_calls']==136335
 assert unsigned['summary']['machine_calls']==822050
 means={p:common['routines']['MATH_UMOD32_32']['metrics'][p]['mean_cycles'] for p in ALL}
 previous=302.353079
 assert means[ALL[-1]]<previous and means[ALL[-1]]>0,means
 perf('MATH_UMOD32_32',means)
 py('publish_standalone_sources')
 py('generate_consolidated_routine_table')
 py('generate_public_indexes')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 official=screen['corpus_means']['official']
 document=f"""# Issue #39 — V5 UMOD32/32 quotient-preserving delayed-zero front end

**12 October 2026 — qualified V5 source-backed public-ABI improvement.**
The broader unsigned DIV/MOD campaign remains OPEN.

## Design and ABI

V5 historically exposes MATH_UMOD32_32 at $5E03 as an alias of its
quotient-producing MATH_UDIV32_32. Unlike the V2/V3/V4 remainder-only
front ends, V5's documented public API returns **Q32 and R32** even for
UMOD32_32. The candidate honors both outputs, success/divisor-zero carry,
input N/D ownership, and leaves MATH_UDIV32_32 unchanged.

A dedicated 147-byte NMOS 6510 private gate, generated from
`tools/v5_umod32_qpreserving_source.py`, is installed at $5E80 into a
checked empty resident island. Public $5E03 changes from JMP $5957 to
JMP $5E80, without moving any public symbol or increasing the PRG size.
Normal ZP stays 31 bytes.

The new 32-bit high-to-low comparison sends N<D directly to Q=0/R=N.
Only the rare equality test checks D=0. For N>D the original high-qone
helper receives the saved compare accumulator and carry; PHA/PLA protects
A/C during the D=0 check. Zero divisors still go to the original routine.
The alternate V5 configuration compiles from the same symbolic source.

## Measured, with explicit distribution caveat

V5 public-entry Reduced6502 A/B screen: **4,314 identical operand pairs**
on old/new complete resident images, with Q32/R32/C/N/D and external
sentinel exact on all. Overall weighted mean saving
**{-screen['mean_delta_cycles']:.6f} cycles** (1,518 faster, 540 ties,
2,256 slower); this constructed stress mix is *not* an unbiased workload.
On the official 1,705 same-input UMOD32_32 corpus, mean saving
**{-official['mean_delta']:.6f} cycles** (official new V5 mean
**{means[ALL[-1]]:.6f} cycles**, previous V5 **{previous:.6f}**).
Some divide-by-zero and N>D fallback cases slow down, up to their recorded
class maximum; no global cycle dominance is claimed.

Repose-derived exploration first screened two alternatives (127-byte
full-gate and 51-byte high-byte-only) that were +7.34 and +7.36 cycles
slower on the constructed 4,314-pair corpus. This is a hand-written source
synthesis, not a direct import of unpublished OptiSearch machine-code blobs.

Native VICE x64sc full-resident A/B completed **512 calls** (256 input
pairs, each original and candidate), with correct Q32/R32/carry including
divide-by-zero and quotient boundary cases. Evidence: `{VICE}`.
It is a correctness validation, *not* cycle timing or REU DMA measurement.

Reference source assembly **exactly matches the VICE-tested candidate**
SHA-256 `{NEW}`, and alternate relocated source builds successfully.
Only $5E03–$5E05 and $5E80–$5F12 differ from the previous resident.
V1–V4 images are byte-identical. All five-profile unsigned and signed
correctness/cycle reports, paired unsigned common corpus and historical
SHA-frozen UMOD8/zero-high-bypass audits were rerun.

Next work: examine remaining quotient-tail DIV/MOD optimizations, then the
integer-root campaign. The unsigned campaign checkbox is **NOT** crossed.
"""
 (ROOT/DOC).write_text(document)
 blurb=f'- Issue #39 V5 UMOD32/32 full-Q remainder front end: [source/native verified delayed-zero comparator]({DOC}); V1–V4 unchanged, unsigned family campaign remains open.'
 for p in ('README.md','USER_MANUAL.md'):
  f=ROOT/p;s=f.read_text()
  if blurb not in s:f.write_text(s.rstrip()+'\n\n'+blurb+'\n')
 log=f"""{TAG}
- V5 MATH_UMOD32_32 new 147-byte Q32+R32-compatible delayed-zero front end in previously free $5E80 island, public JMP redirected at $5E03. Existing MATH_UDIV32_32 untouched. No resident, normal-ZP, API or other profile growth. Native VICE 512 old/new calls passed.
- Official 1,705-pair identical-input common corpus: {-official['mean_delta']:.6f} cycles faster, V5 mean {previous:.6f}->{means[ALL[-1]]:.6f}; full 4,314-pair quotient-stratified stress mix saves {-screen['mean_delta_cycles']:.6f} cycles but includes some slower high-quotient/zero-divisor cases. Source and alternate V5 hybrid builds reproduce candidate. Full unsigned/signed corpus and historical audit checks, standalone source catalogs, changelogs, checksums refreshed. Issue39 unsigned family remains open. {DOC}
"""
 for p in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=ROOT/p;s=f.read_text()
  if TAG not in s:f.write_text(log+'\n'+s)
 state=json.loads(statep.read_text());state['date']='2026-10-12'
 state['reference_prg_sha256']={p:sha(prg(p)) for p in ALL}
 state['alternate_prg_sha256']={p:json.loads((ROOT/'build_source/alternate'/p/'source_build_manifest.json').read_text())['output_sha256'] for p in ALL[:4]}
 state['alternate_prg_sha256'][ALL[-1]]=json.loads((ROOT/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
 state['issue39_v5_umod32_qcomplete_2026_10_12']={
   'status':'PASS','document':DOC,'unsigned_family_complete':False,
   'changed_profile':ALL[-1],'unchanged_profiles':list(ALL[:-1]),
   'old_resident_sha256':OLD,'new_resident_sha256':NEW,
   'private_code_bytes':147,'resident_growth':0,'normal_zp_growth':0,
   'public_abi_changed':False,'native_x64sc_old_new_calls':512,
   'native_report_sha256':sha(VICE),'paired_report_sha256':sha(PRF),
   'source_build_sha256':sha(SRC),'official_corpus_cases':official['cases'],
   'official_corpus_mean':means[ALL[-1]],
   'full_unsigned_correctness_calls':unsigned['summary']['machine_calls'],
   'total_unsigned_common_corpus_calls':common['total_calls'],
   'historical_v5_restorer_sha256':sha('tools/issue39_v5_umod32_parent.py')}
 for key,p,field in (
   ('issue39_common_input_unsigned_divmod','validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json','benchmark_sha256'),
   ('issue39_unsigned_small_width_workloads_2026_10_11','validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','data_sha256'),
   ('issue39_unsigned_3216_multiworkload_2026_10_11','validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json','report_sha256')):
  if isinstance(state.get(key),dict):state[key][field]=sha(p)
 if isinstance(state.get('documentation'),dict):
  p=ROOT/'USER_MANUAL.md';state['documentation'].update(
    user_manual_bytes=p.stat().st_size,user_manual_lines=len(p.read_text().splitlines()),
    user_manual_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 statep.write_text(json.dumps(state,indent=2)+'\n')
 py('verify_deterministic_rebuild')
 cmd('make','clean')
 for _ in range(4):
  checksum();py('package_audit')
  if all(line.split('  ',1)[0]==sha(line.split('  ',1)[1]) for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines()):break
 else:raise AssertionError('checksums/package seal did not stabilize')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 checksum();py('package_audit')
 print('ISSUE39 PR71 V5 UMOD32 Q-PRESERVING NATIVE QUALIFIED RELEASE STAGING PASS',flush=True)
if __name__=='__main__':main()
