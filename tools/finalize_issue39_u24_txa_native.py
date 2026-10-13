#!/usr/bin/env python3
"""Seal tested native x64sc old/new public-resident verification for issue39."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
EVIDENCE=R/'validation/review/ISSUE39_U24_TXA_NATIVE_VICE.json'
DOC=R/'docs/ISSUE39_U24_TXA_SOURCE_INTEGRATION_2026-10-13.md'
TAG='2026-10-13 ISSUE39 NATIVE VICE GENERIC U24 TXA PUBLIC RESIDENT'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def checksum():
 files=sorted((p for p in R.rglob('*') if p.is_file() and '.git' not in p.parts
  and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in files))
def main():
 evidence=json.loads(Path(sys.argv[1]).read_text())
 assert evidence['status']=='PASS_NATIVE_VICE_OLD_NEW_FULL_RESIDENT'
 assert evidence['native_full_resident_calls']==960 and len(evidence['rows'])==10
 assert evidence['cases_per_image_per_api']==48 and evidence['native_cycles_claimed'] is False
 statusp=R/'RELEASE_STATUS.json'
 status=json.loads(statusp.read_text())
 stage=status['issue39_u24_txa_production_source_2026_10_13']
 assert stage['status']=='PASS_STAGED_NATIVE_VICE_GATE_PENDING'
 ps=set(stage['changed_profiles'])
 assert ps=={'v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp'}
 assert {(row['profile'],row['operation']) for row in evidence['rows']}=={
  (p,op) for p in ps for op in ('MATH_UDIV24','MATH_UMOD24')}
 for row in evidence['rows']:
  p=row['profile']
  assert row['native_old_calls']==row['native_new_calls']==48
  assert row['native_total_calls']==96
  assert row['old_resident_sha256']==stage['before_reference_sha256'][p]
  assert row['new_resident_sha256']==stage['after_reference_sha256'][p]
  assert row['new_resident_sha256']==sha(R/p/'resident'/f'math_{p}_game_math.prg')
 EVIDENCE.parent.mkdir(parents=True,exist_ok=True)
 EVIDENCE.write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
 source=DOC.read_text()
 old=('**Native VICE verification is still a separate gate.** No emulator\n'
      'native call or VIC/REU DMA timing is claimed by this staged proof.\n'
      'Do not merge solely on this script if native evidence is required.')
 new=('**Native VICE x64sc correctness passed.** Old and new complete resident\n'
      'UDIV24/UMOD24 programs were run with 48 identical operands in each of\n'
      'five profiles: **960 native emulator calls** with zero failures in\n'
      'contracted Q, R, carry, N/D preservation, and high-R sentinel.\n'
      'The 48-input vectors include zero divisors and full/high-width cases.\n'
      'V5 was tested with RAM visible under BASIC ROM. All exact input and\n'
      'output fingerprints are recorded in the companion native VICE JSON.\n'
      'These are native correctness calls, not native cycle-time or real\n'
      'REU/VIC bus-load performance measurements.')
 assert old in source
 DOC.write_text(source.replace(old,new))
 for name in ('README.md','USER_MANUAL.md'):
  f=R/name
  f.write_text(f.read_text().replace(
    'Native VICE must be qualified separately; family campaign open.',
    'Native VICE full-resident 960-call correctness verified; family campaign open.'))
 log=(TAG+'\n'
  '- Ran 960 true x64sc native emulator calls: 48 identical inputs per old and new complete resident, UDIV24/UMOD24 in all five profiles, zero Q where promised, R, carry, input/high sentinel errors. V5 executed RAM under BASIC ROM. No native cycles or REU/VIC wall-time measured.\n'
  '- Pinned official headless VICE r46274 package SHA, source harness, operand/output digest evidence, both changelogs, docs, status and checksums; full 822,050 unsigned and 364,533 signed emulated validation already passed. Issue39 unsigned family OPEN. '+str(DOC.relative_to(R))+'\n\n')
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if TAG not in f.read_text():f.write_text(log+f.read_text())
 stage['status']='PASS_SOURCE_AND_NATIVE_VICE_QUALIFIED'
 stage['native_vice_calls']=960
 stage['native_vice_report']=str(EVIDENCE.relative_to(R))
 stage['native_vice_report_sha256']=sha(EVIDENCE)
 stage['native_vice_package']='VICE headlessvice_3.10+r46274.deb'
 stage['native_vice_package_sha256']='5d85ab7b73e9b32007ac7f844603e101fdd7009c47d1898216bfff4b2a44996a'
 if isinstance(status.get('documentation'),dict):
  f=R/'USER_MANUAL.md'
  status['documentation'].update(user_manual_bytes=f.stat().st_size,
   user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 statusp.write_text(json.dumps(status,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(4):
  checksum()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
  if all(x.split('  ',1)[0]==sha(R/x.split('  ',1)[1].strip())
    for x in (R/'SHA256SUMS.txt').read_text().splitlines()):break
 else:raise AssertionError('package hash did not stabilize')
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
 subprocess.run([sys.executable,'tools/validate_standalone_sources.py'],cwd=R,check=True)
 checksum()
 subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 print('ISSUE39 U24 TXA NATIVE X64SC PUBLIC RESIDENT PROOF SEALED',flush=True)
if __name__=='__main__':main()
