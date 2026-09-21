#!/usr/bin/env python3
from pathlib import Path
import csv,json,re,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pub',ROOT/'tools/publish_standalone_sources.py'); pub=importlib.util.module_from_spec(spec); spec.loader.exec_module(pub)
from mini6502 import Assembler
checks=[]; errors=[]
def ok(name,cond,detail=''):
 checks.append({'check':name,'pass':bool(cond),'detail':detail})
 if not cond: errors.append(f'{name}: {detail}')
# API/table/standalone coverage
cons=list(csv.DictReader((ROOT/'docs/CONSOLIDATED_ROUTINE_TABLE.csv').open()))
for p in pub.PROFILES:
 expected=dict(pub.CANONICAL); expected.update(pub.PROFILE_EXTRAS.get(p,{}))
 man=list(csv.DictReader((ROOT/p/'standalone/MANIFEST.csv').open()))
 ok(f'{p}: manifest count',len(man)==len(expected),f'{len(man)} vs {len(expected)}')
 ok(f'{p}: consolidated count',len([r for r in cons if r['profile']==p])==len(expected))
 mm={r['legacy_api']:r for r in man}
 for n,c in expected.items():
  ok(f'{p}:{n}: manifest mapping',n in mm and mm[n]['canonical_name']==c)
  if n in mm: ok(f'{p}:{n}: file exists',(ROOT/p/'standalone'/mm[n]['file']).is_file())
  row=next((r for r in cons if r['profile']==p and r['routine']==n),None)
  ok(f'{p}:{n}: table mapping',row is not None and row.get('canonical_name')==c)
  # canonical alias in math_api
  txt=(ROOT/p/'resident/math_api.inc').read_text()
  ok(f'{p}:{n}: typed alias',re.search(rf'^\s*{re.escape(c)}\s*=\s*{re.escape(n)}\s*$',txt,re.M) is not None)
# exact source annotations against initialized executable image
ann=re.compile(r'; @([0-9A-F]{4}) ((?:[0-9A-F]{2}(?: |$))+)',re.I)
for p in pub.PROFILES:
 mem,vals,prg=pub.initialized(p)
 for r in csv.DictReader((ROOT/p/'standalone/MANIFEST.csv').open()):
  fp=ROOT/p/'standalone'/r['file']; count=0; same=True
  for m in ann.finditer(fp.read_text()):
   a=int(m.group(1),16); bs=bytes(int(x,16) for x in m.group(2).split()); count+=1
   if bytes(mem[a:a+len(bs)])!=bs: same=False; break
  source='\n'.join(line for line in fp.read_text().splitlines() if not line.strip().lower().startswith('!cpu'))
  emitted,_,_=Assembler().assemble(source)
  same=same and all(mem[a]==v for a,v in emitted.items())
  ok(f'{p}:{r["legacy_api"]}: executable bytes',same and count>0,f'{count} assembled and annotated instructions')
# stable public table mapping
api=list(csv.DictReader((ROOT/'docs/PUBLIC_API_COMPLETE.csv').open()))
ok('PUBLIC_API_COMPLETE stable count',len(api)==46,str(len(api)))
for r in api: ok(f'public table {r["entry"]}',r['canonical_name']==pub.CANONICAL[r['entry']])
# No measured value was changed in tables that existed in incoming refresh overlay: only canonical_name may be added.
BASE=Path('/mnt/data/c64audit/base')
for p in sorted(ROOT.rglob('*.csv')):
 rel=p.relative_to(ROOT); bp=BASE/rel
 if not bp.exists(): continue
 with p.open(newline='') as f:new=list(csv.DictReader(f)); nf=[x for x in (new[0].keys() if new else []) if x!='canonical_name']
 with bp.open(newline='') as f:old=list(csv.DictReader(f)); of=list(old[0].keys()) if old else []
 if nf!=of:
  ok(f'{rel}: original columns preserved',False,f'{nf} != {of}'); continue
 stripped=[{k:r.get(k,'') for k in of} for r in new]
 ok(f'{rel}: measurements/content unchanged',stripped==old,f'{len(old)} rows')
# Current refresh provenance on updated arithmetic families in consolidated table.
refresh_names={'MATH_UMUL24','MATH_UMUL32','MATH_UMUL32_READY','MATH_SMUL8','MATH_SMUL24','MATH_SMUL32','MATH_UDIV8','MATH_UDIV16','MATH_UDIV24','MATH_UDIV32_32','MATH_SDIV8','MATH_SDIV16','MATH_SDIV24','MATH_SDIV32_16','MATH_SDIV32_32'}
for p in pub.PROFILES:
 for n in refresh_names:
  r=next(x for x in cons if x['profile']==p and x['routine']==n)
  ok(f'{p}:{n}: current evidence',('2026-09-20' in r['cycle_basis'] or 'current native' in r['cycle_basis'] or (n=='MATH_UMUL24' and p in ('v2_pareto_fast','v3_reu_512k','v4_reu_16m') and '2026-09-14 record-upgrade' in r['cycle_basis'])),r['cycle_basis'])
report={'status':'PASS' if not errors else 'FAIL','checks':len(checks),'failed':len(errors),'errors':errors,'summary':{'profiles':{p:len(list(csv.DictReader((ROOT/p/'standalone/MANIFEST.csv').open()))) for p in pub.PROFILES},'consolidated_rows':len(cons),'stable_api_entries':len(api)}}
(ROOT/'validation/STANDALONE_API_CONSISTENCY_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],report['checks'],'checks;',report['failed'],'failed')
if errors:
 print('\n'.join(errors[:30]));sys.exit(1)
