#!/usr/bin/env python3
"""Seal issue39 V2-V5 16-bit unchanged-size D-high dispatch sweep; no binary changes."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
REP=R/'validation/review/ISSUE39_V2V5_U16_D1_CUTOFF_SWEEP.json'
DOC=R/'docs/ISSUE39_V2V5_U16_D1_CUTOFF_SCREEN_2026-10-12.md'
TAG='2026-10-12 ISSUE39 V2-V5 U16 D-HIGH CUTOFF SWEEP (RESEARCH ONLY)'
PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV16','MATH_UMOD16')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seal():
 fs=sorted((p for p in R.rglob('*') if p.is_file() and '.git' not in p.parts
         and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
           key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in fs))
def main():
 s=json.loads(Path(sys.argv[1]).read_text())
 state=json.loads((R/'RELEASE_STATUS.json').read_text())
 assert s['status']=='PASS' and set(s['profiles'])==set(PROFILES)
 assert len(s['correctness_rejections'])==64
 counts={'MATH_UDIV16':4201,'MATH_UMOD16':3177}
 summary={}
 for p in PROFILES:
  group=s['profiles'][p]
  assert group['resident_sha256']==state['reference_prg_sha256'][p]
  assert group['cutoff_operand_address']=='0xb8ef'
  summary[p]={}
  for op in OPS:
   vals=group['operations'][op];assert vals['cases']==counts[op]
   rows=vals['threshold_results']
   assert len(rows)==17
   rejected=[x['threshold'] for x in rows if x['status']=='REJECT_CORRECTNESS']
   assert rejected==[1,2,4,8,10,12,13,14],(p,op,rejected)
   baseline=next(x for x in rows if x['threshold']==15)
   assert baseline['status']=='PASS' and baseline['faster']==baseline['slower']==0
   valid=[x for x in rows if x['status']=='PASS']
   best=min(valid,key=lambda v:v['after_mean'])
   gain=next(v for v in rows if v['threshold']==16)
   assert gain['status']=='PASS'
   if op=='MATH_UDIV16':
    assert (gain['faster'],gain['slower'])==(9,10)
    assert abs(gain['mean_delta']-0.054035)<0.00001
    assert best['threshold']==15
   else:
    assert (gain['faster'],gain['slower'])==(11,7)
    assert abs(gain['mean_delta']+0.116147)<0.00001
    assert best['threshold']==16
   summary[p][op]={'cases':vals['cases'],'baseline_mean':baseline['before_mean'],
      'best_mean':best['after_mean'],'best_cutoff':best['threshold'],
      'best_regression_count':best['slower']}
 lines=['# Issue #39 — V2–V5 16-bit high-divisor dispatch sweep',
 '',
 '**12 October 2026. Research-only. No shipped binary or ABI changes.**',
 '',
 'The source already dispatches through LDX D1 / CPX #15 / BCS.',
 'This exhaustive **17-value candidate sweep** changes only the CPX',
 'immediate operand at $B8EF in each in-memory resident copy and checks',
 'UDIV16 and UMOD16 public entries for V2/V3/V4/V5 using the same input',
 'sequence per threshold and routine. No extra RAM, ZP, stack, or wrapper.',
 'Q/R/C, N/D preservation, stack, and UMOD16 current Q-buffer side effects',
 'are compared to an unpatched current resident. CPU cycles include public',
 'entry and RTS; not native VIC memory contention.',
 '',
 '| Profile | Public entry | Tested cases | Default 15 cycles | Best correct cutoff | Mean cycles | Slower individual calls |',
 '|---|---|---:|---:|---:|---:|---:|']
 for p in PROFILES:
  for op in OPS:
   x=summary[p][op]
   lines.append(f"| {p} | {op} | {x['cases']} | {x['baseline_mean']:.6f} | {x['best_cutoff']} | {x['best_mean']:.6f} | {x['best_regression_count']} |")
 lines += ['','**64 configurations fail arithmetic correctness:**',
 'cutoffs 1, 2, 4, 8, 10, 12, 13, and 14 on each',
 'profile/API. These are invalid optimizations, regardless of speed.',
 '',
 'At cutoff 16, UDIV16 is **0.054035 cycles slower on average**',
 '(9 inputs faster, 10 slower); UMOD16 is **0.116147 cycles faster**',
 'but **7 individual inputs become slower** (11 faster). These',
 'statistics are identical in each of the four profile images because',
 'they share the same producer. No non-default threshold has',
 'zero regressions across both public APIs and all four profiles.',
 '',
 'The official corpus is supplemented by 256 samples each of',
 'q2..9, q10..31, q32..255, 384 full random, 256 small divisors,',
 'and 64 zero divisors per API. The extended 4,201/3,177-input',
 'corpora must not be confused with the official ranking corpus.',
 'Exact operand fingerprints, rejected N/D counterexamples, class means,',
 'and complete delta/faster/slower counts are in',
 'validation/review/ISSUE39_V2V5_U16_D1_CUTOFF_SWEEP.json.',
 '',
 '**Decision:** retain #15 on V2–V5 as the shared default.',
 'Do not promote #16 based solely on its tiny modulo mean gain and',
 'do not promote any of #1–#14 because they fail correctness.',
 'This finishes only the cutoff-constant experiment, not the full',
 'unsigned DIV/MOD campaign; issue #39 remains open.']
 DOC.write_text('\n'.join(lines)+'\n')
 REP.parent.mkdir(parents=True,exist_ok=True)
 REP.write_text(json.dumps(s,sort_keys=True,indent=2)+'\n')
 log=f"""{TAG}
- Tested 17 existing-size CPX D1 dispatch cutoffs for UDIV16 and UMOD16 in unchanged V2/V3/V4/V5 images. Exact current resident SHA pins; 4,201 UDIV16 and 3,177 UMOD16 inputs per candidate/profile, preserved Q/R/C, N/D, SP and modulo quotient side effect. 64 combinations (cutoffs 1–14) fail correctness.
- Cutoff 16: UDIV16 +0.054035 cycles mean (9 faster,10 slower); UMOD16 -0.116147 cycles mean (11 faster,7 slower). No universally zero-regression non-default candidate; retain cutoff 15. Published complete per-class source-backed evidence, manual, both logs and checksums; no resident/source/API change. Issue #39 unsigned campaign OPEN. {DOC.relative_to(R)}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if TAG not in f.read_text():f.write_text(log+'\n'+f.read_text())
 link='- Issue #39 V2–V5 UDIV16/UMOD16 D-high gate microarchitecture audit: '+str(DOC.relative_to(R))+'. Keep #15; no family-wide signoff.'
 for name in ('README.md','USER_MANUAL.md'):
  f=R/name
  if link not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+link+'\n')
 state['issue39_u16_dhigh_threshold_sweep_2026_10_12']={
   'status':'PASS_RESEARCH_NO_PROMOTION','documentation':str(DOC.relative_to(R)),
   'source_report':str(REP.relative_to(R)),'source_report_sha256':sha(REP),
   'checked_profiles':list(PROFILES),'correctness_rejections':64,
   'default_cutoff':15,'binary_abi_source_changed':False,
   'per_profile':summary,'unsigned_family_complete':False}
 if isinstance(state.get('documentation'),dict):
  f=R/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=f.stat().st_size,
       user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 (R/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  seal();subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 print('ISSUE39 16-BIT DISPATCH SCREEN PUBLICATION PASS',flush=True)
if __name__=='__main__':main()
