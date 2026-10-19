#!/usr/bin/env python3
"""Export a source-reverified pinned C64 math_builder config from measured frames.

This is a *qualified workload snapshot*, not an automatic 56-operation
peak-frame optimizer or evidence of physical PAL/VIC/IRQ/REU timing.
Only complete, source-linked reports at two or more relocations qualify.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
from mixed_frame_frontier import EvidenceError, summarize
from mul32_frame_frontier import select


def address(value, name):
    if type(value) is not int or not 0 <= value <= 65535:
        raise EvidenceError(name + " must be a 16-bit integer address")
    return value


def export_config(report, *, ram_budget, zp_budget,
                  code_base, math_io, zp_base, scratch_base,
                  objective="peak", max_peak_cycles=None):
    """Select one full plan, reassemble at the measured placement, verify PRG.

    No config is emitted if the linked PRG hash, original source SHA, layout
    or resource envelope disagrees with the original public-call evidence.
    """
    report_summary = summarize(report)
    choice = select(report_summary, ram_budget, zp_budget,
                    max_peak_cycles=max_peak_cycles, objective=objective)
    selected = choice["choice"]
    operations = report_summary["operations"]
    location = {key: address(value, key) for key, value in {
        "code_base": code_base, "math_io": math_io, "zp_base": zp_base,
        "scratch_base": scratch_base}.items()}
    matches = [p for p in report["placements"]
               if p["code"] == "$%04X" % code_base
               and p["io"] == "$%04X" % math_io]
    if len(matches) != 1:
        raise EvidenceError("Selected memory placement was not source-qualified")
    place = matches[0]
    tested = place["per_option"][selected]
    if scratch_base != math_io + 0x40:
        # Current signed/unsigned/sqrt mixed benchmark uses IO+64 scratch.
        # Never silently pretend a different scratch layout was measured.
        raise EvidenceError("Scratch placement differs from qualified linked report")
    # The report now records the actual zero-page address (not only count).
    if place.get("zp_base") != "$%04X" % zp_base:
        raise EvidenceError("ZP address differs from qualified linked report")
    if place.get("scratch_base") != "$%04X" % scratch_base:
        raise EvidenceError("Scratch address differs from qualified linked report")
    variants = dict(tested["variant_map"])
    if set(variants) != set(operations):
        raise EvidenceError("Pinned source list omits a public operation")
    config = {
        "target": "c64", "objective": "size",
        "operations": list(operations),
        "pins": dict(sorted(variants.items())),
        "constraints": {"max_ram_bytes": ram_budget,
                        "max_zp_bytes": zp_budget},
        "memory": location,
    }
    index = math_builder.operation_index()
    try:
        plan = math_builder.create_plan(
            index, config["operations"], target="c64", objective="size",
            pins=config["pins"], ram_budget=ram_budget, zp_budget=zp_budget)
        with tempfile.TemporaryDirectory(prefix="qualified_frame_config_") as folder:
            directory = Path(folder)
            manifest = linker.build(plan, directory, memory=location)
            real_hash = hashlib.sha256((directory / "math_selective.prg").read_bytes()).hexdigest()
    except (math_builder.SelectionError, linker.LinkError, OSError) as error:
        raise EvidenceError("The qualified project plan can no longer be linked: " + str(error)) from error
    real_variants = {op["api"]: op["variant"] for op in manifest["operations"]}
    resources = manifest["resource_use"]
    measured_resources = ("main_ram_total_bytes", "zero_page_bytes")
    if (real_variants != variants or
        real_hash != tested["linked_prg_sha256"] or
        len(manifest["link_order"]) != tested["linked_source_count"] or
        any(resources[key] != tested[key] for key in measured_resources)):
        raise EvidenceError("Current binary/physical resources differ from the measured source")
    for api, variant in variants.items():
        source = linker.MODULES[api][variant]["source"]
        if hashlib.sha256((linker.ROOT / source).read_bytes()).hexdigest() != tested["source_sha256"][api]:
            raise EvidenceError("Source hash changed since the public-call qualification: " + api)
    return config, {
        "schema": "qualified-synthetic-frame-installer-evidence-v1",
        "choice": selected, "operations": operations,
        "cpu_model_only": True, "physical_pal_feasibility_claim": False,
        "input_corpus_sha256": report_summary["input_corpus_sha256"],
        "locations_tested": report_summary["placements"],
        "public_calls_per_location": report_summary["paired_calls"],
        "frames_per_location": report_summary["frames"],
        "selected_location": {"code": place["code"], "io": place["io"],
                              "zp_base": place["zp_base"], "scratch_base": place["scratch_base"]},
        "qualified_prg_sha256": real_hash,
        "selected_source_sha256": dict(sorted(tested["source_sha256"].items())),
        "linked_sources": len(manifest["link_order"]),
        "worst_placement_measured_envelope": choice["measured_envelope"],
        "selection": {
            "objective": objective, "ram_budget": ram_budget,
            "zp_budget": zp_budget, "max_peak_math_cycles": max_peak_cycles,
        },
        "limits": ("Measured linked-source CPU-model math-only calls/JSR; "
                   "not physical PAL/VIC-II/SID/IRQ/REU/DMA or program frame timing"),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in-report", type=Path, required=True)
    ap.add_argument("--out-config", type=Path, required=True)
    ap.add_argument("--out-evidence", type=Path, required=True)
    ap.add_argument("--ram-budget", type=int, required=True)
    ap.add_argument("--zp-budget", type=int, required=True)
    ap.add_argument("--max-peak-math-cycles", type=int)
    ap.add_argument("--objective", choices=("peak", "ram", "zp"), default="peak")
    ap.add_argument("--code-base", type=lambda s:int(s, 0), required=True)
    ap.add_argument("--math-io", type=lambda s:int(s, 0), required=True)
    ap.add_argument("--zp-base", type=lambda s:int(s, 0), required=True)
    ap.add_argument("--scratch-base", type=lambda s:int(s, 0), required=True)
    args = ap.parse_args()
    if args.out_config.resolve() == args.out_evidence.resolve():
        ap.error("Config and provenance reports require different output paths")
    try:
        report = json.loads(args.in_report.read_text(encoding="utf-8"))
        config, evidence = export_config(
            report, ram_budget=args.ram_budget, zp_budget=args.zp_budget,
            code_base=args.code_base, math_io=args.math_io, zp_base=args.zp_base,
            scratch_base=args.scratch_base, objective=args.objective,
            max_peak_cycles=args.max_peak_math_cycles)
    except (OSError, ValueError, KeyError) as error:
        ap.error(str(error))
    for path, payload in ((args.out_config, config), (args.out_evidence, evidence)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")


if __name__ == "__main__":
    main()
