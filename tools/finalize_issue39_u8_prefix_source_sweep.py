#!/usr/bin/env python3
"""Publish bounded 8-bit quotient-prefix architecture sweep; no default change."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
REP=R/'validation/review/ISSUE39_UDIV8_PREFIX_PUBLIC_ABI_SWEEP.json'
DOC=R/'docs/ISSUE39_UDIV8_PREFIX_PERPROFILE_SCREEN_2026-10-13.md'
PS=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
KS=(8,12,16,20,24,28)
MAPS=('ram_0800','ram_0851')
MARK='2026-10-13 ISSUE39 UDIV8 PREFIX PUBLIC ABI SOURCE SWEEP'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seal():
 files=sorted((p for p in R.rglob('*') if p.is_file() and '.git' not in p.parts
  and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in files))
def main():
 j=json.loads(Path(sys.argv[1]).read_text())
 state=json.loads((R/'RELEASE_STATUS.json').read_text())
 assert j['status']=='PASS_BOUNDED_PREFIX_SCREEN_RESEARCH_ONLY'
 assert j['K_values']==list(KS) and j['locations']==list(MAPS)
 assert set(j['profiles'])==set(PS)
 assert j['paired_inputs']>100000 and j['cpu_calls']==2*j['paired_inputs']
 assert j['caller_owned_extra_zp_bytes']==1
 assert not j['normal_resident_changed'] and not j['public_api_changed']
 assert len(j['corpus'])==9
 rows=[]
 record={}
 for p in PS:
  pg=j['profiles'][p]
  assert sha(R/p/'resident'/f'math_{p}_game_math.prg')==pg['resident_sha256']==state['reference_prg_sha256'][p],p
  assert set(pg['variants'])==set(map(str,KS))
  candidates=[]
  for k in KS:
   maps=pg['variants'][str(k)]
   assert set(maps)==set(MAPS)
   a=maps['ram_0800'];b=maps['ram_0851']
   assert a['code_bytes']==b['code_bytes']
   assert a['extra_zp']==b['extra_zp']==1
   for g,item in j['corpus'].items():
    assert a['classes'][g]['cases']==b['classes'][g]['cases']==item['cases']
   off=a['classes']['official_common']
   uni=a['classes']['uniform']
   narrow=a['classes']['small_divisor']
   assert all(x['cases']>0 for x in (off,uni,narrow))
   rows.append(f"| {p} | {k} | {a['code_bytes']} | {off['delta_mean']:+.3f} | {off['faster']} / {off['slower']} | {uni['delta_mean']:+.3f} | {narrow['delta_mean']:+.3f} |")
   candidates.append((off['candidate_mean'],k,a['code_bytes']))
  record[p]={'official_best_K':min(candidates)[1],
    'official_best_candidate_cycles':min(candidates)[0],
    'official_public_mean':pg['variants']['12']['ram_0800']['classes']['official_common']['old_mean'],
    'all_tested_K_source_sizes':{str(k):pg['variants'][str(k)]['ram_0800']['code_bytes'] for k in KS}}
 REP.parent.mkdir(parents=True,exist_ok=True)
 REP.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
 lines=['# Issue 39 — UDIV8 manual 8/12/16/20/24/28 prefix-source screen','',
 '13 October 2026 — reproducible full public-ABI resource and workload screen.',
 '',
 'Manual source synthesis reproduces the existing **quotient-prefix',
 'compare/SBC** followed by **aligned shifted-divisor tail** architecture,',
 'used by V1/V2 (and inherited relatives). This is NOT a direct',
 'transplant of private OptiSearch source; the private package is',
 'kept private, and earlier OptiSearch small-quotient observations',
 'informed the manual source analysis.',
 '',
 'All six prefix-length variants are assembled at two caller-owned',
 'RAM addresses ($0800 and $0851), using exactly one extra ZP',
 'scratch byte ($70) outside the resident default resource contracts.',
 'They execute alongside each current SHA256-pinned V1–V5 public',
 'resident. Complete Q8, R8, carry (including D=0), preserved N/D,',
 'unchanged high Q/R buffer sentinels and balanced stack verified.',
 'The resident binaries, normal ZP windows and public entry addresses',
 'are NOT changed; native VICE was not used for candidate validation.',
 '',
 f"**{j['paired_inputs']:,} identical input pairs, {j['cpu_calls']:,} 6502 executions**,",
 'for the official common corpus and eight additional independent',
 'input classes (random, tiny and large divisors, q=0/1, powers of 2,',
 'divisor zero and structured edges). All input and cycle vectors',
 'are SHA-pinned in the JSON. Cycle values include public-entry',
 'execution through RTS, but do not model REU DMA/VIC bus stalls.',
 '',
 '| Profile | Prefix K | Code bytes (RAM) | Official delta cycles | Faster / slower | Uniform delta | Tiny-D delta |',
 '|---|---:|---:|---:|---:|---:|---:|']+rows+['',
 '**Negative candidate-minus-current-resident means faster** for',
 'that particular class only. Do not treat weighted benchmark means',
 'as a workload-neutral optimization; also compare extra code and',
 'scratch byte versus the resident normal-ZP budgets.',
 '',
 'Best K by this corpus within the six SOURCE-GENERATED variants:',
 ]+[f"- {p}: K={record[p]['official_best_K']}, candidate {record[p]['official_best_candidate_cycles']:.3f} cycles vs current public {record[p]['official_public_mean']:.3f} cycles." for p in PS]+[
 '',
 'The experiment does not prove the current source byte arrangement',
 'could be replaced in its present library-reserved slot without',
 'affecting REU, V5 hybrid, alternate-map or other routines. Public',
 'default replacement is therefore NOT made by this audit. A',
 'qualifying improvement would require real resident-source packing,',
 'zero additional normal ZP, exhaustive 65,536-case each profile,',
 'native VICE and reference/alternate ownership checks.',
 '',
 'Reproducer: tools/screen_issue39_u8_prefix_source_sweep.py',
 'Evidence: validation/review/ISSUE39_UDIV8_PREFIX_PUBLIC_ABI_SWEEP.json',
 'Published resident source anchors:',
 'relocatable_source/v1_balanced/udiv8_direct_public.inc and',
 'relocatable_source/v2_pareto_fast/udiv8_direct_public.inc.',
 'The private Repose OptiSearch engine is not published.',
 '',
 '**Issue #39 remains OPEN; unsigned DIV/MOD family not complete.**']
 DOC.write_text('\n'.join(lines)+'\n')
 log=f"""{MARK}
- Source-synthesized six established 8-bit compare/SBC quotient prefixes (K8/12/16/20/24/28) in two caller-owned RAM maps; validated exact full public Q8/R8/carry/ownership/stack against the current SHA-pinned V1–V5 resident UDIV8. {j['paired_inputs']:,} identical paired operands and {j['cpu_calls']:,} complete CPU calls, 9 workloads, 0 mathematical or promised-ABI errors.
- Published profile-specific code-byte, mean/tail cycle and workload fingerprints and bounded manual/OptiSearch-informed architecture ranking. Candidates need caller-owned RAM and 1 scratch ZP, not resident source-owned code resources; no default source/binary/API/normal ZP change or native-VICE timing claim. README/manual, both changelogs, release-status metadata and checksum seal updated. Issue #39 OPEN. {DOC.relative_to(R)}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if MARK not in f.read_text():f.write_text(log+'\n'+f.read_text())
 ref='- Issue39 current-resident UDIV8 quotient-prefix source architecture sweep: '+str(DOC.relative_to(R))+'. No default API/binary change.'
 for name in ('README.md','USER_MANUAL.md'):
  f=R/name
  if ref not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+ref+'\n')
 state['issue39_udiv8_prefix_source_screen_2026_10_13']={
  'status':'PASS_RESEARCH_NO_DEFAULT_PROMOTION',
  'evidence':str(REP.relative_to(R)),'evidence_sha256':sha(REP),
  'reproducer':'tools/screen_issue39_u8_prefix_source_sweep.py',
  'documentation':str(DOC.relative_to(R)),
  'current_residents_sha256':{p:j['profiles'][p]['resident_sha256'] for p in PS},
  'profile_results':record,'K_values':list(KS),'RAM_maps':list(MAPS),
  'paired_operands':j['paired_inputs'],'cpu_calls':j['cpu_calls'],
  'normal_ZP_growth':0,'caller_extra_ZP':1,'native_vice_calls':0,
  'production_binaries_changed':False,'public_api_changed':False,
  'unsigned_family_complete':False}
 if isinstance(state.get('documentation'),dict):
  f=R/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=f.stat().st_size,
   user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 (R/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  seal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 print('ISSUE39 UDIV8 BOUNDED PREFIX SCREEN SEALED',flush=True)
if __name__=='__main__':main()
