#!/usr/bin/env python3
"""Publish exact-current-resident 16-bit OptiSearch donor performance/ABI audit."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
REP=R/'validation/review/ISSUE39_U16_OPTISEARCH_PUBLIC_ABI_MATRIX.json'
DOC=R/'docs/ISSUE39_U16_OPTISEARCH_PUBLIC_ABI_MATRIX_2026-10-13.md'
PS=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
DS=('biased_2zp','direct_mod_0zp')
OPS=('MATH_UDIV16','MATH_UMOD16')
MAPS=('ram_0800','ram_0851')
MARK='2026-10-13 ISSUE39 U16 OPTISEARCH PUBLIC ABI AND WORKLOAD AUDIT'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seal():
 paths=sorted((p for p in R.rglob('*') if p.is_file() and '.git' not in p.parts
  and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
  key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in paths))
def main():
 report=json.loads(Path(sys.argv[1]).read_text())
 state=json.loads((R/'RELEASE_STATUS.json').read_text())
 assert report['status']=='PASS_SOURCE_BACKED_PUBLIC_ABI_NO_DEFAULT_PROMOTION'
 assert (report['paired_inputs'],report['cpu_calls'])==(86652,173304)
 assert not report['resident_changed'] and not report['public_entries_patched']
 assert set(report['profiles'])==set(PS) and set(report['donors'])==set(DS)
 assert report['ram_maps']==list(MAPS)
 for a in report['donors'].values():
  assert sha(R/a['source'])==a['sha256']
 rows=[];decision={}
 for p in PS:
  pr=report['profiles'][p]
  assert sha(R/p/'resident'/f'math_{p}_game_math.prg')==pr['resident_sha256']==state['reference_prg_sha256'][p]
  decision[p]={}
  for donor in DS:
   data=pr['donors'][donor]
   if p=='v1_balanced' and donor=='direct_mod_0zp':
    assert 'quotient output' in data['skipped']
    decision[p][donor]='incompatible with V1 UMOD16 quotient-output contract'
    continue
   assert set(data)==set(MAPS),(p,donor,'RAM map missing')
   base=data['ram_0800']
   alt=data['ram_0851']
   assert base['source_bytes']==report['donors'][donor]['code_and_data_bytes']
   assert base['extra_zp']==report['donors'][donor]['extra_zero_page_bytes']
   for op in ((OPS[1],) if donor=='direct_mod_0zp' else OPS):
    o=base['operations'][op]['official']
    u=base['operations'][op]['uniform16']
    n=base['operations'][op]['narrow_d8']
    assert (o['cases'],u['cases'],n['cases'])==(2729 if op==OPS[0] else 1705,128,128)
    assert alt['operations'][op]['official']['cases']==o['cases']
    if donor=='direct_mod_0zp':
     assert o['delta_mean']>0,(p,donor,op,'reconsider candidate')
    if donor=='biased_2zp' and p!='v1_balanced':
     assert u['delta_mean']>0,(p,donor,op,'reconsider promotion')
    # Cycle phase changes by origin. Exact input hashes and arithmetic
    # oracles were checked independently at both code locations.
    rows.append(f"| {p} | {donor} | {op[5:]} | {o['delta_mean']:+.3f} | {o['faster']} / {o['slower']} | {u['delta_mean']:+.3f} | {n['delta_mean']:+.3f} | {o['quotient_side_effect_differences']} |")
    decision[p][donor+'_'+op]={
     'official_delta':o['delta_mean'],'official_faster':o['faster'],
     'official_slower':o['slower'],'uniform_delta':u['delta_mean'],
     'narrow_d8_delta':n['delta_mean'],
     'official_mod_quotient_side_effect_differences':o['quotient_side_effect_differences'],
     'code_and_data_bytes':base['source_bytes'],
     'extra_normal_zp':base['extra_zp'],'extra_temp_ram':base['scratch_ram']}
 REP.parent.mkdir(parents=True,exist_ok=True)
 REP.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 lines=['# Issue 39 — V1–V5 OptiSearch 16-bit source/public-ABI replay','',
  '13 October 2026 — published donor audit; NO default resident promotion.','',
  'This replays two existing public Repose/OptiSearch NMOS 6510 sources:',
  'a 323-byte, 2-ZP full quotient/remainder UDIV16 producer and a',
  '976-byte, zero-ZP UMOD16 direct-chain specialist with 2 ordinary',
  'scratch-RAM bytes and an extra nested JSR return-address frame.',
  'Both were source-reassembled to two caller-owned code-RAM maps and',
  'compared against the EXACT reference SHA256-pinned current V1–V5',
  'public entry images. No private generator/source is distributed.',
  '',
  '**86,652 identical-input paired calls = 173,304 full 6502 CPU executions**',
  'across official common inputs plus 128 inputs in each of eight',
  'additional independent workload classes: uniform, D8, tiny D4,',
  'q=0, q=1, q=2..7, power of two, divisor zero.',
  'No arithmetic, carry, preserved N/D, output high-sentinel, stack,',
  'or caller memory sentinel mismatches; all input and cycle vectors',
  'are SHA256-identified. Instruction cycles do not include REU/VIC',
  'physical bus contention; no new native VICE run is claimed.',
  '',
  'The V1 UMOD16 public entry is a quotient-producing alias to UDIV16.',
  'The remainder-only direct-chain donor is consequently explicitly',
  '**incompatible with V1 UMOD16** and deliberately not tested as a',
  'valid V1 replacement. V2–V5 remainder-only outputs can have',
  'different Q side effects, which are counted rather than silently',
  'equated to a promised quotient-producing contract.',
  '',
  '| Resident profile | Source donor | Public API | Official delta cycles | Faster / slower cases | Uniform delta | D8 delta | Q-side differences |',
  '|---|---|---|---:|---:|---:|---:|---:|']+rows+['',
  'Delta is donor-minus-resident, where **negative is faster**.',
  'The 2-ZP full quotient donor wins some official input-weighted',
  'means, particularly with small divisors, but V2–V5 explicitly',
  'lose on uniform-random 16-bit inputs. The zero-ZP modulo donor',
  'does not improve the official current-resident mean; its distinct',
  'resource envelope remains useful for individually lifted code.',
  'This does NOT disqualify the transplant of individual borrow/branch',
  'strategies into the already optimized resident kernels.',
  '',
  '**Resource decision:** code is at caller-owned RAM, not owned',
  'resident code islands; the biased donor requires 2 additional ZP',
  'bytes, and the direct modulo donor uses 976 code/data bytes,',
  '2 scratch RAM bytes and extra nested JSR stack depth.',
  'Neither is a resource-neutral common default in the five profiles.',
  'Do not replace stable V1/V2/V3/V4/V5 resident defaults, alter any',
  'public ABI or claim full-profile optimality from this test.',
  '',
  'Reproducer: tools/screen_issue39_u16_optisearch_public_abi.py',
  'Exact evidence: validation/review/ISSUE39_U16_OPTISEARCH_PUBLIC_ABI_MATRIX.json',
  'Existing public donor source remains accessible under',
  'routines/standalone_lab/portable/. OptiSearch provenance: Repose.',
  'The private OptiSearch workspace stays private.',
  '',
  'Issue 39 remains OPEN. This is a U16 donor-class no-default',
  'decision, not the entire unsigned DIV/MOD architecture audit.']
 DOC.write_text('\n'.join(lines)+'\n')
 log=f"""{MARK}
- Replayed two already-published Repose/OptiSearch 16-bit sources across all SHA-pinned V1-V5 public ABI residents at two RAM maps: 86,652 paired operands / 173,304 actual 6502-model calls, zero correctness/ownership/stack failures. V1 modulo quotient alias is explicitly not replaced by remainder-only candidate.
- 323-byte 2-ZP biased producer wins official mean cycles on some profiles but regresses on V2-V5 uniform workload; 976-byte zero-ZP direct remainder source is slower than current resident on official inputs. No default promotion; source and standalone liftability preserved. New full class/cycle SHA JSON, docs, both changelogs, README/manual, status and hashes. No resident/ABI/ZP change. No new native VICE timing; issue39 remains OPEN. {DOC.relative_to(R)}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  path=R/name
  if MARK not in path.read_text():path.write_text(log+'\n'+path.read_text())
 ref='- Issue39 current-resident 16-bit OptiSearch donor ABI matrix: '+str(DOC.relative_to(R))+'. No default promotion.'
 for name in ('README.md','USER_MANUAL.md'):
  path=R/name
  if ref not in path.read_text():path.write_text(path.read_text().rstrip()+'\n\n'+ref+'\n')
 state['issue39_u16_optisearch_public_abi_2026_10_13']={
  'status':'PASS_NO_DEFAULT_PROMOTION',
  'report':str(REP.relative_to(R)),'report_sha256':sha(REP),
  'documentation':str(DOC.relative_to(R)),
  'reproducer':'tools/screen_issue39_u16_optisearch_public_abi.py',
  'profiles':list(PS),'donor_source_classes':list(DS),
  'paired_inputs':86652,'cpu_calls':173304,'native_vice_calls':0,
  'source_reassembled_code_maps':list(MAPS),
  'findings_by_profile':decision,'resident_binaries_changed':False,
  'public_api_changed':False,'unsigned_divmod_campaign_complete':False}
 if isinstance(state.get('documentation'),dict):
  path=R/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=path.stat().st_size,
   user_manual_lines=len(path.read_text().splitlines()),user_manual_sha256=sha(path))
 (R/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  seal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 print('ISSUE39 U16 PUBLIC OPTISEARCH DONOR MATRIX SEALED',flush=True)
if __name__=='__main__':main()
