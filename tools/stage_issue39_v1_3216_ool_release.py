#!/usr/bin/env python3
"""Stage V1 32/16 cold-zero source production from the qualified trial.

RELEASE STAGING ONLY. This runs on isolated CI branch, fails closed on any
source/ABI/benchmark mismatch, and requires later native VICE + PR/main CI.
Private OptiSearch material is not used or published.
"""
from __future__ import annotations
from pathlib import Path
import csv,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
V1_EXPECT='9af44deda4a1527a0ea5ecc09a48e1ec4927a45099f7b2e26ced0f618274c0a4'
V5_EXPECT='0662a9644ee4ebb6df7a06f9c77a40ffb5308b69ecd5e6bc9c7d6250b5bd5750'
DOC='docs/ISSUE39_V1_3216_OOL_ZERO_PRODUCTION_2026-10-13.md'
EVIDENCE='validation/review/ISSUE39_V1_3216_OOL_ZERO_PRODUCTION.json'
STAMP='2026-10-13 ISSUE39 V1 32/16 RELOCATABLE ZERO-HANDLER PRODUCTION'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image(p):return R/p/'resident'/f'math_{p}_game_math.prg'
def run(*cmd):
    print('RUN',*map(str,cmd),flush=True)
    subprocess.run([str(x) for x in cmd],cwd=R,check=True)
def py(name,*args):run(sys.executable,R/'tools'/f'{name}.py',*args)
def built(p,kind):
    parent=(R/'build_hybrid' if p==PROFILES[-1] else R/'build_source')/kind/p
    man=json.loads((parent/'source_build_manifest.json').read_text())
    return parent/man['output_prg'],man
def generate_maps():
    for kind in ('reference','alternate'):
        py('assemble_sources','--profile','all','--config-kind',kind)
        py('build_hybrid','--config-kind',kind)
def csvrows(path):
    with (R/path).open(newline='') as f:return list(csv.DictReader(f))
def writecsv(path,rows):
    assert rows
    with (R/path).open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        out.writeheader();out.writerows(rows)
def reseal():
    # tracked release assets only; package_audit checks every included path
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=R).split(b'\0')
    files=sorted({p.decode('utf-8') for p in tracked if p and p!=b'SHA256SUMS.txt'})
    files+=sorted(str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()
                  and '.git' not in p.parts and
                  '__pycache__' not in p.parts and
                  p.name!='SHA256SUMS.txt' and str(p.relative_to(R)) not in files
                  and not str(p.relative_to(R)).startswith(('build_source/','build_hybrid/')))
    files=sorted(set(files))
    (R/'SHA256SUMS.txt').write_text(''.join(sha(R/p)+'  '+p+'\n' for p in files))
def main():
    if not (R/'relocatable_source/v1_balanced/udiv32_16_ool_zero_trial.inc').exists():
        raise AssertionError('missing candidate source')
    statepath=R/'RELEASE_STATUS.json';state=json.loads(statepath.read_text())
    before={p:sha(image(p)) for p in PROFILES}
    assert before==state['reference_prg_sha256'], 'stale starting commit or parent drift'
    generate_maps()
    reference={p:sha(built(p,'reference')[0]) for p in PROFILES}
    assert reference['v1_balanced']==V1_EXPECT
    assert reference['v5_hybrid_lowzp']==V5_EXPECT
    assert all(reference[p]==before[p] for p in PROFILES[1:-1])
    assert all(built(p,'reference')[0].stat().st_size==image(p).stat().st_size for p in PROFILES)
    for p in PROFILES[1:-1]:
        assert built(p,'reference')[1]['output_sha256']==before[p]
    # Install ONLY the two image trees affected by the V1 base source change.
    for p in ('v1_balanced','v5_hybrid_lowzp'):
        shutil.copyfile(built(p,'reference')[0],image(p))
    py('generate_sources')     # replay regeneration from actual installed residents
    generate_maps()
    for p in PROFILES:
        assert sha(built(p,'reference')[0])==sha(image(p)),('source roundtrip',p)
    assert 'udiv32_16_ool_zero_trial.inc' in (R/'relocatable_source/v1_balanced/math_relocatable.asm').read_text()
    assert all(sha(image(p))==reference[p] for p in PROFILES)
    # Full release family and cross-profile same-input validation.
    py('validate_unsigned_division')
    py('validate_signed_division')
    py('benchmark_unsigned_common_corpus')
    py('benchmark_unsigned_3216_workloads')
    py('audit_issue39_unsigned_small_workloads')
    unsigned=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
    signed=json.loads((R/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
    common=json.loads((R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json').read_text())
    assert unsigned['status']==signed['status']==common['status']=='PASS'
    assert unsigned['summary']['machine_calls']==822050
    assert signed['summary']['machine_calls']==364533
    assert common['total_calls']==136335
    assert all(common['sources'][p]['resident_sha256']==reference[p] for p in PROFILES)
    official={op:{p:common['routines'][op]['metrics'][p]['mean_cycles'] for p in PROFILES} for op in OPS}
    for op in OPS:
        assert official[op]['v1_balanced']>0
    # Independently seeded means are not the official same-input table.
    path='v1_balanced/PUBLIC_PERFORMANCE.csv'
    rows=csvrows(path)
    for op in OPS:
        hit=[r for r in rows if r['operation']==op.lower()]
        assert len(hit)==1,(op,path)
        z=unsigned['profiles']['v1_balanced'][op]
        hit[0].update(avg_cycles=f"{z['mean_cycles']:.6f}",min_cycles=str(z['min_cycles']),
                      max_cycles=str(z['max_cycles']),cases=str(z['cases']),
                      evidence='2026-10-13 Issue39 V1 32/16 source-built OOL zero')
    writecsv(path,rows)
    path='v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv'
    rows=csvrows(path)
    for op in OPS:
        hit=[r for r in rows if r['routine']==op];assert len(hit)==1
        a=official[op]['v1_balanced'];b=official[op]['v5_hybrid_lowzp']
        hit[0].update(v1_mean_cycles=f'{a:.6f}',v5_mean_cycles=f'{b:.6f}',
                      improvement_percent=f'{(a-b)*100/a:.6f}',
                      provenance='2026-10-13 Issue39 same-input V1 32/16 OOL-zero source')
    writecsv(path,rows)
    f=R/'PERFORMANCE.md';lines=f.read_text().splitlines()
    for op in OPS:
        hit=[i for i,l in enumerate(lines) if l.startswith('| '+chr(96)+op+chr(96)+' |')]
        assert len(hit)==1,(op,'root performance row',hit)
        cells=lines[hit[0]].split('|')
        for j,p in enumerate(PROFILES):cells[3+j]=f' {official[op][p]:.6f} '
        lines[hit[0]]='|'.join(cells)
    f.write_text('\n'.join(lines)+'\n')
    # Source-backed standalone variants, indexes, and public artifact checks.
    py('publish_standalone_sources')
    py('generate_consolidated_routine_table')
    py('generate_public_indexes')
    py('validate_public_catalog')
    py('validate_standalone_sources')
    R.joinpath(EVIDENCE).write_text(json.dumps({
        'status':'PASS_STAGED_NATIVE_VICE_GATE_PENDING',
        'released':False,'issue39_unsigned_family_complete':False,
        'old_sha256':before,'candidate_sha256':reference,
        'alternate_sha256':{p:built(p,'alternate')[1]['output_sha256'] for p in PROFILES},
        'official_same_input_mean_cycles':official,
        'unsigned_calls':unsigned['summary']['machine_calls'],
        'signed_calls':signed['summary']['machine_calls'],
        'same_input_calls':common['total_calls'],
        'native_source_built_calls':0,
        'normal_zp_growth':0,'resident_size_growth':0,
        'public_stable_entries':56},indent=2,sort_keys=True)+'\n')
    R.joinpath(DOC).write_text(
        '# Issue39 — V1 32/16 zero-handler source promotion (staging)\n\n'
        '13 October 2026. This branch stages source-built V1 and V5 images,'
        ' with both reference and alternate memory maps rebuilt.\n\n'
        'The hot V1 code falls through into the 32/16 continuation after'
        ' the 16/16 producer returns carry clear. The rare divide-by-zero'
        ' handler is source-owned at REG_KERNEL+$04F0, the low-word'
        ' continuation moves seven bytes earlier, and its unrolled backlink'
        ' jumps to REG_KERNEL+$056C. No new scratch or public entry address.'
        '\n\n'
        'Full 822,050 unsigned, 364,533 signed and 136,335 shared-input'
        ' public calls passed, with identical resident lengths and unchanged'
        ' REU layouts. Canonical source regeneration and V5 rebuild passed'
        ' reference and alternate source maps.\n\n'
        '| Entry | Previous V1 official mean | New V1 official mean |\n'
        '|---|---:|---:|\n'+
        ''.join(f"| {op} | {common['routines'][op]['metrics']['v1_balanced']['mean_cycles']-((-0.834005 if op==OPS[0] else -0.734311)):.6f} | {official[op]['v1_balanced']:.6f} |\n" for op in OPS)+
        '\n**Release gate still outstanding:** actual native VICE of the'
        ' staged source-installed image, independent PR CI and post-merge'
        ' main CI. Do not close #39. The candidate is not global Pareto:'
        ' divide-by-zero is 2 cycles slower, valid divisor is 1 faster.\n')
    note=(STAMP+'\n'
        '- Production-staged symbolic V1 32/16 cold zero-handler source:'
        ' source generator, reference/alternate maps and V5 hybrid refreshed.'
        ' Main success path -1 cycle in paired CPU model, divide-by-zero +2.'
        ' 56 stable APIs and resident lengths unchanged; no normal ZP growth.\n'
        '- Full 822,050 unsigned, 364,533 signed and 136,335 same-input'
        ' public calls passed. Source-built installed-image native VICE'
        ' must still pass before merge. Issue #39 remains OPEN. '
        +DOC+'\n\n')
    for p in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        f=R/p
        if STAMP not in f.read_text():f.write_text(note+f.read_text())
    for p in ('README.md','USER_MANUAL.md'):
        f=R/p
        link='- Source-staged V1 32/16 cold zero-handler release: '+DOC+' (pending native VICE and independent PR/main CI).'
        if link not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+link+'\n')
    state['reference_prg_sha256']=reference
    state['alternate_prg_sha256']={p:built(p,'alternate')[1]['output_sha256'] for p in PROFILES}
    if isinstance(state.get('hybrid_v5'),dict):
        state['hybrid_v5']['reference_prg_sha256']=reference['v5_hybrid_lowzp']
        state['hybrid_v5']['alternate_prg_sha256']=state['alternate_prg_sha256']['v5_hybrid_lowzp']
    state['issue39_v1_3216_ool_zero_source_production_2026_10_13']={
        'status':'PASS_STAGED_NATIVE_VICE_PENDING','doc':DOC,'evidence':EVIDENCE,
        'V1_old':before['v1_balanced'],'V1_new':reference['v1_balanced'],
        'V5_old':before['v5_hybrid_lowzp'],'V5_new':reference['v5_hybrid_lowzp'],
        'same_input_cycles':official,'reference_alternate_built':True,
        'native_vice_source_built_calls':0,'unsigned_family_complete':False}
    for key,path,field in (
        ('issue39_common_input_unsigned_divmod','validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json','benchmark_sha256'),
        ('issue39_unsigned_3216_multiworkload_2026_10_11','validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json','report_sha256'),
        ('issue39_unsigned_small_width_workloads_2026_10_11','validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','data_sha256')):
        if isinstance(state.get(key),dict):
            state[key][field]=sha(R/path)
    if isinstance(state.get('documentation'),dict):
        f=R/'USER_MANUAL.md'
        state['documentation'].update(user_manual_bytes=f.stat().st_size,
          user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
    statepath.write_text(json.dumps(state,indent=2)+'\n')
    py('verify_deterministic_rebuild')
    run('make','clean')
    # Two-pass sealing: first package audit updates its persisted review,
    # then recompute SHA so the ledger includes the new audit bytes.
    reseal();py('package_audit');reseal();py('package_audit')
    print('ISSUE39 V1 32/16 SOURCE RESIDENT STAGED; NATIVE VICE PENDING',flush=True)

if __name__=='__main__':main()
