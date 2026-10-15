#!/usr/bin/env python3
"""Publish qualified Issue144 SEEK16_INIT inline/jump source only; no default promotion."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from stage_issue39_v1_3216_ool_release import reseal
from issue144_seek16_accum_all_profiles_v2 import PROFILES,make
MODEL='validation/review/ISSUE144_SEEK16_ACCUM_INLINE_ALL_MODEL.json'
VICE='validation/review/ISSUE144_SEEK16_ACCUM_NATIVE_VICE.json'
DOC='docs/ISSUE144_SEEK16_INIT_INLINE_ACCUM_V1_V5_2026-10-15.md'
DIR='optional/issue144_seek16_accum_inline_all'
STAMP='2026-10-15 ISSUE144 SEEK16 INIT ACCUMULATOR INLINING FIVE PROFILE OPTIN'
def data(path):return json.loads((R/path).read_text())
def sha(path):return hashlib.sha256((R/path).read_bytes()).hexdigest()
def main():
 proof=data(MODEL);native=data(VICE);status=data('RELEASE_STATUS.json')
 assert proof['status']=='PASS_SOURCE_ASSEMBLED_PUBLIC_ABI'
 assert native['status']=='PASS_NATIVE_VICE_SEEK16_INIT_SOURCE_RELOCATED_FIVE_PROFILES'
 assert native['total_original_plus_candidate_public_init_calls']==70
 assert set(proof['profiles'])==set(native['profiles'])==set(PROFILES)
 reference=dict(status['reference_prg_sha256']);reu=dict(status.get('reference_reu_sha256',{}))
 rows={}
 for p in PROFILES:
  a=proof['profiles'][p];b=native['profiles'][p]
  assert a['status']=='PASS_SOURCE_ASSEMBLED_6510_PUBLIC_ABI_STATE_STEP'
  assert a['cases']==4080 and a['mean_saving']>20
  assert a['minimum_saving']>=(-1 if p in ('v1_balanced','v5_hybrid_lowzp') else 0)
  assert a['code_bytes'] in (328,399)
  assert b['status']=='PASS_REU_NATIVE_FRAME_STATUS_X_STACK_IDENTICAL'
  assert b['original_init_calls']==b['candidate_init_calls']==7
  assert b['native_step_calls_each']==112
  text,code,labels=make(p)
  path=DIR+'/'+p+'.asm'
  assert (R/path).read_text()==text
  assert a['source_sha256']==b['source_sha256']==sha(path)
  assert len(code)==a['code_bytes']
  assert sha(p+'/resident/math_'+p+'_game_math.prg')==reference[p]
  rows[p]={'baseline':a['public_mean_before'],'optin':a['public_mean_after'],
           'saved':a['mean_saving'],'smallest_saving':a['minimum_saving'],
           'largest_saving':a['maximum_saving'],'machine_code_bytes':a['code_bytes']}
 lines=['# Issue144 D — source-only SEEK16_INIT inlined accumulator V1–V5','',
  '**Optional source, not a production resident substitution or universal Pareto improvement.**','',
  'The ordinary SEEK16_INIT repeats a Bresenham accumulator helper with JSR/RTS',
  'overhead for each integer speed quantum, then invokes the same helper for',
  'the fractional component. The alternative uses the exact public source',
  'mirror, copies only its INIT island into caller-owned RAM, **inlines the',
  'first helper** (V1–V5), and replaces the second JSR/RTS with a JMP/JMP',
  'continuation at a separately placed instance. The original helpers,',
  'normal SEEK16_STEP routines, original executable bytes and lookup/state',
  'arrays are never modified. Absolute external branch/helper addresses are',
  'preserved, local control-flow labels are reassembled by the real 6510 assembler.',
  '', '## Same-input CPU-model public-call results (4,080 INIT + STEP pairs/profile)',
  '', '| Profile | Before | Source opt-in | Saved | Worst saved | Executable bytes |',
  '|---|---:|---:|---:|---:|---:|']
 for p in PROFILES:
  r=rows[p]
  lines.append('| %s | %.3f | %.3f | %.3f | %+d | %d |'%(p,r['baseline'],r['optin'],r['saved'],int(r['smallest_saving']),r['machine_code_bytes']))
 lines += ['',
  'These are 408 canonical movement paths × ten major/Euclidean speed',
  'classes = 4,080 comparisons per profile; **20,400 matched INIT calls**',
  'in total, each followed by a normal SEEK16_STEP and comparison of the',
  'complete public SEEK state arrays plus carry, X and stack.',
  'The V1/V5 inline expansion needs two complemented long branches;',
  'this can cost **one extra CPU-model cycle on certain degenerate moves**.',
  'Do not erase this minor worst-case regression when reporting means.',
  'The V2–V4 candidate has no measured slower call in that corpus.',
  '', 'Native real x64sc validates **seven baseline and seven candidate**',
  'SEEK16_INIT speed/mode scenarios per profile (70 total INIT calls)',
  'and 112 baseline + 112 candidate SEEK16_STEP frames/profile',
  '(1,120 total frame-step calls) with identical positions, carry, X,',
  'SP and post-arrival behavior. V3 and V4 load their actual REU images.',
  'Native VICE correctness is certified, **native cycle timing is not**.',
  '', 'The source example places the relocated main code and helper copies',
  'into caller-owned low RAM **$0D00–$0F8B**. The occupied foreign byte',
  '$19F0 and V1/V5 live table $1A00, plus V2–V4 $90E0..$91FF SEEK',
  'object state, remain untouched. This RAM is NOT automatically free',
  'in every application, loader or memory map. The code is not IRQ/NMI',
  'reentrant because the original math helpers and state/ZP are shared.',
  'For direct opt-in JSR use the candidate source entry at $0D00;',
  'alternatively, redirect ONLY the installed public JMP $5E48 in',
  'application-owned writable memory while no caller/interrupt can enter.',
  'Do not silently install into ordinary resident PRGs or REU payloads.',
  '', 'Verified reproduction: tools/issue144_seek16_accum_all_profiles_v2.py',
  'Native x64sc: tools/native_issue144_seek16_accum_all_profiles.py',
  'Machine-readable model: '+MODEL,
  'Machine-readable native: '+VICE,
  'Five individually accessible ASM sources: '+DIR+'/<profile>.asm',
  'No private OptiSearch code is published.']
 p=R/DOC;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(lines)+'\n')
 (R/DIR/'README.md').write_text('# SEEK16 INIT repeated-accumulator source option\n\nSee ../../'+DOC+' before integrating.\n')
 status['issue144_seek16_accumulator_inline_v1v5_2026_10_15']={
  'status':'PASS_MODEL_NATIVE_SOURCE_ONLY_NO_DEFAULT_PROMOTION',
  'profiles':list(PROFILES),'public_model_pair_count':20400,
  'native_before_and_after_init_calls':70,'native_before_and_after_step_calls':1120,
  'profile_cycle_pairs':rows,'source_dir':DIR,'documentation':DOC,
  'model_evidence':MODEL,'native_evidence':VICE,
  'V1_V5_one_cycle_minor_regression':True,
  'normal_resident_PRGs_REUs_changed':False,'extra_normal_ZP':0,
  'extra_application_RAM_bytes_by_profile':{p:rows[p]['machine_code_bytes'] for p in PROFILES},
  'native_cycles_measured':False}
 (R/'RELEASE_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
 note=STAMP+'\n- SEEK16_INIT accumulator direct inline + JMP continuation in separately allocated caller RAM: five public profiles, 20,400 paired full-state CPU model calls with STEP follow-up, 70 real native INIT and 1,120 STEP executions PASS. Mean savings V1/V5 22.105 cycles (some -1 worst), V2 25.451, V3/V4 23.704. Original residents and REU images unchanged; not a default promotion. '+DOC+'\n\n'
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  path=R/name
  if STAMP not in path.read_text():path.write_text(note+path.read_text())
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 assert all(sha(p+'/resident/math_'+p+'_game_math.prg')==reference[p] for p in PROFILES)
 assert dict(data('RELEASE_STATUS.json').get('reference_reu_sha256',{}))==reu
 print('ISSUE144 SEEK16 ACCUM FIVE PROFILE NATIVE/CPU RESEARCH SHA SEALED')
if __name__=='__main__':main()
