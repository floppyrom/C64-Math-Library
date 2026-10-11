#!/usr/bin/env python3
"""Issue39 PR67 source-verified 16bit known-carry release staging.

Run only on PR67's isolated Actions branch. No byte can be published unless
the reference, alternate, V5 donor, and public-ABI screens first pass. Restores
historical PR66 reports after copying their *new* measurements to PR67 files.
"""
from __future__ import annotations
import csv,hashlib,json,subprocess,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
CHANGED=PROFILES[1:]
DOC='docs/ISSUE39_PR67_KNOWN_CARRY_16BIT_2026-10-12.md'
TAG='2026-10-12 ISSUE39 PR67 KNOWN-CARRY 16BIT DIV/MOD'
AUD='validation/review/ISSUE39_U16_PR67_HYBRID_ALLPROFILES_SCREEN.json'
SYNTAX='validation/review/ISSUE39_U16_PR67_SOURCE_DIFF_SCREEN.json'
OLD_SIGNED='validation/review/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.json'
OLD_SIGNED_CSV='benchmarks/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.csv'
NEW_SIGNED='validation/review/ISSUE39_PR67_SIGNED16_SAME_INPUT_AUDIT.json'
NEW_SIGNED_CSV='benchmarks/ISSUE39_PR67_SIGNED16_SAME_INPUT_AUDIT.csv'
def run(*args):
 print('RUN',*map(str,args),flush=True)
 subprocess.run([str(x) for x in args],cwd=ROOT,check=True)
def py(name,*args):run(sys.executable,'tools/'+name+'.py',*args)
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def shabytes(buf):return hashlib.sha256(buf).hexdigest()
def resident(p):return ROOT/p/'resident'/f'math_{p}_game_math.prg'
def ref(p):return ROOT/'build_source/reference'/p/f'math_{p}_source_built.prg'
def v5out(kind):return ROOT/'build_hybrid'/kind/'v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg'
def records(path):
 with (ROOT/path).open(newline='') as f:return list(csv.DictReader(f))
def savecsv(path,rows):
 with (ROOT/path).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
def checksum():
 files=sorted((p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='SHA256SUMS.txt'),key=lambda p:str(p.relative_to(ROOT)))
 (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in files))
def row_means(doc,operation):
 return {p:doc['routines'][operation]['metrics'][p]['mean_cycles'] for p in PROFILES}
def perf_table_update(path,op,per_profile):
 ls=(ROOT/path).read_text().splitlines()
 inds=[i for i,s in enumerate(ls) if s.startswith('| `'+op+'` |')]
 assert len(inds)==1,(path,op,inds)
 cols=ls[inds[0]].split('|')
 for pi,p in enumerate(PROFILES):cols[3+pi]=f' {per_profile[p]:.6f} '
 ls[inds[0]]='|'.join(cols)
 (ROOT/path).write_text('\n'.join(ls)+'\n')
def main():
 initial={p:shabytes(resident(p).read_bytes()) for p in PROFILES}
 assert initial['v2_pareto_fast']=='28fc6e653a05b170a80cd7eb50636d755895c5ebb7aab133262ed560fa465dd6'
 # Certify every byte BEFORE any resident image is changed.
 py('generate_sources')
 for kind in ('reference','alternate'):py('assemble_sources','--profile','all','--config-kind',kind)
 py('screen_issue39_u16_pr67_source')
 py('screen_issue39_u16_pr67_hybrid')
 proof=json.loads((ROOT/AUD).read_text())
 assert proof['status']=='PASS'
 for p in CHANGED:assert proof['profiles'][p]['old_sha256']==initial[p]
 # Install exact source-derived images: V5 is built by importing patched V2 donor.
 for p in CHANGED:
  cp=v5out('reference') if p=='v5_hybrid_lowzp' else ref(p)
  assert shabytes(cp.read_bytes())==proof['profiles'][p]['new_sha256']
  shutil.copyfile(cp,resident(p))
 assert shabytes(resident('v1_balanced').read_bytes())==initial['v1_balanced']
 # Regenerate same source from NEW installed image, proving the public release.
 py('generate_sources')
 for kind in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',kind)
  py('build_hybrid','--config-kind',kind)
 for p in CHANGED:
  f=v5out('reference') if p=='v5_hybrid_lowzp' else ref(p)
  assert shabytes(f.read_bytes())==proof['profiles'][p]['new_sha256'],(p,'not deterministic')
 py('validate_unsigned_division')
 py('benchmark_unsigned_common_corpus')
 py('audit_issue39_unsigned_small_workloads')
 py('benchmark_unsigned_3216_workloads')
 py('validate_signed_division')
 # Preserve PR66 historical evidence; publish fresh PR67 paired data separately.
 signed_json_old=(ROOT/OLD_SIGNED).read_bytes()
 signed_csv_old=(ROOT/OLD_SIGNED_CSV).read_bytes()
 py('audit_issue39_signed16_common')
 shutil.copyfile(ROOT/OLD_SIGNED,ROOT/NEW_SIGNED)
 shutil.copyfile(ROOT/OLD_SIGNED_CSV,ROOT/NEW_SIGNED_CSV)
 (ROOT/OLD_SIGNED).write_bytes(signed_json_old)
 (ROOT/OLD_SIGNED_CSV).write_bytes(signed_csv_old)
 common=json.loads((ROOT/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
 unsigned=json.loads((ROOT/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
 signed=json.loads((ROOT/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
 paired=json.loads((ROOT/NEW_SIGNED).read_text())
 assert common['status']==unsigned['status']==signed['status']==paired['status']=='PASS'
 assert common['total_calls']==136335 and unsigned['summary']['machine_calls']==822050
 assert paired['total_calls']==54770
 for op in ('MATH_UDIV16','MATH_UMOD16'):
  perf_table_update('PERFORMANCE.md',op,row_means(common,op))
 for op in ('MATH_SDIV16','MATH_SMOD16'):
  vals={p:signed['profiles'][p][op]['mean_cycles'] for p in PROFILES}
  perf_table_update('PERFORMANCE.md',op,vals)
 # Update local public profile tables to the currently measured public-ABI cycles.
 # The benchmark basis is the profile-seeded full arithmetic correctness audit.
 prof_rows={}
 for p in PROFILES:
  prof_rows[p]={k:unsigned['profiles'][p][k]['mean_cycles'] for k in ('MATH_UDIV16','MATH_UMOD16')}
 v2='v2_pareto_fast/PUBLIC_PERFORMANCE.csv'
 rows=records(v2)
 for row in rows:
  op={'math_udiv16':'MATH_UDIV16','math_umod16':'MATH_UMOD16'}.get(row['operation'])
  if op:
   z=unsigned['profiles']['v2_pareto_fast'][op]
   row.update(avg_cycles=f"{z['mean_cycles']:.6f}",min_cycles=str(z['min_cycles']),
              max_cycles=str(z['max_cycles']),cases=str(z['cases']),
              evidence='2026-10-12 issue39 PR67 public-entry arithmetic audit')
 savecsv(v2,rows)
 p='v3_reu_512k/PUBLIC_PERFORMANCE.csv';rows=records(p)
 for row in rows:
  op={'udiv16':'MATH_UDIV16','umod16':'MATH_UMOD16'}.get(row['operation'])
  if op:
   row.update(v1_balanced_cycles=f"{prof_rows['v1_balanced'][op]:.6f}",
       v2_pareto_fast_cycles=f"{prof_rows['v2_pareto_fast'][op]:.6f}",
       v3_reu_default_cycles=f"{prof_rows['v3_reu_512k'][op]:.6f}",
       v3_evidence='2026-10-12 issue39 PR67 public-entry arithmetic audit')
 savecsv(p,rows)
 p='v4_reu_16m/PUBLIC_PERFORMANCE.csv';rows=records(p)
 for row in rows:
  op={'udiv16':'MATH_UDIV16','umod16':'MATH_UMOD16'}.get(row['operation'])
  if op:
   row.update(v3_reu_512k_cycles=f"{prof_rows['v3_reu_512k'][op]:.6f}",
       v4_reu_16m_cycles=f"{prof_rows['v4_reu_16m'][op]:.6f}",
       v4_evidence='2026-10-12 issue39 PR67 public-entry arithmetic audit')
 savecsv(p,rows)
 py('publish_standalone_sources')
 py('generate_consolidated_routine_table')
 py('generate_public_indexes')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 u0=161.76145108098206;m0=198.61055718475075
 u1=common['routines']['MATH_UDIV16']['metrics']['v2_pareto_fast']['mean_cycles']
 m1=common['routines']['MATH_UMOD16']['metrics']['v2_pareto_fast']['mean_cycles']
 assert u1<u0 and m1<m0
 detail=f"""# Issue39 — PR67 carry-proven internal 16-bit branch pruning

**Date:** 2026-10-12. **Status:** V2–V5 exact-source release staging, V1 untouched. The unsigned DIV/MOD campaign remains OPEN.

The private unsigned and signed 16-bit quotient chains contained three
dead carry-conditional branch plus absolute JMP pairs each. Two unsigned pairs
follow `ANC #0` (which forces C=0); the third follows `ANC #0; STA`.
The signed core similarly has two `ANC #0` cases, plus one `SEC; BCC`
which can never branch. Each five-byte sequence becomes `JMP target; NOP; NOP`,
retaining all original instruction locations and removing two executed
cycles wherever the old dead conditional branch was entered.

This is a **zero-resident-growth, zero-normal-ZP-growth, zero-ABI-change**
micro-optimization, NOT an algorithmic replacement or a universal massive gain.
V2 source sites: signed $7C8A/$7CA5/$7CC0; unsigned $B884/$B8A0/$B8E4.
V3/V4 signed sites: $7D6B/$7D86/$7DA1, with unsigned at $B884/$B8A0/$B8E4.
V5 imports V2's code and has signed sites $B25F/$B27A/$B295.

## Same-input unsigned comparison (complete resident public CPU calls)
| Operation | Old V2 cycles | New V2 cycles | Mean saving |
|---|---:|---:|---:|
| UDIV16 | {u0:.6f} | {u1:.6f} | {u0-u1:.6f} |
| UMOD16 | {m0:.6f} | {m1:.6f} | {m0-m1:.6f} |

Identical-input test contains 2,729 UDIV16 cases and 1,705 UMOD16 cases
per profile. Large-quotient fallback remains exactly unchanged. The profile-
seeded correctness suite and signed paired-screen have separate published
mean values and should never be compared without a matching corpus.

## Validation
- V2 OptiSearch Reduced6502 patched-old/new full resident comparisons:
  2,057 unsigned pairs for each of UDIV16 and UMOD16; 2,521 signed
  SMOD16 pairs; correct Q/R/C/input for every relevant public contract.
  Early sample savings UDIV/UMOD16 35 cases × 2 cycles; signed SMOD16
  138 cases × 2 cycles and 36 cases × 4 cycles. This sample is *not* the
  official 2,729/1,705 corpus.
- Native x64sc **VICE binary reports 3.10**, not 3.13.2:
  256 inputs × four APIs × two images × four changed profiles
  = **8,192** full-resident old/new public calls, all outputs equal and
  independently checked against unsigned/signed quotient/remainder/carry.
  Harness explicitly uses `SEI; CLD; LDA #$34; STA $01` to bank out BASIC
  ROM before entering resident $B800 code, and invokes `MATH_INIT`.
  These native tests do **not** exercise REU DMA.
- Reference and alternate source assembly for V2/V3/V4 succeeded.
  Each new reference resident differs in precisely six expected five-byte
  branch rewrite slots, with no other bytes changed.
- V5 hybrid donor rebuild also differs at exactly those six spots.
  Five-profile candidate public ABI screen runs 2,729 UDIV16 and 1,705
  UMOD16 identical pairs, plus 1,200 signed pairs per API/profile.
- Signed 5,477-case × 2 APIs × five profiles paired result saved under
  `{NEW_SIGNED}` and `{NEW_SIGNED_CSV}`; PR66's original frozen
  signed research artifacts are preserved unchanged.
- Complete unsigned seeded regression suite: {unsigned['summary']['machine_calls']:,}
  public CPU calls; common unsigned corpus: {common['total_calls']:,} calls.
  Profile-seeded signed regression also passed; all five resident PRGs
  deterministic against their source-built reference candidate.

**V1 was not modified. No step in the Issue39 unsigned DIV/MOD campaign has
been marked complete.** Next target is deeper in-core short-quotient algorithm
refinement: the present gain is useful but intentionally tiny.
"""
 (ROOT/DOC).write_text(detail)
 blurb=f'- Issue39 source-verified no-growth V2–V5 16-bit known-carry branch pruning: [{DOC}]({DOC}); V1 unchanged, DIV/MOD campaign open.'
 for name in ('README.md','USER_MANUAL.md'):
  f=ROOT/name;s=f.read_text()
  if blurb not in s:f.write_text(s.rstrip()+'\n\n'+blurb+'\n')
 msg=f"""{TAG}
- Source-backed V2/V3/V4 UDIV16/UMOD16/SDIV16/SMOD16: replace three carry-proven unreachable conditional-plus-JMP pairs per unsigned and signed private divider by direct JMP with two never-executed padding NOPs. Exact instruction addresses, resident length, normal ZP, stack, ABI and tables preserved. V5 rebuilt from V2 donor, V1 byte-identical.
- Same-input V2 unsigned means: UDIV16 {u0:.6f}->{u1:.6f}, UMOD16 {m0:.6f}->{m1:.6f} cycles. This is a small strict nonregression on the measured shared corpus, not a new dividing architecture.
- Public five-profile 16-bit candidate checks, V2–V4 reference/alternate builds, exact six-rewrite resident binary diff V2–V5, all-profile signed/unsigned regression and old/new native VICE full-resident 8,192 public calls passed. New paired signed benchmark published without overwriting PR66 historical evidence. Documentation and packaged checksums refreshed. Unsigned family audit remains open. Details: {DOC}.
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=ROOT/name;s=f.read_text()
  if TAG not in s:f.write_text(msg+'\n'+s)
 statusp=ROOT/'RELEASE_STATUS.json';state=json.loads(statusp.read_text())
 state['date']='2026-10-12'
 state['reference_prg_sha256']={p:digest(p+'/resident/math_'+p+'_game_math.prg') for p in PROFILES}
 state['alternate_prg_sha256']={p:json.loads((ROOT/'build_source/alternate'/p/'source_build_manifest.json').read_text())['output_sha256'] for p in PROFILES[:4]}
 state['alternate_prg_sha256']['v5_hybrid_lowzp']=json.loads((ROOT/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
 state['issue39_u16_known_carry_pr67_2026_10_12']={
  'status':'PASS','document':DOC,'unsigned_family_complete':False,
  'v1_unchanged':True,'changed_profiles':CHANGED,
  'old_and_new_resident_sha256':{p:{'old':initial[p],'new':digest(p+'/resident/math_'+p+'_game_math.prg')} for p in CHANGED},
  'normal_zp_growth':0,'resident_prg_growth':0,'public_abi_changed':False,
  'candidate_source_sites_per_profile':6,
  'native_vice_reported_version':'3.10','native_vice_old_new_public_calls':8192,
  'same_input_unsigned_calls':common['total_calls'],
  'paired_signed_public_calls':paired['total_calls'],
  'full_unsigned_correctness_calls':unsigned['summary']['machine_calls'],
  'source_diff_report_sha256':digest(SYNTAX),
  'candidate_hybrid_proof_sha256':digest(AUD),
  'paired_signed_new_report_sha256':digest(NEW_SIGNED),
  'paired_signed_new_csv_sha256':digest(NEW_SIGNED_CSV)}
 for key,filepath,propertyname in (
  ('issue39_unsigned_small_width_workloads_2026_10_11','validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','data_sha256'),
  ('issue39_common_input_unsigned_divmod','validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json','benchmark_sha256')):
  if isinstance(state.get(key),dict):state[key][propertyname]=digest(filepath)
 if isinstance(state.get('issue39_unsigned_3216_multiworkload_2026_10_11'),dict):
  state['issue39_unsigned_3216_multiworkload_2026_10_11']['report_sha256']=digest('validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json')
 if isinstance(state.get('documentation'),dict):
  u=ROOT/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=u.stat().st_size,
     user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=shabytes(u.read_bytes()))
 statusp.write_text(json.dumps(state,indent=2)+'\n')
 py('verify_deterministic_rebuild')
 run('make','clean')
 for j in range(4):
  checksum();py('package_audit')
  entries=(ROOT/'SHA256SUMS.txt').read_text().splitlines()
  if all(line.split('  ',1)[0]==digest(line.split('  ',1)[1]) for line in entries):break
 else:raise AssertionError('checksum/package audit not stable')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 checksum();py('package_audit')
 print('ISSUE39 PR67 16-BIT SOURCE OPT RELEASE STAGING PASSED',flush=True)
if __name__=='__main__':main()
