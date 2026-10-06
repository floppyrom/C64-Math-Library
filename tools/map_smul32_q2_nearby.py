#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import preprocess
p="v2_pareto_fast"
src=ROOT/"relocatable_source"/p/"math_relocatable.asm"
cfg=ROOT/"relocatable_source"/p/"math_config_reference.inc"
mem,labels,const=Assembler().assemble(preprocess(src,cfg))
lo,hi=0x5480,0x56a0
runs=[]; a=lo
while a<=hi:
    used=a in mem; b=a
    while b+1<=hi and ((b+1 in mem)==used): b+=1
    runs.append((used,a,b,b-a+1)); a=b+1
print("near_q2_memory_map")
for used,a,b,n in runs:
    print(("USED" if used else "FREE"),f"${a:04x}-${b:04x}",n)
print("near_q2_labels")
for name,addr in sorted(labels.items(),key=lambda kv:kv[1]):
    if lo<=addr<=hi:
        print(f"${addr:04x}",name)
