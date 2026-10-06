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
qlo=labels["S32V28_q1_fast_core_start"]
qhi=labels["S32V28_q1_cg_code_end"]
lo=max(0,qlo-0x100); hi=min(0xffff,qhi+0x100)
runs=[]; a=lo
while a<=hi:
    used=a in mem; b=a
    while b+1<=hi and ((b+1 in mem)==used): b+=1
    runs.append((used,a,b,b-a+1)); a=b+1
print(f"q1_core 0x{qlo:04x}-0x{qhi-1:04x} bytes={qhi-qlo}")
for used,a,b,n in runs:
    print(("USED" if used else "FREE"),f"0x{a:04x}-0x{b:04x}",n)
print("q1_labels")
for name,addr in sorted(labels.items(),key=lambda kv:kv[1]):
    if lo<=addr<=hi and name.startswith("S32V28_q1_"):
        print(f"0x{addr:04x}",name)

print("game_api_free_runs")
lo,hi=0x5e00,0x5fff
a=lo
while a<=hi:
    used=a in mem; b=a
    while b+1<=hi and ((b+1 in mem)==used): b+=1
    if not used or b-a+1>=16:
        print(("USED" if used else "FREE"),f"0x{a:04x}-0x{b:04x}",b-a+1)
    a=b+1
