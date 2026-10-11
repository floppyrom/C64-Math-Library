#!/usr/bin/env python3
"""Issue #39 V2 UMOD8 D24 release staging on an isolated PR branch.

Consumes the SHA-qualified full-resident qualification; never promotes a
candidate unless reference/alternate builds, old/new arithmetic and V5 donor
isolation pass. Run in a fresh GitHub Actions checkout, not on main.
"""
from __future__ import annotations
from pathlib import Path
import csv, hashlib, json, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OP='MATH_UMOD8'
TAG='2026-10-12 ISSUE39 V2 GUARDED D24 REMAINDER-ONLY UMOD8'
DOC='docs/ISSUE39_V2_UMOD8_D24_RELEASE_2026-10-12.md'
AUDIT='validation/review/ISSUE39_V2_UMOD8_D24_CANDIDATE.json'
OLD='e1e828a2748099b6f05b224b98ca26960d120f8ba886c4906e8b52bdb8b4fbcd'
NEW='28fc6e653a05b170a80cd7eb50636d755895c5ebb7aab133262ed560fa465dd6'

def run(*args):
    print('RUN', ' '.join(map(str,args)), flush=True)
    subprocess.run([str(x) for x in args],cwd=ROOT,check=True)
def py(script,*args):run(sys.executable,'tools/'+script+'.py',*args)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(path):
    with (ROOT/path).open(newline='') as f:return list(csv.DictReader(f))
def save_csv(path,rs):
    p=ROOT/path
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n')
        w.writeheader();w.writerows(rs)
def checksum():
    files=sorted((p for p in ROOT.rglob('*') if p.is_file()
                   and '.git' not in p.parts
                   and p.name!='SHA256SUMS.txt'),
                 key=lambda p:str(p.relative_to(ROOT)))
    (ROOT/'SHA256SUMS.txt').write_text(''.join(
       f'{digest(p)}  {p.relative_to(ROOT)}\n' for p in files))

def main():
    # Build and certify against old shipped binary BEFORE installing candidate.
    assert digest(ROOT/'v2_pareto_fast/resident/math_v2_pareto_fast_game_math.prg') in (OLD,NEW)
    py('generate_sources')
    for kind in ('reference','alternate'):
        py('assemble_sources','--profile','v2_pareto_fast','--config-kind',kind)
    py('build_hybrid','--config-kind','reference')
    py('qualify_issue39_v2_umod8_candidate')
    cert=json.loads((ROOT/AUDIT).read_text())
    assert cert['status']=='PASS' and cert['paired_calls']==131072
    assert cert['new_resident_sha256']==NEW and cert['old_resident_sha256']==OLD
    assert cert['v5_resident_byte_identical'] and cert['reference_and_alternate_relocation_validated']
    assert cert['faster']==58290 and cert['equal']==504 and cert['slower']==6742

    # Install only the tested V2 image. No other profile's shipped PRG changes.
    newimage=ROOT/'build_source/reference/v2_pareto_fast/math_v2_pareto_fast_source_built.prg'
    target=ROOT/'v2_pareto_fast/resident/math_v2_pareto_fast_game_math.prg'
    shutil.copyfile(newimage,target)
    assert digest(target)==NEW
    # Source regeneration now consumes the *new* installed resident. Confirm
    # symbolic D24 overlay wins over decoded provenance and remains deterministic.
    py('generate_sources')
    for kind in ('reference','alternate'):
        py('assemble_sources','--profile','all','--config-kind',kind)
        py('build_hybrid','--config-kind',kind)
    assert digest(ROOT/'build_source/reference/v2_pareto_fast/math_v2_pareto_fast_source_built.prg')==NEW
    assert digest(ROOT/'build_hybrid/reference/v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg')==digest(ROOT/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg')
    py('qualify_issue39_v2_umod8_candidate')

    # Update independent and common-input measured vectors (not inferred from
    # the D24 full-domain mean); 5-profile unsigned correctness is the gate.
    py('validate_unsigned_division')
    py('benchmark_unsigned_common_corpus')
    py('audit_issue39_unsigned_small_workloads')
    py('benchmark_unsigned_3216_workloads')  # baseline-independent provenance follows new V2 SHA
    full=json.loads((ROOT/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
    common=json.loads((ROOT/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
    assert full['status']=='PASS' and full['summary']['machine_calls']==822050
    assert common['status']=='PASS' and common['total_calls']==136335
    assert common['sources']['v2_pareto_fast']['resident_sha256']==NEW
    measured=full['profiles']['v2_pareto_fast'][OP]
    assert measured['errors']==0 and measured['cases']==1313
    shared=common['routines'][OP]['metrics']['v2_pareto_fast']

    # Update profile-local published measurement and V3 comparison convenience
    # row, without pretending full-domain and independent sampled means coincide.
    p='v2_pareto_fast/PUBLIC_PERFORMANCE.csv';rs=rows(p)
    match=[x for x in rs if x['operation']=='math_umod8']
    assert len(match)==1
    match[0].update(avg_cycles=f"{measured['mean_cycles']:.6f}",
      min_cycles=str(measured['min_cycles']),max_cycles=str(measured['max_cycles']),
      evidence='2026-10-12 issue39 V2 D24 full-resident exhaustive paired proof',
      )
    save_csv(p,rs)
    p='v3_reu_512k/PUBLIC_PERFORMANCE.csv';rs=rows(p)
    match=[x for x in rs if x['operation']=='umod8']
    assert len(match)==1
    match[0]['v2_pareto_fast_cycles']=f"{measured['mean_cycles']:.6f}"
    save_csv(p,rs)

    # Update V2 source ownership and extraction manifest.
    p='v2_pareto_fast/resident/SEGMENTS.csv';rs=rows(p)
    matches=[x for x in rs if x['segment']=='umod8_guard_d24']
    assert len(matches)<=1
    if not matches:
        entry={k:'' for k in rs[0]}
        entry.update(segment='umod8_guard_d24',load_address='$5323',bytes='101',
                     file='integrated PRG',purpose='V2-only source-backed guarded D>=24 remainder-only UMOD8')
        rs.append(entry)
    save_csv(p,rs)

    # Regenerate the exact shipped per-entry mirror and benchmark catalog
    # AFTER the reference executable is installed, never from a proposal.
    py('publish_standalone_sources')
    py('generate_consolidated_routine_table')
    py('generate_public_indexes')
    py('validate_public_catalog')
    py('validate_standalone_sources')
    lines=(ROOT/'PERFORMANCE.md').read_text().splitlines()
    inds=[i for i,x in enumerate(lines) if x.startswith('| '+chr(96)+OP+chr(96)+' |')]
    assert len(inds)==1
    cols=lines[inds[0]].split('|')
    for i,profile in enumerate(PROFILES):
        cols[3+i]=f" {common['routines'][OP]['metrics'][profile]['mean_cycles']:.6f} "
    lines[inds[0]]='|'.join(cols)
    (ROOT/'PERFORMANCE.md').write_text('\n'.join(lines)+'\n')

    blurb=(f'- Issue #39 V2 source-backed 101-byte D>=24 UMOD8: '
           f'[qualification and resource/ABI contract]({DOC}); '
           'V5 remains byte-for-byte unchanged, no additional ZP.')
    for name in ('README.md','USER_MANUAL.md'):
        f=ROOT/name
        s=f.read_text()
        if blurb not in s:f.write_text(s.rstrip()+'\n\n'+blurb+'\n')
    detail=f'''# Issue #39 — V2 D>=24 guarded remainder-only UMOD8

Date: 2026-10-12. Status: validated candidate for PR #65; unsigned DIV/MOD campaign remains open.

The stable V2 \`MATH_UMOD8\` address stays $3200. A 3-byte JMP reaches a
**101-byte** independently symbolic V2 helper at \`REG_KERNEL+$1323\`
(reference $5323..$5387); under D<24 it falls back into the *original*
public V2 wrapper at \`MATH_UMOD8+3\`, including the certified private core
and its self-modifying small-divisor tail. For D>=24, ten compare/subtract
stages calculate remainder without allocating extra ZP, writing Q, or
modifying N/D. The helper reuses verified former zero bytes between UMUL8
and UMUL16; resident length and API do not change.

### Full-domain paired results

On exactly 65,536 N/D pairs, 131,072 complete resident 6502 executions:
- Original V2 **64.819153** cycles, optimized **52.204453** (-19.46%).
- 58,290 faster, 504 identical, 6,742 slower; worst +15 cycles.
- All remainder, divide-by-zero carry, all Q bytes, N/D/high-R
  sentinel and historical parent-hash checks passed.
- A separate native VICE x64sc (reported 3.10) test executed **4,096**
  complete old/new V2-resident calls, including MATH_INIT, with no errors.
- Original resident SHA-256: \`{OLD}\`.
- New resident SHA-256: \`{NEW}\`.
- Exact guard helper SHA-256:
  \`6a733be6ca05992b46585c8443ae6ce7b21a075bfdfdfe34cf844e748b8f6f29\`.

Reference and alternate relocations pass. V5's hybrid builder normalizes
the first V2 donor entry instruction **in its transient import image only**,
before reachability tracing; V5's shipped source and final resident remain
byte-identical (SHA-256 \`bed1ee986857d045d452036d78d0d6cbdc078dbc3407f8a860a8fd54f8395fa2\`).
Custom Pareto inherits this builder and must retain the normal validation.

### Proper use and qualification

Use the entire V2 resident for a fully supported stable API, including
\`MATH_INIT\` and matching \`math_api.inc\`. The exact individually named
\`v2_pareto_fast/standalone/mod_u8_u8_u8.asm\` is an executable *audit mirror*,
not a dependency-free drop-in: the V2 fallback wrapper and
\`REG_KERNEL+$1200\` remainder engine plus scratch ZP are required below D=24.
The symbolic \`relocatable_source/v2_pareto_fast/v2_umod8_guard_d24.inc\`
is the liftable overlay in a matching resident/source layout.

The 52.204 figure uses exhaustive 8x8 inputs; the separate common-corpus
performance rank uses the exact same operands for all profiles. No new stable
API, ordinary ZP bytes, stack reservation, REU payload or PRG span were added.
OptiSearch native records are not attributed as public-entry gains without
their own transplant and ABI/placement qualification.

Evidence: \`{AUDIT}\`, \`validation/review/UNSIGNED_DIVISION_VALIDATION.json\`,
\`validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json\`, native VICE
handoff on issue #39, and independent PR/main CI checks.
'''
    (ROOT/DOC).write_text(detail)
    msg=f'''{TAG}
- V2 UMOD8 public ABI stable, source-backed 101-byte D>=24 guard at REG_KERNEL+$1323; preserves Q/N/D, upper R and divide-by-zero carry. Ten inline subtract/compare stages; original fallback retained for smaller divisors. No normal ZP, stack, resident PRG length or REU growth.
- 131,072 exhaustive historical parent/new complete-resident CPU calls: 64.819153→52.204453 mean cycles (-19.46%), 58,290 faster / 504 equal / 6,742 slower, worst +15 cycles. 4,096 independent native VICE old/new full-resident calls passed.
- V5 donor guard isolation restored certified identical V5 output; alternate relocation and five-profile unsigned correctness verified. Source mirrors, common-input benchmark catalog, documentation, release status and checksums updated.
- Original V2 parent SHA {OLD}; new resident {NEW}. This is not universal Pareto dominance. Unsigned DIV/MOD family campaign is still open; see {DOC}.
'''
    for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        p=ROOT/name;s=p.read_text()
        if TAG not in s:p.write_text(msg+'\n'+s)

    # Release metadata uses actual source/binary hashes, never guessed values.
    statusp=ROOT/'RELEASE_STATUS.json';state=json.loads(statusp.read_text())
    state['date']='2026-10-12'
    state['reference_prg_sha256']={p:digest(ROOT/p/'resident'/f'math_{p}_game_math.prg') for p in PROFILES}
    state['alternate_prg_sha256']={p:json.loads((ROOT/'build_source/alternate'/p/'source_build_manifest.json').read_text())['output_sha256'] for p in PROFILES[:4]}
    state['alternate_prg_sha256']['v5_hybrid_lowzp']=json.loads((ROOT/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
    state['issue39_v2_umod8_d24_2026_10_12']={
      'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
      'previous_v2_sha256':OLD,'new_v2_sha256':NEW,'public_abi_changed':False,
      'normal_zp_growth':0,'stack_growth':0,'resident_prg_growth':0,
      'source_helper_bytes':101,'guard_min_divisor':24,
      'paired_complete_resident_cpu_calls':131072,'native_vice_old_new_calls':4096,
      'full_input_old_mean':64.81915283203125,
      'full_input_new_mean':52.20445251464844,'max_case_regression_cycles':15,
      'independent_v2_profile_mean':measured['mean_cycles'],
      'same_input_v2_mean':shared['mean_cycles'],
      'v5_resident_unchanged':True,
      'all_profile_unsigned_calls':822050,'same_input_calls':136335,
      'certificate_sha256':digest(ROOT/AUDIT)}
    if isinstance(state.get('issue39_unsigned_3216_multiworkload_2026_10_11'),dict):
        state['issue39_unsigned_3216_multiworkload_2026_10_11']['report_sha256']=digest(ROOT/'validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json')
        state['issue39_unsigned_3216_multiworkload_2026_10_11']['revalidated_against_v2_d24_resident_sha256']=NEW
    for key,filepath,propertyname in (
      ('issue39_unsigned_small_width_workloads_2026_10_11','validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','data_sha256'),
      ('issue39_common_input_unsigned_divmod','validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json','benchmark_sha256')):
      if isinstance(state.get(key),dict):state[key][propertyname]=digest(ROOT/filepath)
    if isinstance(state.get('documentation'),dict):
        u=ROOT/'USER_MANUAL.md'
        state['documentation'].update(user_manual_bytes=u.stat().st_size,
          user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=digest(u))
    statusp.write_text(json.dumps(state,indent=2)+'\n')

    # Prepare required deterministic evidence, then seal package without
    # build artifacts/cache pollution. SHA256SUMS covers the final generated
    # audit JSON; repeat checksum/audit once to reach a stable fixed point.
    py('verify_deterministic_rebuild')
    run('make','clean')
    for i in range(3):
        checksum()
        py('package_audit')
        if all(line.split('  ',1)[0]==digest(ROOT/line.split('  ',1)[1].strip())
              for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines()):
            break
    else:raise AssertionError('package audit/checksum did not stabilize')
    py('validate_public_catalog')
    py('validate_standalone_sources')
    checksum()
    py('package_audit')
    print('ISSUE39 V2 UMOD8 RELEASE STAGING PASS',NEW,flush=True)

if __name__=='__main__':
    main()
