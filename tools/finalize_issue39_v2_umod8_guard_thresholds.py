#!/usr/bin/env python3
"""Seal exact full-domain V2 UMOD8 guard boundary research; no binary changes."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
src=json.loads(Path(sys.argv[1]).read_text())
state=json.loads((R/'RELEASE_STATUS.json').read_text())
prg=R/'v2_pareto_fast/resident/math_v2_pareto_fast_game_math.prg'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert src['status']=='PASS' and src['sample_count']==65536
assert src['dual_route_pairs']==59136 and src['fully_real_direct_threshold_spot_checks']==2277
assert src['resident_sha256']==sha(prg)==state['reference_prg_sha256']['v2_pareto_fast']
a={int(k):v for k,v in src['thresholds'].items()}
assert len(a)==20 and a[24]['cycles']==3421271
assert all(v['cycles']>a[24]['cycles'] for k,v in a.items() if k!=24)
assert (a[25]['faster'],a[25]['slower'])==(24,232)
assert (a[32]['faster'],a[32]['slower'])==(88,1960)
p=R/'validation/review/ISSUE39_V2_UMOD8_GUARD_THRESHOLD_SWEEP.json'
p.write_text(json.dumps(src,indent=2,sort_keys=True)+'\n')
d=R/'docs/ISSUE39_V2_UMOD8_GUARD_THRESHOLD_SWEEP_2026-10-12.md'
lines=['# Issue #39: exhaustive V2 UMOD8 fast-path guard study',
'','2026-10-12. No resident/code/API changes. Retain D>=24.',
'','The 10-stage unrolled magnitude-subtraction path is valid for D>=24',
'because floor(255/24)=10. A lower cutoff without a new algorithm',
'could give a wrong remainder and was not considered.',
'','All 65,536 N/D operands were checked for remainder, carry, all Q',
'bytes unchanged, inputs unchanged, high-R sentinels, and stack.',
'Each D>=24 pair ran both fast and fallback resident paths; 2,277',
'direct-cutoff reruns confirmed reconstructed CPU timing.',
'This is 6502 instruction timing, not a native bus contention measure.',
'','| Fast guard | Mean cycles | Difference | Faster | Slower |',
'|---|---:|---:|---:|---:|']
for k,v in sorted(a.items()):
 lines.append(f"| D>={k} | {v['mean_cycles']:.6f} | {v['delta_cycles_per_call']:+.6f} | {v['faster']} | {v['slower']} |")
lines+=['','The current D>=24 boundary wins all 20 tested cutoffs:',
'52.204453 cycles; D>=25 averages 52.274643, D>=32 52.845413.',
'The best cutoff for this specific existing kernel is unchanged.',
'This does not establish whole-family or global UMOD8 optimality.',
'Full report: validation/review/ISSUE39_V2_UMOD8_GUARD_THRESHOLD_SWEEP.json.',
'Keep issue #39 unsigned DIV/MOD family open.']
d.write_text('\n'.join(lines)+'\n')
mark='2026-10-12 ISSUE39 V2 UMOD8 GUARD D24 EXHAUSTIVE SCREEN'
entry=f'{mark}\n- Full-domain 65,536 N/D calls, 59,136 two-route checks, 2,277 direct candidate calls. V2 D>=24 guard gives the lowest measured mean: 52.204453; D>=25 52.274643, D>=32 52.845413. All higher cutoffs lose overall; no default binary/ABI/ZP/stack change. Source/data, docs and SHA256SUMS updated; issue #39 open. {d.relative_to(R)}\n'
for n in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 f=R/n
 if mark not in f.read_text():f.write_text(entry+'\n'+f.read_text())
for n in ('README.md','USER_MANUAL.md'):
 f=R/n
 line='- Issue #39 V2 UMOD8 exact-D24 guard no-gain screen: '+str(d.relative_to(R))+'.'
 if line not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+line+'\n')
state['issue39_v2_umod8_guard_cutoff_2026_10_12']={'status':'PASS_NO_PROMOTION',
 'report':str(p.relative_to(R)),'report_sha256':sha(p),'documentation':str(d.relative_to(R)),
 'tested_cutoffs':20,'exact_cases':65536,'best_guard':24,'best_mean':a[24]['mean_cycles'],
 'binary_changed':False,'unsigned_family_complete':False}
if isinstance(state.get('documentation'),dict):
 f=R/'USER_MANUAL.md'
 state['documentation'].update(user_manual_bytes=f.stat().st_size,
   user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
(R/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
subprocess.run(['make','clean'],cwd=R,check=True)
for i in range(3):
 files=sorted((q for q in R.rglob('*') if q.is_file() and '.git' not in q.parts and '__pycache__' not in q.parts and q.name!='SHA256SUMS.txt'),key=lambda q:str(q.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(q)+'  '+str(q.relative_to(R))+'\n' for q in files))
 subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=R,check=True)
print('ISSUE39 V2 UMOD8 GUARD NO-GAIN SEALED',flush=True)
