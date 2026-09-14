#!/usr/bin/env python3
"""Verify every published signed source mirror against the executable resident bytes."""
from __future__ import annotations
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from publish_native_signed_sources import PROFILES,MUL,DIV,initialized,trace,PAIR
RX=re.compile(r';\s*@([0-9A-F]{4})\s+((?:[0-9A-F]{2})(?:\s+[0-9A-F]{2}){0,2})\s*$')
checks=[]; profiles={}
def ck(name,cond,detail=None):
 if not cond: raise AssertionError(f'{name}: {detail}')
 checks.append({'check':name,'status':'PASS','detail':detail})
for p in PROFILES:
 mem,vals=initialized(p); pr={}
 for kind,names in [('multiply',MUL),('division',DIV)]:
  d=ROOT/p/'resident/signed'/kind/'native'; kr={}
  ck(f'{p}_{kind}_readme',(d/'README.md').exists())
  for name,fn in names.items():
   f=d/fn; ck(f'{p}_{name}_source_present',f.exists(),str(f.relative_to(ROOT)))
   got={}
   for line in f.read_text().splitlines():
    m=RX.search(line)
    if m: got[int(m.group(1),16)]=bytes(int(x,16) for x in m.group(2).split())
   code=trace(mem,vals[name]); unsigned=trace(mem,vals[PAIR[name]])
   ck(f'{p}_{name}_zero_overlap',not(code&unsigned),len(code&unsigned))
   ck(f'{p}_{name}_instruction_count',set(got)==code,{'published':len(got),'runtime':len(code),'missing':len(code-set(got)),'extra':len(set(got)-code)})
   mism=[]
   for pc,b in got.items():
    if bytes(mem[pc:pc+len(b)])!=b: mism.append((pc,b.hex(),bytes(mem[pc:pc+len(b)]).hex()))
   ck(f'{p}_{name}_bytes_exact',not mism,mism[:3])
   kr[name]={'file':str(f.relative_to(ROOT)),'instructions':len(code),'bytes_verified':sum(len(x) for x in got.values())}
  pr[kind]=kr
 profiles[p]=pr
out={'status':'PASS','profiles':profiles,'summary':{'profiles':len(PROFILES),'published_routines':len(PROFILES)*(len(MUL)+len(DIV)),'checks_passed':len(checks)},'checks':checks}
p=ROOT/'validation/review/PUBLISHED_SIGNED_SOURCES_VALIDATION.json';p.write_text(json.dumps(out,indent=2)+'\n')
print('PUBLISHED SIGNED SOURCES PASS',out['summary']['published_routines'],'routines,',len(checks),'checks')
