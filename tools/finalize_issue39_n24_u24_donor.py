#!/usr/bin/env python3
"""Publish issue39 N24->UDIV24 donor no-gain proof without changing residents."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
REP=R/'validation/review/ISSUE39_N24_U24_DONOR_SCREEN.json'
DOC=R/'docs/ISSUE39_N24_TO_U24_DONOR_SCREEN_2026-10-12.md'
PS=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
MARK='2026-10-12 ISSUE39 N24 TO U24 DONOR NO-GAIN AUDIT'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seal():
    files=sorted((p for p in R.rglob('*') if p.is_file() and '.git' not in p.parts
      and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
      key=lambda p:str(p.relative_to(R)))
    (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in files))
def main():
    report=json.loads(Path(sys.argv[1]).read_text())
    state=json.loads((R/'RELEASE_STATUS.json').read_text())
    assert report['status']=='PASS_RESEARCH_NO_DEFAULT_PROMOTION'
    assert report['compared_pairs']==11580 and report['cpu_calls']==23160
    assert report['abi_errors']==0 and not report['source_or_resident_modified']
    assert report['native_vice_calls']==0
    assert set(report['profiles'])==set(PS)
    rows=[]
    for p in PS:
        image=R/p/'resident'/f'math_{p}_game_math.prg'
        assert report['profiles'][p]['resident_sha256']==sha(image)==state['reference_prg_sha256'][p]
        for op in OPS:
            a=report['profiles'][p]['operations'][f'{op}_0800']
            b=report['profiles'][p]['operations'][f'{op}_0B00']
            assert a==b,(p,op,'origin/branch phase not equivalent')
            assert a['n24_dhi']['mean_delta']>0,(p,op,'unexpected winning wide architecture')
            rows.append(f"| {p} | {op} | {a['n24_d8']['mean_delta']:+.2f} | {a['n24_dhi']['mean_delta']:+.2f} | {a['n16_dhi']['mean_delta']:+.2f} | {a['q0']['mean_delta']:+.2f} |")
    REP.parent.mkdir(parents=True,exist_ok=True)
    REP.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    lines=['# Issue #39 — N24-to-UDIV24 reuse under the 32/16 public contract','',
      '12 October 2026. **Research-only no-gain finding: keep default engines.**','',
      'Manual architecture candidate: when the 32-bit numerator fits in 24 bits,',
      'call the existing 24/24 unsigned producer ($3170) instead of the 32/16',
      'producer. A 30-byte RAM helper saves/restores D2 and R2, zeros D2 for',
      'the call and clears Q3. It retains full Q32/R16/carry, untouched high',
      'remainder, dividend/divisor, sentinels and stack behavior for both public',
      '32/16 aliases. This is a dependent helper, **not** a standalone divider.','',
      'All five exact resident images SHA-pinned against RELEASE_STATUS, two',
      'caller RAM placements ($0800 and $0B00), 11,580 paired operand tests,',
      '23,160 complete 6502 executions, zero observed arithmetic/ABI mismatch.',
      'The 30-byte helper uses four temporary bytes of return/data stack and',
      'no new persistent normal zero-page space. No native VICE claim and no',
      'real C64 VIC/REU contention model in the cycle measurements.','',
      '| Profile | Public API | N24/D8 delta | N24/D>=256 delta | N16/D>=256 delta | Q=0 delta |',
      '|---|---|---:|---:|---:|---:|']+rows+['',
      'Values are mean **candidate minus current public entry** cycles;',
      'positive means slower. Genuine 24-bit numerators with D>=256 lose',
      'in every profile in the screened class. Some special Q=0 and N16',
      'inputs win, but the separately released 12-byte N16 opt-in helper',
      'already addresses the latter without using the bulkier 24-bit core.',
      'No default or public ABI change is justified by this architecture.',
      '',
      'Exact per-class faster/slower counts, hashes, edge/divide-zero tests',
      'and two-map proof are in '+str(REP.relative_to(R))+'.',
      'Re-run on current checked-out residents:',
      'python3 tools/screen_issue39_n24_u24_donor.py --out /tmp/n24.json',
      '',
      'This is one **manual architecture** rejection, not an exhaustive',
      'OptiSearch 24-bit architecture result, proof of mathematical timing',
      'optimality, or completion of issue #39. The family remains OPEN.']
    DOC.write_text('\n'.join(lines)+'\n')
    log=f"""{MARK}
- Five exact-profile research screen of N24->resident UDIV24 reuse for 32/16 quotient and modulo: 30-byte RAM helper, two RAM maps, 11,580 identical operands / 23,160 complete CPU calls, zero arithmetic/Q/R/C/input/SP/sentinel errors.
- N24 with D>=256 loses in all five profiles on 128 seeded operands per API; Q0/N16 niche wins do not justify universal promotion and 12-byte N16 opt-in is already available. Research only, no production code, API, ZP or PRG changes. Native VICE not claimed.
- Source-backed JSON, docs, release-status and checksums; issue #39 unsigned family remains OPEN. {DOC.relative_to(R)}
"""
    for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        f=R/name
        if MARK not in f.read_text():f.write_text(log+'\n'+f.read_text())
    for name in ('README.md','USER_MANUAL.md'):
        f=R/name
        line='- Issue39 N24->UDIV24 donor no-gain research: '+str(DOC.relative_to(R))+'. Existing 32/16 defaults retained.'
        if line not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+line+'\n')
    state['issue39_n24_u24_architecture_screen_2026_10_12']={
      'status':'PASS_RESEARCH_NO_DEFAULT_PROMOTION',
      'source':'tools/screen_issue39_n24_u24_donor.py',
      'validation':str(REP.relative_to(R)),
      'validation_sha256':sha(REP),
      'documentation':str(DOC.relative_to(R)),
      'paired_inputs':11580,'cpu_calls':23160,
      'native_vice_calls':0,'profile_count':5,
      'candidate_bytes':30,'temporary_stack_bytes':4,
      'released_residents_changed':False,'public_api_changed':False,
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
    print('ISSUE39 N24 U24 research sealed',flush=True)
if __name__=='__main__':main()
