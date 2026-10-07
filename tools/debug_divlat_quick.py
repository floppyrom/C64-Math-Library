#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import validate_division_latency_escape as V
from validate_unsigned_division import load as load_resident
from validate_udiv32_16_integrated import load_source

p='v2_pareto_fast'
old,Ao=load_resident(p);new,An,io=load_source(p,'reference')
C=V.corpora()
for tag,entry,nb,db,sent in [
 ('n24','MATH_UDIV24',24,24,0xA5),('q024','MATH_UDIV24',24,24,0xA5),
 ('n32','MATH_UDIV32_32',32,32,None),('w32','MATH_UDIV32_32',32,32,None),
 ('h24','MATH_UDIV24',24,24,0xA5),('h32','MATH_UDIV32_32',32,32,None)]:
    vec=C[tag][:2000]
    r=V.paired(old,new,Ao[entry],An[entry],io,vec,nb,db,sent)
    print(tag,r)
    if tag in ('q024','w32'):
        assert r['slower_cases']==0 and r['min_saved_cycles']==0 and r['max_saved_cycles']==0,(tag,r)
print('QUICK DIVISION LATENCY PASS')
