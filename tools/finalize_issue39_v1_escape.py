#!/usr/bin/env python3
"""Publish issue39 V1 narrow tail transplant, after all full validation and same-input benchmark."""
from pathlib import Path
import csv,hashlib,json
from finalize_signed_core_reuse import rebuild_game_math_aggregate
from common_corpus_ranking import load_common, EXPECTED as UNSIGNED
R=Path(__file__).resolve().parents[1]
V1='v1_balanced'; V5='v5_hybrid_lowzp'
PROFILES=(V1,'v2_pareto_fast','v3_reu_512k','v4_reu_16m',V5)
EXPECTED={V1:'1a81ec4f8ded86353c919e531bf4e8030a48cf86cac2f3758fff2878f3ae83b7',
 V5:'d3b654f56f7ddfe26ce7130d5e925fdde85e41875e7da4bcd5aafe62440483a7'}
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for p,h in EXPECTED.items():
 path=R/p/'resident'/f'math_{p}_game_math.prg'
 assert sha(path)==h,(p,sha(path),h)
for name,cases in [('UNSIGNED_DIVISION_VALIDATION',822050),('SIGNED_DIVISION_VALIDATION',364533)]:
 report=json.loads((R/'validation/review'/f'{name}.json').read_text())
 assert report['status']=='PASS' and report['summary']['machine_calls']==cases
 assert len(report['profiles'])==5
 assert not any(x['errors'] for z in report['profiles'].values() for x in z.values())
common=load_common(R)
assert common['total_calls']==136335 and len(common['routines'])==11
d24=common['routines']['MATH_UDIV24']['metrics'][V1]
m24=common['routines']['MATH_UMOD24']['metrics'][V1]
for got,mean in ((d24,179.964654),(m24,276.590470)):
 assert abs(got['mean_cycles']-mean)<0.000002,(got,mean)
# Refresh profile-specific validation metadata, independently of the common-input rank.
report=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
for p in PROFILES:
 f=(R/p/'HYBRID_PERFORMANCE.csv') if p==V5 else (R/p/'PUBLIC_PERFORMANCE.csv')
 if not f.exists():continue
 with f.open(newline='') as h:rows=list(csv.DictReader(h))
 fields=list(rows[0]);seen=set()
 for row in rows:
  key=row['routine'] if p==V5 else row['operation']
  key=key.upper().replace('MATH_','')
  if key not in ('UDIV24','UMOD24'):continue
  name='MATH_'+key
  if p==V1:
   val=report['profiles'][V1][name]
   assert val['cases']==int(row['cases'])
   row['avg_cycles']=f"{val['mean_cycles']:.6f}"
   row['min_cycles']=str(val['min_cycles'])
   row['max_cycles']=str(val['max_cycles'])
   row['evidence']='2026-10-11 issue39 V1 narrow-quotient escape machine-code audit'
  elif p=='v3_reu_512k':
   row['v1_balanced_cycles']=f"{report['profiles'][V1][name]['mean_cycles']:.6f}"
  elif p==V5:
   old=report['profiles'][V1][name]['mean_cycles']
   new=report['profiles'][V5][name]['mean_cycles']
   row['v1_mean_cycles']=f"{old:.6f}"
   row['v5_mean_cycles']=f"{new:.6f}"
   row['improvement_percent']=f"{(old-new)/old*100:.6f}"
   row['provenance']='2026-10-11 issue39 changed-V1 paired ABI and all-profile audit'
  seen.add(name)
 # Some profiles carry these symbols in their own custom catalog.
 if p in (V1,'v3_reu_512k',V5):assert seen=={'MATH_UDIV24','MATH_UMOD24'},(p,seen)
 with f.open('w',newline='') as h:
  w=csv.DictWriter(h,fieldnames=fields,lineterminator='\n')
  w.writeheader();w.writerows(rows)
rebuild_game_math_aggregate()
# These 11 rows represent true shared-input ranking, not the per-profile validators.
f=R/'PERFORMANCE.md';lines=f.read_text().splitlines()
for name in UNSIGNED:
 matches=[i for i,x in enumerate(lines) if x.startswith(f'| ' + chr(96)+name+chr(96)+' |')]
 assert len(matches)==1,(name,matches)
 fields=lines[matches[0]].split('|')
 for j,p in enumerate(PROFILES):fields[j+3]=f" {common['routines'][name]['metrics'][p]['mean_cycles']:.6f} "
 lines[matches[0]]='|'.join(fields)
f.write_text('\n'.join(lines)+'\n')
DOC='docs/ISSUE39_V1_UDIV24_NARROW_ESCAPE_2026-10-11.md'
marker='2026-10-11 ISSUE39 V1 BALANCED 24-BIT NARROW-DIVISOR LATENCY ESCAPE'
entry=f"""{marker}
- V1 Balanced UDIV24/UMOD24: route the costly N2>0,D2=0 and Q>=65536 fallback through the existing V1 32/16 division core; preserve original low-quotient path and reuse LAX-provided X=N2. V5 keeps the optimized V2 donor behavior.
- Paired same-input 4,753 UDIV24 and 1,553 UMOD24 calls: V1 means 189.741847→179.964654 and 306.577592→276.590470 cycles. 162 calls faster, 91 slower (maximum +19), remainder unchanged; the large Q example $FFFFFF/$000001 improves 3235→1986.
- Explicit Pareto tradeoff; selected for much shorter heavy tail and lower means, not all-input dominance. No new ZP, no PRG length or public ABI relocation, V5 helper placed after signed donor islands at $7FA0.
- Full V1/V5 164,410 unsigned and 97,329/36,273 signed machine-code validations plus VICE x64sc paired native checks, V1–V4 reference/alternate maps, published all-API and common-input ranking proof requalified. Other profile code unchanged.
- Benchmarks, source mirrors, profile cross-references, both changelogs, status, checksums and package audit updated. Wider issue #39 unsigned DIV/MOD campaign remains open.
- Detail: {DOC}
"""
for filename in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 p=R/filename
 if marker not in p.read_text():p.write_text(entry+'\n'+p.read_text())
link=f'- V1 Balanced UDIV24/UMOD24 narrow-quotient latency escape: {DOC} (explicit latency/mean trade-off; other issue39 unsigned audits open).'
for filename in ('README.md','USER_MANUAL.md'):
 p=R/filename
 if link not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+link+'\n')
r=R/'RELEASE_STATUS.json';st=json.loads(r.read_text())
st['date']='2026-10-11'
st['reference_prg_sha256']={p:sha(R/p/'resident'/f'math_{p}_game_math.prg') for p in PROFILES}
alts={}
for p in PROFILES[:-1]:
 f=R/'build_source/alternate'/p/'source_build_manifest.json'
 alts[p]=json.loads(f.read_text())['output_sha256']
alts[V5]=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
st['alternate_prg_sha256']=alts
if isinstance(st.get('hybrid_v5'),dict):
 st['hybrid_v5'].update(reference_prg_sha256=EXPECTED[V5],alternate_prg_sha256=alts[V5])
st['issue39_v1_udiv24_escape_2026_10_11']={
 'status':'PASS','documentation':DOC,'unsigned_family_completed':False,
 'v1_paired_calls':6306,'paired_errors':0,'paired_improved_calls':162,
 'paired_slower_calls':91,'max_regression_cycles':19,
 'source_reference_sha256':EXPECTED,
 'all_profile_unsigned_calls':822050,'all_profile_signed_calls':364533,
 'common_input_calls':136335,
 'common_report_sha256':sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json'),
 'stable_abi_changed':False,'normal_zp_growth_bytes':0,'resident_size_growth_bytes':0}
if 'issue39_common_input_unsigned_divmod' in st:
 st['issue39_common_input_unsigned_divmod']['benchmark_sha256']=sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
 st['issue39_common_input_unsigned_divmod']['arithmetic_binaries_changed']=True
if isinstance(st.get('documentation'),dict):
 u=R/'USER_MANUAL.md';st['documentation'].update(user_manual_bytes=u.stat().st_size,user_manual_lines=len(u.read_text().splitlines()),user_manual_sha256=sha(u))
r.write_text(json.dumps(st,indent=2)+'\n')
print('ISSUE39 V1 UDIV24 NARROW ESCAPE PUBLICATION PASS')
