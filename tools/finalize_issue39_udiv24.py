#!/usr/bin/env python3
"""Issue #39 V1–V5 UDIV24/UMOD24 source-backed, live-X publication finalizer."""
from pathlib import Path
import csv, hashlib, json
R=Path(__file__).resolve().parents[1]
NAMES=('MATH_UDIV24','MATH_UMOD24')
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
EXPECTED={
 'v1_balanced':'759ca1e9d683eba2b56f818e9f3f4f36f5322a832daadf06493380d610f8f0b5',
 'v2_pareto_fast':'e1e828a2748099b6f05b224b98ca26960d120f8ba886c4906e8b52bdb8b4fbcd',
 'v3_reu_512k':'026243976c2156b68ddc7527c6b1f1a4420cd4973026dd90d60cd4fef04f77bc',
 'v4_reu_16m':'61d2f5bc88e5394035c51a7be9cf6b99e329dfea37419ae7f1c72d97262470b7',
 'v5_hybrid_lowzp':'e875c010f1eef2bbf90e6678faf79d3ef641a8e59f3073ccb6b4700e271b1f5c'}
MEANS={
 'v1_balanced':(194.0326109825,302.877655),
 'v2_pareto_fast':(154.218178,205.325821),
 'v3_reu_512k':(161.533347,207.136510),
 'v4_reu_16m':(158.385020,205.247263),
 'v5_hybrid_lowzp':(157.655376,210.894398)}
DOC='docs/ISSUE39_UDIV24_EQUAL_HIGH_X_LIFETIME_2026-10-11.md'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ud=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
sd=json.loads((R/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
for data,count in ((ud,822050),(sd,364533)):
 assert data['status']=='PASS' and len(data['profiles'])==5
 assert data['summary']['machine_calls']==count
 assert all(z['errors']==0 for profile in data['profiles'].values() for z in profile.values())
for p in PROFILES:
 resident=R/p/'resident'/f'math_{p}_game_math.prg'
 assert digest(resident)==EXPECTED[p],(p,digest(resident))
 for name,mean in zip(NAMES,MEANS[p]):
  entry=ud['profiles'][p][name]
  assert entry['cases']==(4753 if name==NAMES[0] else 1553),(p,name,entry['cases'])
  assert abs(entry['mean_cycles']-mean)<0.000002,(p,name,entry['mean_cycles'],mean)
 # Refresh per-profile public performance from the newly generated machine-code data.
 csvfile=R/p/'PUBLIC_PERFORMANCE_GAME_MATH.csv'
 with csvfile.open(newline='') as f:rows=list(csv.DictReader(f))
 for row in rows:
  key='MATH_'+row['routine']
  if key in NAMES:
   t=ud['profiles'][p][key]
   row['mean_cycles']=f"{t['mean_cycles']:.6f}"
   row['min_cycles']=str(t['min_cycles'])
   row['max_cycles']=str(t['max_cycles'])
 with csvfile.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
  w.writeheader();w.writerows(rows)
from finalize_signed_core_reuse import rebuild_game_math_aggregate
rebuild_game_math_aggregate()
perf=R/'PERFORMANCE.md';lines=perf.read_text().splitlines()
for name in NAMES:
 where=[i for i,x in enumerate(lines) if x.startswith('| '+chr(96)+name+chr(96)+' |')]
 assert len(where)==1,(name,where)
 i=where[0];fields=lines[i].split('|')
 for j,p in enumerate(PROFILES):fields[j+3]=f" {ud['profiles'][p][name]['mean_cycles']:.6f} "
 lines[i]='|'.join(fields)
perf.write_text('\n'.join(lines)+'\n')
marker='2026-10-11 ISSUE39 UDIV24/UMOD24 LIVE-X EQUALITY FAST PATH'
changelog=f"""{marker}
- In V1 Balanced and V2/V3/V4 direct 24-bit quotient cores, reuse the already-live X=N2=D2 high byte using TXA instead of an extra LDA MATH_D+2, shortening the fast path by two cycles and two code bytes; V5 inherits both donor improvements.
- Paired deterministic public-entry corpus: 31,530 calls across V1–V5, no arithmetic/carry mismatches and no slower calls; exactly 1,994 calls save two cycles. Mean UDIV24 cycles V1–V5: {', '.join(f"{ud['profiles'][p][NAMES[0]]['mean_cycles']:.6f}" for p in PROFILES)}. UMOD24 means: {', '.join(f"{ud['profiles'][p][NAMES[1]]['mean_cycles']:.6f}" for p in PROFILES)}.
- V2–V4 UMOD24 dedicated remainder paths are unchanged on the benchmark corpus; public ABI and normal-ZP/resource contracts remain unchanged.
- Initial genuine VICE x64sc 3.13.2 paired spot proof: 80 before + 80 after native calls, including REU 512 KiB/16 MiB and V5 C64 CPU-port ROM banking.
- Source/relocation, signed and unsigned family checks, source mirrors, public benchmarks, README/manual, both changelogs, release metadata, SHA256 manifest and package audit refreshed.
- This is a manual register-lifetime synthesis on OptiSearch/Repose-derived architectures, not an independent generic OptiSearch native record. The larger issue #39 unsigned DIV/MOD campaign remains open.
- Documentation: {DOC}
"""
for path in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 f=R/path
 if marker not in f.read_text():f.write_text(changelog+'\n'+f.read_text())
link=f"- Issue #39 UDIV24/UMOD24 live-X equal-high optimization: {DOC}. Wider unsigned family campaign not yet complete."
for path in ('README.md','USER_MANUAL.md'):
 f=R/path
 if link not in f.read_text(): f.write_text(f.read_text().rstrip()+'\n\n'+link+'\n')
statusfile=R/'RELEASE_STATUS.json'
d=json.loads(statusfile.read_text());d['date']='2026-10-11'
d['reference_prg_sha256']=dict(EXPECT)
d['alternate_prg_sha256']={}
for p in PROFILES[:4]:
 m=R/'build_source/alternate'/p/'source_build_manifest.json'
 d['alternate_prg_sha256'][p]=json.loads(m.read_text())['output_sha256']
alt=json.loads((R/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())
d['alternate_prg_sha256']['v5_hybrid_lowzp']=alt['output_sha256']
if isinstance(d.get('hybrid_v5'),dict):
 d['hybrid_v5']['reference_prg_sha256']=EXPECTED['v5_hybrid_lowzp']
 d['hybrid_v5']['alternate_prg_sha256']=alt['output_sha256']
d['issue39_udiv24_equal_high_live_x_2026_10_11']={
 'status':'PASS','documentation':DOC,'unsigned_family_complete':False,
 'paired_calls':31530,'paired_errors':0,'paired_slowdowns':0,'paired_faster_calls':1994,
 'native_x64sc_calls_baseline':80,'native_x64sc_calls_candidate':80,
 'unsigned_family_validation_calls':822050,'signed_family_validation_calls':364533,
 'reference_prg_sha256':EXPECTED,
 'published_mean_cycles':{p:{n:ud['profiles'][p][n]['mean_cycles'] for n in NAMES} for p in PROFILES},
 'stable_abi_changed':False,'normal_zp_growth_bytes':0}
if isinstance(d.get('documentation'),dict):
 f=R/'USER_MANUAL.md'
 d['documentation']['user_manual_bytes']=f.stat().st_size
 d['documentation']['user_manual_lines']=len(f.read_text().splitlines())
 d['documentation']['user_manual_sha256']=digest(f)
statusfile.write_text(json.dumps(d,indent=2)+'\n')
print('ISSUE39 UDIV24 MANUAL POST-OPTISEARCH PUBLICATION PASS')
