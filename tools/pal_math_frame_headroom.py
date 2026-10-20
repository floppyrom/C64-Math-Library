#!/usr/bin/env python3
"""Conservative PAL CPU-slot preflight for REPLAY-VERIFIED arithmetic frames.

A source-linked CPU-model math peak above 312*63 cannot fit into that many
nominal PAL frame CPU slots as modeled. A peak below the limit proves NOTHING
about VIC-II steals, badlines, IRQ/SID, REU DMA, machine-code placement or
actual 50 Hz playback. This tool never reports physical timing certification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from mixed_frame_frontier import summarize
from frame_evidence_replay import replay

PAL_LINES = 312
PAL_CYCLES_PER_LINE = 63
PAL_FRAME_SLOTS = PAL_LINES * PAL_CYCLES_PER_LINE


def model_headroom(summary, *, reserve_cycles=0, ram_budget=None, zp_budget=None):
    """Rank source-measured plans against a necessary, not sufficient bound.

    The caller MUST replay() the original source-linked report before using
    this analysis to publish a selection. Passing a summary alone never
    establishes provenance or native correctness.
    """
    if type(reserve_cycles) is not int or not 0 <= reserve_cycles < PAL_FRAME_SLOTS:
        raise ValueError("Nonmath reserve must be a nonnegative integer below PAL slots")
    if (ram_budget is None) != (zp_budget is None):
        raise ValueError("RAM and ZP budgets must be provided together")
    for label, number in (("RAM", ram_budget), ("ZP", zp_budget)):
        if number is not None and (type(number) is not int or number < 0):
            raise ValueError(label + " budget must be a nonnegative integer")
    if summary.get("cpu_model_only") is not True or summary.get("physical_pal_feasibility_claim") is not False:
        raise ValueError("Expected source-measured arithmetic-only summary")
    available = PAL_FRAME_SLOTS - reserve_cycles
    plans = []
    for name, row in summary["per_option"].items():
        ram, zp, peak = (row["main_ram_total_bytes"], row["zero_page_bytes"],
                         row["peak_frame_math_cycles"])
        if (ram_budget is not None and ram > ram_budget) or (zp_budget is not None and zp > zp_budget):
            continue
        free = available - peak
        plans.append({
            "choice": name,
            "linked_main_ram_bytes": ram,
            "zero_page_bytes": zp,
            "measured_peak_math_cycles": peak,
            "reserved_nonmath_cycles": reserve_cycles,
            "nominal_slots_left_after_math_and_reserve": free,
            "classification": ("math-model-over-budget" if free < 0
                               else "within-nominal-model-budget-PAL-unverified"),
        })
    plans.sort(key=lambda p: (p["measured_peak_math_cycles"],
                              p["linked_main_ram_bytes"], p["choice"]))
    under = sum(p["nominal_slots_left_after_math_and_reserve"] >= 0 for p in plans)
    return {
        "schema": "pal-arithmetic-headroom-preflight-v1",
        "timing_basis": "source-linked-cpu-model-arithmetic-only",
        "physical_pal_timing_certified": False,
        "pal_raster_lines": PAL_LINES,
        "cycles_per_raster_line": PAL_CYCLES_PER_LINE,
        "nominal_pal_cpu_slots": PAL_FRAME_SLOTS,
        "reserved_nonmath_cycles": reserve_cycles,
        "math_budget_cycles": available,
        "operations": summary["operations"],
        "input_corpus_sha256": summary["input_corpus_sha256"],
        "relocations_checked": summary["placements"],
        "synthetic_frames": summary["frames"],
        "calls_per_relocation": summary["paired_calls"],
        "ram_budget_bytes": ram_budget,
        "zp_budget_bytes": zp_budget,
        "eligible_plans": len(plans),
        "plans_with_nonnegative_model_headroom": under,
        "plans_exceeding_nominal_math_budget": len(plans) - under,
        "plans": plans,
        "interpretation": ("A positive number is unallocated nominal slots, NOT "
                           "PAL/VIC-II/IRQ/SID/REU feasibility or native timing. "
                           "A negative number identifies a source-model "
                           "arithmetic workload overrun at the measured frame."),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in-report", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--reserve-nonmath-cycles", type=int, default=0)
    ap.add_argument("--ram-budget", type=int)
    ap.add_argument("--zp-budget", type=int)
    ap.add_argument("--require-model-headroom", action="store_true",
                    help="exit 2 if no measured, budget-eligible plan remains")
    args = ap.parse_args()
    try:
        report = json.loads(args.in_report.read_text(encoding="utf-8"))
        # Reject forged frame peaks, source maps, input histories and layout.
        measured = replay(report)
        output = model_headroom(
            summarize(measured), reserve_cycles=args.reserve_nonmath_cycles,
            ram_budget=args.ram_budget, zp_budget=args.zp_budget)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        ap.error(str(exc))
    output["source_replay_verified"] = True
    payload = json.dumps(output, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    if args.require_model_headroom and not output["plans_with_nonnegative_model_headroom"]:
        ap.exit(2, "No budget-eligible plan meets even the nominal PAL arithmetic bound\n")


if __name__ == "__main__":
    main()
