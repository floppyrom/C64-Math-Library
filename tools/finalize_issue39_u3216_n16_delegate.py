#!/usr/bin/env python3
"""Publish five-profile N16-transplant research, not a deployable resident."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
DOC=R/'docs/ISSUE39_U3216_N16_DELEGATE_CURRENT_MAIN_2026-10-12.md'
REP=R/'validation/review/ISSUE39_U3216_N16_DELEGATE_CURRENT_MAIN.json'
ASM=R/'tools/candidates/issue39_u3216_n16_delegate_research.asm'
MARK='2026-10-12 ISSUE39 N16 DELEGATE U32BY16 FIVE-PROFILE SCREEN'
P=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 a=json.loads(Path(sys.argv[1]).read_text())
 state=json.loads((R/'RELEASE_STATUS.json').read_text())
 assert a['status']=='PASS_RESEARCH_SCREEN'
 assert a['totals']=={'old_new_calls':158260,'compared_input_pairs':79130,'mismatches':0}
 assert a['native_vice_calls']==0 and a['ROM_visible_overlay_not_qualified']
 assert a['overlay_code_bytes']==26 and not a['resident_binary_changed']
 assert set(a['profiles'])==set(P)
 for prof in P:
  assert a['profiles'][prof]['resident_sha256']==state['reference_prg_sha256'][prof]
  for op in OPS:
   x=a['profiles'][prof]['routines'][op]
   assert x['uniform_32x16']['mean_delta']==17
   assert x['n16_target']['mean_delta'] < -350
   if prof=='v1_balanced':assert x['n16_small_d']['mean_delta']< -500
   else:assert x['n16_small_d']['mean_delta']>290
 REP.parent.mkdir(parents=True,exist_ok=True)
 REP.write_text(json.dumps(a,sort_keys=True,indent=2)+'\n')
 ASM.parent.mkdir(parents=True,exist_ok=True)
 ASM.write_text('''; Research-only 26-byte library-dependent 32/16 N16 delegate.
; CPU-model overlay at E100 under default KERNAL ROM; not deployable without
; bank-state design. Patch public $31B0 LDA N to JMP $E100 only in an owned
; live RAM placement; original 32/16 code resumes at $31B3.
; This is not independent standalone arithmetic, and uses a nested JSR.
* = $E100
N16_GATE:
    lda $C012
    ora $C013
    bne OLD
    jsr $3140
    lda #0
    sta $C01A
    sta $C01B
    rts
OLD:
    lda $C010
    jmp $31B3
''')
 lines=['# Issue #39: 32/16 N16 donor screen on exact current residents',
 '','12 October 2026. Research only: NO stable source or binary change.',
 '',
 'A 26-byte in-memory dispatcher checks N2|N3 and calls the existing',
 '16/16 public divider when both are zero, clearing Q2/Q3 afterwards.',
 'Otherwise it resumes original 32/16 code. Both 32/16 public entries',
 'and Q/R/C/N/D, high-R sentinels and stack were compared old/new.',
 '',
 '79,130 identical input pairs and 158,260 complete 6502 public calls',
 'across five profile residents; zero mismatches. This candidate requires',
 'an additional nested JSR (+2 stack bytes) on the narrow path.',
 'The $E100 prototype lies below the KERNAL ROM map on a normal C64:',
 'native VICE, legal executable RAM placement, banking, full relocation',
 'and interrupt behavior have NOT been qualified. CPU-cycle counts only.',
 '',
 '| Profile | API | Official mean delta | N16 mean delta | N16 with D8 mean delta | Full-N32 mean delta |',
 '|---|---|---:|---:|---:|---:|']
 for p in P:
  for op in OPS:
   x=a['profiles'][p]['routines'][op]
   lines.append(f"| {p} | {op} | {x['official']['mean_delta']:+.6f} | {x['n16_target']['mean_delta']:+.6f} | {x['n16_small_d']['mean_delta']:+.6f} | {x['uniform_32x16']['mean_delta']:+.6f} |")
 lines.extend(['','Negative deltas are faster. On V1 the N16/D8 class wins',
 'more than 500 cycles, but on V2–V5 the same class loses about 292.',
 'Every uniform full-width N32 sample loses 17 cycles. The official',
 'mixed corpus is not representative of full-width uniform usage.',
 '',
 'Verdict: do NOT promote to a universal default. Preserve the',
 'research assembly under tools/candidates and detailed per-class JSON.',
 'Next try a D-high-aware filter, with a separate screen for full-width',
 'regressions. Also compare with any independently produced OptiSearch',
 'architecture only after compatible public ABI/resource certification.',
 'Issue #39 stays OPEN; unsigned division/modulo family is incomplete.'])
 DOC.write_text('\n'.join(lines)+'\n')
 log=f"""{MARK}
- Tested 26-byte ephemeral N16->UDIV16 producer reuse on V1–V5 exact resident public UDIV32/16 and UMOD32/16 entries; 79,130 input pairs, 158,260 old/new calls, no Q/R/C/input/stack mismatches.
- V1 N16-target ~469 cycles faster and N16/D8 ~542 faster; V2–V5 N16-target ~366 faster but N16/D8 ~292 slower; all full-width-uniform operands +17. Reject default, preserve candidate/source-backed detailed report. Ephemeral E100 code not native-ROM/bank qualified. No binary change. Campaign #39 open. {DOC.relative_to(R)}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if MARK not in f.read_text():f.write_text(log+'\n'+f.read_text())
 note='- Issue39 five-profile 32/16 N16 delegate A/B research: '+str(DOC.relative_to(R))+'. No default promotion.'
 for name in ('README.md','USER_MANUAL.md'):
  f=R/name
  if note not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+note+'\n')
 state['issue39_u3216_n16_donor_2026_10_12']={
 'status':'PASS_RESEARCH_NO_PROMOTION','report':str(REP.relative_to(R)),
 'report_sha256':sha(REP),'documentation':str(DOC.relative_to(R)),
 'candidate':str(ASM.relative_to(R)),'paired_machine_calls':158260,
 'native_vice_calls':0,'default_kernal_rom_placement_unsafe':True,
 'production_changed':False,'unsigned_family_complete':False}
 if isinstance(state.get('documentation'),dict):
  f=R/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=f.stat().st_size,
    user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 (R/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  fs=sorted((f for f in R.rglob('*') if f.is_file() and '.git' not in f.parts and '__pycache__' not in f.parts and f.name!='SHA256SUMS.txt'),key=lambda f:str(f.relative_to(R)))
  (R/'SHA256SUMS.txt').write_text(''.join(sha(f)+'  '+str(f.relative_to(R))+'\n' for f in fs))
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 print('ISSUE39 N16 DONOR RESEARCH SEALED',flush=True)
if __name__=='__main__':main()
