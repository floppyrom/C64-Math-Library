#!/usr/bin/env python3
"""Native PAL VIC/CIA compare source-qualified *installer-built* 7-API plans.

This is NOT a consecutive 50 Hz demo. All 24 synthetic frames are timed as
independent raster-zero-aligned public-call bursts; no music, IRQ or REU.
Only full source-replayed and installer-hash-identical pinned plans qualify.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

import frame_evidence_replay
import math_builder
import mixed_seven_d65536_frame as crossed
import native_pal_vic_cia_probe as cia
import selective_linker as linker

CHOICES=("fast31-stock-v2","fast31-u65536-s65536","fast31-uv2-s65536")
FRAMES=tuple(range(24))
CODE, IO, ZP = 0x4123, 0xc040, 0x70
PAL=cia.PAL_SLOTS
assert PAL==19656


def build_one(label, report, folder):
    if label not in CHOICES or report.get("basis")!=crossed.BASIS:
        raise ValueError("Unqualified source-linked seven-API D65536 plan")
    entries_report=[p for p in report["placements"]
                    if p["code"]=="$4123" and p["io"]=="$C040"
                    and p["zp_base"]=="$0070" and p["scratch_base"]=="$C080"]
    if len(entries_report)!=1:
        raise ValueError("Unqualified physical installer location")
    measured=entries_report[0]["per_option"][label]
    expected=measured["variant_map"]
    if set(expected)!=set(crossed.OPS):
        raise ValueError("Incomplete source-evidence pins")
    index=math_builder.operation_index()
    plan=math_builder.create_plan(
        index,list(crossed.OPS),objective="size",
        zp_budget=31,ram_budget=16000,
        pins={api[5:]:v for api,v in expected.items()},
    )
    folder.mkdir(parents=True,exist_ok=True)
    manifest=linker.build(plan,folder,memory={
        "code_base":CODE,"math_io":IO,"zp_base":ZP,"scratch_base":IO+0x40,
    })
    image=(folder/"math_selective.prg").read_bytes()
    observed_hash=hashlib.sha256(image).hexdigest()
    entries={row["api"]:int(row["entry"][1:],16) for row in manifest["operations"]}
    pins={row["api"]:row["variant"] for row in manifest["operations"]}
    resource=manifest["resource_use"]
    if (observed_hash!=measured["linked_prg_sha256"]
            or pins!=expected or set(entries)!=set(crossed.OPS)
            or resource["main_ram_total_bytes"]!=measured["main_ram_total_bytes"]
            or resource["zero_page_bytes"]!=measured["zero_page_bytes"]
            or len(manifest["link_order"])!=measured["linked_source_count"]
            or image[:2]!=CODE.to_bytes(2,"little")
            or CODE+len(image)-2>=cia.HARNESS):
        raise AssertionError("Native linked PRG differs from registered frame source")
    for api,variant in expected.items():
        original=linker.MODULES[api][variant]["source"]
        source_hash=hashlib.sha256((linker.ROOT/original).read_bytes()).hexdigest()
        if source_hash!=measured["source_sha256"][api]:
            raise AssertionError("Native source SHA differs: "+api)
    return image,entries,{"label":label,"linked_prg_sha256":observed_hash,
                          "variants":pins,"linked_ram_bytes":resource["main_ram_total_bytes"],
                          "zero_page_bytes":resource["zero_page_bytes"]}


def summarize(rows, labels=CHOICES, frames=FRAMES):
    expected={(label,f,d) for label in labels for f in frames for d in (False,True)}
    actual=[(x["plan"],x["frame"],x["display_enabled"]) for x in rows]
    if (len(actual)!=len(expected) or set(actual)!=expected or
            any(type(x["measured_cia_phi2_slots"]) is not int or
                x["measured_cia_phi2_slots"]<=0 for x in rows)):
        raise ValueError("Missing, repeated or invalid native exact-frame samples")
    by_plan={}
    output_by_frame={}
    for label in labels:
        per=[]
        for frame in frames:
            paired={x["display_enabled"]:x for x in rows
                    if x["plan"]==label and x["frame"]==frame}
            off,on=paired[False],paired[True]
            for key in ("source_frame_inputs_sha256","captured_outputs_sha256",
                        "qualified_prg_sha256","source_linked_calls"):
                if off[key]!=on[key]:
                    raise AssertionError("Paired native display/source evidence mismatch")
            output_by_frame.setdefault(frame,set()).add(on["captured_outputs_sha256"])
            output_by_frame.setdefault((frame,"input"),set()).add(
                on["source_frame_inputs_sha256"])
            if on["measured_cia_phi2_slots"] < off["measured_cia_phi2_slots"]:
                raise AssertionError("Visible VIC unexpectedly faster than control")
            per.append({
                "frame":frame,
                "display_off_slots":off["measured_cia_phi2_slots"],
                "display_on_slots":on["measured_cia_phi2_slots"],
                "visible_vic_overhead_slots":on["measured_cia_phi2_slots"]-off["measured_cia_phi2_slots"],
                "nominal_frame_headroom_slots":PAL-on["measured_cia_phi2_slots"],
                "source_linked_calls":on["source_linked_calls"],
                "output_sha256":on["captured_outputs_sha256"],
            })
        peak=max(per,key=lambda x:x["display_on_slots"])
        by_plan[label]={
            "prg_sha256":next(x["qualified_prg_sha256"] for x in rows if x["plan"]==label),
            "total_public_calls_per_display":sum(x["source_linked_calls"] for x in per),
            "peak_visible_slots":peak["display_on_slots"],
            "peak_frame_index":peak["frame"],
            "worst_nominal_headroom_slots":peak["nominal_frame_headroom_slots"],
            "nominal_deadline_overruns":sum(x["nominal_frame_headroom_slots"]<0 for x in per),
            "per_frame":per,
        }
    if any(len(h)!=1 for h in output_by_frame.values()):
        raise AssertionError("Different source plans produced different public outputs or input history")
    return by_plan


def run(vice,*,frames=FRAMES,labels=CHOICES):
    if not vice or not Path(vice).is_file():
        raise ValueError("Pinned x64sc r46284 is required")
    if frames!=FRAMES or labels!=CHOICES:
        raise ValueError("Production qualification requires complete 24-frame three-plan sweep")
    source_report=crossed.complete_report()
    if frame_evidence_replay.replay(source_report)!=source_report:
        raise AssertionError("Source-linked D65536 frame basis did not replay")
    rows=[]
    sources=[]
    with tempfile.TemporaryDirectory(prefix="d65536_installed_pal_") as td:
        root=Path(td)
        for i,label in enumerate(labels):
            folder=root/label
            image,entries,proof=build_one(label,source_report,folder)
            sources.append(proof)
            for frame in frames:
                for display in (False,True):
                    tag=f"{label}_f{frame:02d}_screen{int(display)}"
                    sample=cia.run_one(
                        vice,image,entries,folder,tag,
                        17100+i*64+frame*2+int(display),
                        frame=frame,display=display)
                    sample["plan"]=label
                    sample["qualified_prg_sha256"]=proof["linked_prg_sha256"]
                    rows.append(sample)
                    print("NATIVE INSTALLED PAL",tag,
                          sample["measured_cia_phi2_slots"],flush=True)
    summary=summarize(rows,labels,frames)
    stock=summary["fast31-stock-v2"]
    both=summary["fast31-u65536-s65536"]
    signed_only=summary["fast31-uv2-s65536"]
    mapped={x["label"]:x for x in sources}
    if (signed_only["peak_visible_slots"]>=both["peak_visible_slots"]
            or signed_only["peak_visible_slots"]>=stock["peak_visible_slots"]
            or signed_only["nominal_deadline_overruns"]!=0
            or mapped["fast31-uv2-s65536"]["linked_ram_bytes"]
               !=mapped["fast31-stock-v2"]["linked_ram_bytes"]
            or mapped["fast31-u65536-s65536"]["linked_ram_bytes"]
               <=mapped["fast31-stock-v2"]["linked_ram_bytes"]):
        raise AssertionError(
            "Signed-only D65536 native worst-frame/linked-RAM Pareto win not reproduced")
    return {
        "schema":"installed-d65536-three-plan-independent-pal-cia-v1",
        "native_emulator":"pinned-x64sc-r46284",
        "nominal_pal_slots":PAL,
        "native_public_calls_per_display":150*len(labels),
        "consecutive_50hz_frames_measured":False,
        "sid_irq_reu_application_work_measured":False,
        "real_application_frame_certified":False,
        "source_report_basis":source_report["basis"],
        "sources":sources,"by_plan":summary,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    result=run(os.environ.get("VICE_WRAPPER",""))
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    else:
        print(output,end="")


if __name__=="__main__":
    main()
