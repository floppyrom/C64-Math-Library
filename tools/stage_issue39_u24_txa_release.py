#!/usr/bin/env python3
"""Stage all five actual 24-bit TXA source-built residents, tables and manifests.

Branch-only release staging. This fails closed before the branch is committed:
source builds, current SHA parent, reference/alternate, V5 hybrid import,
all-profile unsigned/signed correctness, common input performance, public
standalone mirrors and deterministic release source proof must pass.
Native VICE correctness is a separate required release gate.
"""
from pathlib import Path
import csv,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
PS=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV24','MATH_UMOD24')
TAG='2026-10-13 ISSUE39 GENERIC U24 HIGH-GT LIVE-X PRODUCTION SOURCE'
DOC=R/'docs/ISSUE39_U24_TXA_SOURCE_INTEGRATION_2026-10-13.md'
PROOF=R/'validation/review/ISSUE39_U24_TXA_SOURCE_INTEGRATION.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(p):return R/p/'resident'/f'math_{p}_game_math.prg'
def execute(*cmd):
 print('RUN',*map(str,cmd),flush=True)
 subprocess.run([str(z) for z in cmd],cwd=R,check=True)
def py(name,*args):execute(sys.executable,R/'tools'/f'{name}.py',*args)
def build():
 for kind in ('reference','alternate'):
  py('assemble_sources','--profile','all','--config-kind',kind)
  py('build_hybrid','--config-kind',kind)
def built(p,kind):
 parent=(R/'build_hybrid' if p==PS[-1] else R/'build_source')/kind/p
 man=json.loads((parent/'source_build_manifest.json').read_text())
 f=parent/man['output_prg']
 assert f.exists() and sha(f)==man['output_sha256'],(p,kind)
 return f,man
def loadcsv(name):
 with (R/name).open(newline='') as f:return list(csv.DictReader(f))
def savecsv(name,rows):
 assert rows
 with (R/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def checksum():
 paths=sorted((x for x in R.rglob('*') if x.is_file() and '.git' not in x.parts
  and '__pycache__' not in x.parts and x.name!='SHA256SUMS.txt'),key=lambda x:str(x.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(x)+'  '+str(x.relative_to(R))+'\n' for x in paths))
def main():
 status=R/'RELEASE_STATUS.json'
 state=json.loads(status.read_text())
 before={p:sha(path(p)) for p in PS}
 assert before==state['reference_prg_sha256'],('parent release is stale',before)
 # Current exact file-based source candidate test BEFORE any shipped PRGs change
 # covers 5 profiles, two maps, official + 6 operand classes and mixed case checks.
 build()
 py('qualify_issue39_u24_txa_integration','--out','/tmp/issue39_u24_txa_preinstall.json')
 tested=json.loads(Path('/tmp/issue39_u24_txa_preinstall.json').read_text())
 assert tested['status']=='PASS_CANDIDATE_SOURCE_MAPS_NO_INSTALL' and set(tested['profiles'])==set(PS)
 proposed={}
 for p in PS:
  source,man=built(p,'reference')
  assert sha(source)!=before[p],(p,'candidate must actually differ')
  assert source.stat().st_size==path(p).stat().st_size,(p,'resident byte size growth')
  proposed[p]=sha(source)
  if p in ('v3_reu_512k','v4_reu_16m'):
   reu=man['reu_image']
   bundled=R/p/'reu'/('c64_math_v3_512k_game_math.reu' if p=='v3_reu_512k' else 'c64_math_v4_16m_game_math.reu')
   assert sha(source.parent/reu['file'])==sha(bundled),(p,'REU must not change')
  assert len(man['public_entries'])>=56
 for p in PS:
  src,man=built(p,'reference')
  shutil.copyfile(src,path(p))
 assert {p:sha(path(p)) for p in PS}==proposed
 # Full regenerated monoliths must now reproduce installed source-built PRGs.
 py('generate_sources')
 build()
 for p in PS:
  src,man=built(p,'reference')
  assert sha(src)==sha(path(p)),(p,'regenerated source is noncanonical')
  if p in ('v3_reu_512k','v4_reu_16m'):
   reu=man['reu_image']
   bundle=R/p/'reu'/('c64_math_v3_512k_game_math.reu' if p=='v3_reu_512k' else 'c64_math_v4_16m_game_math.reu')
   assert sha(src.parent/reu['file'])==sha(bundle)
 # Per-profile full 8-bit-exhaustive/wide width correctness & same-input official.
 py('validate_unsigned_division')
 py('validate_signed_division')
 py('benchmark_unsigned_common_corpus')
 py('audit_issue39_unsigned_small_workloads')
 py('benchmark_unsigned_3216_workloads')
 unsigned=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
 signed=json.loads((R/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
 common=json.loads((R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
 assert unsigned['status']==signed['status']==common['status']=='PASS'
 assert unsigned['summary']['machine_calls']==822050
 assert signed['summary']['machine_calls']==364533
 assert common['total_calls']==136335
 assert all(common['sources'][p]['resident_sha256']==proposed[p] for p in PS)
 # Genuine before/after current common-corpus results: only selected two APIs.
 official={op:{p:common['routines'][op]['metrics'][p]['mean_cycles'] for p in PS} for op in OPS}
 for p in PS:
  for op in OPS:
   assert official[op][p]>0
  assert abs(official['MATH_UDIV24'][p]-tested['profiles'][p]['reference']['operations']['MATH_UDIV24']['official']['source_mean'])<0.001,(p,'benchmark inconsistency')
 # Independent per-profile seeded validation drives local metadata, never
 # confuse with the shared-corpus cross-profile PERFORMANCE.md.
 for p in PS[:2]:
  name=f'{p}/PUBLIC_PERFORMANCE.csv';rs=loadcsv(name)
  for op in OPS:
   hits=[x for x in rs if x['operation']==op.lower()]
   assert len(hits)==1,(p,op)
   z=unsigned['profiles'][p][op]
   hits[0].update(avg_cycles=f"{z['mean_cycles']:.6f}",min_cycles=str(z['min_cycles']),
                  max_cycles=str(z['max_cycles']),cases=str(z['cases']),
                  evidence='2026-10-13 issue39 source-integrated U24 high-gt live-X public ABI')
  savecsv(name,rs)
 # Cross-profile comparison sheets also derive from the independent-seed
 # validation report; baseline and candidate were already proven on shared cases.
 name='v3_reu_512k/PUBLIC_PERFORMANCE.csv';rs=loadcsv(name)
 for op in OPS:
  hits=[x for x in rs if x['operation']==op[5:].lower()]
  assert len(hits)==1,(name,op)
  hits[0]['v1_balanced_cycles']=f"{unsigned['profiles'][PS[0]][op]['mean_cycles']:.6f}"
  hits[0]['v2_pareto_fast_cycles']=f"{unsigned['profiles'][PS[1]][op]['mean_cycles']:.6f}"
  hits[0]['v3_reu_default_cycles']=f"{unsigned['profiles'][PS[2]][op]['mean_cycles']:.6f}"
  hits[0]['v3_evidence']='2026-10-13 live-X generic U24 source integration'
 savecsv(name,rs)
 name='v4_reu_16m/PUBLIC_PERFORMANCE.csv';rs=loadcsv(name)
 for op in OPS:
  hits=[x for x in rs if x['operation']==op[5:].lower()]
  assert len(hits)==1,(name,op)
  hits[0]['v3_reu_512k_cycles']=f"{unsigned['profiles'][PS[2]][op]['mean_cycles']:.6f}"
  hits[0]['v4_reu_16m_cycles']=f"{unsigned['profiles'][PS[3]][op]['mean_cycles']:.6f}"
  hits[0]['v4_evidence']='2026-10-13 live-X generic U24 source integration'
 savecsv(name,rs)
 name='v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv';rs=loadcsv(name)
 for op in OPS:
  hits=[x for x in rs if x['routine']==op]
  assert len(hits)==1,(name,op)
  v1,v5=official[op][PS[0]],official[op][PS[-1]]
  hits[0].update(v1_mean_cycles=f'{v1:.6f}',v5_mean_cycles=f'{v5:.6f}',
    improvement_percent=f'{(v1-v5)*100/v1:.6f}',
    provenance='2026-10-13 exact same-input U24 TXA source promotion')
 savecsv(name,rs)
 # Root performance table always uses official same-input cross-profile mean.
 f=R/'PERFORMANCE.md';lines=f.read_text().splitlines()
 for op in OPS:
  idx=[i for i,x in enumerate(lines) if x.startswith('| '+chr(96)+op+chr(96)+' |')]
  assert len(idx)==1,(op,'PERFORMANCE row')
  cols=lines[idx[0]].split('|')
  for i,p in enumerate(PS):cols[3+i]=f' {official[op][p]:.6f} '
  lines[idx[0]]='|'.join(cols)
 f.write_text('\n'.join(lines)+'\n')
 # Publish source-backed accessible mirrors using newly installed source PRGs.
 py('publish_standalone_sources')
 py('generate_consolidated_routine_table')
 py('generate_public_indexes')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 # Publication is based on *actual installed* source-built SHA/cycle evidence.
 evidence={'status':'PASS_STAGED_PENDING_INDEPENDENT_NATIVE_VICE',
  'old_sha256':before,'new_sha256':proposed,
  'tested_reference_and_alternate':tested,
  'official_same_input_means':official,
  'signed_abi_calls':signed['summary']['machine_calls'],
  'unsigned_abi_calls':unsigned['summary']['machine_calls'],
  'same_input_unsigned_calls':common['total_calls'],
  'native_vice_calls':0,
  'stable_public_api_entries':56,'normal_zp_growth':0,
  'source_prg_size_growth':0,'reu_images_changed':False,
  'unsigned_family_complete':False}
 PROOF.parent.mkdir(parents=True,exist_ok=True)
 PROOF.write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n')
 rows=[]
 for p in PS:
  rows.append('| '+p+' | '+before[p][:12]+' | '+proposed[p][:12]+' | '+
    f"{official['MATH_UDIV24'][p]:.6f} | {official['MATH_UMOD24'][p]:.6f} |")
 DOC.write_text('\n'.join([
  '# Issue 39 — generic unsigned 24-bit high-quotient TXA source integration',
  '',
  '13 October 2026. Source-backed staged resident candidate.',
  '',
  'On N2>D2, earlier NMOS LAX N2 keeps N2 in X. Replacing LDA N2',
  'with TXA directly before high-byte SBC saves two CPU cycles/two',
  'instruction bytes without additional zero page or public ABI changes.',
  'V1 and V2–V4 source files were separately edited; V5 hybrid imports',
  'the rebuilt V2 dividend kernel from its relocated private ROM-underlay.',
  '',
  'Both reference and alternate address-map builds passed with real',
  'source-assembled PRGs and V3/V4 REU images. Every candidate public',
  'UDIV24 and UMOD24 entry passed signed/unsigned cross-family ABI checks,',
  'preserved N/D, quotient where promised, remainder, carry including D=0,',
  'high sentinel and caller stack. The V2–V5 remainder-only frontend',
  'can change branch phase, creating minor per-case modulo slowdowns.',
  '',
  '| Profile | Parent SHA prefix | Candidate SHA prefix | Official UDIV24 mean | Official UMOD24 mean |',
  '|---|---|---|---:|---:|']+rows+[
  '',
  'Official mean uses exactly the same current library comparison corpus',
  'for every V1–V5 resident, not an independent-seed profile-validator mean.',
  'No size, REU bank or normal zero-page growth. Full 822,050 unsigned,',
  '364,533 signed and 136,335 same-input public executions passed.',
  '',
  'The exact reference/alternate qualified input/cycle vectors and',
  'full SHA-pinned image evidence are retained in',
  'validation/review/ISSUE39_U24_TXA_SOURCE_INTEGRATION.json.',
  '',
  '**Native VICE verification is still a separate gate.** No emulator',
  'native call or VIC/REU DMA timing is claimed by this staged proof.',
  'Do not merge solely on this script if native evidence is required.',
  '',
  'The other unsigned DIV/MOD classes and issue #39 remain OPEN.'
 ])+'\n')
 blurb='- Source-integrated general-purpose UDIV24 live-X optimization: '+str(DOC.relative_to(R))+'. Native VICE must be qualified separately; family campaign open.'
 for name in ('README.md','USER_MANUAL.md'):
  file=R/name
  if blurb not in file.read_text():file.write_text(file.read_text().rstrip()+'\n\n'+blurb+'\n')
 log=(TAG+'\n'
  '- Source-installed generic 24-bit N2>D2 live-X high-byte subtraction LDA N2 -> TXA for V1/V2/V3/V4; V5 inherited donor code refreshed by source builder. Stable 56-entry API, resident PRG lengths, REU images and normal ZP unchanged. Full source reference/alternate maps and paired current-resident full public ABI qualified; V2–V5 dedicated UMOD24 layout-phase tradeoff recorded.\n'
  '- Full five-profile 822,050 unsigned, 364,533 signed and 136,335 same-input performance calls passed. Documentation, independent/full-input ranking tables, standalone sources, both changelogs, release-status PRG hashes and checksums regenerated. No native VICE calls have yet been claimed; require separate native proof before production merge. Issue #39 OPEN. '+str(DOC.relative_to(R))+'\n\n')
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if TAG not in f.read_text():f.write_text(log+f.read_text())
 state['date']='2026-10-13'
 state['reference_prg_sha256']=proposed
 state['alternate_prg_sha256']={p:built(p,'alternate')[1]['output_sha256'] for p in PS}
 state['issue39_u24_txa_production_source_2026_10_13']={
  'status':'PASS_STAGED_NATIVE_VICE_GATE_PENDING',
  'doc':str(DOC.relative_to(R)),'evidence':str(PROOF.relative_to(R)),
  'evidence_sha256':sha(PROOF),'changed_profiles':list(PS),
  'before_reference_sha256':before,'after_reference_sha256':proposed,
  'official_same_input_means':official,
  'resident_size_growth':0,'normal_zp_growth':0,
  'native_vice_calls':0,'unsigned_family_complete':False}
 for key,filename,field in (
  ('issue39_common_input_unsigned_divmod','validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json','benchmark_sha256'),
  ('issue39_unsigned_small_width_workloads_2026_10_11','validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','data_sha256'),
  ('issue39_unsigned_3216_multiworkload_2026_10_11','validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json','report_sha256')):
  if isinstance(state.get(key),dict):state[key][field]=sha(R/filename)
 if isinstance(state.get('documentation'),dict):
  f=R/'USER_MANUAL.md';state['documentation'].update(user_manual_bytes=f.stat().st_size,
    user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 status.write_text(json.dumps(state,indent=2)+'\n')
 py('verify_deterministic_rebuild')
 execute('make','clean')
 for _ in range(4):
  checksum();py('package_audit')
  if all(line.split('  ',1)[0]==sha(R/line.split('  ',1)[1].strip())
       for line in (R/'SHA256SUMS.txt').read_text().splitlines()):break
 else:raise AssertionError('package SHA did not stabilize')
 py('validate_public_catalog')
 py('validate_standalone_sources')
 checksum();py('package_audit')
 print('ISSUE39 U24 LIVE-X FULL PROFILE PRODUCTION RELEASE STAGED; NATIVE VICE PENDING',flush=True)
if __name__=='__main__':main()
