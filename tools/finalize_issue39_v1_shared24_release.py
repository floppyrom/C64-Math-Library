#!/usr/bin/env python3
"""Issue39 V1 24/8 69-byte release finalizer; run after complete proof/rebuild."""
from pathlib import Path
import hashlib,csv,json
from common_corpus_ranking import load_common
from finalize_signed_core_reuse import rebuild_game_math_aggregate
R=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV24','MATH_UMOD24')
NEW='28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0'
V5='5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222'
DOC='docs/ISSUE39_V1_UDIV24_SHARED_SUBTRACTION_RELEASE_2026-10-12.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/'v1_balanced/resident/math_v1_balanced_game_math.prg')==NEW
assert sha(R/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg')==V5
u=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
s=json.loads((R/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
small=json.loads((R/'validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json').read_text())
assert u['status']==s['status']==small['status']=='PASS'
assert u['summary']['machine_calls']==822050 and s['summary']['machine_calls']==364533 and small['total_calls']==53760
common=load_common(R);assert common['total_calls']==136335
expected={'MATH_UDIV24':(170.72669892699346,170.23816536924048),
          'MATH_UMOD24':(248.31745009658724,246.8222794591114)}
for name,(old,new) in expected.items():
 assert abs(common['routines'][name]['metrics']['v1_balanced']['mean_cycles']-new)<1e-9
def rows(path,cb):
 p=R/path
 with p.open(newline='') as f:data=list(csv.DictReader(f))
 cols=list(data[0]);cb(data)
 with p.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');writer.writeheader();writer.writerows(data)
def v1(rows):
 for r in rows:
  name=r['operation'].upper()
  if name in OPS:
   a=u['profiles']['v1_balanced'][name]
   assert int(r['cases'])==a['cases']
   r.update(avg_cycles=f"{a['mean_cycles']:.6f}",min_cycles=str(a['min_cycles']),max_cycles=str(a['max_cycles']),
            evidence='2026-10-12 Issue39 V1 shared-subtraction source and complete unsigned ABI proof')
def v1game(rows):
 for r in rows:
  name='MATH_'+r['routine'].upper()
  if name in OPS:
   a=u['profiles']['v1_balanced'][name]
   r.update(cases=str(a['cases']),mean_cycles=f"{a['mean_cycles']:.6f}",
            min_cycles=str(a['min_cycles']),max_cycles=str(a['max_cycles']))
def v3(rows):
 for r in rows:
  name='MATH_'+r['operation'].upper()
  if name in OPS:r['v1_balanced_cycles']=f"{u['profiles']['v1_balanced'][name]['mean_cycles']:.6f}"
def v5(rows):
 for r in rows:
  name=r['routine']
  if name in OPS:
   a=common['routines'][name]['metrics']['v1_balanced']['mean_cycles']
   b=common['routines'][name]['metrics']['v5_hybrid_lowzp']['mean_cycles']
   r.update(v1_mean_cycles=f'{a:.6f}',v5_mean_cycles=f'{b:.6f}',
            improvement_percent=f'{(a-b)*100/a:.6f}',
            provenance='2026-10-12 Issue39 shared-subtraction V1 only; V5 resident unchanged')
for p,fn in [('v1_balanced/PUBLIC_PERFORMANCE.csv',v1),
             ('v1_balanced/PUBLIC_PERFORMANCE_GAME_MATH.csv',v1game),
             ('v3_reu_512k/PUBLIC_PERFORMANCE.csv',v3),
             ('v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv',v5)]:rows(p,fn)
rebuild_game_math_aggregate()
p=R/'PERFORMANCE.md';line=p.read_text().splitlines()
for name in OPS:
 idx=[i for i,x in enumerate(line) if x.startswith('| '+chr(96)+name+chr(96)+' |')]
 assert len(idx)==1,(name,idx)
 c=line[idx[0]].split('|')
 for i,prof in enumerate(PROFILES):
  c[3+i]=f" {common['routines'][name]['metrics'][prof]['mean_cycles']:.6f} "
 line[idx[0]]='|'.join(c)
p.write_text('\n'.join(line)+'\n')
doc="""# Issue #39 — V1 24/8 shared-subtraction release (2026-10-12)

The V1 Balanced exact 24-by-8 kernel at REG_LOW+$0D00 now shares a carry-aware subtraction path. It shrinks from **84 to 69 bytes** (15 unused bytes zero-filled). No additional ZP/stack, API address, or resident size growth. V2–V5 executables are unchanged.

On the official same-input corpus: **UDIV24 170.726699 → 170.238165**, **UMOD24 248.317450 → 246.822279** mean 6502 instruction cycles. The independent public-entry 48,388-call old/new comparison, including the D8 stress and wide-divisor control workloads, had **zero slower calls** and checked Q/R/C, input sentinels and stack balance. Full validation: 822,050 unsigned, 364,533 signed, 136,335 comparable and 53,760 workload-conditioned calls, all correct. A separate native x64sc old/new campaign successfully checked **256 public calls** for Q/R/C; no native timing claim. Refer to the preserved standalone test procedure and Issue #39 screening PR #77 for reproducing the public paired timings.

Source: relocatable_source/v1_balanced/udiv24_latency_escape_balanced.inc. Generated canonical source, V1 binary and standalone mirrors are released together. This is one improvement; Issue #39 unsigned DIV/MOD campaign **remains open**.
"""
(R/DOC).write_text(doc)
marker='2026-10-12 ISSUE39 V1 24/8 SHARED-SUBTRACTION RELEASE'
entry=f"""{marker}
- Source-backed V1 UDIV24/UMOD24 84→69 byte carry-aware shared-subtract kernel, no new ZP/stack, ABI or resident-byte growth; V2–V5 unchanged.
- Identical-input means UDIV24 170.726699→170.238165 and UMOD24 248.317450→246.822279; 48,388 old/new calls with no slower result; 256 native x64sc correctness calls. Full unsigned/signed, comparable and seven-workload checks passed.
- Refreshed standalone mirrors, public tables, release metadata and checksums. Issue #39 remains open. {DOC}.
"""
for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 p=R/name
 if marker not in p.read_text():p.write_text(entry+'\n'+p.read_text())
for name in ('README.md','USER_MANUAL.md'):
 p=R/name;content=p.read_text()
 link=f'- V1 24/8 shared-subtraction DIV/MOD improvement: {DOC}. Issue #39 remains open.'
 if link not in content:p.write_text(content.rstrip()+'\n\n'+link+'\n')
p=R/'RELEASE_STATUS.json';state=json.loads(p.read_text());state['date']='2026-10-12'
state['reference_prg_sha256']={k:sha(R/k/'resident'/f'math_{k}_game_math.prg') for k in PROFILES}
alt={k:json.loads((R/'build_source/alternate'/k/'source_build_manifest.json').read_text())['output_sha256'] for k in PROFILES[:4]}
alt[PROFILES[-1]]=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())['output_sha256']
state['alternate_prg_sha256']=alt
if isinstance(state.get('hybrid_v5'),dict):
 state['hybrid_v5']['reference_prg_sha256']=V5
 state['hybrid_v5']['alternate_prg_sha256']=alt[PROFILES[-1]]
state['issue39_v1_sharedsub24_2026_10_12']={
 'status':'PASS','document':DOC,'resident_sha256':NEW,'old_code_bytes':84,
 'new_code_bytes':69,'normal_zp_growth':0,'stack_growth':0,
 'paired_public_calls':48388,'paired_regressions':0,'native_vice_old_new_calls':256,
 'unsigned_validation_calls':822050,'signed_validation_calls':364533,
 'common_input_calls':136335,'small_workload_calls':53760,'unsigned_family_complete':False}
if isinstance(state.get('issue39_common_input_unsigned_divmod'),dict):
 state['issue39_common_input_unsigned_divmod']['benchmark_sha256']=sha(R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json')
 state['issue39_common_input_unsigned_divmod']['arithmetic_binaries_changed']=True
if isinstance(state.get('issue39_unsigned_small_width_workloads_2026_10_11'),dict):
 state['issue39_unsigned_small_width_workloads_2026_10_11']['data_sha256']=sha(R/'validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json')
if isinstance(state.get('documentation'),dict):
 f=R/'USER_MANUAL.md'
 state['documentation'].update(user_manual_bytes=f.stat().st_size,
                               user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
p.write_text(json.dumps(state,indent=2)+'\n')
print("ISSUE39 V1 24/8 RELEASE FINALIZATION PASS",NEW)
