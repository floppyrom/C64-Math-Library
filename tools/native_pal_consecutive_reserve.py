#!/usr/bin/env python3
"""Real x64sc PAL deadline sensitivity to *explicit NOP CPU work*.

Run 24 consecutive copies of source-authenticated busiest math frame 8
under VIC display on/off, real line-90 raster IRQ and four SID writes.
Add 0..2048 instruction CPU cycles of NOPs *after the original JSR math
body*, before the original every-frame output/carry oracle. Native CIA
captures real PHI2 elapsed slots including VIC contention.

An injected NOP loop is NOT an actual SID player or rendering equivalent.
The result is a scheduling sensitivity experiment, not a game certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

import frame_evidence_replay
import mixed_seven_d65536_frame as source
import native_installed_d65536_pal as installer
import native_pal_consecutive_busiest as consecutive

PLANS=("fast31-uv2-s65536","fast31-u65536-s65536")
DEFAULT_RESERVES=(0,256,512,768,1024,1536,2048)


def parse_reserves(raw):
    if not isinstance(raw,str) or not raw:
        raise ValueError("Missing non-math CPU reserve list")
    fields=raw.split(",")
    if any(not field.isascii() or not field.isdecimal() for field in fields):
        raise ValueError("Reserves must be ascending comma-separated decimal CPU cycles")
    levels=tuple(int(field) for field in fields)
    if (not levels or levels[0]!=0 or len(levels)!=len(set(levels))
            or levels!=tuple(sorted(levels))
            or any(level < 0 or level > 2048 or level%2 for level in levels)):
        raise ValueError("Require zero baseline and increasing even 0..2048 NOP cycles")
    return levels


def rank(rows,levels,plan,display):
    entries={r["injected_nonmath_nop_cpu_cycles"]:r for r in rows
             if r["plan"]==plan and r["display_enabled"]==display}
    if set(entries)!=set(levels):
        raise AssertionError("Missing native display/plan/reserve sample")
    by_level=[]
    expected_digest=None
    source_sha=None
    for cycles in levels:
        item=entries[cycles]
        if (item["frame_count"]!=24 or item["public_output_error_count"]!=0
                or item["observed_raster_irq_events"]<24
                or item["total_public_calls"]!=576):
            raise AssertionError("Native PAL original public ABI/IRQ evidence incomplete")
        if expected_digest is None:
            expected_digest=item["public_output_sha256"]
            source_sha=(item["qualified_prg_sha256"],
                        item["source_frame_inputs_sha256"])
        elif (item["public_output_sha256"]!=expected_digest or
              (item["qualified_prg_sha256"],item["source_frame_inputs_sha256"])!=source_sha):
            raise AssertionError("Nonmath reserve changed source PRG or public Q/R/C outputs")
        if item["geometry"]["injected_nonmath_nop_cpu_cycles"]!=cycles:
            raise AssertionError("Recorded NOP body not the declared instruction reserve")
        minimum=min(row["deadline_margin_slots"] for row in item["records"])
        if item["nominal_deadline_misses"]!=sum(
            r["nominal_deadline_missed"] for r in item["records"]):
            raise AssertionError("Deadline miss counts inconsistent")
        by_level.append({
            "nonmath_nop_cpu_cycles_per_burst":cycles,
            "worst_cumulative_deadline_margin_slots":minimum,
            "last_deadline_margin_slots":24*consecutive.PAL-item["last_completed_elapsed_slots"],
            "cumulative_deadline_misses":item["nominal_deadline_misses"],
            "actual_raster_irq_events":item["observed_raster_irq_events"],
            "extra_irq_events_due_to_skipped_opportunities":
                item["extra_raster_irq_events_vs_completed_work_items"],
        })
    first_fail=next((r["nonmath_nop_cpu_cycles_per_burst"] for r in by_level
                     if r["cumulative_deadline_misses"]),None)
    return {
        "plan":plan,"vic_display_enabled":display,
        "source_prg_sha256":source_sha[0],
        "public_output_sha256":expected_digest,
        "first_tested_failing_nonmath_nop_cpu_reserve":first_fail,
        "largest_tested_passing_nonmath_nop_cpu_reserve":max(
            (r["nonmath_nop_cpu_cycles_per_burst"] for r in by_level
             if not r["cumulative_deadline_misses"]),default=None),
        "level_results":by_level,
    }


def run(vice,levels):
    if not vice or not Path(vice).is_file():
        raise ValueError("Native pinned x64sc executable required")
    if (not levels or tuple(levels)!=tuple(sorted(set(levels))) or
            levels[0]!=0 or any(type(x) is not int or x%2 or x<0 or x>2048 for x in levels)):
        raise ValueError("Unqualified nonmath NOP reserve choices")
    report=source.complete_report()
    if frame_evidence_replay.replay(report)!=report:
        raise AssertionError("Source linked nine-choice frame evidence does not replay")
    rows=[]
    with tempfile.TemporaryDirectory(prefix="native_pal_reserve_") as td:
        root=Path(td)
        for i,plan in enumerate(PLANS):
            folder=root/plan
            image,entries,proof=installer.build_one(plan,report,folder)
            for j,cycles in enumerate(levels):
                for screen in (False,True):
                    label=f"{plan}_nonmath{cycles:04d}_screen{int(screen)}"
                    row=consecutive.read_monitor(
                        vice,image,entries,folder,label,
                        19100+i*100+j*2+int(screen),
                        display=screen,reserve_cpu_cycles=cycles)
                    if row["qualified_prg_sha256"]!=proof["linked_prg_sha256"]:
                        raise AssertionError("Source-linked PRG digest differs from builder")
                    row["plan"]=plan
                    row["linked_ram_bytes"]=proof["linked_ram_bytes"]
                    row["zero_page_bytes"]=proof["zero_page_bytes"]
                    rows.append(row)
                    print("PAL NOP RESERVE",plan,cycles,screen,
                          row["nominal_deadline_misses"],
                          row["last_completed_elapsed_slots"],flush=True)
    outcomes=[rank(rows,levels,plan,display)
              for plan in PLANS for display in (False,True)]
    if len({x["public_output_sha256"] for x in outcomes})!=1:
        raise AssertionError("Production source plans disagree on public Q/R/C outputs")
    return {
        "schema":"native-pal-24-consecutive-frame8-nonmath-nop-reserve-v1",
        "nominal_pal_slots_per_period":consecutive.PAL,
        "tested_nop_cpu_reserves":list(levels),
        "nop_instruction_cycles_not_physical_cpu_bus_reservations":True,
        "includes_vic_display_and_real_raster_irq_and_sid_io_writes":True,
        "actual_sid_player_or_game_rendering_tested":False,
        "real_application_50hz_certified":False,
        "source_busiest_frame8_repeated_24_times":True,
        "source_profiles":list(PLANS),
        "summaries":outcomes,
        "runs":rows,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reserves",default=",".join(map(str,DEFAULT_RESERVES)))
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    try:
        levels=parse_reserves(args.reserves)
    except ValueError as e:
        ap.error(str(e))
    report=run(os.environ.get("VICE_WRAPPER",""),levels)
    payload=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")


if __name__=="__main__":
    main()
