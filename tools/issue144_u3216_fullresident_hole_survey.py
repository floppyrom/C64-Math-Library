#!/usr/bin/env python3
"""Issue #144 B: source-owned RAM placement survey for 461-byte low-D 32/16 tail.

Only assembled code within the explicit relocatable source regions counts as
potential free resident space. Caller-owned $0800, arbitrary blank pages, I/O,
zero-page and REU registers are never counted. Holes are *candidates*, not
verified dead data or available application resource allocations.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import Assembler
from assemble_sources import preprocess,parse_config
from source_relocation import REGIONS,REGION_DEFAULT
PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
CANDIDATE=461
NAME_LIMITS={"REG_LOW":0x2000,"REG_API":0x1000,"REG_KERNEL":0x1e00,
             "REG_GAME_API":0x0200,"REG_TABLE":0x3c00,"REG_GAME":0x0b74}

def gaps(memory,start,stop):
    output=[];pos=start
    while pos<stop:
        if pos in memory:pos+=1;continue
        end=pos+1
        while end<stop and end not in memory:end+=1
        output.append({"start":pos,"end_exclusive":end,"bytes":end-pos})
        pos=end
    return output

def main():
    report={"status":"PASS_ALL_SOURCE_OWNED_REGION_GEOMETRY_SURVEY",
            "candidate_bytes":CANDIDATE,
            "not_proven":"Holes must still pass referential, relocatability, source ownership and interrupt safety proof",
            "profiles":{}}
    summary={}
    for p in PROFILES:
        report["profiles"][p]={}
        for layout in ("reference","alternate"):
            cfg=R/"relocatable_source"/p/("math_config_"+layout+".inc")
            val=parse_config(cfg)
            program=preprocess(R/"relocatable_source"/p/"math_relocatable.asm",cfg)
            mem,labels,_=Assembler().assemble(program)
            result={}
            for name,start_old,end_old in REGIONS:
                start=val[name];end=start+NAME_LIMITS[name]
                assert end-start==end_old-start_old+1 or name=="REG_KERNEL",(
                   p,layout,name,hex(end-start),hex(end_old-start_old+1))
                h=gaps(mem,start,end)
                eligible=[x for x in h if x["bytes"]>=CANDIDATE]
                result[name]={
                    "range":[hex(start),hex(end)],
                    "mapped_bytes":sum(start<=a<end for a in mem),
                    "largest_gap":max((x["bytes"] for x in h),default=0),
                    "eligible_candidates":[{"start":hex(x["start"]),
                                            "end_exclusive":hex(x["end_exclusive"]),
                                            "bytes":x["bytes"]} for x in eligible],
                    "top5_gaps":[{"start":hex(x["start"]),
                                  "end_exclusive":hex(x["end_exclusive"]),
                                  "bytes":x["bytes"]} for x in
                                 sorted(h,key=lambda v:-v["bytes"])[:5]],
                }
            overall=[(name,x) for name,section in result.items() for x in section["eligible_candidates"]]
            summary[p+"/"+layout]=len(overall)
            report["profiles"][p][layout]={"sections":result,"qualified_hole_count":len(overall)}
            print("REGION SCAN",p,layout,
                  "eligible physical holes",len(overall),
                  "largest",max(v["largest_gap"] for v in result.values()),
                  flush=True)
    report["counts_by_profile_and_map"]=summary
    report["all_six_maps_have_at_least_one_owned_candidate"]=all(summary.values())
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
