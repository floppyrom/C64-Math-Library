#!/usr/bin/env python3
"""Independently raster-align and native-timestamp every frame of a math trace.

Every synthetic frame is replayed as its *own* source-linked 6510 burst under
pinned PAL x64sc with CIA timers, both with VIC display enabled and disabled.
This is NOT a continuous 50 Hz application loop or IRQ/SID/REU proof.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

import mixed_seven_frame_parity as seven
import mixed_seven_cross_pareto as crossed
from native_seven_frame_installer import build_exact_frame_prg
from native_pal_vic_cia_probe import PAL_SLOTS, run_one

PROFILES = {"compact": 0, "fast31": 31}


def parse_frames(raw: str) -> tuple[int, ...]:
    """Explicitly reject duplicate, missing, out-of-range and malformed frames."""
    if raw == "all":
        return tuple(range(seven.FRAMES))
    if not isinstance(raw, str) or not raw:
        raise ValueError("Frame selector must be 'all' or comma-separated decimal frames")
    pieces = raw.split(",")
    if any(not part.isascii() or not part.isdecimal() for part in pieces):
        raise ValueError("Frame selector requires decimal frames without spaces")
    selected = tuple(int(part) for part in pieces)
    if not selected or len(selected) != len(set(selected)) or any(
        frame < 0 or frame >= seven.FRAMES for frame in selected
    ):
        raise ValueError("Missing, duplicated or out-of-range frame")
    if selected != tuple(sorted(selected)):
        raise ValueError("Frame selector must be ascending")
    return selected


def percentile95(values: list[int]) -> int:
    if not values or any(type(value) is not int or value < 0 for value in values):
        raise ValueError("Expected positive native elapsed-slot samples")
    return sorted(values)[(len(values)*95 + 99)//100-1]


def summarize(rows: list[dict], *, frames: tuple[int, ...], profile: str) -> dict:
    if profile not in PROFILES or not rows:
        raise ValueError("Unknown or empty native sweep")
    expected_keys = {(frame, display) for frame in frames for display in (False, True)}
    got_keys = [(row["frame"], row["display_enabled"]) for row in rows]
    if len(got_keys) != len(expected_keys) or set(got_keys) != expected_keys:
        raise ValueError("Incomplete, duplicated or mixed native PAL frame/display pairs")
    per_frame = []
    for frame in frames:
        off = next(row for row in rows if row["frame"] == frame and not row["display_enabled"])
        on = next(row for row in rows if row["frame"] == frame and row["display_enabled"])
        if (off["captured_outputs_sha256"] != on["captured_outputs_sha256"] or
                off["source_frame_inputs_sha256"] != on["source_frame_inputs_sha256"] or
                off["qualified_prg_sha256"] != on["qualified_prg_sha256"] or
                off["source_linked_calls"] != on["source_linked_calls"]):
            raise AssertionError("Paired native runs used different source or public inputs")
        a, b = off["measured_cia_phi2_slots"], on["measured_cia_phi2_slots"]
        if (type(a) is not int or type(b) is not int or a <= 0 or b <= 0):
            raise ValueError("Invalid native elapsed CIA slots")
        if b < a:
            raise AssertionError("Display-on elapsed slots less than control for frame %d" % frame)
        per_frame.append({
            "frame": frame, "calls": on["source_linked_calls"],
            "display_off_native_slots": a, "display_on_native_slots": b,
            "display_vic_overhead_slots": b-a,
            "nominal_frame_headroom_slots": PAL_SLOTS-b,
            "nominal_deadline_missed": b > PAL_SLOTS,
            "source_frame_inputs_sha256": on["source_frame_inputs_sha256"],
            "output_sha256": on["captured_outputs_sha256"],
        })
    peak = max(per_frame, key=lambda x:(x["display_on_native_slots"],-x["frame"]))
    return {
        "profile": profile, "qualified_prg_sha256": rows[0]["qualified_prg_sha256"],
        "frames_measured": len(frames), "frame_indices": list(frames),
        "native_calls_measured_per_display": sum(row["calls"] for row in per_frame),
        "peak_display_on_native_slots": peak["display_on_native_slots"],
        "peak_display_on_frame": peak["frame"],
        "p95_display_on_native_slots": percentile95([r["display_on_native_slots"] for r in per_frame]),
        "nominal_pal_deadline_misses": sum(r["nominal_deadline_missed"] for r in per_frame),
        "worst_nominal_headroom_slots": PAL_SLOTS-peak["display_on_native_slots"],
        "per_frame": per_frame,
    }


def run(vice: str, *, frames: tuple[int, ...], profiles: tuple[str, ...]) -> dict:
    if not vice or not Path(vice).is_file():
        raise ValueError("Pinned native x64sc executable is required")
    if not frames or any(frame not in range(seven.FRAMES) for frame in frames):
        raise ValueError("Unqualified frame range")
    if not profiles or len(set(profiles)) != len(profiles) or any(x not in PROFILES for x in profiles):
        raise ValueError("Unknown or duplicate native source profile")
    report = crossed.complete_report()
    summaries=[]
    native_runs=[]
    with tempfile.TemporaryDirectory(prefix="native_pal_sweep_") as td:
        root=Path(td)
        for i, profile in enumerate(profiles):
            folder=root/profile
            zp=PROFILES[profile]
            image, entries, proof=build_exact_frame_prg(
                report, folder, zp_budget=zp, frame_optimize="peak")
            rows=[]
            for frame in frames:
                for display in (False,True):
                    tag=f"{profile}_f{frame:02d}_screen{int(display)}"
                    port=14000+i*128+frame*2+int(display)
                    sample=run_one(vice,image,entries,folder,tag,port,
                                   frame=frame,display=display)
                    sample["selected_choice"]=proof["choice"]
                    rows.append(sample)
                    native_runs.append(sample)
                    print("PAL FRAME SAMPLE",tag,
                          sample["measured_cia_phi2_slots"],flush=True)
            summaries.append(summarize(rows,frames=frames,profile=profile))
    for frame in frames:
        hashes={r["captured_outputs_sha256"] for r in native_runs if r["frame"]==frame}
        if len(hashes)!=1:
            raise AssertionError("Different linked sources produced different native results")
    return {
        "schema":"independent-native-pal-vic-cia-frame-sweep-v1",
        "native_pal_probe":True,
        "nominal_pal_cpu_slots":PAL_SLOTS,
        "consecutive_50hz_frames_measured":False,
        "real_application_frame_certified":False,
        "irq_sid_reu_dma_measured":False,
        "frames":list(frames), "profiles":list(profiles),
        "runs":native_runs,
        "summaries":summaries,
        "limitation":("Independent synthetic math bursts, each raster-aligned on a "
                      "separate x64sc invocation; includes operand staging "
                      "and measurement overhead, excludes IRQ/SID/REU and "
                      "other application logic. Not continuous 50 Hz playback."),
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--frames',default='all',help="'all' or ascending comma-separated frame indices")
    ap.add_argument('--profiles',choices=('fast31','compact','both'),default='both')
    ap.add_argument('--out',type=Path)
    args=ap.parse_args()
    try:
        frames=parse_frames(args.frames)
    except ValueError as err:
        ap.error(str(err))
    vice=os.environ.get('VICE_WRAPPER','')
    profiles=("compact","fast31") if args.profiles=='both' else (args.profiles,)
    result=run(vice,frames=frames,profiles=profiles)
    output=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding='utf-8')
    else:
        print(output,end='')


if __name__=='__main__':
    main()
