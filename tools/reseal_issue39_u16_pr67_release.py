#!/usr/bin/env python3
"""Reseal PR67 after updating the V2/V5 UMOD16 public-cycle parity fixture.

This does not rebuild or change any PRG. Fail if any 16-bit resident hash
departs from the source-qualified, already published PR67 candidate.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
TAG='2026-10-12 ISSUE39 PR67 V5 PAIR-CORPUS FIXTURE REFRESH'
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def py(name):subprocess.run([sys.executable,'tools/'+name+'.py'],cwd=ROOT,check=True)
def checksum():
 items=sorted((p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='SHA256SUMS.txt'),
  key=lambda p:str(p.relative_to(ROOT)))
 (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in items))
def main():
 doc=ROOT/'RELEASE_STATUS.json';state=json.loads(doc.read_text())
 assert state['issue39_u16_known_carry_pr67_2026_10_12']['status']=='PASS'
 for p in PROFILES:
  actual=digest(p+'/resident/math_'+p+'_game_math.prg')
  assert actual==state['reference_prg_sha256'][p],(p,'resident image unexpectedly changed')
 py('validate_v5_umod16_frontend')
 msg=f'''{TAG}
- Removed the obsolete hard-coded 198.610557-cycle V5/ V2 UMOD16 comparison.
- The permanent 1,705-pair exact V2/V5 public ABI parity test now pins both current shipped resident SHA-256 hashes against the same-input benchmark report and checks each measured mean against the corresponding report metric. This preserves a strict cycle regression check across further source-qualified changes while avoiding stale pre-release literals. All four candidate resident images remain byte-identical to the already staged PR67 release.
'''
 for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  p=ROOT/fn;s=p.read_text()
  if TAG not in s:p.write_text(msg+'\n'+s)
 state['issue39_u16_known_carry_pr67_2026_10_12']['v5_umod16_frontend_source_sha256']=digest('tools/validate_v5_umod16_frontend.py')
 doc.write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=ROOT,check=True)
 for _ in range(4):
  checksum();py('package_audit')
  if all(h==digest(path) for h,path in (line.split('  ',1) for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines())):break
 else:raise AssertionError('manifest not stable')
 py('validate_public_catalog')
 checksum();py('package_audit')
 print('ISSUE39 PR67 RELEASE RESEAL PASS: CURRENT V2/V5 PARITY',flush=True)
if __name__=='__main__':main()
