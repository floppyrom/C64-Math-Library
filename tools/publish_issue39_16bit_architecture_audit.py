#!/usr/bin/env python3
"""Publish issue #39's certified signed-16 paired screen and V2 donor rejection.

This is an evidence-only publication. No public ABI, profile PRG, ZP
allocation, independent historical benchmark, or routine selection changes.
"""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
J=ROOT/'validation/review/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.json'
D=ROOT/'validation/review/ISSUE39_V2_UDIV16_UMOD16_DONOR_SCREEN.json'
DOC='docs/ISSUE39_SIGNED16_PAIRED_AND_V2_16BIT_DONOR_SCREEN_2026-10-12.md'
MARKER='2026-10-12 ISSUE39 SIGNED16 PAIRED AND V2 U16 DONOR SCREEN'

def hashfile(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*args):subprocess.run(args,cwd=ROOT,check=True)
def py(tool):run(sys.executable,'tools/'+tool+'.py')
def checksum():
    allfiles=sorted((f for f in ROOT.rglob('*') if f.is_file()
                     and '.git' not in f.parts and f.name!='SHA256SUMS.txt'),
                    key=lambda f:str(f.relative_to(ROOT)))
    (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{hashfile(p)}  {p.relative_to(ROOT)}\n' for p in allfiles))

def main():
    py('audit_issue39_signed16_common')
    py('screen_issue39_v2_udiv16_donor')
    x=json.loads(J.read_text());d=json.loads(D.read_text())
    assert x['status']==d['status']=='PASS'
    assert x['total_calls']==54770
    assert x['cases_per_operation_per_profile']==5477
    assert d['routines']['MATH_UDIV16']['cases']==2729
    assert d['routines']['MATH_UMOD16']['cases']==1705
    allprofiles=x['profiles']
    for op in ('MATH_SMOD16','MATH_SDIV16'):
        vals=x['routines'][op]['profiles']
        assert all(abs(vals['v1_balanced']['mean_cycles']-229.47781632280445)<.001 for _ in (0,))
        assert abs(vals['v2_pareto_fast']['mean_cycles']-251.54847544276064)<.001
    for op in ('MATH_UDIV16','MATH_UMOD16'):
        t=d['routines'][op]
        assert all(q['mean_delta_vs_V2']>0 and q['faster']==0 for q in t['all_selectors']),op
    profiles=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
    s=x['routines']['MATH_SMOD16']
    means={p:s['profiles'][p]['mean_cycles'] for p in profiles}
    class_rows=[]
    for cl,count in sorted(s['class_counts'].items()):
        class_rows.append(f"| {cl.replace('_',' ')} | {count:,} | {s['profiles']['v1_balanced']['class_mean_cycles'][cl]:.3f} | {s['profiles']['v2_pareto_fast']['class_mean_cycles'][cl]:.3f} |")
    u=d['routines']['MATH_UDIV16'];m=d['routines']['MATH_UMOD16']
    doc=f'''# Issue #39 — signed16 paired audit and rejected V2 UDIV16/UMOD16 donor gates

**Date:** 2026-10-12. **Status:** independently executable research **PASS**, no arithmetic publication or source promotion. The unsigned DIV/MOD campaign remains open.

## Why the existing 16-bit rankings seemed inconsistent

The earlier `SIGNED_DIVISION_VALIDATION.json` deliberately used a *different*
random seed per profile. Signed SMOD16/SDIV16 numbers from that file were
not a valid paired profile ranking.

`tools/audit_issue39_signed16_common.py` executes all five initialized,
real resident PRGs on **5,477 identical signed N/D operand pairs per API**:
**54,770 complete public API calls** across signed DIV16 and MOD16. It
verifies quotient, remainder, carry and preservation of N/D on every call,
including sign combinations, zero divisors and high-quotient stress.
The same operand SHA is used across all five profiles, with signed-quotient
class means and cycle-vector SHA-256 values in the machine-readable report.

For *both* signed APIs (which share the semantic signed divider):

| Profile | Measured cycles, common signed corpus |
|---|---:|
'''+ '\n'.join(f'| {p} | {means[p]:.6f} |' for p in profiles)+f'''

V2 beats V1 on **{s['v2_minus_v1']['faster']:,}** individual operands, loses on
**{s['v2_minus_v1']['slower']:,}**, and ties on **{s['v2_minus_v1']['equal']:,}**;
yet V1 wins the overall mean because its q=2..31 path is much shorter:

| Absolute signed quotient class | Cases | V1 cycles | V2 cycles |
|---|---:|---:|---:|
'''+ '\n'.join(class_rows)+f'''

Do **not** overwrite `PERFORMANCE.md`'s earlier signed-family
varied-seed correctness measurements with these values; the benchmarks use
distinct and explicitly labeled bases. These paired results support only the
specific deterministic sampled workload.

## Rejected V2 V1-donor 16-bit architecture

`tools/screen_issue39_v2_udiv16_donor.py` transplants the already certified
V1 323-byte UDIV16/UMOD16 core from reference $4200-$4342 to V2
$B000-$B142 in an *ephemeral CPU image*. It relocates the sole absolute
internal JMP. A 13-byte selector at $B200-$B20C selects V1 or V2 using
divisor-high thresholds. The original V2 arithmetic is preserved as fallback,
and **none of these bytes are shipped**.

The screen uses the existing exact same-input unsigned corpus, checks
Q/R/C for UDIV16 and R/C for UMOD16 (because UMOD16 does not promise
a quotient), and verifies both inputs unchanged. The complete lifted V1
core matches its original entry's cycle counts.

| Operation | Shipped V2 | Best gated V1-donor candidate | Outcome |
|---|---:|---:|---|
| UDIV16 | {u['mean_cycles']['V2']:.6f} | {u['best_selectors'][0]['mean_cycles']:.6f} (D-high >= {u['best_selectors'][0]['min_divisor_high']}) | +{u['best_selectors'][0]['mean_delta_vs_V2']:.3f} cycles, rejected |
| UMOD16 | {m['mean_cycles']['V2']:.6f} | {m['best_selectors'][0]['mean_cycles']:.6f} (D-high >= {m['best_selectors'][0]['min_divisor_high']}) | +{m['best_selectors'][0]['mean_delta_vs_V2']:.3f} cycles, rejected |

All tested threshold gates are slower on every input in the measured
corpus. The theoretical zero-dispatch, per-case best-of-two *oracle*
for UDIV16 is {u['ideal_costless_case_oracle_mean']:.6f} cycles and for
UMOD16 {m['ideal_costless_case_oracle_mean']:.6f}; those numbers are **not
achievable measured implementations**. A productive next attempt must
optimize V2's q=2..9 *inside* its native branch or arithmetic dispatch
rather than impose an expensive new universal wrapper. Bounded
low-level mutations require live VICE, source relocation, V5-hybrid
isolation, same-input distributions, OptiSearch differential screening,
and full release qualification before adoption.

## Evidence and release status

- `validation/review/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.json`
- `benchmarks/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.csv`
- `validation/review/ISSUE39_V2_UDIV16_UMOD16_DONOR_SCREEN.json`
- `tools/audit_issue39_signed16_common.py`
- `tools/screen_issue39_v2_udiv16_donor.py`

All five resident PRG binaries, unsigned profile winners, signed routine
selection and published public-entry ABIs are **unchanged**. No new ZP,
table, resident RAM region, or stack depth has been committed. Private
OptiSearch remains outside the repository. Proof is restricted to the
specified input distributions and complete-resident source-executed
instruction counts.
'''
    (ROOT/DOC).write_text(doc)
    msg=f'''{MARKER}
- Published exact same-input signed16 DIV/MOD audit: 5,477 operands per routine x 2 routines x 5 initialized resident profiles = 54,770 verified public machine-code calls. For SMOD16/SDIV16, V1 {means['v1_balanced']:.6f} vs V2 {means['v2_pareto_fast']:.6f} cycles on THIS common signed corpus, not the old profile-varying RNG sample. V2 wins most individual cases but regresses q=2..31 substantially; earlier unsigned-source table rankings remain untouched.
- Rejected V2 UDIV16/UMOD16 donor + 13-byte high-divisor selector at unused research islands. Best UDIV16 candidate {u['best_selectors'][0]['mean_cycles']:.6f} vs V2 {u['mean_cycles']['V2']:.6f}; best UMOD16 {m['best_selectors'][0]['mean_cycles']:.6f} vs V2 {m['mean_cycles']['V2']:.6f}. No candidate has a faster case; no arithmetic or ABI changes published.
- Deterministic proof generator, machine-readable evidence and docs: {DOC}. Issue39 unsigned family remains open.
'''
    for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        p=ROOT/fn;s0=p.read_text()
        if MARKER not in s0:p.write_text(msg+'\n'+s0)
    link=f'- Issue #39 signed16 identical-input and rejected V2 donor gate architecture: [{DOC}]({DOC}) (no code promotion).'
    for fn in ('README.md','USER_MANUAL.md'):
        p=ROOT/fn;s0=p.read_text()
        if link not in s0:p.write_text(s0.rstrip()+'\n\n'+link+'\n')
    p=ROOT/'RELEASE_STATUS.json';state=json.loads(p.read_text())
    state['issue39_signed16_paired_and_v2_donor_screen_2026_10_12']={
        'status':'PASS','report_document':DOC,
        'common_signed_calls':x['total_calls'],
        'operand_pairs_per_api':len(s['class_counts']) and 5477,
        'source_candidate_promoted':False,
        'shipped_prgs_unchanged':True,
        'public_abi_unchanged':True,
        'routine_family_completed':False,
        'signed_paired_report_sha256':hashfile(J),
        'signed_paired_csv_sha256':hashfile(ROOT/'benchmarks/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.csv'),
        'v2_donor_negative_report_sha256':hashfile(D)}
    if isinstance(state.get('documentation'),dict):
        p2=ROOT/'USER_MANUAL.md'
        state['documentation'].update(user_manual_bytes=p2.stat().st_size,
          user_manual_lines=len(p2.read_text().splitlines()),user_manual_sha256=hashfile(p2))
    p.write_text(json.dumps(state,indent=2)+'\n')
    run('make','clean')
    checksum();py('package_audit')
    checksum();py('package_audit')
    py('validate_public_catalog')
    # Audit rewriting the same report is idempotent; fresh package checksums
    # include both new audit JSON files and the generated package JSON.
    checksum();py('package_audit')
    print('ISSUE39 16-BIT RESEARCH EVIDENCE PACKAGE SEALED',flush=True)

if __name__=='__main__':main()
