#!/usr/bin/env python3
"""Seal the native V1 PR81 public-ABI validation report into public release metadata.

This script validates recorded native evidence; it does not pretend a GitHub
runner has VICE or re-run native emulation. Native harness/results are supplied
separately, each SHA pinned, and all publication assets are rechecked.
"""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE='validation/review/ISSUE39_V1_24BY8_ACCUMULATOR_FULL_RESIDENT_NATIVE_VICE.json'
DOC='docs/ISSUE39_V1_24BY8_FULL_RESIDENT_NATIVE_VICE_2026-10-12.md'
TAG='2026-10-12 ISSUE39 V1 ACCUMULATOR FULL-RESIDENT NATIVE VICE 384-CALL CERTIFICATE'
V1='cdc2ca502d664055f896d7ad1601e8dd994b61be33e24bde3e25fc0dcbee1cdd'
PR78='28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0'
SCRIPT='2a107ef5b8c23d9ac62ad79cd7092175cd5c47e3be81715da6f44d9f62f9d82a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regen_sha():
 paths=sorted((p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts
               and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
              key=lambda p:str(p.relative_to(ROOT)))
 (ROOT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(ROOT))+'\n' for p in paths))
def run(*args):subprocess.run([str(x) for x in args],cwd=ROOT,check=True)
def main():
 e=json.loads((ROOT/EVIDENCE).read_text())
 assert e['status']=='PASS'
 assert e['pr78_sha256']==PR78 and e['pr81_sha256']==V1
 assert e['harness_script_sha256']==SCRIPT
 assert e['total_native_full_resident_calls']==384
 assert e['input_pairs_per_api']==96 and not e['native_cycle_timing_measured']
 assert set(e['results'])=={'MATH_UDIV24','MATH_UMOD24'}
 for p in e['results'].values():
  assert p['native_calls_old_plus_new']==192 and p['errors']==p['old_new_differences']==0
 assert sha(ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg')==V1
 statepath=ROOT/'RELEASE_STATUS.json'
 state=json.loads(statepath.read_text())
 assert state['reference_prg_sha256']['v1_balanced']==V1
 assert state['issue39_v1_24by8_accumulator_release_2026_10_12']['status']=='PASS'
 assert state['issue39_v1_24by8_accumulator_release_2026_10_12']['new_v1_sha256']==V1
 assert state['issue39_v1_24by8_accumulator_release_2026_10_12']['unsigned_family_complete'] is False
 state['issue39_v1_24by8_accumulator_full_resident_native_vice_2026_10_12']={
  'status':'PASS','documentation':DOC,'evidence':EVIDENCE,
  'evidence_sha256':sha(ROOT/EVIDENCE),'harness_script_sha256':SCRIPT,
  'resident_sha256':V1,'old_resident_sha256':PR78,
  'native_public_entry_calls':384,'pairs_per_api':96,
  'oracle_errors':0,'old_new_differences':0,'native_cycle_timing_claim':False,
  'resident_source_or_binary_changed':False,'unsigned_family_complete':False}
 statepath.write_text(json.dumps(state,indent=2)+'\n')
 note=f'''{TAG}
- Native VICE x64sc full-resident proof supplements the earlier isolated source-kernel test: exact SHA-pinned PR78 versus released PR81 V1 residents, MATH_INIT plus true MATH_UDIV24/UMOD24 public-entry JSRs, 96 same-input pairs per API per resident, 384 native calls total, zero oracle, flag, input preservation, stack or old/new output errors.
- Full-resident result applies to Q/R/C and public ABI correctness only, NOT VICE cycle counts. No source code, public API, code size, profile binary, standalone pickup or ranking changed. Detail: {DOC}, evidence: {EVIDENCE}. Issue #39 and unsigned family stage remain OPEN.
'''
 for fname in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  p=ROOT/fname
  if TAG not in p.read_text():p.write_text(note+'\n'+p.read_text())
 for fname in ('README.md','USER_MANUAL.md'):
  p=ROOT/fname
  line=f'- Issue #39 full-resident native VICE x64sc V1 24/8 verification: {DOC}; 384 correct old/new public calls, no native cycle claim.'
  if line not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+line+'\n')
 if isinstance(state.get('documentation'),dict):
  f=ROOT/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=f.stat().st_size,
         user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 statepath.write_text(json.dumps(state,indent=2)+'\n')
 run('make','clean')
 for _ in range(3):
  regen_sha()
  run(sys.executable,'tools/package_audit.py')
 run(sys.executable,'tools/validate_public_catalog.py')
 run(sys.executable,'tools/validate_standalone_sources.py')
 assert sha(ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg')==V1
 print('NATIVE FULL RESIDENT CERTIFICATE SEALED: 384 PASS, no resident changes')
if __name__=='__main__':main()
