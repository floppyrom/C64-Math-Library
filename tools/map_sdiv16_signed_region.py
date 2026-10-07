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
for n in ["D16F_sg_code_start","D16F_s_zero","D16F_sg_code_end","D16F_cg_code_start","D16F_s_qge2_pp","D16F_quotient_ge_two"]:
    print(n,hex(labels[n]))
print("gap",labels["D16F_cg_code_start"]-labels["D16F_sg_code_end"])
lo=labels["D16F_sg_code_start"]; hi=labels["D16F_cg_code_start"]+0x100
a=lo
while a<=hi:
    used=a in mem; b=a
    while b+1<=hi and ((b+1 in mem)==used):b+=1
    if not used: print("FREE",hex(a),hex(b),b-a+1)
    a=b+1
