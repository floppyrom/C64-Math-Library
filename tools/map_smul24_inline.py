#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import preprocess

for p in ("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m"):
    src=ROOT/"relocatable_source"/p/"math_relocatable.asm"
    cfg=ROOT/"relocatable_source"/p/"math_config_reference.inc"
    mem,labels,const=Assembler().assemble(preprocess(src,cfg))
    print("\nPROFILE",p)
    for n in ("S24_c0_1","S24_umult","S24_summation","S24_public_impl","S24_smul24_composed",
              "S24_smul24_xneg","S24_smul24_yneg_only","S24_smul24_nn","S24_smul24_composed_end"):
        print(n,hex(labels[n]))
    end=labels["S24_smul24_composed_end"]
    print("end",hex(end),"next occupied:")
    for a in range(end,min(0x10000,end+0x80)):
        if a in mem and (a==end or a-1 not in mem):
            print(" used starts",hex(a))
