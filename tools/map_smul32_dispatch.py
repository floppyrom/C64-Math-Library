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
names=[
"S32V28_api_smul32_speed31_v26","S32V28_api_s31_v26_xpos",
"S32V28_api_s31_v25_bind_q0","S32V28_api_s31_v25_bind_q1",
"S32V28_api_s31_v25_bind_q2","S32V28_api_s31_v25_nn",
"S32V28_q0_kernel","S32V28_q1_kernel","S32V28_q2_kernel"
]
for n in names: print(n,hex(labels[n]))
lo=min(labels[n] for n in names if n in labels)-0x80
hi=max(labels[n] for n in names if n in labels)+0x180
a=lo
while a<=hi:
    used=a in mem; b=a
    while b+1<=hi and ((b+1 in mem)==used): b+=1
    if not used or b-a+1>=16:
        print(("USED" if used else "FREE"),hex(a),hex(b),b-a+1)
    a=b+1
