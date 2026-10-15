#!/usr/bin/env python3
"""Gate and seal native/model-qualified unrestricted ISQRT32 four-profile opt-in."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from stage_issue39_v1_3216_ool_release import reseal
from issue144_isqrt32_highword_direct_experiment import build,PROFILES
from validate_unsigned_division import PROFILES as ALL_PROFILES
MODEL='validation/review/ISSUE144_ISQRT32_DIRECT_HIGHWORD_SEED_MODEL.json'
NATIVE='validation/review/ISSUE144_ISQRT32_DIRECT_HIGHWORD_SEED_NATIVE_VICE.json'
DOC='docs/ISSUE144_ISQRT32_FULL_INPUT_DIRECT_HIGHWORD_SEED_2026-10-15.md'
SOURCE='optional/issue144_isqrt32_highword_direct'
STAMP='2026-10-15 ISSUE144 ISQRT32 ALL-DOMAIN DIRECT HIGHWORD SEED'
def read(path):return json.loads((ROOT/path).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 m,n=read(MODEL),read(NATIVE)
 assert m['status']=='PASS_UNRESTRICTED_ISQRT32_DIRECT_HIGHWORD_SEED_CPU_MODEL'
 assert n['status']=='PASS_REAL_NATIVE_VICE_UNRESTRICTED_ISQRT32_HIGHWORD_SEED'
 assert m['cases_per_profile']==4130 and n['native_baseline_and_candidate_calls']==192
 assert set(m['profiles'])==set(n['profiles'])==set(PROFILES)
 assert n['v4_16m_REU_original_only']['actual_REU_image_loaded']
 assert n['v4_16m_REU_original_only']['candidate_not_applicable']
 state=read('RELEASE_STATUS.json')
 old_prgs=dict(state['reference_prg_sha256'])
 old_reu=dict(state.get('reference_reu_sha256',{}))
 assert set(old_prgs)==set(ALL_PROFILES)
 rows={}
 for p in PROFILES:
  a=m['profiles'][p];b=n['profiles'][p]
  assert a['status']=='PASS_PUBLIC_ENTRY_ALL_DOMAIN_INPUT_CARRY_X_Y_SP'
  assert b['status']=='PASS_NATIVE_ALL_32BITS_ROOT_AND_CARRY'
  assert a['cases']==4130 and b['native_pairs']==24
  assert a['paired_savings']['minimum']==a['paired_savings']['maximum'] in (47,51)
  assert a['paired_savings']['mean_cycles'] in (47,51)
  assert a['mixed_ISQRT16_interleaved'] and a['original_public_entry_restored']
  src,code=build(p)
  f=SOURCE+'/'+p+'.asm'
  assert (ROOT/f).read_text()==src
  assert sha(f)==a['source_sha256']==b['source_sha256']
  assert len(code)==a['program_bytes']==b['source_code_bytes']
  assert min(code)==0xC00 and max(code)==0xCB5
  assert sha(p+'/resident/math_'+p+'_game_math.prg')==old_prgs[p]
  rows[p]={'stock_public_mean':a['stock']['mean_cycles'],
           'direct_highword_mean':a['specialist']['mean_cycles'],
           'paired_saving':a['paired_savings']['mean_cycles'],
           'code_bytes':len(code)}
 assert sha('v4_reu_16m/resident/math_v4_reu_16m_game_math.prg')==old_prgs['v4_reu_16m']
 lines=['# Issue144 — unrestricted ISQRT32 direct high-word seed opt-ins',
  '',
  '**Four non-REU producer profiles qualified: V1/V2/V3/V5; V4 REU path unchanged.**',
  '',
  'Original ISQRT32 writes the source low word to resident scratch,',
  'copies the input high word to the low-word slot, uses the existing',
  'exact ISQRT16 lookup to obtain its initial high root byte, then',
  'restores the low word before eight base-4 refinement steps.',
  'This opt-in source separately assembles the same high-root seed',
  'to address **$C012/$C013 directly**, bypassing redundant input',
  'copy/save/restore. Refinement uses the original initialized resident',
  'radix-4 helper, normal zero-page scratch and square tables.',
  'All 32-bit radicands are valid, no narrow-input precondition.',
  '',
  '## Canonical 4,130 case identical-input public entry comparisons',
  '',
  '| Profile | Stock CPU cycles | Source opt-in | Saved | Program bytes |',
  '|---|---:|---:|---:|---:|']
 for p in PROFILES:
  a=rows[p]
  lines.append('| %s | %.3f | %.3f | %d | %d |'%(p,a['stock_public_mean'],a['direct_highword_mean'],a['paired_saving'],a['code_bytes']))
 lines += ['',
  'All **16,520 matched CPU-model calls PASS** with root equality to',
  'Python math.isqrt(), low-level carry=0, X, Y, stack, preserved input,',
  'ordinary ISQRT16 interleaved and restoration of normal public JMP.',
  'Every paired call saves **exactly 47 cycles (V2/V3)** or **51 cycles',
  '(V1/V5)**, with no tail regressions in the measured corpus.',
  '',
  'Native VICE x64sc: **192 baseline/direct-entry opt-in calls** passed',
  'correct 16-bit result and carry on the four changed profiles.',
  'Native V4 control: 24 additional original calls with the actual',
  '**16 MiB REU image loaded** PASS. **No V4 replacement is claimed**.',
  'The CPU-model includes the preserved public $5E30 JMP entry, while',
  'the native opt-in harness calls the separate $0C00 entry directly.',
  'Native cycle timing is NOT measured; REU wall/bus cycles are not',
  'inferred from the CPU model.',
  '',
  '### ABI, resources and safe use',
  '',
  '- Original public MATH_ISQRT32 entry remains $5E30; call the',
  '  separate $0C00 entry directly, or redirect only the original',
  '  two-byte in-memory JMP target ($5E31/$5E32) under exclusive',
  '  access. No shipped PRG or resident source is modified.',
  '- Source islands occupy $0C00..$0CB5 including gaps; program',
  '  requires 95 bytes V2/V3 or 102 bytes V1/V5.',
  '- This address range is **example caller-owned RAM**, not reserved',
  '  by the library; check application/loader/IRQ/stack maps.',
  '- Exact resident MATH_INIT and precomputed square lookup tables',
  '  must remain accessible and unchanged.',
  '- Uses the resident shared zero page and original radix-4 helper;',
  '  safe for sequential mixed calls, **not** interrupt-reentrant.',
  '- Source is per-profile, relocations need fresh validation.',
  '- V4 uses an unrelated REU table architecture; this alternative',
  '  is **not** compatible with V4 and leaves it unchanged.',
  '- Default resident PRGs, both REU images, ordinary API symbols,',
  '  default zero-page budgets and PERFORMANCE leaderboard unchanged.',
  '',
  'Assembly sources: '+SOURCE+'/<profile>.asm',
  'Source generator: tools/issue144_isqrt32_highword_direct_experiment.py',
  'Canonical public-entry benchmark: tools/issue144_isqrt32_direct_seed_canonical.py',
  'Real native VICE: tools/native_issue144_isqrt32_highword_direct.py',
  'CPU proof: '+MODEL,'VICE proof: '+NATIVE,
  'No private OptiSearch code or archive is redistributed.']
 (ROOT/DOC).parent.mkdir(parents=True,exist_ok=True)
 (ROOT/DOC).write_text('\n'.join(lines)+'\n')
 (ROOT/SOURCE/'README.md').write_text('# Unrestricted ISQRT32 highword direct seed source\n\nSee ../../'+DOC+'.\nFour profiles only; reserve low RAM, initialize tables and do not use the V4 REU producer with this source.\n')
 state['issue144_isqrt32_direct_highword_seed_2026_10_15']={
  'status':'PASS_SOURCE_NATIVE_PUBLIC_CPU_OPTIONAL_NON_REU_ONLY',
  'optimized_profiles':list(PROFILES),'unchanged_REU_profile':'v4_reu_16m',
  'canonical_paired_model_cases':16520,'native_old_new_calls':192,
  'v4_actual_16MiB_REU_native_reference_calls':24,
  'actual_cpu_savings_by_profile':{p:rows[p]['paired_saving'] for p in PROFILES},
  'code_bytes_by_profile':{p:rows[p]['code_bytes'] for p in PROFILES},
  'no_new_normal_zero_page':True,'interrupt_reentrant':False,
  'default_resident_or_REU_modified':False,'native_cycle_timing_measured':False,
  'model_record':MODEL,'native_record':NATIVE,'documentation':DOC,'source_directory':SOURCE}
 (ROOT/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 note=(STAMP+'\n- Source-only all-domain ISQRT32 non-REU highword-seed opt-in (V1/V2/V3/V5): '+
   '47 cycles faster V2/V3, 51 cycles V1/V5 on all 16,520 canonical paired CPU calls; '+
   '192 native original/opt-in x64sc calls PASS; V4 original 16MiB REU 24-call control PASS but unchanged. '+
   '95–102 bytes in caller-owned RAM, no ordinary ZP/PRG/REU/API/PERFORMANCE changes. '+DOC+'\n\n')
 for n in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=ROOT/n
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(['make','clean'],cwd=ROOT,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=ROOT,check=True)
 assert all(sha(p+'/resident/math_'+p+'_game_math.prg')==old_prgs[p] for p in ALL_PROFILES)
 assert dict(read('RELEASE_STATUS.json').get('reference_reu_sha256',{}))==old_reu
 print('ISSUE144 ISQRT32 DIRECT HIGHWORD SEED V1/V2/V3/V5 SOURCE/NATIVE/30CHECK SEALED')
if __name__=='__main__':main()
