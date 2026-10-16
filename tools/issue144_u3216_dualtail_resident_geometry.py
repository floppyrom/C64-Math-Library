#!/usr/bin/env python3
"""Issue144 B: physical normal-source region availability for 461-byte dual tail.

Blank RAM outside source-owned regions is NOT automatically valid library RAM.
Report precise vacant spans between U3216_MAIN_END and U3216_D8_BASE, showing
whether the second unrolled core could fit without claiming caller RAM.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"tools"))
from mini6502 import Assembler
from assemble_sources import preprocess,parse_config
P=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")

def holes(mem,start,end):
    spans=[];p=start
    while p<end:
        if p in mem:
            p+=1;continue
        q=p
        while q<end and q not in mem:q+=1
        spans.append({"start":hex(p),"end_exclusive":hex(q),"bytes":q-p})
        p=q
    return spans

def main():
    report={"status":"PASS_GEOMETRY_AUDIT","profiles":{},"candidate_code_bytes":461,
            "no_caller_RAM_promotion_claim":True}
    for profile in P:
        report["profiles"][profile]={}
        for layout in ("reference","alternate"):
            cfg=R/"relocatable_source"/profile/("math_config_"+layout+".inc")
            val=parse_config(cfg)
            code,labels,_=Assembler().assemble(preprocess(R/"relocatable_source"/profile/"math_relocatable.asm",cfg))
            start=labels["U3216_MAIN_END"]
            end=val["REG_KERNEL"]+0x1272
            assert start<end,(profile,layout,hex(start),hex(end))
            h=holes(code,start,end)
            largest=max((x["bytes"] for x in h),default=0)
            report["profiles"][profile][layout]={
               "candidate_bytes":461,
               "main_end":hex(start),"d8_base":hex(end),
               "largest_contiguous_unused_span":largest,
               "candidate_fits_reclaimed_main_to_d8_gap":largest>=461,
               "empty_spans":h}
            print("U3216 RESIDENT GAP",profile,layout,"largest",largest,"candidate",461,flush=True)
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
