#!/usr/bin/env python3
"""Seal Issue144 signed32/16 alias direct-public-JMP opt-in and proof.

No alteration of production PRGs, REUs, standard ZP allocation or ordinary
PERFORMANCE leaderboard. Only matching profile's in-memory JMP operand bytes
may be changed by caller, under exclusive transition.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from issue144_signed_divmod_alias_direct_research import PROFILES,API,EXPECTED_CHAINS
from stage_issue39_v1_3216_ool_release import reseal
MODEL='validation/review/ISSUE144_SIGNED32_16_DIRECT_PUBLIC_JUMP_RESEARCH.json'
NATIVE='validation/review/ISSUE144_SIGNED32_16_DIRECT_PUBLIC_JUMP_NATIVE_VICE.json'
INSTALL='validation/review/ISSUE144_SIGNED32_16_DIRECT_PUBLIC_JUMP_INSTALLER.json'
DOC='docs/ISSUE144_SIGNED32_DIVMOD_DIRECT_JMP_2026-10-15.md'
DIR='optional/issue144_signed32_divmod_direct_jump'
TAG='2026-10-15 ISSUE144 SIGNED32/16 ZERO-FOOTPRINT PUBLIC-JMP DIRECT OPTIN'
def j(path):return json.loads((R/path).read_text())
def sha(path):return hashlib.sha256((R/path).read_bytes()).hexdigest()
def main():
 model,native,installer=map(j,(MODEL,NATIVE,INSTALL))
 assert model['status']=='PASS_ZERO_EXTRA_RAM_SIGNED32_16_ALIAS_HOPS'
 assert native['status']=='PASS_FIVE_PROFILE_NATIVE_SIGNED32_16_JMP_DIRECT'
 assert installer['status']=='PASS_S32_16_REAL_6510_SOURCE_BEGIN_END'
 assert model['same_input_pairs_per_op']==3279 and model['public_calls_model']==65580
 assert native['native_baseline_and_candidate_calls']==480
 assert set(model['profiles'])==set(native['profiles'])==set(installer['profiles'])==set(PROFILES)
 status=j('RELEASE_STATUS.json');resident=dict(status['reference_prg_sha256']);reu=dict(status.get('reference_reu_sha256',{}))
 for p in PROFILES:
  for op in API:
   row=model['profiles'][p][op]
   gain=EXPECTED_CHAINS[p][op][1]
   assert row['saving']['min']==row['saving']['max']==row['saving']['mean']==gain
   assert row['bytes_edited']==(2 if gain>0 else 0)
   assert native['profiles'][p][op]['all_status_registers_outputs_and_stack_exact']
   assert native['profiles'][p][op]['source_assembled_ENABLE_DISABLE_executed_on_native']
  if p=='v5_hybrid_lowzp':assert installer['profiles'][p]['already_direct']
  else:
   record=installer['profiles'][p]
   assert record['restored_original_signed_divmod']
   assert record['changed_operand_bytes'] in (2,4)
   assert record['source_sha256']==sha(DIR+'/'+p+'.asm')
  assert sha(p+'/resident/math_'+p+'_game_math.prg')==resident[p]
 report=[]
 for p in PROFILES:
  a=model['profiles'][p]
  report.append('| %s | %.3f | %.3f | %s | %.3f | %.3f | %s |'%(
   p,a['MATH_SDIV32_16']['baseline']['mean'],a['MATH_SDIV32_16']['candidate']['mean'],
   a['MATH_SDIV32_16']['saving']['mean'],a['MATH_SMOD32_16']['baseline']['mean'],
   a['MATH_SMOD32_16']['candidate']['mean'],a['MATH_SMOD32_16']['saving']['mean']))
 doc=['# Issue144: signed 32÷16 full-contract public-entry JMP-chain pruning',
      '', '**Unrestricted signed input domain; original full quotient AND remainder ABI.**',
      '', 'An arithmetic-source audit found redundant JMP-to-JMP chains before',
      'the actual signed32/16 producer, with profile-specific routing.',
      'This is a true all-input public-call Pareto micro-optimization:',
      'no additional division state, no changed arithmetic producer, and',
      'no worst-case slowdown; only existing JMP target operand bytes change.',
      '', '| Profile | SDIV stock | SDIV direct | SDIV saved | SMOD stock | SMOD direct | SMOD saved |',
      '|---|---:|---:|---:|---:|---:|---:|',*report,'',
      '3279 identical operand pairs/API/profile: 32,790 paired tests,',
      '**65,580 total model public calls**, including all sign quadrants,',
      'divisor zero, signed 32-bit boundary cases, and q0/q1 cases.',
      'Exact quotient Q32, remainder R16, C, X/Y, stack, inputs and',
      'sentinel memory bytes match the original, not just arithmetic.',
      'All model savings are 0, 3 or 6 cycles, **constant per profile/API**.',
      'All 480 native x64sc baseline/optimized public calls pass',
      'the same complete output and status comparisons.',
      'Native correctness tested; native cycle count NOT measured.',
      '', '## Profile-specific executable routes',
      '', '- **V1:** SMOD alias `$3FDD JMP $3EE0 JMP $2590`; the',
      '  `$2590` instruction is **JSR**, not a jump. The patch MUST stop',
      '  at `$2590`; only SMOD gains 3 cycles, SDIV unchanged.',
      '- **V2/V4:** SDIV `$3EE0 JMP $2590 JMP $9200` and',
      '  SMOD `$3FDD JMP $3EE0 JMP $2590 JMP $9200`.',
      '  Redirect both public JMP targets to `$9200`.',
      '- **V3:** same but via `$2690` instead of `$2590`.',
      '- **V5:** both public JMPs already target the real signed',
      '  producer at `$5D00`; **zero improvement** so no patch.',
      '', '## Use and integration safety',
      '', 'Four readable per-profile reversible 6510 enable/disable sources',
      'are under `'+DIR+'/<profile>.asm`; V5 is explicitly a no-op.',
      'The V1 installer is 22 bytes, V2/V3/V4 installer 42 bytes.',
      'The example source installer RAM at `$0C80` is NOT reserved:',
      'check actual application map or reassemble elsewhere.',
      'Enable+disable **CPU-model cost**: V1 18+18 cycles; V2-V4 30+30',
      'cycles, plus JSR overhead if invoked by subroutine call. For V2/3/4',
      'the patch pays for itself when 3×SDIV_calls + 6×SMOD_calls exceeds',
      'the actual enable/disable invocation overhead. Static builder-time',
      'patching of exactly 2 (V1) or 4 (V2/3/4) JMP operands costs **no**',
      'additional resident code, ZP or data; no V5 patch is needed.',
      '', '**Changing a JMP target is not atomic.** Never run concurrent math',
      'in an IRQ/NMI or enter either public routine mid-install/mid-restore.',
      'Resident must be writable RAM, or patch the actual generated image',
      'at build time and requalify its checksum. The public API addresses',
      'and both full Q32+R16+carry output contracts remain intact.',
      'Do not attempt to redirect V1 to the `$9200` area, which is not',
      'the V1 signed producer (it contains data).',
      '', 'No production PRGs, REU images, shared ZP, arithmetic core, public',
      'PERFORMANCE leaderboard or normal linker map was changed.',
      'The change is intentionally published as optional, because the',
      'mean benefit is below the general 5% triage heuristic.',
      'No private OptiSearch source or donor code is included.',
      '', 'CPU reproducible benchmark: tools/issue144_signed_divmod_alias_direct_research.py',
      'Model-generated installers: tools/issue144_signed32_divmod_alias_installer.py',
      'Native VICE: tools/native_issue144_signed32_divmod_alias_direct.py',
      'CPU evidence: '+MODEL,'Installer evidence: '+INSTALL,'Native evidence: '+NATIVE]
 target=R/DOC;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('\n'.join(doc)+'\n')
 (R/DIR/'README.md').write_text('# Signed32/16 full-output public-entry JMP direct paths\n\nSee ../../'+DOC+'.\n')
 status['issue144_signed32_divmod_direct_public_jmp_2026_10_15']={
   'status':'PASS_SOURCE_CPU_NATIVE_OPTIN_NOT_DEFAULT',
   'profiles':list(PROFILES),'model_public_calls':65580,
   'native_public_calls':480,'normal_zero_page_growth':0,
   'changed_JMP_operand_bytes_by_profile':model['only_code_bytes_modified_by_profile'],
   'savings_by_profile':{p:{op:EXPECTED_CHAINS[p][op][1] for op in API} for p in PROFILES},
   'all_input_signs_and_divide_by_zero_qualified':True,
   'full_Q32_R16_and_C_contract':True,'native_cycles_measured':False,
   'production_PRGs_REUs_unchanged':True,
   'docs':DOC,'sources':DIR,'CPU_proof':MODEL,'native_proof':NATIVE,'installer_proof':INSTALL}
 (R/'RELEASE_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
 note=(TAG+'\n- All-input signed32/16 SDIV/SMOD full-Q+R public-entry JMP-chain micro-optins: V2/3/4 save 3/6 cycles per call, V1 SMOD saves 3, V5 already direct. 32,790 matched input cases and 480 real native x64sc calls PASS; reversible V1/2/3/4 source installers 22/42 B. No ordinary resident PRG/REU/zero-page/API/PERFORMANCE changes. '+DOC+'\n\n')
 for fname in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  file=R/fname
  if TAG not in file.read_text():file.write_text(note+file.read_text())
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 assert all(sha(p+'/resident/math_'+p+'_game_math.prg')==v for p,v in resident.items())
 assert dict(j('RELEASE_STATUS.json').get('reference_reu_sha256',{}))==reu
 print('ISSUE144 S32/16 FULL Q/R DIRECT PUBLIC JMP SOURCE/NATIVE/CHANGELOG/SHA SEALED')
if __name__=='__main__':main()
