#!/usr/bin/env python3
"""Isolate carry-on-entry effect of full resident REU UDIV8 public entry."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import load,PROFILES,expected
cases=((4,1),(1,1),(0,1),(5,2),(127,3),(255,1),(255,255),(0,0),(4,0),(128,128))
results=[]
for p in PROFILES:
 for kind in ('clean','heavy_sentinels'):
  for n,d in cases:
   vals=[]
   for incoming in (0,1):
    cpu,api=load(p)
    m=cpu.mem
    m[0xc010]=n;m[0xc014]=d
    if kind=='heavy_sentinels':
     m[0xc018:0xc01c]=bytes.fromhex('586c9ba7')
     m[0xc01c:0xc020]=bytes.fromhex('56927be4')
     m[0xc012]=0xab;m[0xc016]=0xcd;m[0xc020]=0x72
    cpu.c=incoming
    cycles=cpu.call(api['MATH_UDIV8'],2_000_000)
    q,r,ref=expected(n,d,8,8)
    actual=(m[0xc018],m[0xc01c],cpu.c)
    vals.append({'incoming_c':incoming,'actual':actual,'expected':(q,r,ref),'cycles':cycles})
   if vals[0]['actual']!=vals[1]['actual'] or vals[0]['actual']!=vals[0]['expected']:
    results.append({'profile':p,'mode':kind,'N':n,'D':d,'results':vals})
print(json.dumps(results,sort_keys=True,indent=2),flush=True)
print('CARRY ON ENTRY DIAGNOSTIC',len(results),'differences',flush=True)
