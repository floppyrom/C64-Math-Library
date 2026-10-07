#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import preprocess
p="v2_pareto_fast"; src=ROOT/"relocatable_source"/p/"math_relocatable.asm"; cfg=ROOT/"relocatable_source"/p/"math_config_reference.inc"
mem,labels,const=Assembler().assemble(preprocess(src,cfg))
lo,hi=0x3d20,0x3ddf
print("labels")
for n,a in sorted(labels.items(),key=lambda kv:kv[1]):
    if lo<=a<=hi: print(hex(a),n)
print("byte_runs")
a=lo
while a<=hi:
    z=(mem.get(a,0)==0); b=a
    while b+1<=hi and ((mem.get(b+1,0)==0)==z): b+=1
    print("ZERO" if z else "NONZERO",hex(a),hex(b),b-a+1)
    a=b+1
