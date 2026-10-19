#!/usr/bin/env python3
"""Offline source-linked dual-MUL32 project frontier; CPU-model frames, not PAL."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

FIELDS=("main_ram_total_bytes","zero_page_bytes","peak_frame_math_cycles",
        "p95_frame_math_cycles","total_math_cycles")

class EvidenceError(ValueError): pass

def summarize(report):
    places=report.get("placements") if isinstance(report,dict) else None
    if not isinstance(places,list) or len(places)<2:
        raise EvidenceError("At least two source-linked placements required")
    seen=set()
    options=None
    corpus=None
    counts=None
    all_data={}
    for place in places:
        if not isinstance(place,dict) or place.get("cpu_model_only") is not True or place.get("native_pal_timing") is not False:
            raise EvidenceError("CPU-model evidence only; no PAL claims")
        address=(place.get("code"),place.get("io"))
        if address in seen or not all(isinstance(x,str) and x.startswith("$") for x in address):
            raise EvidenceError("Invalid or repeated relocation")
        seen.add(address)
        observed=(place.get("paired_calls"),place.get("frames"))
        if any(type(x) is not int or x<=0 for x in observed) or counts is not None and observed!=counts:
            raise EvidenceError("Inconsistent frame/call count")
        counts=observed
        digest=place.get("input_corpus_sha256")
        if (not isinstance(digest,str) or len(digest)!=64 or
            any(c not in "0123456789abcdef" for c in digest) or
            corpus is not None and corpus!=digest):
            raise EvidenceError("Missing or mismatched identical-input digest")
        corpus=digest
        per=place.get("per_option")
        if not isinstance(per,dict) or not per or options is not None and set(per)!=options:
            raise EvidenceError("Candidate sets differ between placements")
        options=set(per)
        for name,data in per.items():
            if not isinstance(data,dict) or not isinstance(name,str) or not name:
                raise EvidenceError("Invalid plan")
            measures={key:data.get(key) for key in FIELDS}
            if any(type(value) is not int or value<0 for value in measures.values()):
                raise EvidenceError("Invalid measurement")
            if (measures["main_ram_total_bytes"]==0 or measures["peak_frame_math_cycles"]==0
                or measures["p95_frame_math_cycles"]>measures["peak_frame_math_cycles"]):
                raise EvidenceError("Invalid peak or resource envelope")
            if type(data.get("linked_source_count")) is not int or data["linked_source_count"]<1:
                raise EvidenceError("Missing physical producer count")
            variants=data.get("variant_map")
            shas=data.get("source_sha256")
            if (not isinstance(variants,dict) or set(variants)!={"MATH_UMUL32","MATH_SMUL32"}
                or not isinstance(shas,dict) or set(shas)!=set(variants)
                or any(not isinstance(v,str) or len(v)!=64 or any(c not in "0123456789abcdef" for c in v) for v in shas.values())):
                raise EvidenceError("Source hash/public ABI provenance missing")
            slot=all_data.setdefault(name,{"source":(variants,shas),"values":[]})
            if slot["source"]!=(variants,shas):
                raise EvidenceError("Variant/source drift across relocations")
            slot["values"].append(measures)
    combined={}
    for name,info in sorted(all_data.items()):
        combined[name]={key:(sum(x[key] for x in info["values"]) if key=="total_math_cycles"
                             else max(x[key] for x in info["values"])) for key in FIELDS}
        combined[name]["variant_map"],combined[name]["source_sha256"]=info["source"]
    return {"per_option":combined,"placements":len(places),"paired_calls":counts[0],
            "frames":counts[1],"input_corpus_sha256":corpus,"cpu_model_only":True,
            "physical_pal_feasibility_claim":False}

def frontier(summary):
    plans=summary["per_option"]
    return [name for name in sorted(plans) if not any(
        alt!=name and all(plans[alt][key]<=plans[name][key] for key in FIELDS)
        and any(plans[alt][key]<plans[name][key] for key in FIELDS)
        for alt in plans)]

def select(summary,ram_budget,zp_budget,max_peak_cycles=None,objective="peak"):
    if (objective not in ("peak","ram","zp") or type(ram_budget) is not int or ram_budget<=0
        or type(zp_budget) is not int or not 0<=zp_budget<=254
        or max_peak_cycles is not None and (type(max_peak_cycles) is not int or max_peak_cycles<=0)):
        raise EvidenceError("Invalid objective or resource/frame constraint")
    choices={name:row for name,row in summary["per_option"].items()
             if row["main_ram_total_bytes"]<=ram_budget and row["zero_page_bytes"]<=zp_budget
             and (max_peak_cycles is None or row["peak_frame_math_cycles"]<=max_peak_cycles)}
    if not choices:
        raise EvidenceError("No measured combined plan fits all resource/frame limits")
    order={
        "peak":("peak_frame_math_cycles","p95_frame_math_cycles","total_math_cycles",
                "main_ram_total_bytes","zero_page_bytes"),
        "ram":("main_ram_total_bytes","zero_page_bytes","peak_frame_math_cycles",
               "p95_frame_math_cycles","total_math_cycles"),
        "zp":("zero_page_bytes","main_ram_total_bytes","peak_frame_math_cycles",
              "p95_frame_math_cycles","total_math_cycles")}[objective]
    best=min(choices,key=lambda name:tuple(choices[name][k] for k in order)+(name,))
    return {"choice":best,"objective":objective,"main_ram_budget":ram_budget,
            "zp_budget":zp_budget,"max_peak_math_cycles":max_peak_cycles,
            "measured_envelope":choices[best],"eligible_plans":sorted(choices),
            "physical_pal_feasibility_claim":False}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in-report",required=True,type=Path)
    ap.add_argument("--out",type=Path)
    ap.add_argument("--ram-budget",type=int)
    ap.add_argument("--zp-budget",type=int)
    ap.add_argument("--max-peak-math-cycles",type=int)
    ap.add_argument("--objective",choices=("peak","ram","zp"),default="peak")
    args=ap.parse_args()
    if (args.ram_budget is None)!=(args.zp_budget is None) or (args.max_peak_math_cycles is not None and args.ram_budget is None):
        ap.error("Supply RAM+ZP budgets together, and both with a peak-frame limit")
    report=summarize(json.loads(args.in_report.read_text(encoding="utf-8")))
    result={"summary":report,"pareto_source_plans":frontier(report)}
    if args.ram_budget is not None:
        result["selection"]=select(report,args.ram_budget,args.zp_budget,
                                    args.max_peak_math_cycles,args.objective)
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    else:print(output,end="")

if __name__=="__main__":main()
