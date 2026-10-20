#!/usr/bin/env python3
"""Nine pinned seven-operation source-linked frame plans with opt-in D65536.

All reported CPU-model elapsed call costs are reexecuted on the identical
24-frame/150-call public-ABI trace at TWO relocations. This is a new
independently registered frame-basis option, not a reinterpretation of
the previously validated 16-way source frontier. No physical PAL
feasibility or automatic global 56-operation optimizer is claimed.
"""
from __future__ import annotations

import json
from pathlib import Path
import mixed_seven_frame_parity as seven
import mixed_seven_cross_pareto as crossed

BASIS="seven-api-registered-d65536-nine-source-linked-frame-choices-v1"
OPS=tuple(seven.OPS)
LOCATIONS=tuple(crossed.LOCATIONS)
D65536="link:d65536-hybrid"
UOPS=("MATH_UDIV32_32","MATH_UMOD32_32")
SOPS=("MATH_SDIV32_32","MATH_SMOD32_32")
CONTROL={
    "compact-zerozp":"mul-compact+sqrt-radix4+udiv-compact+sdiv-compact",
    "lowzp-stock-v2":"mul-compact+sqrt-table+udiv-v2+sdiv-v2",
    "fast31-stock-v2":"mul-fast31+sqrt-table+udiv-v2+sdiv-v2",
}


def options():
    """Keep 0ZP and two stock V2 controls, and six D65536 source crosses."""
    crossed_options=crossed.options()
    result={label:dict(crossed_options[key]) for label,key in CONTROL.items()}
    for mul in ("compact","fast31"):
        for fast_unsigned,fast_signed in ((True,False),(False,True),(True,True)):
            label=("lowzp" if mul=="compact" else "fast31")
            label+="-"+("u65536" if fast_unsigned else "uv2")
            label+="-"+("s65536" if fast_signed else "sv2")
            selection=dict(crossed_options[
                "mul-%s+sqrt-table+udiv-v2+sdiv-v2"%mul])
            for api in UOPS if fast_unsigned else ():
                selection[api]=D65536
            for api in SOPS if fast_signed else ():
                selection[api]=D65536
            result[label]=selection
    if len(result)!=9 or len({tuple(x.items()) for x in result.values()})!=9:
        raise AssertionError("Nine-source D65536 frame option set drift")
    for label,choice in result.items():
        if (set(choice)!=set(OPS) or
                choice[UOPS[0]]!=choice[UOPS[1]] or
                choice[SOPS[0]]!=choice[SOPS[1]]):
            raise AssertionError("Incomplete or unshared full public source: "+label)
    if result["compact-zerozp"]!=seven.OPTIONS["compact-everywhere"]:
        raise AssertionError("Historical zero-ZP source comparison drifted")
    if result["fast31-stock-v2"]!=seven.OPTIONS["fast-everywhere"]:
        raise AssertionError("Historical fast full7 source comparison drifted")
    return result


def compare(code,io,zp):
    if (code,io,zp) not in LOCATIONS:
        raise ValueError("D65536 source evidence has only two verified RAM maps")
    return seven.compare(code,io,zp,candidates=options())


def complete_report():
    selections=options()
    measurements=[compare(*place) for place in LOCATIONS]
    first,second=measurements
    if (first["input_corpus_sha256"]!=second["input_corpus_sha256"]
            or set(first["per_option"])!=set(second["per_option"])
            or set(first["per_option"])!=set(selections)
            or first["paired_calls"]!=150 or second["paired_calls"]!=150):
        raise AssertionError("D65536 full-source two-map public-call parity drift")
    return {
        "basis":BASIS,"operations":list(OPS),
        "cpu_model_only":True,
        "physical_pal_frame_qualified":False,
        "candidate_count":9,
        "placements":measurements,
    }


def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    report=json.dumps(complete_report(),sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(report,encoding="utf-8")
    else:
        print(report,end="")


if __name__=="__main__":
    main()
