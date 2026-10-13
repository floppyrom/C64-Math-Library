#!/usr/bin/env python3
"""Fail-closed release proof sealer after real native x64sc source-installed calls."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from stage_issue39_v1_3216_ool_release import reseal,sha
MARK='2026-10-13 ISSUE39 V2 UMUL8 SOURCE-RELEASE NATIVE VICE'
NATIVE='validation/review/ISSUE39_V2_UMUL8_DIRECTOUT_NATIVE.json'
DOC='docs/ISSUE39_V2_UMUL8_DIRECT_OUTPUT_2026-10-13.md'
PROFILE='v2_pareto_fast'
def main():
    proof=json.loads((ROOT/NATIVE).read_text())
    assert proof['status']=='PASS_NATIVE_VICE_V2_UMUL8_PUBLIC_DIRECT_OUTPUT'
    assert proof['native_calls']==128 and proof['paired_operands']==64
    assert proof['all_guaranteed_public_results_identical'] is True
    assert proof['noncarry_flags_volatile_per_USER_MANUAL'] is True
    assert proof['native_cycles_measured'] is False
    statusfile=ROOT/'RELEASE_STATUS.json'
    state=json.loads(statusfile.read_text())
    row=state['issue39_v2_umul8_directout_2026_10_13']
    assert row['status'] in ('PASS_STAGED_NATIVE_VICE_PENDING',
                             'PASS_NATIVE_VICE_SOURCE_INSTALLED_PR_CI_PENDING')
    assert state['reference_prg_sha256'][PROFILE]==proof['new_sha256']==row['new_sha256']
    assert proof['old_sha256']==row['old_sha256']
    assert sha(ROOT/PROFILE/'resident'/f'math_{PROFILE}_game_math.prg')==row['new_sha256']
    row.update(status='PASS_NATIVE_VICE_SOURCE_INSTALLED_PR_CI_PENDING',
       native_vice_calls=128,native_evidence=NATIVE,
       volatile_status_differences=proof['noncarry_status_flag_differences'],
       native_evidence_sha256=sha(ROOT/NATIVE),native_cycles_measured=False)
    f=ROOT/DOC
    s=f.read_text().replace(
        'staged release; native VICE and PR/main CI pending',
        'native-qualified source release; independent PR/main CI pending')
    s=s.replace('**Pending**: native x64sc comparison on actual source-installed V2 resident, full PR CI and post-merge main CI.',
        '**Native x64sc PASS:** 128 actual full-resident old/new calls over 64 fixed/edge/random operand pairs. Guaranteed public output, caller inputs, carry, stack and sentinels agree with the pinned pre-release image. Non-carry N/Z/V status flags are explicitly volatile per USER_MANUAL.md; the observed status differences are recorded in the native report. Native cycle timing was not measured. **Pending:** independent PR and post-merge main CI.')
    assert '**Native x64sc PASS:**' in s
    f.write_text(s)
    note=(MARK+'\n'
      '- 128 actual x64sc old/new source-installed V2 UMUL8 public calls'
      ' (64 identical operands per image), exact Q16/input/carry/stack/sentinel'
      ' outputs. Non-carry status bits (N/Z/V) are explicitly volatile and their differences are recorded. No native cycle-timing assertion; six-cycle saving is from'
      ' exhaustive same-input model. V2-only, no resource growth.'
      ' See '+NATIVE+'. Issue #39 remains OPEN.\n\n')
    for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        p=ROOT/fn
        if MARK not in p.read_text():p.write_text(note+p.read_text())
    for fn in ('README.md','USER_MANUAL.md'):
        p=ROOT/fn
        s=p.read_text().replace('(native VICE pending).',
            '(native x64sc 128 old/new public calls PASS; independent PR/main CI pending).')
        p.write_text(s)
    if isinstance(state.get('documentation'),dict):
        f=ROOT/'USER_MANUAL.md'
        state['documentation'].update(user_manual_bytes=f.stat().st_size,
          user_manual_lines=len(f.read_text().splitlines()),
          user_manual_sha256=sha(f))
    statusfile.write_text(json.dumps(state,indent=2)+'\n')
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(ROOT/'tools/package_audit.py')],
                       cwd=ROOT,check=True)
    print('V2 UMUL8 FULL-RESIDENT x64sc NATIVE VALIDATION SEALED; PR/MAIN CI PENDING',flush=True)
if __name__=='__main__':main()
