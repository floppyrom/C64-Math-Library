#!/usr/bin/env python3
"""Finalize issue39 V5 UMOD16 source, common-input ranking and release seals."""
from pathlib import Path
import csv,hashlib,json
from common_corpus_ranking import load_common
R=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
V5='v5_hybrid_lowzp';NAME='MATH_UMOD16'
EXPECTED='6aff56fc151a2bf6037323764f2317c6f3416cf8c181332a5592e31f2cf91f1d'
BASELINE='23833dcaf92d5b69cc16e215e67a38776c6feee6523526d7e5592813ceeb7939'
DOC='docs/ISSUE39_V5_UMOD16_REMAINDER_TRANSPLANT_2026-10-11.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/V5/'resident/math_v5_hybrid_lowzp_game_math.prg')==EXPECTED
for nam,num in [('UNSIGNED_DIVISION_VALIDATION',822050),('SIGNED_DIVISION_VALIDATION',364533)]:
    d=json.loads((R/'validation/review'/f'{nam}.json').read_text())
    assert d['status']=='PASS' and len(d['profiles'])==5 and d['summary']['machine_calls']==num
    assert all(not val['errors'] for pr in d['profiles'].values() for val in pr.values())
    if nam=='UNSIGNED_DIVISION_VALIDATION':
        z=d['profiles'][V5][NAME]
        assert z['cases']==1553 and abs(z['mean_cycles']-192.90534449452673)<1e-7
common=load_common(R)
assert common['total_calls']==136335
metrics=common['routines'][NAME]['metrics']
new=metrics[V5]['mean_cycles']
old=205.02873900293255
assert new==metrics['v2_pareto_fast']['mean_cycles']
assert abs(new-198.61055718475075)<1e-9
assert common['routines']['MATH_UMOD24']['metrics'][V5]['mean_cycles']==common['routines']['MATH_UMOD24']['metrics']['v2_pareto_fast']['mean_cycles']
# Refresh main performance comparison only from identically seeded operands.
p=R/'PERFORMANCE.md';lines=p.read_text().splitlines()
for name,q in common['routines'].items():
    match=[i for i,s in enumerate(lines) if s.startswith('| '+chr(96)+name+chr(96)+' |')]
    assert len(match)==1,(name,match)
    cells=lines[match[0]].split('|')
    for j,prof in enumerate(PROFILES):cells[j+3]=f" {q['metrics'][prof]['mean_cycles']:.6f} "
    lines[match[0]]='|'.join(cells)
p.write_text('\n'.join(lines)+'\n')
# Hybrid headline for 16-bit modulo must share its V1 and V5 operands.
csvfile=R/V5/'HYBRID_PERFORMANCE.csv'
with csvfile.open(newline='') as f:rows=list(csv.DictReader(f))
count=0
for row in rows:
    if row['routine']==NAME:
        v1=metrics['v1_balanced']['mean_cycles']
        row.update(v1_mean_cycles=f'{v1:.6f}',v5_mean_cycles=f'{new:.6f}',
                   improvement_percent=f'{(v1-new)*100/v1:.6f}',
                   provenance='2026-10-11 issue39 identical-input 1705-case V1/V5 benchmark')
        count+=1
assert count==1
with csvfile.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader();w.writerows(rows)
marker='2026-10-11 ISSUE39 V5 UMOD16 REMAINDER-ONLY SOURCE TRANSPLANT'
log=f"""{marker}
- Imported 69-byte V2 UMOD16 remainder-only frontend into the 77 bytes remaining in the same already-unoccupied V5 REG_LOW final page after PR #52 UMOD24. Final combined code: $2F00-$2FF7 (248/256); reference UMOD16 $2FB3-$2FF7; alternate $AFB3-$AFF7. No additional normal ZP or resident PRG file bytes, no stable API relocation.
- V5 UMOD16 identical-input mean {old:.6f}->{new:.6f} cycles (−6.418182, −3.13%); 1,705/1,705 V2 matched per-call cycle values, 1,613 faster than old V5, 92 slower by two cycles. UMOD24, UDIV16 and UDIV24 timing unchanged on 9,035 independently paired controls.
- Full 822,050 all-profile unsigned, 364,533 signed, 136,335 common-input calls; V5 native VICE x64sc old/new 16+16; source reference and alternate 56 public API/mixed-call/ZP confinement certification; standalone/source catalogs, indexes, both changelogs and release seals refreshed.
- Permanent V2/V5 UMOD16 exact timing+output gate in comparable-unsigned CI. Source design is manual transplantation of a V2 frontend (not novel OptiSearch native synthesis); private OptiSearch stays private. Issue39 unsigned family stays unchecked.
- Details: {DOC}
"""
for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
    p=R/fn
    if marker not in p.read_text():p.write_text(log+'\n'+p.read_text())
link=f'- V5 16/24-bit dedicated remainder paths fit within one final-page 256-byte region: {DOC}. Unsigned family campaign remains open.'
for fn in ('README.md','USER_MANUAL.md'):
    p=R/fn
    if link not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+link+'\n')
p=R/'RELEASE_STATUS.json';d=json.loads(p.read_text());d['date']='2026-10-11'
d['reference_prg_sha256']={q:sha(R/q/'resident'/f'math_{q}_game_math.prg') for q in PROFILES}
a=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())
d['alternate_prg_sha256'][V5]=a['output_sha256']
d['hybrid_v5']['reference_prg_sha256']=EXPECTED
d['hybrid_v5']['alternate_prg_sha256']=a['output_sha256']
d['issue39_common_input_unsigned_divmod']['benchmark_sha256']=sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
d['issue39_common_input_unsigned_divmod']['arithmetic_binaries_changed']=True
d['issue39_v5_umod16_remainder_transplant_2026_10_11']={
    'status':'PASS','documentation':DOC,'unsigned_family_completed':False,
    'prior_v5_reference_sha256':BASELINE,'new_v5_reference_sha256':EXPECTED,
    'alternate_v5_reference_sha256':a['output_sha256'],
    'umod16_same_input_calls':1705,'prior_mean_cycles':old,'new_mean_cycles':new,
    'faster_cases':1613,'slower_cases':92,'max_regression_cycles':2,
    'added_code_bytes':69,'joint_umod16_umod24_low_page_code_bytes':248,
    'normal_zp_growth_bytes':0,'resident_file_growth_bytes':0,
    'all_profile_unsigned_calls':822050,'all_profile_signed_calls':364533,'common_input_calls':136335,
    'vice_native_old_new_calls':32,'public_abi_changed':False}
if isinstance(d.get('documentation'),dict):
    u=R/'USER_MANUAL.md'
    d['documentation'].update(user_manual_bytes=u.stat().st_size,user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=sha(u))
p.write_text(json.dumps(d,indent=2)+'\n')
print('ISSUE39 V5 UMOD16 SOURCE TRANSPLANT PUBLICATION PASS')
