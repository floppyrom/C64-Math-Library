#!/usr/bin/env python3
"""Fail-closed opt-in peak-frame selection through the real math_builder CLI.

This accepts *qualified complete linked-image evidence* only. It never
converts means or per-operation worsts into a fictitious frame schedule.
The selected image and its public API are revalidated before publication.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from frame_qualified_config import export_config
from mixed_frame_frontier import EvidenceError


def run(args, cfg, names, pins, constraints, workloads, index):
    import math_builder
    import selective_linker as linker

    if not args.build or args.measure or args.preview:
        raise EvidenceError("Frame qualification requires --build; no --preview/--measure")
    if (pins or workloads is not None or args.calls
            or args.pin):
        raise EvidenceError("Frame mode derives all pins; no manual pins or workload means")
    if args.target and args.target != "c64" or cfg.get("target", "c64") != "c64":
        raise EvidenceError("Only the source-qualified stock C64 target is available")
    report_path = args.frame_report or cfg.get("frame_report")
    if not isinstance(report_path, (str, Path)) or not str(report_path):
        raise EvidenceError("Frame mode needs --frame-report or config.frame_report")
    memory = cfg.get("memory")
    required = {"code_base", "math_io", "zp_base", "scratch_base"}
    if not isinstance(memory, dict) or set(memory) != required:
        raise EvidenceError("Frame mode needs exact qualified code/I-O/ZP/scratch map")
    budget_ram = args.ram_budget if args.ram_budget is not None else constraints.get("max_ram_bytes")
    budget_zp = args.zp_budget if args.zp_budget is not None else constraints.get("max_zp_bytes")
    if budget_ram is None or budget_zp is None:
        raise EvidenceError("Frame mode requires explicit RAM and zero-page budgets")
    limit = args.frame_max_cycles if args.frame_max_cycles is not None else constraints.get("max_peak_math_cycles")
    optimize = args.frame_optimize or cfg.get("frame_optimize", "peak")
    if optimize not in ("peak", "ram", "zp"):
        raise EvidenceError("Unsupported qualified frame optimization goal")
    data = json.loads(Path(report_path).read_text(encoding="utf-8"))
    # A self-consistent report alone cannot authenticate its alleged timings.
    # Re-execute the registered complete public-call trace against current sources.
    from frame_evidence_replay import replay
    replay(data)
    pinned, evidence = export_config(
        data, ram_budget=budget_ram, zp_budget=budget_zp,
        code_base=memory["code_base"], math_io=memory["math_io"],
        zp_base=memory["zp_base"], scratch_base=memory["scratch_base"],
        objective=optimize, max_peak_cycles=limit)
    expected_ops = math_builder.parse_operations(names, index)
    if set(expected_ops) != set(pinned["operations"]) or len(expected_ops) != len(pinned["operations"]):
        raise EvidenceError("The requested operations differ from the measured full linked plan")
    plan = math_builder.create_plan(
        index, expected_ops, target="c64", objective="size",
        pins=pinned["pins"], zp_budget=budget_zp, ram_budget=budget_ram)
    # Publish nothing until the actual linked image matches the recorded source
    # evidence. The usual builder output remains a normal selective C64 PRG.
    with tempfile.TemporaryDirectory(prefix="math_frame_build_") as temp:
        stage = Path(temp)
        manifest = linker.build(plan, stage, memory=pinned["memory"])
        digest = hashlib.sha256((stage / "math_selective.prg").read_bytes()).hexdigest()
        if (digest != evidence["qualified_prg_sha256"] or
            manifest["prg_sha256"] != digest or
            set(manifest["link_exports"]) != set(expected_ops) or
            {op["api"]: op["variant"] for op in manifest["operations"]}
                != pinned["pins"] or
            manifest["resource_use"]["main_ram_total_bytes"]
                != next(p["per_option"][evidence["choice"]]["main_ram_total_bytes"]
                        for p in data["placements"]
                        if p["code"] == "$%04X" % memory["code_base"]
                        and p["io"] == "$%04X" % memory["math_io"])):
            raise EvidenceError("Installer output diverges from qualified physical source image")
        parent = args.out.parent
        parent.mkdir(parents=True, exist_ok=True)
        (stage / "frame_qualified_config.json").write_text(
            json.dumps(pinned, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        (stage / "frame_qualified_evidence.json").write_text(
            json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        for filename in ("math_selective.prg", "math_api.inc",
                         "selective_manifest.json", "frame_qualified_config.json",
                         "frame_qualified_evidence.json"):
            # This opt-in mode preserves original linker filenames. Publication
            # only occurs after all source/ABI/checksum checks have passed.
            os.replace(stage / filename, parent / filename)
    print("Built frame-qualified PRG:", args.out.parent / "math_selective.prg")
    print("Selected measured plan:", evidence["choice"])
    print("Exact source-linked SHA-256:", evidence["qualified_prg_sha256"])
    print("Qualification: synthetic math-only CPU-model cycles, NOT physical PAL")
    return 0
