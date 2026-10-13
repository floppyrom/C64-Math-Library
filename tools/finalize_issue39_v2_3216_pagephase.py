#!/usr/bin/env python3
"""Publish the bounded 32/16 page-phase feasibility no-gain with strict evidence.

No resident/source arithmetic, ABI, resource or performance changes. This
research excludes only isolated shifts, NOT joint restructuring of neighbours.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from stage_issue39_v1_3216_ool_release import reseal

REPORT='validation/review/ISSUE39_V2_3216_PAGE_PHASE_RESEARCH.json'
DOC='docs/ISSUE39_V2_3216_PAGE_PHASE_FEASIBILITY_2026-10-13.md'
MARKER='2026-10-13 ISSUE39 V2 UDIV32/16 PAGE PHASE SOURCE OWNERSHIP AUDIT'

def main():
    p=ROOT/REPORT
    subprocess.run([sys.executable,str(ROOT/'tools/screen_issue39_v2_3216_pagephase.py'),
                    '--out',str(p)],cwd=ROOT,check=True)
    report=json.loads(p.read_text())
    statefile=ROOT/'RELEASE_STATUS.json'
    status=json.loads(statefile.read_text())
    assert report['baseline_resident_sha256']==status['reference_prg_sha256']['v2_pareto_fast']
    assert report['status']=='PASS_RESEARCH_ONLY_NO_DEFAULT_CHANGE'
    assert report['validated_candidate_count']==0
    assert report['rejected_candidate_count']==14
    assert report['pairwise_6502_public_calls']==0
    assert report['baseline_main_span']==['0x4e00','0x50de']
    assert report['d8_island_start']=='0x5272'
    assert set(report['variants'])=={f'{n:+d}' for n in
        (-48,-32,-24,-16,-12,-8,-4,0,4,8,12,16,24,32,48)}
    for delta,info in report['variants'].items():
        if delta=='+0':assert info['status']=='BASELINE'
        else:
            assert info['status']=='REJECTED'
            assert 'no empty placement' in info['reason'],(delta,info['reason'])
    # This exactly bounds the claim: main starts $4E00, ends $50DE.
    # +/- shifts conflict with independently occupied bytes, so NONE
    # are valid resident candidates, and no timing comparison was possible.
    docs='''# Issue #39 — V2 32÷16 isolated page-phase feasibility screen

13 October 2026. **Research-only; do not promote or close issue #39.**

Post-PR100 reference baseline: V2 resident SHA-256
\x60c3c0898bc61a9836e7f58d1b51088ccc644613bf68d9e4199aa1243c4f164c84\x60.
The V2–V5 shared unrestricted 32÷16 algorithm owns the kernel source
\x60U3216_ENTRY\x60 at $4E00 with \x60U3216_MAIN_END\x60 at $50DE,
and its separate byte-divisor path begins at $5272.

The reproducible symbolic assembler experiment independently attempted 14
isolated shifts, from −48 to +48 bytes, while preserving the public
entry addresses, unrelated source owners, 32/8 island and reference
resident length. The original reference source was reproduced
**byte-for-byte** before any trial.

| Candidate placements | Outcome |
|---|---|
| −48, −32, −24, −16, −12, −8, −4 | Invalid: occupied bytes immediately before $4E00 |
| +4, +8, +12, +16, +24, +32, +48 | Invalid: first collision at $50DE |
| 0 (current placement) | Valid source/reference baseline |

**All 14 alternative layouts were rejected by strict source-ownership
checks before 6502 timing, because the displaced bytes would collide
with an existing owner.** Thus the valid candidate count is zero and
the number of paired old/new CPU executions is zero. This is a **bounded
address-layout infeasibility result**, **not** evidence that a redesigned
kernel or coordinated relocation cannot be faster, and **not** a claim
that all possible 32÷16 optimizations are exhausted.

See \x60tools/screen_issue39_v2_3216_pagephase.py\x60 and
\x60validation/review/ISSUE39_V2_3216_PAGE_PHASE_RESEARCH.json\x60.
The next legitimate architecture screen should modify an instruction
transition within a fixed resource envelope or jointly repack the
conflicting neighbouring source owners, followed by identical-input
UDIV/UMOD ABI/cycle audits across V2–V5.

**No production resident, ABI, ZP ownership or standalone implementation
was changed. OptiSearch remains private. The unsigned-family campaign
checkbox in issue #39 stays unchecked.**
'''
    target=ROOT/DOC
    target.write_text(docs)
    note=(MARKER+'\n'
          '- Bounded source-assembled V2–V5 shared 32/16 kernel page-phase screen:'
          ' 14 isolated +/-4..48-byte origin shifts rejected because neighbouring'
          ' source-owned bytes were occupied. No candidate qualified for timing;'
          ' this is a geometry no-gain only, not a global optimality claim.\n'
          '- No PRG, public ABI, ZP, stack, runtime cycles or profile defaults'
          ' changed. Full exact source baseline and rejected origins recorded in '
          +DOC+' and '+REPORT+'. Issue #39 remains OPEN.\n\n')
    for path in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        f=ROOT/path
        text=f.read_text()
        if MARKER not in text:f.write_text(note+text)
    row={
        'status':'PASS_BOUNDED_LAYOUT_REJECTION_NO_PRODUCTION_CHANGE',
        'documentation':DOC,'evidence':REPORT,
        'evidence_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
        'baseline_v2_sha256':report['baseline_resident_sha256'],
        'candidate_shifts_screened':14,
        'source_valid_alternate_shifts':0,
        'paired_calls':0,
        'native_vice_calls':0,
        'ABI_changed':False,
        'normal_ZP_growth':0,
        'unsigned_family_complete':False}
    status['issue39_v2_3216_page_phase_feasibility_2026_10_13']=row
    statefile.write_text(json.dumps(status,indent=2)+'\n')
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(ROOT/'tools/package_audit.py')],
                       cwd=ROOT,check=True)
    print('ISSUE39 PAGE PHASE SOURCE-OWNERSHIP REJECTION SEALED; ISSUE 39 OPEN',flush=True)

if __name__=='__main__':
    main()
