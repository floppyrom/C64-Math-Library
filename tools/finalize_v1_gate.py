#!/usr/bin/env python3
"""Publish V1 issue #39 zero-ZP UDIV32/32 and UMOD32/32 gate evidence."""
import csv,hashlib,json
from pathlib import Path
from finalize_signed_core_reuse import rebuild_game_math_aggregate
R=Path(__file__).resolve().parents[1]
P='v1_balanced'
SHA='00ea3816ee39fac3ee3c04ae05c276bde43f05e3073fbdcc12f7f2fa74f97ad0'
DOC='docs/V1_UDIV32_32_PRECHECKED_GATE_2026-10-11.md'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(R/P/'resident/math_v1_balanced_game_math.prg')==SHA
u=json.loads((R/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
s=json.loads((R/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
for d in (u,s):
 assert d['status']=='PASS' and len(d['profiles'])==5
 assert all(v['errors']==0 for pr in d['profiles'].values() for v in pr.values())
v=u['profiles'][P]
assert v['MATH_UDIV32_32']['cases']==6801 and abs(v['MATH_UDIV32_32']['mean_cycles']-416.8611968828)<1e-5
assert v['MATH_UMOD32_32']['cases']==1553 and abs(v['MATH_UMOD32_32']['mean_cycles']-541.401802962)<1e-5
p=R/P/'PUBLIC_PERFORMANCE_GAME_MATH.csv'
with p.open() as f: rows=list(csv.DictReader(f))
for row in rows:
 if row['routine'] in ('UDIV32_32','UMOD32_32'):
  record=v['MATH_UDIV32_32']
  row.update(mean_cycles=f"{record['mean_cycles']:.6f}",min_cycles=str(record['min_cycles']),max_cycles=str(record['max_cycles']))
with p.open('w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
 writer.writeheader();writer.writerows(rows)
rebuild_game_math_aggregate()
p=R/'PERFORMANCE.md'
lines=p.read_text().splitlines()
for name in ('MATH_UDIV32_32','MATH_UMOD32_32'):
 head='| '+chr(96)+name+chr(96)+' | '
 selected=[i for i,line in enumerate(lines) if line.startswith(head)]
 assert len(selected)==1,(name,selected)
 i=selected[0];parts=lines[i].split('|')
 parts[3]=' '+f"{v[name]['mean_cycles']:.6f}"+' '
 lines[i]='|'.join(parts)
p.write_text('\n'.join(lines)+'\n')
marker='2026-10-11 V1 UDIV32/32 + UMOD32/32 NONZERO GATE'
news=f"""{marker}
- V1 zero-ZP shared 32/32 divider reuses the prechecked nonzero-divisor decision, avoiding duplicate D!=0 work on N>D.
- UDIV32/32 428.554036 -> {v['MATH_UDIV32_32']['mean_cycles']:.6f} cycles on 6,801 calls; UMOD32/32 552.220863 -> {v['MATH_UMOD32_32']['mean_cycles']:.6f} cycles on 1,553 calls.
- ABI and RAM envelope unchanged; 21,508 paired calls with zero slower paths; full unsigned and signed family regression requalified.
- Generated mirrors, performance indexes, 2 changelogs, documentation, checksum and package audits updated.
- The unsigned DIV/MOD family in issue #39 remains open. Full evidence: {DOC}.
"""
for filename in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
 p=R/filename;old=p.read_text()
 if marker not in old:p.write_text(news+'\n'+old)
note=f"- V1 32/32 shared nonzero-divisor gate (issue #39): {DOC}; remaining unsigned family audit stays open."
for filename in ('README.md','USER_MANUAL.md'):
 p=R/filename;old=p.read_text()
 if note not in old:p.write_text(old.rstrip()+'\n\n'+note+'\n')
p=R/'RELEASE_STATUS.json';d=json.loads(p.read_text())
d['date']='2026-10-11'
d.setdefault('reference_prg_sha256',{})[P]=SHA
alt=R/'build_source/alternate'/P/'source_build_manifest.json'
d.setdefault('alternate_prg_sha256',{})[P]=json.loads(alt.read_text())['output_sha256']
d['issue_39_v1_32_32_prechecked']={'status':'PASS','whole_unsigned_family_complete':False,'documentation':DOC,'reference_prg_sha256':SHA,'paired_calls':21508,'paired_mismatches':0,'paired_slowdowns':0,'unsigned_divmod_calls':u['summary']['machine_calls'],'signed_divmod_calls':s['summary']['machine_calls'],'means':{name:v[name]['mean_cycles'] for name in ('MATH_UDIV32_32','MATH_UMOD32_32')}}
if isinstance(d.get('documentation'),dict):
 m=R/'USER_MANUAL.md'; d['documentation'].update(user_manual_bytes=m.stat().st_size,user_manual_lines=len(m.read_text().splitlines()),user_manual_sha256=digest(m))
p.write_text(json.dumps(d,indent=2)+'\n')
print('V1 publication metadata PASS',SHA)
