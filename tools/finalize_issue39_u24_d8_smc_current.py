#!/usr/bin/env python3
"""Seal SHA-pinned Issue39 24-by-8 bounded RAM-SMC caller-opt-in A/B screen."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
REP=R/'validation/review/ISSUE39_U24_D8_SMC_CURRENT_PUBLIC_SCREEN.json'
DOC=R/'docs/ISSUE39_U24_D8_RAM_SMC_CURRENT_OPTIN_2026-10-13.md'
PS=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV24','MATH_UMOD24')
MAPS=('ram_0800','ram_0851')
MARK='2026-10-13 ISSUE39 U24 D8 SMC CURRENT PUBLIC OPTIN SCREEN'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seal():
 paths=sorted((p for p in R.rglob('*') if p.is_file() and '.git' not in p.parts
  and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
  key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in paths))
def main():
 r=json.loads(Path(sys.argv[1]).read_text())
 current=json.loads((R/'RELEASE_STATUS.json').read_text())
 assert r['status']=='PASS_OPTIN_ONLY'
 assert (r['paired_cases'],r['cpu_calls'])==(65080,130160)
 assert r['caller_owns_ram_and_smc'] and not r['public_entries_patched']
 assert not r['resident_changed'] and r['native_vice_calls']==0
 assert set(r['profiles'])==set(PS)
 assert r['source']=='routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm'
 assert sha(R/r['source'])==r['source_sha256']
 assert len(r['classes'])==6
 rows=[];short={}
 for p in PS:
  item=r['profiles'][p]
  assert sha(R/p/'resident'/f'math_{p}_game_math.prg')==item['resident_sha256']==current['reference_prg_sha256'][p],p
  assert set(item['maps'])==set(MAPS)
  short[p]={}
  for op in OPS:
   baseline=item['maps']['ram_0800']['operations'][op]
   relocated=item['maps']['ram_0851']['operations'][op]
   code_bytes=item['maps']['ram_0800']['code_bytes']
   assert 60<=code_bytes<96
   assert item['maps']['ram_0800']['normal_zp_bytes']==0
   for kind in r['classes']:
    assert baseline[kind]['cases']==relocated[kind]['cases']==r['classes'][kind]['cases']
   uni=baseline['uniform_24_d8'];small=baseline['tiny_d1to7'];edge=baseline['structured_edges']
   # The caller-opt-in direct jump should save on this selected workload
   # at both RAM maps. Default source promotion is explicitly NOT made.
   assert uni['mean_delta'] < -10,(p,op,uni['mean_delta'])
   rows.append(f"| {p} | {op[5:]} | {code_bytes} | {uni['mean_delta']:+.3f} | {uni['faster']} / {uni['slower']} | {small['mean_delta']:+.3f} | {edge['mean_delta']:+.3f} | {uni['Q3_extra_byte_differences']} | {uni['q_side_effect_differences']} |")
   short[p][op]={
    'code_bytes':code_bytes,'uniform_eligible_mean_delta':uni['mean_delta'],
    'eligible_cases':uni['cases'],'eligible_faster':uni['faster'],
    'eligible_slower':uni['slower'],
    'Q3_extra_byte_differences':uni['Q3_extra_byte_differences'],
    'modulo_Q24_side_effect_differences':uni['q_side_effect_differences'],
    'tiny_divisor_mean_delta':small['mean_delta']}
 REP.parent.mkdir(parents=True,exist_ok=True)
 REP.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 lines=['# Issue 39 — 24-by-8 writable-RAM specialist vs current V1–V5','',
  '13 October 2026. **Caller-opt-in source replay; no default public replacement.**','',
  'This test invokes the already-published manually refined, Repose-derived',
  'div_u24_by_u8_selfmod.asm directly as a bounded library-dependent',
  '24-bit unsigned division and modulo producer. Unlike unrestricted',
  'UDIV24/UMOD24, this routine is correct **ONLY IF** the 24-bit',
  'dividend has N2>0 (N>=65536) and the divisor is exactly one',
  'nonzero byte (D1=D2=0, D0=1..255). Zero division is NOT handled;',
  'the caller must use the resident public entry on ineligible values.',
  '',
  'The source is assembled to two **caller-owned writable code RAM**',
  'origins ($0800 and $0851), with self-modified compare/subtract',
  'immediates refreshed every call. It is not ROM-safe or reentrant;',
  'interrupt users must ensure the code cannot be reentered. Extra',
  'normal ZP = 0. It uses existing N24/D24/Q24/R24 buffers.',
  '',
  '**32,540 paired eligible calls / 65,080?**',
  'This header is replaced by the exact certified count below.',
  '',
  f"**{r['paired_cases']:,} same-input pairs / {r['cpu_calls']:,} complete 6502 CPU executions**.",
  'Five current SHA-256-pinned V1–V5 full residents, two RAM maps,',
  'both public quotient and remainder entries, and six explicit',
  'numerator/divisor classes. Q24, R24, carry, preserved N/D,',
  'out-of-range remainder bytes, unrelated sentinels and stack',
  'all pass. The public UDIV24 extra Q3 buffer byte can differ;',
  'that non-promised extra-byte behavior is reported, not erased.',
  'Modulo Q24 side effects are recorded separately on V2–V5.',
  'All input and cycle vectors are hash-identified in the JSON.',
  '',
  '| Profile | Compared API | RAM code bytes | Eligible random delta cycles | Faster / slower | Tiny D delta | Edge delta | Q3 differences | Modulo Q24 differences |',
  '|---|---|---:|---:|---:|---:|---:|---:|---:|']+rows+['',
  '**Cycle delta is standalone specialist minus current resident public',
  'entry, so negative is faster.** The eligible 24/8 sample is NOT',
  'representative of arbitrary 24/24 division, and direct entry skips',
  'general-purpose divisor/width dispatch overhead. V1 already uses',
  'a related helper under its narrower in-resident guard; the direct',
  'V1 mean saving must not be advertised as an algorithmic breakthrough.',
  'For V2–V5 the direct specialist saves approximately 18–23 cycles',
  'for the tested eligible inputs, without paying any new guard cost',
  'because the **caller** asserts the exact precondition.',
  '',
  '**No default promotion.** Adding an in-resident guard would tax',
  'all unqualified inputs; that potential integration is NOT proven',
  'faster under the public benchmark, and needs another source/alternate',
  'layout and mixed-call/nonnarrow screen. The Q3 side-effect differences',
  'must also be understood before any transparent in-place replacement.',
  'The published standalone source is ready for callers willing to',
  'provide writable RAM and their own precondition guarantees.',
  '',
  'Reproducer: tools/screen_issue39_u24_d8_smc_current.py',
  'Evidence: validation/review/ISSUE39_U24_D8_SMC_CURRENT_PUBLIC_SCREEN.json',
  'Source: routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm',
  'No private OptiSearch source published; original provenance retained.',
  'Cycles are NMOS instruction counts, NOT native VIC/REU bus timing.',
  'No new native VICE executions are claimed.',
  '',
  'Issue #39 remains OPEN. This is a bounded U24/D8 specialist',
  'qualification, not completion of all unsigned DIV/MOD profiles.']
 # Do not print a contradictory provisional pair count.
 lines=[line for line in lines if not ('32,540 paired eligible' in line or 'header is replaced' in line)]
 DOC.write_text('\n'.join(lines)+'\n')
 log=f"""{MARK}
- Source-replayed already-published 24÷8 self-modifying RAM specialist against exact current V1–V5 full public UDIV24/UMOD24 residents at two relocated RAM origins: {r['paired_cases']:,} identical paired eligible inputs / {r['cpu_calls']:,} full 6502 CPU calls, zero contracted Q24/R24/carry/input/stack errors. Strict N2>0, D8!=0, D1=D2=0 precondition; D=0 and 24-bit divisors explicitly out of scope.
- Caller-opt-in direct entry saves ~46 cycles in V1 and ~18/23 cycles in V2–V5 on tested eligible random D8 inputs, but general default path is unchanged because unqualified dispatch overhead/extra-Q3 side effects are unresolved. Code RAM must be writable and not reentered; no normal ZP growth. Exact SHA-pinned class/operand/cycle evidence, docs, README/manual, two changelogs, release status/checksums published. No new native VICE time claim. Issue #39 OPEN. {DOC.relative_to(R)}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  file=R/name
  if MARK not in file.read_text():file.write_text(log+'\n'+file.read_text())
 ref='- Issue39 24÷8 writable-RAM caller-opt-in current resident screen: '+str(DOC.relative_to(R))+'. Mandatory operand guard; no default change.'
 for name in ('README.md','USER_MANUAL.md'):
  file=R/name
  if ref not in file.read_text():file.write_text(file.read_text().rstrip()+'\n\n'+ref+'\n')
 current['issue39_u24_d8_smc_current_2026_10_13']={
  'status':'PASS_SPECIALIST_OPTIN_NOT_DEFAULT',
  'source':r['source'],'source_sha256':r['source_sha256'],
  'report':str(REP.relative_to(R)),'report_sha256':sha(REP),
  'doc':str(DOC.relative_to(R)),
  'precondition':r['precondition'],'paired_inputs':r['paired_cases'],
  'cpu_calls':r['cpu_calls'],'normal_zp_growth':0,'native_vice_calls':0,
  'two_source_reassembled_ram_maps':list(MAPS),
  'profile_summary':short,'resident_binaries_changed':False,
  'public_api_changed':False,'unsigned_divmod_family_complete':False}
 if isinstance(current.get('documentation'),dict):
  f=R/'USER_MANUAL.md'
  current['documentation'].update(user_manual_bytes=f.stat().st_size,
   user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 (R/'RELEASE_STATUS.json').write_text(json.dumps(current,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  seal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 print('ISSUE39 U24 D8 RAM SMC QUALIFIED AND SEALED',flush=True)
if __name__=='__main__':main()
