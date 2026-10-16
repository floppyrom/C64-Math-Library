#!/usr/bin/env python3
"""Issue144 B: inspect possible source-owned secondary tail placement at REG_KERNEL+$1B00.

Snapshot SEGMENTS.csv does not prove current occupancy: generated old image
uses !byte provenance and writes every address, including padding. This script
checks current *assembled* bytes, exact emitted labels, and old segment claims.
It deliberately does not modify production source or declare an owner.
"""
from __future__ import annotations
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler,REV,SIZE
from assemble_sources import preprocess,parse_config
from issue144_u3216_dualtail_direct_dispatch_screen import low_divisor_tail
PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
CAND_BYTES=461
REG_OFFSET=0x1b00

def main():
    report={"status":"PASS_POTENTIAL_KERNEL_PLACEMENT_INVENTORY",
            "qualification":"padding bytes, label starts and historical segment claims only",
            "new_default_claim":False,"locations":{}}
    for profile in PROFILES:
        report["locations"][profile]={}
        with (ROOT/profile/"resident/SEGMENTS.csv").open() as fin:
            segments=list(csv.DictReader(fin))
        for kind in ("reference","alternate"):
            config=ROOT/"relocatable_source"/profile/("math_config_"+kind+".inc")
            vals=parse_config(config)
            src=preprocess(ROOT/"relocatable_source"/profile/"math_relocatable.asm",config)
            mem,labels,const=Assembler().assemble(src)
            start=vals["REG_KERNEL"]+REG_OFFSET
            src_candidate=low_divisor_tail().replace("* = $0800",f"* = ${start:04X}",1)
            compiled,clabels,_=Assembler().assemble(src+src_candidate)
            end=clabels["U3216_LD_END"]
            assert end-start==CAND_BYTES,(profile,kind,end-start)
            old_nonzero=[i for i in range(start,end) if mem.get(i,0)!=0]
            names=[{"name":key,"address":hex(address)} for key,address in labels.items()
                   if start<=address<end]
            ownership=[]
            for rec in segments:
                orig=int(rec["load_address"].replace("$","0x"),16)
                new=orig+start-(0x5b00 if kind=="reference" else 0x3b00)
                # Relative mapping inside the REG_KERNEL region, not global.
                if not 0x4000<=orig<0x5e00:continue
                addr=vals["REG_KERNEL"]+(orig-0x4000)
                a,b=addr,addr+int(rec["bytes"])
                if max(a,start)<min(b,end):
                    ownership.append({"segment":rec["segment"],"start":hex(a),
                                      "end":hex(b),"reason":rec["purpose"][:90]})
            affected=sum(mem.get(i,0)!=compiled.get(i,0) for i in range(start,end))
            region_bounds={"REG_LOW":0x2000,"REG_API":0x1000,
                           "REG_KERNEL":0x1e00,"REG_GAME_API":0x200,
                           "REG_TABLE":0x3c00,"REG_GAME":0xb74}
            zero_runs=[]
            for reg,length in region_bounds.items():
                rs=vals[reg];re=rs+length;cursor=rs
                while cursor<re:
                    if mem.get(cursor,0)!=0:cursor+=1;continue
                    endzero=cursor
                    while endzero<re and mem.get(endzero,0)==0:endzero+=1
                    if endzero-cursor>=461:
                        labels_here=[name for name,pc in labels.items()
                                     if cursor<=pc<endzero]
                        zero_runs.append({"region":reg,
                            "start":hex(cursor),"end_exclusive":hex(endzero),
                            "start_offset":hex(cursor-rs),
                            "bytes":endzero-cursor,
                            "old_labels":labels_here[:10]})
                    cursor=endzero
            zero_runs=sorted(zero_runs,key=lambda x:-x["bytes"])
            print("ZERO SPANS",profile,kind,"candidate_count",len(zero_runs),
                  "largest",zero_runs[0]["bytes"] if zero_runs else 0,flush=True)
            report["locations"][profile][kind]={
              "zero_runs_461":zero_runs[:35],
              "zero_run_461_count":len(zero_runs),
              "start":hex(start),"end_exclusive":hex(end),"candidate_bytes":end-start,
              "existing_nonzero_byte_count":len(old_nonzero),
              "existing_nonzero_examples":[hex(i) for i in old_nonzero[:12]],
              "old_emitted_labels_in_range":names[:25],
              "historical_SEGMENTS_claims":ownership,
              "byte_differences_if_overlaid":affected,
              "all_existing_bytes_are_zero":not old_nonzero,
              "not_proven":"no indirect executable or data references, no IRQ/concurrency proof"}
            print("POTENTIAL RESIDENT",profile,kind,hex(start),hex(end),
                  "nonzero",len(old_nonzero),"labels",len(names),
                  "legacy claims",len(ownership),flush=True)
    print(json.dumps(report,sort_keys=True,indent=2))
if __name__=="__main__":main()
