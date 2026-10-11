#!/usr/bin/env python3
"""Finalize issue #39 V5 UMOD24 remainder-only source transplant publication."""
from pathlib import Path
import csv,hashlib,json
from common_corpus_ranking import load_common
R=Path(__file__).resolve().parents[1]
NAMES=('MATH_UMOD24',)
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
V5='v5_hybrid_lowzp'
EXPECTED='23833dcaf92d5b69cc16e215e67a38776c6feee6523526d7e5592813ceeb7939'
OLD='d3b654f56f7ddfe26ce7130d5e925fdde85e41875e7da4bcd5aafe62440483a7'
DOC='docs/ISSUE39_V5_UMOD24_REMAINDER_TRANSPLANT_2026-10-11.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/V5/'resident/math_v5_hybrid_lowzp_game_math.prg')==EXPECTED
for key,calls in [('UNSIGNED_DIVISION_VALIDATION',822050),('SIGNED_DIVISION_VALIDATION',364533)]:
    z=json.loads((R/'validation/review'/f'{key}.json').read_text())
    assert z['status']=='PASS' and z['summary']['machine_calls']==calls
    assert len(z['profiles'])==5 and all(not e['errors'] for pr in z['profiles'].values() for e in pr.values())
unsigned=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
assert unsigned['profiles'][V5]['MATH_UMOD24']['cases']==1553
assert abs(unsigned['profiles'][V5]['MATH_UMOD24']['mean_cycles']-203.296200901481)<1e-7
common=load_common(R)
assert common['total_calls']==136335 and len(common['routines'])==11
z=common['routines']['MATH_UMOD24']
old_v1=z['metrics']['v1_balanced']['mean_cycles']
new_v5=z['metrics'][V5]['mean_cycles']
v2=z['metrics']['v2_pareto_fast']['mean_cycles']
assert abs(new_v5-207.49066323245333)<1e-9 and new_v5==v2
assert abs(old_v1-276.590470)<0.000002
# The five-profile public table is comparative: use a single shared input corpus.
perf=R/'PERFORMANCE.md'
lines=perf.read_text().splitlines()
for name,info in common['routines'].items():
    match=[i for i,line in enumerate(lines) if line.startswith('| '+chr(96)+name+chr(96)+' |')]
    assert len(match)==1,(name,match)
    cells=lines[match[0]].split('|')
    for i,p in enumerate(PROFILES):
        cells[i+3]=f" {info['metrics'][p]['mean_cycles']:.6f} "
    lines[match[0]]='|'.join(cells)
perf.write_text('\n'.join(lines)+'\n')
# The old V5 HYBRID_PERFORMANCE row had mixed-seed V1/V5 averages.
f=R/V5/'HYBRID_PERFORMANCE.csv'
with f.open(newline='') as h:rows=list(csv.DictReader(h))
matched=0
for row in rows:
    if row['routine']=='MATH_UMOD24':
        row['v1_mean_cycles']=f"{old_v1:.6f}"
        row['v5_mean_cycles']=f"{new_v5:.6f}"
        row['improvement_percent']=f"{(old_v1-new_v5)*100/old_v1:.6f}"
        row['provenance']='2026-10-11 issue39 identical-input 1553-case V1/V5 same-corpus benchmark'
        matched+=1
assert matched==1
with f.open('w',newline='') as h:
    w=csv.DictWriter(h,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader();w.writerows(rows)
marker='2026-10-11 ISSUE39 V5 UMOD24 REMAINDER-ONLY SOURCE TRANSPLANT'
msg=f"""{marker}
- Imported existing V2 179-byte q=0/q=1 remainder-only frontend into V5's previously free REG_LOW final page, reference $2F00-$2FB2 and alternate $AF00-$AFB2. Preserve full public modulo remainder/carry/input semantics with no new normal ZP, no PRG span growth, and unchanged UDIV24.
- Identical-input UMOD24 V5 mean 214.991629 -> {new_v5:.6f} cycles (3.49% faster), exactly matches V2/V3/V4 on all 1,553 calls. 914 faster, 375 slower (max +7 cycles); explicitly accepted mean/fast-exit trade-off, 179 newly occupied code bytes. Other V5 unsigned API means unchanged.
- Native VICE x64sc paired 16+16 calls; 9,716 old/new paired public calls; V5 164,410 unsigned and 36,273 signed regression calls; full all-profile 822,050 unsigned/364,533 signed and 136,335 common-input validation; source/alternate builds, mirrors, stable 56-entry ABI, package/checksums requalified.
- Permanent exact V2/V5 output/cycle-parity regression in tools/validate_v5_umod24_frontend.py. Public performance ranks use only common-input corpora. No private OptiSearch code published; full unsigned campaign remains unchecked.
- Detail: {DOC}
"""
for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
    p=R/name
    if marker not in p.read_text():p.write_text(msg+'\n'+p.read_text())
link=f'- Issue39 V5 dedicated 24-bit remainder frontend (zero extra ZP; 179 code bytes): {DOC}. Unsigned campaign remains open.'
for name in ('README.md','USER_MANUAL.md'):
    p=R/name
    if link not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+link+'\n')
p=R/'RELEASE_STATUS.json';status=json.loads(p.read_text());status['date']='2026-10-11'
status['reference_prg_sha256']={q:sha(R/q/'resident'/f'math_{q}_game_math.prg') for q in PROFILES}
m=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())
status['alternate_prg_sha256'][V5]=m['output_sha256']
status['hybrid_v5']['reference_prg_sha256']=EXPECTED
status['hybrid_v5']['alternate_prg_sha256']=m['output_sha256']
status['issue39_common_input_unsigned_divmod']['benchmark_sha256']=sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
status['issue39_common_input_unsigned_divmod']['arithmetic_binaries_changed']=True
status['issue39_v5_umod24_remainder_transplant_2026_10_11']={
    'status':'PASS','documentation':DOC,'unsigned_family_completed':False,
    'prior_v5_reference_sha256':OLD,'new_v5_reference_sha256':EXPECTED,
    'alternate_v5_sha256':m['output_sha256'],
    'same_input_umod24_calls':1553,'prior_mean_cycles':214.99162910495815,
    'new_mean_cycles':new_v5,'faster_cases':914,'slower_cases':375,
    'maximum_regression_cycles':7,'added_used_code_bytes':179,
    'normal_zp_growth_bytes':0,'resident_file_growth_bytes':0,
    'all_profile_unsigned_calls':822050,'all_profile_signed_calls':364533,
    'common_input_calls':136335,'native_x64sc_paired_calls':32,'public_abi_changed':False}
if isinstance(status.get('documentation'),dict):
    u=R/'USER_MANUAL.md'
    status['documentation'].update(user_manual_bytes=u.stat().st_size,
        user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=sha(u))
p.write_text(json.dumps(status,indent=2)+'\n')
print('ISSUE39 V5 UMOD24 REMAINDER-ONLY PUBLICATION PASS')
