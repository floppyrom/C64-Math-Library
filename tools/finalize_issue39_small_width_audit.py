#!/usr/bin/env python3
"""Publish Issue39 8/16/24 audit without modifying any shipped arithmetic bytes."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
A=R/'validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json'
B=R/'validation/review/ISSUE39_V1_UDIV24_NARROW_REJECTION.json'
DOC='docs/ISSUE39_UNSIGNED_SMALL_WIDTH_WORKLOADS_2026-10-11.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads(A.read_text());b=json.loads(B.read_text())
assert a['status']=='PASS' and a['total_calls']==53760
assert len(a['results'])==6 and all(len(row)==7 for row in a['results'].values())
assert b['status']=='REJECT' and b['no_source_changes'] and b['machine_calls']>15000
for op in ('MATH_UDIV24','MATH_UMOD24'):
 d=b['routines'][op]['narrow_corner']
 assert d['slower']>d['faster'] and d['worst_regression_cycles']>=400
for p,cert in a['resident_sha256'].items():
 assert cert==sha(R/p/'resident'/f'math_{p}_game_math.prg'),p
line='- Issue #39 unsigned 8/16/24 seven-workload audit: '+DOC+'; 53,760 public calls, negative V1 24-bit selector proof; no resident changes. Overall family campaign remains open.'
for file in ('README.md','USER_MANUAL.md'):
 path=R/file
 if line not in path.read_text():path.write_text(path.read_text().rstrip()+'\n\n'+line+'\n')
msg="""2026-10-11 ISSUE39 UNSIGNED SMALL-WIDTH ARCHITECTURE AUDIT
- Added a new public ABI and cycle gate for 8/16/24-bit UDIV/UMOD: seven same-input classes, 256 operands per class, five resident profiles, 53,760 complete 6502 calls. The corpus demonstrates workload-conditioned V1/V2/V3/V4/V5 trade-offs, particularly V1 16-bit small-divisor efficiency versus V2 24-bit small-divisor efficiency.
- Rejected widening the V1 24-bit narrow-divisor escape: the seemingly improved canonical mean conceals up to 422-cycle regressions on a dedicated >1,700-case corner suite. A separate deterministic paired negative proof prevents accidentally promoting that unsound performance trade-off.
- Ran five native OptiSearchV2 executable strategies per 8/16/24 width on 101 vectors. Native timing is NOT a public ABI comparison or an optimality claim; private tool material remains outside the repository.
- Added documentation and review JSON/CSV with hashes, branch CI audit and publication checks. Resident PRGs, stable ABI addresses, ZP, REU and relocatable arithmetic source remain unchanged. Unsigned DIV/MOD issue39 checkbox remains unchecked.
- Details: docs/ISSUE39_UNSIGNED_SMALL_WIDTH_WORKLOADS_2026-10-11.md
"""
for file in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 path=R/file
 if '2026-10-11 ISSUE39 UNSIGNED SMALL-WIDTH ARCHITECTURE AUDIT' not in path.read_text():
  path.write_text(msg+'\n'+path.read_text())
path=R/'RELEASE_STATUS.json';j=json.loads(path.read_text())
j['issue39_unsigned_small_width_workloads_2026_10_11']={
 'status':'PASS', 'scope':'UDIV8/16/24 and UMOD8/16/24 profile/architecture screen',
 'public_calls':53760,'profile_count':5,'workload_count':7,
 'cases_per_workload_per_profile':256,'data_sha256':sha(A),
 'negative_v1_24_narrow_status':'REJECT','negative_report_sha256':sha(B),
 'resident_prgs_modified':False,'abi_changed':False,'zero_page_growth':0,
 'documentation':DOC,'unsigned_family_complete':False}
if isinstance(j.get('documentation'),dict):
 u=R/'USER_MANUAL.md'
 j['documentation'].update(user_manual_bytes=u.stat().st_size,
  user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=sha(u))
path.write_text(json.dumps(j,indent=2)+'\n')
print('ISSUE39 SMALL-WIDTH AUDIT PUBLICATION PASS')
