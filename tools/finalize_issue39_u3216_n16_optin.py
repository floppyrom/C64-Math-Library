#!/usr/bin/env python3
"""Publish 12-byte library-dependent N16 32/16 opt-in proof; no resident changes."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
SRC=R/'routines/standalone_lab/library_dependent/div_u32_u16_n16_optin.asm'
REP=R/'validation/review/ISSUE39_U3216_N16_12BYTE_OPTIN.json'
NATIVE=R/'validation/review/ISSUE39_U3216_N16_12BYTE_NATIVE_VICE.json'
DOC=R/'docs/ISSUE39_U3216_N16_12BYTE_OPTIN_2026-10-12.md'
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
MARK='2026-10-12 ISSUE39 12BYTE N16 OPTIN 32BY16 SPECIALIST'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def seal():
 files=sorted((p for p in R.rglob('*') if p.is_file() and '.git' not in p.parts
  and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
  key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in files))
def main():
 data=json.loads(Path(sys.argv[1]).read_text())
 native=json.loads(NATIVE.read_text())
 status=json.loads((R/'RELEASE_STATUS.json').read_text())
 assert data['status']=='PASS' and data['code_bytes']==12
 assert data['paired_inputs']==56680 and data['cpu_calls']==113360
 assert not data['modified_residents'] and not data['public_entry_patched']
 assert data['maps']==['0x800','0xa00']
 assert native['status']=='PASS_REPRESENTATIVE_PROFILES_ONLY'
 assert native['old_new_native_calls']==256 and not native['native_cycle_timing_measured']
 assert set(native['profiles'])=={'v1_balanced','v2_pareto_fast'}
 for p in PROFILES:
  resident=R/p/'resident'/('math_'+p+'_game_math.prg')
  assert sha(resident)==status['reference_prg_sha256'][p]==data['profiles'][p]['resident_sha256']
  group=data['profiles'][p]['maps']
  assert group['0x800']==group['0xa00']
  for op in OPS:
   test=group['0x800'][op]
   assert test['dhi_random']['mean_delta'] < -300
   if p=='v1_balanced':assert test['d8']['mean_delta']<0
   else:assert test['d8']['mean_delta']>0
 REP.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
 lines=['# Issue39: opt-in 12-byte 32/16 helper for known N16',
 '','12 October 2026. Library-dependent specialist, no stable API mutation.',
 '',
 'The caller knows N2=N3=0 and invokes this opt-in entry directly.',
 'The helper calls the installed MATH_UDIV16 and clears Q2/Q3.',
 'It returns the same complete Q32, R16, carry, and preserved operands',
 'as the normal 32/16 quotient and modulo public aliases.',
 '',
 'Existing public 32/16 code is left untouched. No 17-cycle',
 'full-width dispatch cost, unlike the earlier PR87/PR88 redirects.',
 '',
 'Suggested qualifier for V2, V3, V4 and V5: D>=256; for',
 'D8 they are about 274 cycles slower than their native 32/16 producer.',
 'V1 also benefits from D8 with this helper (about 545 cycles saved).',
 'For arbitrary N or uncertain preconditions, call normal 32/16.',
 '',
 'The helper has 12 code bytes and 0 extra ZP, with a two-byte',
 'nested JSR return-stack cost. Sample origin $0800 is caller-owned',
 'executable RAM, NOT memory reserved by the library. Reserve it or',
 'relocate the source; never overwrite the screen/game buffer.',
 'This is NOT an independent div algorithm: it needs the existing',
 'library and correct matching MATH_UDIV16 / IO addresses.',
 '',
 'Evidence: 56,680 identical input pairs / 113,360 CPU calls,',
 'across two independent RAM maps in all five release profiles.',
 'All Q/R/carry/inputs/high-R/sentinels/SP correct, relocation',
 'performance identical. These are instruction cycles, not VIC/REU',
 'bus-inclusive timing.',
 '',
 '| Profile | API | N16 with D>=256 mean delta | N16 with D8 mean delta |',
 '|---|---|---:|---:|']
 for p in PROFILES:
  for op in OPS:
   result=data['profiles'][p]['maps']['0x800'][op]
   lines.append(f"| {p} | {op} | {result['dhi_random']['mean_delta']:+.3f} | {result['d8']['mean_delta']:+.3f} |")
 lines+=['',
 'Native x64sc executed 256 old/new full-resident calls on exact',
 'published V1 and V2 SHA-pinned PRGs: both public APIs, 32 operands',
 'per profile/API, no Q32/R32/carry/input/stack differences.',
 'Native timing was not measured. V3/V4/V5 were validated in the',
 'two-map CPU emulator, NOT natively.',
 '',
 'Source: '+str(SRC.relative_to(R)),
 'Reproduce: python3 tools/qualify_issue39_u3216_n16_optin.py',
 'Full JSON: '+str(REP.relative_to(R)),
 'Native certificate: '+str(NATIVE.relative_to(R)),
 '',
 'Issue #39 unsigned family remains OPEN. This is an opt-in niche',
 'routine, not a global replacement for any of the five profiles.']
 DOC.write_text('\n'.join(lines)+'\n')
 log=f"""{MARK}
- Validated 12-byte opt-in 32/16 specialization for known N16, depending on installed UDIV16; no public redirect, no full-width latency tax. Five-profile two-map paired 56,680 operands / 113,360 6502 calls, zero Q/R/C/inputs/SP mismatches.
- V1 N16 D>=256 about 478/481 cycles faster; V2–V5 about 381/384 faster. V2–V5 D8 about 274 cycles slower, so preserve the precondition for performance. Native x64sc 256 old/new calls on current V1/V2 full resident pass; no native timing or V3–V5 native claim.
- Published individually liftable library-dependent assembly, reproducible test/provenance, both changelogs, docs, release status and checksums; no shipped PRG/API or ZP budget modification. Issue #39 remains OPEN. {DOC.relative_to(R)}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  p=R/name
  if MARK not in p.read_text():p.write_text(log+'\n'+p.read_text())
 note='- Issue39 12-byte N16 32/16 opt-in helper: '+str(DOC.relative_to(R))+'. Uses installed UDIV16; caller owns memory.'
 for name in ('README.md','USER_MANUAL.md'):
  p=R/name
  if note not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+note+'\n')
 status['issue39_u3216_n16_optin12_2026_10_12']={
  'status':'PASS_OPT_IN_NOT_DEFAULT','routine_bytes':12,
  'source':str(SRC.relative_to(R)),'source_sha256':sha(SRC),
  'validation':str(REP.relative_to(R)),'validation_sha256':sha(REP),
  'native_vice':str(NATIVE.relative_to(R)),'native_sha256':sha(NATIVE),
  'documentation':str(DOC.relative_to(R)),
  'cpu_executions':113360,'native_executions_v1v2':256,
  'released_residents_changed':False,'public_api_changed':False,
  'normal_zp_growth':0,'additional_return_stack_bytes':2,
  'signedness':'unsigned','requires_n16':True,
  'v2v5_prefer_d_ge_256':True,'unsigned_family_complete':False}
 if isinstance(status.get('documentation'),dict):
  p=R/'USER_MANUAL.md'
  status['documentation'].update(user_manual_bytes=p.stat().st_size,
   user_manual_lines=len(p.read_text().splitlines()),user_manual_sha256=sha(p))
 (R/'RELEASE_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  seal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 print('ISSUE39 N16 OPT-IN 12 BYTE RELEASE DATA SEALED',flush=True)
if __name__=='__main__':main()
