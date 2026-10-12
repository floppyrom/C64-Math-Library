#!/usr/bin/env python3
"""Seal 32/16 power-of-two caller opt-in evidence; no default engine changes."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
ASM=R/'routines/standalone_lab/library_dependent/div_u32_u16_pow2_optin.asm'
REP=R/'validation/review/ISSUE39_U3216_POW2_OPTIN_SCREEN.json'
DOC=R/'docs/ISSUE39_U3216_POW2_OPTIN_2026-10-12.md'
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
MARK='2026-10-12 ISSUE39 90BYTE POW2 32BY16 OPT-IN SPECIALIST'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seal():
 paths=sorted((p for p in R.rglob('*') if p.is_file()
  and '.git' not in p.parts and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
  key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in paths))
def main():
 j=json.loads(Path(sys.argv[1]).read_text())
 state=json.loads((R/'RELEASE_STATUS.json').read_text())
 assert j['status']=='PASS_OPTIN_NOT_DEFAULT'
 assert j['precondition'].startswith('D16 is exactly')
 assert j['code_bytes']==90 and j['normal_zp_growth']==0 and j['nested_stack_growth']==0
 assert j['pairs']==67520 and j['cpu_calls']==135040
 assert not j['resident_changed'] and not j['public_entries_patched']
 assert j['origin_maps']==['0x800','0xb00']
 assert set(j['profiles'])==set(PROFILES)
 for p in PROFILES:
  image=R/p/'resident'/f'math_{p}_game_math.prg'
  assert sha(image)==state['reference_prg_sha256'][p]==j['profiles'][p]['resident_sha256']
  maps=j['profiles'][p]['maps']
  assert maps['0x800']==maps['0xb00']
  for op in OPS:
   s=maps['0x800'][op]['summary']
   assert s['cases']==3376 and s['faster']>2000 and s['delta_mean'] < -100
 REP.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
 lines=['# Issue #39 — 90-byte power-of-two 32÷16 caller-opt-in specialization','',
  '12 October 2026. Source-backed, optional specialist; **no change to defaults**.','',
  'When the caller already knows **D16 is exactly 2^k (k=0..15)**,',
  'division can be replaced with an unsigned 32-bit right shift and a',
  'remainder mask. This 90-byte routine computes Q32 and R16 in the',
  'existing library buffers, returns carry clear, preserves original',
  'N32/D16, the high R bytes, sentinel memory and SP. It does **not**',
  'detect invalid divisors; calling it on zero or a non-power-of-two',
  'produces an invalid answer. Both normal 32÷16 public entrypoints',
  'remain the correct fallback for arbitrary divisors.','',
  'This is source-available **library-dependent**, not standalone:',
  'it assumes the current C64ML $C010/$C014/$C018/$C01C data ABI.',
  'The caller must install it in **caller-owned executable RAM**;',
  'the sample $0800 address is not reserved. The source may be',
  'reassembled at another RAM address without introducing extra ZP.',
  'The routine clobbers A/X and condition flags; it is not reentrant.',
  'No extra nested-JSR stack frame or persistent scratch is needed.',
  '',
  '**Reproducibility:** exact published V1–V5 resident SHA pins; both',
  'public 32/16 quotient and modulo outputs on identical operands,',
  '16 possible divisors, edge/uniform-full-width/N16 operand groups;',
  '**67,520 paired old/new inputs / 135,040 fully executed 6502 calls**',
  'across two RAM addresses ($0800/$0B00), zero arithmetic, complete',
  'Q/R/carry/input/high-sentinel/stack or relocation-cycle differences.',
  'This is **instruction timing**; no VICE native execution or VIC/REU',
  'bus timing is claimed.','',
  '| Profile | API | Mean candidate-minus-public cycles | Faster | Slower |',
  '|---|---|---:|---:|---:|']
 for p in PROFILES:
  for op in OPS:
   s=j['profiles'][p]['maps']['0x800'][op]['summary']
   lines.append(f"| {p} | {op} | {s['delta_mean']:+.3f} | {s['faster']} | {s['slower']} |")
 lines+=['',
  'The means are for this explicit **power-of-two-only** distribution,',
  'not the library-wide public leaderboard. V2–V5 have a real slower',
  'tail for larger k and small numerators; callers must profile their',
  'specific divisor/numerator mix. Do not substitute this for the',
  'default resident. Crucially, there is **no fast path dispatch tax**',
  'on arbitrary divisors, because the caller opts in knowingly.',
  '',
  'OptiSearch is kept as a separate, private candidate source. This',
  'manual shift/mask strategy is independently developed and does',
  'not reproduce or publish private OptiSearch-generated material.',
  '',
  'Source: '+str(ASM.relative_to(R)),
  'Re-run: python3 tools/qualify_issue39_u3216_pow2_optin.py',
  'Full input class/cycle SHA evidence: '+str(REP.relative_to(R)),
  '',
  'Issue #39 remains OPEN; this is a newly qualified *specialist*,',
  'not a complete unsigned DIV/MOD profile/OptiSearch audit.']
 DOC.write_text('\n'.join(lines)+'\n')
 log=f"""{MARK}
- Qualified 90-byte caller-opt-in 32/16 D=power-of-two producer, providing both full quotient and remainder public-buffer contracts; 0 new ZP, 0 extra nested JSR frames. Exact five resident profiles, two legal RAM maps, 67,520 matched operands / 135,040 CPU executions, zero Q/R/C/N/D/sentinel/SP/relocation errors.
- Large gains on the explicit power-of-two workload, with V2–V5 slower cases at high divisor exponents: **no default promotion**. No shipped PRG or public ABI modification. Source, full JSON, README/manual and both changelogs published. Native VICE cycles not claimed. Issue #39 remains OPEN. {DOC.relative_to(R)}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  p=R/name
  if MARK not in p.read_text():p.write_text(log+'\n'+p.read_text())
 line='- Issue39 32/16 power-of-two caller-opt-in specialist: '+str(DOC.relative_to(R))+'. The divisor precondition is mandatory; public defaults stay unchanged.'
 for name in ('README.md','USER_MANUAL.md'):
  p=R/name
  if line not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+line+'\n')
 state['issue39_u3216_pow2_optin_2026_10_12']={
  'status':'PASS_OPTIN_NOT_DEFAULT',
  'source':str(ASM.relative_to(R)),'source_sha256':sha(ASM),
  'validation':str(REP.relative_to(R)),'validation_sha256':sha(REP),
  'documentation':str(DOC.relative_to(R)),
  'code_bytes':90,'extra_normal_zp':0,'extra_nested_jsr_stack':0,
  'precondition':'D16 is exactly a power of two, between 1 and 32768',
  'paired_inputs':67520,'cpu_calls':135040,'native_vice_calls':0,
  'released_residents_changed':False,'public_api_changed':False,
  'unsigned_family_complete':False}
 if isinstance(state.get('documentation'),dict):
  p=R/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=p.stat().st_size,
   user_manual_lines=len(p.read_text().splitlines()),user_manual_sha256=sha(p))
 (R/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  seal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 print('ISSUE39 32/16 POW2 SPECIALIST RELEASE SEALED',flush=True)
if __name__=='__main__':main()
