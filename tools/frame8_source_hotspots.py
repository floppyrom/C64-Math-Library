#!/usr/bin/env python3
"""Source-linked, matched-input frame-8 arithmetic attribution.

Source-model calls are *not* native per-API timing. The separate optional
native sweep is checked for PRG SHA, public call identities/results and exact
24-frame pairing; only its whole-burst CIA PHI2 elapsed slots are reported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import mixed_seven_cross_pareto as crossed
import mixed_seven_frame_parity as seven
from native_pal_vic_cia_probe import expected_byte
from native_pal_vic_cia_sweep import summarize as summarize_native

PROFILE_LABELS = {
    "compact": "mul-compact+sqrt-table+udiv-compact+sdiv-compact",
    "fast31": "mul-fast31+sqrt-table+udiv-v2+sdiv-v2",
}
CODE, IO, ZP = 0x4123, 0xc040, 0x70
PAL_FRAME = 19656
JSR_CYCLES = 6


def divisor_input_class(api, raw_y):
    """Input-class triage only; no claim of a measured native instruction path."""
    if api not in seven.OPS[3:] or type(raw_y) is not int or not 0 <= raw_y < 2**32:
        return None
    signed = api in seven.OPS[5:]
    value = raw_y-(1<<32) if signed and (raw_y & 0x80000000) else raw_y
    return ("zero" if value == 0 else
            ("negative-" if value < 0 else "positive-") +
            ("narrow16" if abs(value) <= 0xffff else "wide32"))


def model_calls(source, frame=8):
    if frame not in range(seven.FRAMES) or type(frame) is not int:
        raise ValueError("Frame must be an existing source-benchmark frame")
    if source not in PROFILE_LABELS:
        raise ValueError("Unqualified linked source plan")
    label = PROFILE_LABELS[source]
    measured = seven.evaluate(label, CODE, IO, ZP, candidates=crossed.options())
    row = measured["manifest"]["resource_use"]
    call_rows = [c for c in measured["calls"] if c.frame == frame]
    scenario = [x for x in seven.scenario() if x[0] == frame]
    if ([c.key for c in call_rows] !=
            [(x[0], x[1], x[2], x[-1]) for x in scenario]):
        raise AssertionError("Actual linked benchmark public-call identities drifted")
    return {
        "source": source, "label": label, "frame": frame,
        "source_prg_sha256": measured["linked_prg_sha256"],
        "per_api_source_sha256": measured["source_sha256"],
        "main_ram_total_bytes": row["main_ram_total_bytes"],
        "zero_page_bytes": row["zero_page_bytes"],
        "timing_basis": "linked-cpu-model-public-entry-through-rts-plus-jsr",
        "calls": [
            {"frame": c.frame, "ordinal": c.ordinal,
             "operation": c.operation, "input_id": c.input_id,
             "operand_x_u32_hex": "%08X" % original[3],
             "operand_y_u32_hex": "%08X" % original[4],
             "sqrt_n_u16_hex": "%04X" % original[5],
             "divisor_input_class": divisor_input_class(c.operation, original[4]),
             "source_variant": c.variant,
             "entry_through_rts_cycles": c.cycles,
             "math_and_jsr_cycles": c.cycles + JSR_CYCLES}
            for c, original in zip(call_rows, scenario)
        ],
    }


def rank_attribution(compact, fast):
    if (compact["source"] != "compact" or fast["source"] != "fast31"
            or compact["frame"] != fast["frame"]):
        raise ValueError("Need paired compact and FAST31 source traces at one frame")
    left, right = compact["calls"], fast["calls"]
    if (len(left) != len(right) or not left or
            any((a["frame"], a["ordinal"], a["operation"], a["input_id"]) !=
                (b["frame"], b["ordinal"], b["operation"], b["input_id"])
                for a, b in zip(left, right))):
        raise ValueError("Source plans must use identical public calls and input IDs")
    by_api = []
    for operation in seven.OPS:
        matched = [(a, b) for a, b in zip(left, right) if b["operation"] == operation]
        if not matched:
            raise ValueError("Missing selected public source family " + operation)
        before = sum(a["math_and_jsr_cycles"] for a, _ in matched)
        after = sum(b["math_and_jsr_cycles"] for _, b in matched)
        by_api.append({
            "operation": operation, "calls": len(matched),
            "compact_model_math_cycles": before,
            "fast31_model_math_cycles": after,
            "model_math_cycles_saved": before - after,
            "worst_fast31_model_call_cycles": max(
                b["math_and_jsr_cycles"] for _, b in matched),
        })
    by_api.sort(key=lambda row: (-row["fast31_model_math_cycles"],
                                 row["operation"]))
    individual = [
        {"ordinal": b["ordinal"], "operation": b["operation"],
         "input_id": b["input_id"],
         "operand_x_u32_hex": b.get("operand_x_u32_hex"),
         "operand_y_u32_hex": b.get("operand_y_u32_hex"),
         "sqrt_n_u16_hex": b.get("sqrt_n_u16_hex"),
         "divisor_input_class": b.get("divisor_input_class"),
         "compact_math_model_cycles": a["math_and_jsr_cycles"],
         "fast31_math_model_cycles": b["math_and_jsr_cycles"],
         "math_model_cycles_saved": a["math_and_jsr_cycles"] - b["math_and_jsr_cycles"]}
        for a, b in zip(left, right)
    ]
    individual.sort(key=lambda row: (-row["fast31_math_model_cycles"],
                                     row["ordinal"]))
    before = sum(x["math_and_jsr_cycles"] for x in left)
    after = sum(x["math_and_jsr_cycles"] for x in right)
    if sum(a["compact_model_math_cycles"] for a in by_api) != before or (
        sum(a["fast31_model_math_cycles"] for a in by_api) != after
    ):
        raise AssertionError("Model per-operation call cost does not reconcile")
    return {
        "schema": "source-linked-frame-hotspots-v1",
        "frame": fast["frame"],
        "public_calls": len(left),
        "compact_source_prg_sha256": compact["source_prg_sha256"],
        "fast31_source_prg_sha256": fast["source_prg_sha256"],
        "model_math_and_jsr_cycles_compact": before,
        "model_math_and_jsr_cycles_fast31": after,
        "model_math_and_jsr_cycles_saved": before-after,
        "per_operation_ranked_by_fast31_model_cycles": by_api,
        "per_call_ranked_by_fast31_model_cycles": individual,
        "native_per_call_timing_measured": False,
        "no_real_pal_frame_certification": True,
    }


def native_sweep_attribution(report, compact, fast, *, frame=8):
    if (report.get("schema") != "independent-native-pal-vic-cia-frame-sweep-v1"
            or report.get("real_application_frame_certified") is not False
            or report.get("consecutive_50hz_frames_measured") is not False
            or report.get("profiles") != ["compact", "fast31"]
            or report.get("frames") != list(range(seven.FRAMES))
            or report.get("irq_sid_reu_dma_measured") is not False):
        raise ValueError("Expected the registered complete 24-frame native sweep")
    rows = report.get("runs")
    if not isinstance(rows, list) or len(rows) != 4*seven.FRAMES:
        raise ValueError("Missing four runs for every source frame")
    expected_inputs = {}
    expected_outputs = {}
    for idx in range(seven.FRAMES):
        history = [row for row in seven.scenario() if row[0] == idx]
        expected_inputs[idx] = hashlib.sha256(json.dumps(
            [row[-1] for row in history],separators=(",", ":")).encode()).hexdigest()
        expected_outputs[idx] = hashlib.sha256(bytes(
            b for row in history for b in expected_byte(row[2], row[3], row[4], row[5])
        )).hexdigest()
    for item in rows:
        profile = item.get("name", "").split("_f")[0]
        if profile not in PROFILE_LABELS:
            raise ValueError("Native sweep includes unknown source configuration")
        origin = compact if profile == "compact" else fast
        frame_idx = item.get("frame")
        if type(frame_idx) is not int or frame_idx not in expected_inputs:
            raise ValueError("Unqualified native source-frame index")
        count = len([x for x in seven.scenario() if x[0] == frame_idx])
        if (item.get("qualified_prg_sha256") != origin["source_prg_sha256"]
                or item.get("selected_choice") != origin["label"]
                or item.get("source_frame_inputs_sha256") != expected_inputs[frame_idx]
                or item.get("captured_outputs_sha256") != expected_outputs[frame_idx]
                or item.get("source_linked_calls") != count
                or item.get("nominal_pal_frame_slots") != PAL_FRAME
                or item.get("limited_probe_not_application_frame_qualification") is not True):
            raise ValueError("Native evidence and measured source PRG/input/output mismatch")
    native_by_profile = {}
    for source in ("compact", "fast31"):
        these = [x for x in rows if x["name"].startswith(source+"_f")]
        summary = summarize_native(these, frames=tuple(range(seven.FRAMES)), profile=source)
        summary_present = [s for s in report.get("summaries", [])
                           if s.get("profile") == source]
        if summary_present != [summary]:
            raise ValueError("Native report summary inconsistent with source-linked frame runs")
        selected = next(s for s in summary["per_frame"] if s["frame"] == frame)
        native_by_profile[source] = {
            "whole_burst_cia_display_on_slots": selected["display_on_native_slots"],
            "whole_burst_cia_display_off_slots": selected["display_off_native_slots"],
            "display_on_vic_overhead_slots": selected["display_vic_overhead_slots"],
            "nominal_19656_slot_margin": selected["nominal_frame_headroom_slots"],
            "all_24_frame_peak_cia_slots": summary["peak_display_on_native_slots"],
            "all_24_frame_peak_index": summary["peak_display_on_frame"],
            "all_24_frame_deadline_misses": summary["nominal_pal_deadline_misses"],
        }
    return {
        "provenance_check": "linked-PRG-source-and-public-call-output-hashes-match",
        "native_timing_basis": "pinned-pal-x64sc-cia-phi2-whole-burst-only",
        "separate_native_per_api_timing_available": False,
        "real_application_frame_certified": False,
        "native_whole_burst_for_selected_frame": native_by_profile,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frame",type=int,default=8)
    ap.add_argument("--native-sweep",type=Path,
                    help="optional independently captured exact 24-frame PAL JSON")
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    try:
        a=model_calls("compact",args.frame)
        b=model_calls("fast31",args.frame)
        report=rank_attribution(a,b)
        if args.native_sweep:
            data=json.loads(args.native_sweep.read_text(encoding="utf-8"))
            report["native_whole_burst_evidence"]=native_sweep_attribution(
                data,a,b,frame=args.frame)
    except (ValueError,AssertionError,KeyError,OSError) as exc:
        ap.error(str(exc))
    output=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    else:
        print(output,end="")


if __name__=="__main__":
    main()
