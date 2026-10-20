#!/usr/bin/env python3
"""Offline 16-way full-source Pareto sweep for seven linked public C64 APIs.

The registered production replay workload retains its existing FOUR candidate
plans. This separate experiment crosses independent full64 MUL, ISQRT16
lookup strategy, unsigned DIV/MOD and signed DIV/MOD source decisions, and
runs the SAME fully validated public-call corpus across two physical maps.
It must NOT be accepted as production timing until separately replay-registered.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import mixed_seven_frame_parity as seven

BASIS = "seven-api-sixteen-way-fully-crossed-linked-math-only-frame-research"
OPS = tuple(seven.OPS)
LOCATIONS = ((0x2000, 0xc000, 0x50), (0x4123, 0xc040, 0x70))

MUL = {"compact": seven.COMPACT_MUL, "fast31": seven.FAST_MUL}
SQRT = {"radix4": "link:radix4-zerozp", "table": "link:square-table"}
UDIV = {
    "compact": ("link:shared-aligned-zerozp", "link:shared-aligned-zerozp"),
    "v2": ("link:v2-lowdivisor-hybrid", "link:v2-lowdivisor-hybrid"),
}
SDIV = {
    "compact": ("link:portable-zerozp", "link:portable-zerozp"),
    "v2": ("link:v2-hybrid-signed", "link:v2-hybrid-signed"),
}


def options():
    """Enumerate all 2×2×2×2 combinations, preserving complete shared sources."""
    plans = {}
    for mk, sq, ud, sd in itertools.product(MUL, SQRT, UDIV, SDIV):
        label = "mul-%s+sqrt-%s+udiv-%s+sdiv-%s" % (mk, sq, ud, sd)
        variants = MUL[mk] + (SQRT[sq],) + UDIV[ud] + SDIV[sd]
        if len(variants) != len(OPS):
            raise AssertionError("Seven-operation cross has incomplete pins")
        plans[label] = dict(zip(OPS, variants))
    if len(plans) != 16 or len({tuple(p.items()) for p in plans.values()}) != 16:
        raise AssertionError("Crossed seven-API source set collapsed")
    return plans


BASELINE_MAP = {
    "compact-everywhere": "mul-compact+sqrt-radix4+udiv-compact+sdiv-compact",
    "fast-mul-compact-div": "mul-fast31+sqrt-table+udiv-compact+sdiv-compact",
    "compact-mul-fast-div": "mul-compact+sqrt-radix4+udiv-v2+sdiv-v2",
    "fast-everywhere": "mul-fast31+sqrt-table+udiv-v2+sdiv-v2",
}


def compare(code, io, zp):
    """Rebuild exactly the pinned sixteen linked plans at a given RAM map."""
    return seven.compare(code, io, zp, candidates=options())


def complete_report():
    """Measure each complete project; do not estimate by summing API averages."""
    choices = options()
    for old, new in BASELINE_MAP.items():
        if choices[new] != seven.OPTIONS[old]:
            raise AssertionError("Previously qualified source plan changed: " + old)
    output = {
        "basis": BASIS, "operations": list(OPS),
        "cpu_model_only": True, "physical_pal_frame_qualified": False,
        "candidate_count": len(choices),
        "placements": [compare(code, io, zp)
                       for code, io, zp in LOCATIONS],
    }
    a, b = output["placements"]
    if a["input_corpus_sha256"] != b["input_corpus_sha256"]:
        raise AssertionError("Crossed projects did not replay identical public calls")
    if set(a["per_option"]) != set(b["per_option"]) or len(a["per_option"]) != 16:
        raise AssertionError("Crossed plans missing from a measured relocation")
    return output


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    report = json.dumps(complete_report(), sort_keys=True, indent=2) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
