#!/usr/bin/env python3
"""Seal issue39 U32/32 Repose/OptiSearch public ABI/resource research."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
REP=R/'validation/review/ISSUE39_U3232_OPTISEARCH_CURRENT_ABI.json'
DOC=R/'docs/ISSUE39_U3232_OPTISEARCH_ABI_RESOURCE_SCREEN_2026-10-12.md'
PS=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
DS=('aligned_0zp','zptail_4zp','mod_aligned_0zp')
OPS=('MATH_UDIV32_32','MATH_UMOD32_32')
MAPS=('ram_0800','ram_0851')
MARK='2026-10-12 ISSUE39 OPTISEARCH U32BY32 V1V5 PUBLIC ABI RESOURCE AUDIT'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seal():
 files=sorted((p for p in R.rglob('*') if p.is_file() and '.git' not in p.parts
  and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
  key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in files))
def main():
 j=json.loads(Path(sys.argv[1]).read_text())
 state=json.loads((R/'RELEASE_STATUS.json').read_text())
 assert j['status']=='PASS_PUBLIC_OPTISEARCH_ABI_REPLAY_NO_PROMOTION'
 assert (j['paired_cases'],j['cpu_calls'],j['errors'])==(131330,262660,0)
 assert not j['resident_changed'] and not j['public_entries_patched']
 assert j['maps']==list(MAPS) and set(j['profiles'])==set(PS)
 assert set(j['candidate_sources'])==set(DS)
 for v in j['candidate_sources'].values():assert sha(R/v['path'])==v['sha256']
 rows=[];selected={}
 for p in PS:
  image=R/p/'resident'/f'math_{p}_game_math.prg'
  pr=j['profiles'][p]
  assert sha(image)==pr['resident_sha256']==state['reference_prg_sha256'][p]
  selected[p]={}
  for donor in DS:
   maps=pr['donors'][donor]
   assert set(maps)==set(MAPS)
   m=maps[MAPS[0]]
   assert m['code_bytes'] in (576,544,496) and m['extra_zp_bytes'] in (0,4)
   for op in ((OPS[1],) if donor=='mod_aligned_0zp' else OPS):
    a=m['operations'][op]['official_common']
    b=m['operations'][op]['uniform_32']
    c=m['operations'][op]['divisor_8bit']
    assert (a['cases'],b['cases'],c['cases'])==(2729 if op==OPS[0] else 1705,64,64)
    assert a['slower']>0,(p,donor,op,'recheck potential Pareto gain')
    assert maps[MAPS[1]]['operations'][op]['official_common']['cases']==a['cases']
    rows.append(f"| {p} | {donor} | {op[5:]} | {a['delta_mean']:+.3f} | {a['slower']} | {b['delta_mean']:+.3f} | {c['delta_mean']:+.3f} |")
    selected[p][donor+'_'+op]={
     'official_delta_mean':a['delta_mean'],'official_slow_cases':a['slower'],
     'uniform_delta_mean':b['delta_mean'],'d8_delta_mean':c['delta_mean'],
     'extra_zp':m['extra_zp_bytes'],'scratch_ram':m['scratch_ram_bytes']}
 REP.parent.mkdir(parents=True,exist_ok=True)
 REP.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
 lines=['# Issue 39 — OptiSearch 32/32 donor replay against current V1–V5','',
 '12 October 2026. Research-only public ABI qualification; no production promotion.','',
 'This reruns the THREE already-published Repose/OptiSearch standalone',
 'unsigned 32-bit donor sources from routines/standalone_lab/portable',
 'without copying new private OptiSearch material. Two caller-owned',
 'RAM placements are reassembled, and identical input pairs are used',
 'against the exact current SHA-pinned full V1–V5 public 32/32 entries.',
 'Unlike a native standalone leaderboard, this includes full public',
 'entry costs, dividend/divisor preservation, Q/R/carry, mixed calls',
 'and stack/sentinel checks. REU images are loaded in the CPU model.',
 '',
 '131,330 matched input pairs / 262,660 complete CPU executions,',
 'zero mathematical or promised public-ABI mismatches. The operations',
 'include the official common corpus and eight separate distributions:',
 'uniform-full32, D8, D16, D24, quotient 0, quotient 1, high quotient',
 'and divisor zero. Modulo Q side effects are recorded separately',
 'rather than being assumed part of remainder-only contracts.',
 '',
 '| Profile | Source donor | API | Official delta cycles | Official slower calls | Uniform delta | D8 delta |',
 '|---|---|---|---:|---:|---:|---:|']+rows+['',
 'Delta is DONOR MINUS RESIDENT; positive is worse. Mean results are',
 'workload-specific and do not imply universal speed dominance.',
 'Every donor/profile/API has slower official cases. Zero-ZP donors',
 'require four scratch RAM bytes in addition to 496–576 code bytes.',
 'The 544-byte zptail needs four caller-owned additional ZP bytes.',
 'The remainder donor carries a nested JSR return-address cost.',
 'All require caller-owned executable RAM and unproven integration',
 'space in the fixed-profile resident builds. None is demonstrated',
 'to Pareto-dominate the current resident under all contracts.',
 '',
 'Neither public API, resident program, REU image, code origin nor',
 'shipped profile ZP budget was changed. The private OptiSearch search',
 'workspace remains private; Repose is credited for existing sources.',
 'Instruction-cycle timing excludes physical VIC and REU bus delay.',
 'No new native VICE execution or timing is claimed.',
 '',
 'Reproducer: tools/screen_issue39_u3232_optisearch_current_abi.py',
 'Evidence: validation/review/ISSUE39_U3232_OPTISEARCH_CURRENT_ABI.json',
 '',
 'Disposition: reject direct default transplants of these three donors.',
 'This establishes a source-backed audit of this donor class, not',
 'mathematical global optimality or completion of the unsigned family.',
 'Keep issue 39 OPEN; remaining variant/profile audits continue.']
 DOC.write_text('\n'.join(lines)+'\n')
 log=f"""{MARK}
- Screened three already-public Repose/OptiSearch unsigned 32/32 donor assemblies at two code-RAM origins against exact current V1–V5 resident public UDIV32/32 and UMOD32/32 contracts: 131,330 paired operands / 262,660 complete 6502 calls, zero arithmetic/R/C/N/D/SP/sentinel errors.
- All donor/profile/API official corpora contain regressing calls. Larger code-RAM and 4 ZP or 4 scratch RAM obligations remain; no fixed-profile default replacement justified. Full per-class SHA-pinned evidence, docs, README/manual references, both changelogs, release metadata and package hashes. No shipped binary/API changes, no native VICE bus timing claim, campaign issue 39 OPEN. {DOC.relative_to(R)}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if MARK not in f.read_text():f.write_text(log+'\n'+f.read_text())
 link='- Issue39 current-resident OptiSearch unsigned 32/32 donor resource audit: '+str(DOC.relative_to(R))+'. No default promotion.'
 for name in ('README.md','USER_MANUAL.md'):
  f=R/name
  if link not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+link+'\n')
 state['issue39_u3232_optisearch_public_abi_2026_10_12']={
  'status':'PASS_RESEARCH_NO_DEFAULT_PROMOTION',
  'reproducer':'tools/screen_issue39_u3232_optisearch_current_abi.py',
  'report':str(REP.relative_to(R)),'report_sha256':sha(REP),
  'docs':str(DOC.relative_to(R)),
  'profiles':list(PS),'donors':list(DS),'two_ram_maps':list(MAPS),
  'paired_inputs':131330,'cpu_calls':262660,'native_vice_calls':0,
  'outcomes':selected,'shipped_resident_changed':False,
  'public_api_changed':False,'unsigned_family_complete':False}
 if isinstance(state.get('documentation'),dict):
  f=R/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=f.stat().st_size,
   user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 (R/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for i in range(3):
  seal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 print('ISSUE39 OPTISEARCH U32 PUBLIC DONOR AUDIT SEALED',flush=True)
if __name__=='__main__':main()
