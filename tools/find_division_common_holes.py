#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as A
from mini6502 import Assembler

P=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')
K=('reference','alternate')
maps={}
for p in P:
  for k in K:
    cfg=ROOT/'relocatable_source'/p/f'math_config_{k}.inc'
    src=ROOT/'relocatable_source'/p/'math_relocatable.asm'
    mem,lab,const=Assembler().assemble(A.preprocess(src,cfg))
    base=const['REG_KERNEL']
    maps[(p,k)]={a-base for a in mem if base<=a<base+0x2000}

common=[]
for off in range(0x0000,0x2000):
  if all(off not in maps[x] for x in maps): common.append(off)
runs=[]
if common:
  s=pr=common[0]
  for x in common[1:]:
    if x!=pr+1:
      if pr-s+1>=32:runs.append((s,pr+1))
      s=x
    pr=x
  if pr-s+1>=32:runs.append((s,pr+1))
print('COMMON FREE RUNS >=32 bytes, relative REG_KERNEL')
for s,e in runs:
  if not (s < 0x14c0 and e > 0x1480):
    print('+%04X..+%04X  %d bytes' % (s,e-1,e-s))
