#!/usr/bin/env python3
"""Seal independently measured 32/16 D-high-aware delegation research, no promotion."""
from pathlib import Path
import json,hashlib,subprocess,sys
R=Path(__file__).resolve().parents[1]
DOC=R/'docs/ISSUE39_U3216_N16_DHI_GATED_SCREEN_2026-10-12.md'
REP=R/'validation/review/ISSUE39_U3216_N16_DHI_GATED_SCREEN.json'
ASM=R/'tools/candidates/issue39_u3216_n16_dhi_guard_research.asm'
PROFILE=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
THRESHOLDS=(1,4,16,64)
MARK='2026-10-12 ISSUE39 U3216 N16 DHI-GATED DONOR FIVE-PROFILE SCREEN'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seal():
 paths=sorted((p for p in R.rglob('*') if p.is_file()
      and '.git' not in p.parts and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
      key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in paths))
def main():
 report=json.loads(Path(sys.argv[1]).read_text())
 state=json.loads((R/'RELEASE_STATUS.json').read_text())
 assert report['status']=='PASS_RESEARCH_ONLY' and not report['resident_changed']
 assert report['research_under_kernal_rom_not_natively_qualified']
 assert report['thresholds_d1_min']==list(THRESHOLDS)
 assert report['code_bytes']==33 and report['normal_zp_growth']==0
 assert report['pairwise_tests']==79130 and report['complete_resident_cpu_calls']==395650
 assert report['arithmetic_or_abi_errors']==0
 assert set(report['profiles'])==set(PROFILE)
 lines=['# Issue #39 — 32/16 divisor-aware narrow-numerator donor screen',
 '',
 '12 October 2026. **Research-only, no binary or API change.**',
 '',
 'Following the 26-byte N16-only donor A/B (PR87), this screen adds',
 'a high-divisor filter to its source: delegate N<65536 to the',
 'resident 16/16 routine only when the divisor high byte D1 reaches',
 'a chosen minimum threshold (1, 4, 16, 64). This avoids invoking',
 'the inferior 16/16 producer on V2–V5 for D<256, while retaining',
 'the established 32/16 path for other operands and D=0.',
 '',
 'The research helper is 33 bytes and uses a nested JSR (+2 stack',
 'bytes). It resides at $E100 in a **flat CPU model**, under KERNAL',
 'ROM in an unmodified C64 memory configuration. This is NOT a',
 'native VICE-certified loadable implementation, and remains unsafe',
 'to transplant without actual writable RAM placement and source',
 'relocation testing.',
 '',
 'Exact released V1–V5 resident SHA-256 checks; both UDIV32/16 and',
 'UMOD32/16 public-entry calls and Q32/R/C/N/D, sentinel and stack',
 'preservation. **79,130 common old/new input pairs** tested across',
 'all profiles, four live candidate thresholds and originals:',
 '**395,650 fully executed 6502 public calls**, zero ABI errors.',
 'Instruction CPU timing excludes REU/VIC contention.',
 '',
 '| Profile | Public entry | D1 minimum | Official mean delta cycles | N16-target delta | N16/D8 delta | N32 uniform delta |',
 '|---|---|---:|---:|---:|---:|---:|']
 best={}
 for name in PROFILE:
  group=report['profiles'][name]
  assert group['resident_sha256']==state['reference_prg_sha256'][name]
  best[name]={}
  for op in OPS:
   rows=group['operations'][op]
   assert set(rows)==set(['official','uniform_32x16','numerator_24bit','numerator_16bit','small_divisors','power_of_two_divisors','quotient_zero_or_one','n16_target','n16_small_d','n24_target','n32_target','n16_zero_divisor'])
   official=rows['official']['thresholds']
   pick=min(THRESHOLDS,key=lambda t:official[str(t)]['mean_delta'])
   best[name][op]={'best_official_cutoff_d1':pick,'best_official_delta':official[str(pick)]['mean_delta'],
                    'slow_calls_best_official':official[str(pick)]['slower']}
   for t in THRESHOLDS:
    key=str(t);a=rows['official']['thresholds'][key]
    b=rows['n16_target']['thresholds'][key]
    c=rows['n16_small_d']['thresholds'][key]
    d=rows['uniform_32x16']['thresholds'][key]
    assert (a['cases'],b['cases'],c['cases'],d['cases'])==(2729 if op=='MATH_UDIV32_16' else 1705,1024,512,512)
    assert d['mean_delta']==17
    lines.append(f"| {name} | {op} | {t} | {a['mean_delta']:+.6f} | {b['mean_delta']:+.6f} | {c['mean_delta']:+.6f} | {d['mean_delta']:+.6f} |")
 lines.extend(['',
 'These are **paired workload differences**, not a universal speed',
 'ranking. All four candidate gates still add 17 cycles to every',
 'full-width numerator on the tested uniform class. Selection based',
 'only on the official weighted corpus is not an unconditional',
 'improvement and would disadvantage different game/demo workloads.',
 '',
 'The source code and detailed JSON preserve every faster/slower',
 'count, maximum regression, per-class deltas, exact input hashes',
 'and five resident hashes.',
 '',
 '**Disposition:** retain released 32/16 cores as defaults. Publish',
 'this 33-byte source as a reproducible, library-dependent candidate',
 'for future opt-in/narrow-input specialization and potential',
 'source-owned-RAM native qualification. It is not standalone and',
 'must not be installed at $E100 without accounting for ROM banking.',
 'This does not finish the issue #39 unsigned DIV/MOD family campaign.'])
 DOC.write_text('\n'.join(lines)+'\n')
 REP.parent.mkdir(parents=True,exist_ok=True)
 REP.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 ASM.parent.mkdir(parents=True,exist_ok=True)
 ASM.write_text('''; ISSUE39 research-only $E100 flat-memory overlay.
; 33-byte 32/16 N16 + high divisor filter.
; The immediate divisor high-byte lower bound in DHI_MIN may be
; 1,4,16,64; default C64 memory maps KERNAL ROM over $E100.
; Requires legal writable-executable relocation and full native
; verification before deployment. Hook $31B0 LDA $C010 -> JMP $E100.
DHI_MIN = $01
* = $E100
N16_DHI_GATE:
    lda $C012
    ora $C013
    bne ORIGINAL
    lda $C015
    cmp #DHI_MIN
    bcc ORIGINAL
    jsr $3140
    lda #0
    sta $C01A
    sta $C01B
    rts
ORIGINAL:
    lda $C010
    jmp $31B3
''')
 log=f"""{MARK}
- Compared 33-byte in-memory divisor-high-gated 32/16 N16->16/16 reuse on exact V1–V5 residents, public UDIV32/16 and UMOD32/16, four D1 thresholds (1,4,16,64): 79,130 old/new operand pairs / 395,650 public CPU executions, zero Q/R/C/input/SP errors.
- Narrow-divisor reuse is filtered out; full-width numerator controls still incur +17 cycles. Research-only library-dependent donor, additional 2 stack bytes on delegation, $E100 under KERNAL ROM unqualified. Exact per-profile workload and input proof, source, docs, release metadata, both changelogs, SHA256SUMS published, **no production binary/ABI changes**. #39 stays OPEN. {DOC.relative_to(R)}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if MARK not in f.read_text():f.write_text(log+'\n'+f.read_text())
 link='- Issue39 32/16 N16 divisor-high-aware donor research: '+str(DOC.relative_to(R))+'. No default engine changed; family audit open.'
 for name in ('README.md','USER_MANUAL.md'):
  f=R/name
  if link not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+link+'\n')
 state['issue39_u3216_n16_dhi_screen_2026_10_12']={
  'status':'PASS_RESEARCH_NO_PROMOTION','report':str(REP.relative_to(R)),
  'report_sha256':sha(REP),'documentation':str(DOC.relative_to(R)),
  'candidate_assembly':str(ASM.relative_to(R)),
  'paired_inputs':79130,'cpu_calls':395650,'profiles':list(PROFILE),
  'candidate_divisor_high_minimums':list(THRESHOLDS),
  'best_weighted_candidate_by_profile_api':best,
  'native_vice_runs':0,'helper_requires_real_ram_relocation':True,
  'source_or_shipped_binary_changed':False,'unsigned_family_complete':False}
 if isinstance(state.get('documentation'),dict):
  f=R/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=f.stat().st_size,
    user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 (R/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for i in range(3):
  seal();subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 print('ISSUE39 U3216 N16 DHI-GATED RESEARCH SEALED',flush=True)
if __name__=='__main__':main()
