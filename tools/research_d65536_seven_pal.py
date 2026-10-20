#!/usr/bin/env python3
"""Research-only *whole seven-operation* source-exact native PAL frame comparison.

Builds a separate linked research image by temporarily substituting the
unregistered D=65536 source assemblers into only four V2-hybrid public
modules, with their true +96-byte geometry. This alters the local Python
build process, NOT production MODULES, the operation catalog, V1-V5 or the
installer. The resulting legacy-shaped linker manifest is NOT independently
production source-qualified: explicit research source hash is mandatory.
"""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

import math_builder
import selective_linker as linker
import mixed_seven_cross_pareto as crossed
import mixed_seven_frame_parity as seven
import native_seven_frame_installer as native_builder
import native_pal_vic_cia_probe as cia
import research_d65536_hybrid as research

OPS=tuple(seven.OPS)
CODE, IO, ZP = native_builder.CODE, native_builder.IO, native_builder.ZP
CHOICE="mul-fast31+sqrt-table+udiv-v2+sdiv-v2"
VARIANT_BY_API=crossed.options()[CHOICE]
PAIRED={"MATH_UDIV32_32":"link:v2-lowdivisor-hybrid",
        "MATH_UMOD32_32":"link:v2-lowdivisor-hybrid",
        "MATH_SDIV32_32":"link:v2-hybrid-signed",
        "MATH_SMOD32_32":"link:v2-hybrid-signed"}
PAL=312*63


def patched_unsigned(code,io,zp,root=linker.ROOT):
    machine,entries,end=research.assemble_unsigned(code,io,zp,root)
    return machine,entries,[{"name":"KERNEL_CODE","start":"$%04X"%code,
                             "bytes":len(machine)}],end


def patched_signed(code,io,zp,root=linker.ROOT):
    machine,entries,end=research.assemble_signed(code,io,zp,root)
    return machine,entries,[{"name":"KERNEL_CODE","start":"$%04X"%code,
                             "bytes":len(machine)}],end


def research_source_image(folder, *, use_candidate=True):
    """Temporary source-planner override; build is deliberately unregistered."""
    index=math_builder.operation_index()
    plan=math_builder.create_plan(
        index,list(OPS),objective="size",zp_budget=31,ram_budget=16000,
        pins={api[5:]:variant for api,variant in VARIANT_BY_API.items()})
    with ExitStack() as stack:
        for api, variant in (PAIRED.items() if use_candidate else ()):
            rec=linker.MODULES[api][variant]
            size=(research.IMAGE_BYTES if api.startswith("MATH_U")
                  else research.SIGNED_IMAGE_BYTES)
            stack.enter_context(patch.dict(rec,{"segments":(("KERNEL_CODE",size),)}))
        if use_candidate:
            stack.enter_context(patch.object(linker.hybrid_u3232,"assemble",
                                             side_effect=patched_unsigned))
            stack.enter_context(patch.object(linker.signed_u3232,"assemble",
                                             side_effect=patched_signed))
        manifest=linker.build(plan,folder,memory={
            "code_base":CODE,"math_io":IO,"scratch_base":IO+0x40,
            "zp_base":ZP})
    image=(folder/"math_selective.prg").read_bytes()
    entries={op["api"]:int(op["entry"][1:],16) for op in manifest["operations"]}
    pins={op["api"]:op["variant"] for op in manifest["operations"]}
    if pins!=VARIANT_BY_API or set(entries)!=set(OPS):
        raise AssertionError("Seven-source research pins or public exports changed")
    if image[:2]!=CODE.to_bytes(2,"little") or CODE+len(image)-2>=cia.HARNESS:
        raise AssertionError("Research linked image collides with native PAL harness")
    digest=hashlib.sha256(image).hexdigest()
    resource=manifest["resource_use"]
    return image,entries,{
        "research_linked_prg_sha256":digest,
        "research_source_dispatch_sha256":hashlib.sha256(
            (research.ROOT/"tools/research_d65536_hybrid.py").read_bytes()).hexdigest(),
        "selected_public_source_variants":pins,
        "main_ram_bytes":resource["main_ram_total_bytes"],
        "zero_page_bytes":resource["zero_page_bytes"],
        "production_builder_source_qualified":False,
        "research_only_with_temporarily_injected_source_emitters":use_candidate,
    }


def run(vice, frames):
    if not vice or not Path(vice).is_file():
        raise ValueError("Require pinned x64sc as VICE_WRAPPER")
    if not frames or any(type(f) is not int or f not in range(seven.FRAMES) for f in frames):
        raise ValueError("Require qualified synthetic frame indices")
    report=crossed.complete_report()
    rows=[]
    with tempfile.TemporaryDirectory(prefix="d65536_whole_pal_") as td:
        root=Path(td)
        old_binary,old_entries,proof=native_builder.build_exact_frame_prg(
            report,root/"baseline",zp_budget=31,frame_optimize="peak")
        if proof["choice"]!=CHOICE:
            raise AssertionError("Production reference selection moved")
        # Match source geometry against *the same pinned linker plan*.
        # The production frame report counts conservative worst-placement
        # envelopes which need not equal one particular linker's occupied RAM.
        # Byte-identically reconcile the control image to the actual builder.
        baseline_dir=root/"source-control"
        baseline_dir.mkdir()
        control_binary,control_entries,control_proof=research_source_image(
            baseline_dir,use_candidate=False)
        if (control_binary!=old_binary or control_entries!=old_entries):
            raise AssertionError(
                "Same source-pinned production/control builds differ: "
                f"CLI={proof['qualified_prg_sha256']}, "
                f"plain_link={control_proof['research_linked_prg_sha256']}, "
                f"entries_equal={control_entries==old_entries}")
        research_dir=root/"research"
        research_dir.mkdir()
        new_binary,new_entries,new_proof=research_source_image(research_dir)
        if new_proof["zero_page_bytes"]!=control_proof["zero_page_bytes"]:
            raise AssertionError("Research changed mixed-project ZP envelope")
        old_ram=control_proof["main_ram_bytes"]
        if new_proof["main_ram_bytes"]!=old_ram+192:
            raise AssertionError(
                "Research full-image RAM is not two +96-byte source slots: "
                f"control_ram={old_ram} new_ram={new_proof['main_ram_bytes']} "
                f"control_prg={len(control_binary)-2} new_prg={len(new_binary)-2}")
        for candidate_idx,(name,image,entries) in enumerate(
            (("stock",old_binary,old_entries),
             ("d65536",new_binary,new_entries))
        ):
            for frame in frames:
                for display in (False,True):
                    key=f"{name}_f{frame:02d}_display_{int(display)}"
                    row=cia.run_one(vice,image,entries,root,key,
                                    15700+candidate_idx*100+frame*2+int(display),
                                    display=display,frame=frame)
                    row["configuration"]=name
                    rows.append(row)
                    print("NATIVE SEVEN D65536 FRAME",key,
                          row["measured_cia_phi2_slots"],flush=True)
        by_config={}
        for name in ("stock","d65536"):
            frame_rows=[]
            for frame in frames:
                subset={row["display_enabled"]:row for row in rows
                        if row["configuration"]==name and row["frame"]==frame}
                if set(subset)!={False,True}:
                    raise AssertionError("Unpaired whole-frame visible PAL samples")
                off,on=subset[False],subset[True]
                if (on["captured_outputs_sha256"]!=off["captured_outputs_sha256"]
                        or on["source_frame_inputs_sha256"]!=off["source_frame_inputs_sha256"]):
                    raise AssertionError("Research display control changed public outcomes")
                frame_rows.append({
                    "frame":frame,"display_on_slots":on["measured_cia_phi2_slots"],
                    "display_off_slots":off["measured_cia_phi2_slots"],
                    "nominal_pal_margin":PAL-on["measured_cia_phi2_slots"],
                    "public_output_sha256":on["captured_outputs_sha256"],
                    "input_history_sha256":on["source_frame_inputs_sha256"],
                })
            by_config[name]=frame_rows
        paired=[]
        for a,b in zip(by_config["stock"],by_config["d65536"]):
            if ((a["frame"],a["public_output_sha256"],a["input_history_sha256"])!=
                (b["frame"],b["public_output_sha256"],b["input_history_sha256"])):
                raise AssertionError("Baseline/candidate source history or public outputs diverged")
            paired.append({
                "frame":a["frame"],"stock_visible_slots":a["display_on_slots"],
                "research_visible_slots":b["display_on_slots"],
                "native_visible_slots_saved":a["display_on_slots"]-b["display_on_slots"],
                "stock_nominal_margin":a["nominal_pal_margin"],
                "research_nominal_margin":b["nominal_pal_margin"],
            })
    selected=next((r for r in paired if r["frame"]==8),None)
    if selected is None:
        raise AssertionError("Synthetic frame 8 missing")
    return {
        "schema":"research-d65536-seven-api-native-pal-24-bursts-v1",
        "native_pal_vic_cia_timing_measured":True,
        "real_50hz_game_or_demo_certified":False,
        "production_builder_variant_registered":False,
        "full_source_registration_provenance_trusted":False,
        "baseline_production_prg_sha256":proof["qualified_prg_sha256"],
        "baseline_reconstructed_from_identical_pinned_plan":True,
        "research_additional_linked_ram_bytes":new_proof["main_ram_bytes"]-old_ram,
        "research_linked_source_evidence":new_proof,
        "frame8":selected,
        "peak_stock_visible_slots":max(x["stock_visible_slots"] for x in paired),
        "peak_research_visible_slots":max(x["research_visible_slots"] for x in paired),
        "stock_nominal_deadline_misses":sum(x["stock_nominal_margin"]<0 for x in paired),
        "research_nominal_deadline_misses":sum(x["research_nominal_margin"]<0 for x in paired),
        "paired_frames":paired,
    }


def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path)
    ap.add_argument("--frames",default="all")
    args=ap.parse_args()
    frames=tuple(range(seven.FRAMES)) if args.frames=="all" else tuple(
        int(part) for part in args.frames.split(","))
    result=run(os.environ.get("VICE_WRAPPER",""),frames)
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    else:
        print(output,end="")


if __name__=="__main__":
    main()
