#!/usr/bin/env python3
"""Issue144 D: enumerate *unassigned* normal V1 resident executable islands.

This is only a geometry screen: unused assembler addresses can still be used
at runtime and must pass full mixed-call/VICE proof before any installation.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import preprocess,parse_config
from issue144_seek16_v15_normal_resident_feasibility import candidate

PROFILE="v1_balanced"
REGIONS={"REG_LOW":0x2000,"REG_API":0x1000,"REG_KERNEL":0x1E00,
         "REG_GAME":0x0F00,"REG_TABLE":0x4000}

def ranges(mem,begin,end):
    gaps=[];start=None
    for a in range(begin,end+1):
        absent=(a not in mem) if a<end else False
        if absent and start is None:start=a
        if not absent and start is not None:
            gaps.append((start,a-start))
            start=None
    return gaps

def main():
    report,trial=candidate(PROFILE)
    assert trial is not None
    footprint=report["source_bytes"]
    results={}
    candidates=[]
    for layout in ("reference","alternate"):
        cfg=ROOT/"relocatable_source"/PROFILE/("math_config_"+layout+".inc")
        vals=parse_config(cfg)
        source=preprocess(ROOT/"relocatable_source"/PROFILE/"math_relocatable.asm",cfg)
        mem,labels,constants=Assembler().assemble(source)
        rows={}
        for region,length in REGIONS.items():
            lo=vals[region]
            gaps=ranges(mem,lo,lo+length)
            rows[region]=[{"offset":hex(start-lo),"size":size,
                           "begin":hex(start)} for start,size in gaps if size>=footprint]
        results[layout]=rows
    common={}
    for region in REGIONS:
        ref={int(v["offset"],16):v for v in results["reference"][region]}
        alt={int(v["offset"],16):v for v in results["alternate"][region]}
        matches=[]
        for off,a in ref.items():
            for other,b in alt.items():
                left=max(off,other)
                right=min(off+a["size"],other+b["size"])
                if right-left>=footprint:
                    matches.append({"offset":hex(left),"available_bytes":right-left})
        common[region]=sorted(matches,key=lambda r:r["available_bytes"],reverse=True)[:8]
    print(json.dumps({"status":"PASS_UNASSIGNED_RESIDENT_GEOMETRY_SCAN",
                      "candidate_asm_bytes":footprint,"common_holes":common,
                      "individual_layouts":results,
                      "disclaimer":"Unassigned addresses are NOT certified free at runtime; no overwrite or release authorized."},
                     indent=2,sort_keys=True))
if __name__=="__main__":main()
