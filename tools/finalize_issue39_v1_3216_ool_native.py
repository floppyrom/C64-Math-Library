#!/usr/bin/env python3
"""Publish verified native VICE evidence for staged source-built V1/V5 residents.

Called only after 384 native old/new calls succeed in the independent workflow.
Keeps issue #39 open and never claims native/hardware cycle timing.
"""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from stage_issue39_v1_3216_ool_release import reseal,sha,DOC,EVIDENCE,STAMP
NATIVE='validation/review/ISSUE39_V1_3216_OOL_RELEASE_NATIVE.json'
def main():
 data=json.loads((ROOT/NATIVE).read_text())
 assert data['status']=='PASS_STAGED_NATIVE_VICE' and data['full_native_calls']==384
 assert set(data['profiles'])=={'v1_balanced','v5_hybrid_lowzp'}
 assert all(set(x['operations'])=={'MATH_UDIV32_16','MATH_UMOD32_16'} for x in data['profiles'].values())
 prod=ROOT/EVIDENCE
 proof=json.loads(prod.read_text())
 assert proof['status']=='PASS_STAGED_NATIVE_VICE_GATE_PENDING'
 assert proof['candidate_sha256']['v1_balanced']==data['profiles']['v1_balanced']['source_built_sha256']
 assert proof['candidate_sha256']['v5_hybrid_lowzp']==data['profiles']['v5_hybrid_lowzp']['source_built_sha256']
 proof.update(status='PASS_NATIVE_SOURCE_INSTALLED_PR_PENDING',
      native_source_built_calls=384,native_cycles_measured=False,
      native_report=NATIVE)
 prod.write_text(json.dumps(proof,indent=2,sort_keys=True)+'\n')
 f=ROOT/DOC
 s=f.read_text()
 s=s.replace('**Release gate still outstanding:** actual native VICE of the staged source-installed image, independent PR CI and post-merge main CI.',
             '**Native VICE release gate passed:** 384 complete V1/V5 original/candidate public calls in pinned x64sc, covering both 32/16 aliases. No native cycle timings measured. Remaining gates: independent PR CI and post-merge main CI.')
 assert '384 complete V1/V5' in s
 f.write_text(s)
 for p in ('README.md','USER_MANUAL.md'):
  f=ROOT/p
  s=f.read_text().replace(' (pending native VICE and independent PR/main CI).',
                           ' (384 native VICE full-resident calls passed; independent PR/main CI pending).')
  f.write_text(s)
 label='2026-10-13 ISSUE39 V1 32/16 SOURCE INSTALLED NATIVE VICE GATE'
 note=(label+'\n'
       '- Pinned real x64sc executed 384 old/new complete resident calls across V1 and V5, two public 32/16 aliases and 48 matching operands each. No Q32/R16/carry/N/D/ROM-underlay or output-dump differences. V5 32/16 donor behavior unchanged. Native cycle timing NOT measured.\n'
       '- Source-built reference/alternate maps, 56 stable APIs, full 822,050 unsigned / 364,533 signed, comparable 136,335, and package/standalone checks passed. Exact source/PRG SHA evidence and native report sealed. Issue #39 still OPEN. '+DOC+'\n\n')
 for path in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=ROOT/path
  if label not in f.read_text():f.write_text(note+f.read_text())
 statepath=ROOT/'RELEASE_STATUS.json'
 status=json.loads(statepath.read_text())
 status['issue39_v1_3216_ool_zero_source_production_2026_10_13'].update(
      status='PASS_NATIVE_SOURCE_INSTALLED_WAITING_PR_AND_MAIN_CI',
      native_vice_source_built_calls=384,
      native_release_proof=NATIVE,
      native_release_proof_sha256=sha(ROOT/NATIVE),
      unsigned_family_complete=False)
 if isinstance(status.get('documentation'),dict):
  f=ROOT/'USER_MANUAL.md'
  status['documentation'].update(user_manual_bytes=f.stat().st_size,
        user_manual_lines=len(f.read_text().splitlines()),
        user_manual_sha256=sha(f))
 statepath.write_text(json.dumps(status,indent=2)+'\n')
 for i in range(2):
  reseal()
  subprocess.run([sys.executable,str(ROOT/'tools/package_audit.py')],cwd=ROOT,check=True)
 reseal()
 subprocess.run([sys.executable,str(ROOT/'tools/package_audit.py')],cwd=ROOT,check=True)
 print('ISSUE39 V1/V5 NATIVE VICE RELEASE EVIDENCE SEALED; PR/MAIN CI STILL PENDING',flush=True)
if __name__=='__main__':main()
