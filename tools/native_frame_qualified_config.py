#!/usr/bin/env python3
"""Qualify the *exact frame-selected installer PRG* on pinned native x64sc.

Two qualified placements, high-speed and zero-ZP Pareto choices, three
independent native full-result public ABI oracles. No real PAL cycle claim:
the synthetic frame model and physical emulator correctness are separate.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import math_builder
import mixed3_frame_parity as mixed3
from frame_qualified_config import export_config
import native_selective_umul32 as unsigned
import native_selective_smul32 as signed
import native_selective_isqrt16 as sqrt16

ROOT = Path(__file__).resolve().parents[1]
LOCATIONS = ((0x8000, 0xc000, 0x50), (0x7123, 0xc040, 0x70))
CHOICES = (("peak", 31), ("ram", 0))
ORACLES = (
    ("MATH_UMUL32", unsigned.run_native),
    ("MATH_SMUL32", signed.run_native),
    ("MATH_ISQRT16", sqrt16.verify),
)
N = unsigned.N


def build_native_cases():
    """Export source-qualified, fully pinned configs on a single report."""
    report = {
        "basis": "three-operation same-input linked source math-only frames",
        "operations": list(mixed3.OPS),
        "placements": [mixed3.compare(code, io, zp) for code, io, zp in LOCATIONS],
    }
    for i, (code, io, zp) in enumerate(LOCATIONS):
        for choice, budget in CHOICES:
            config, evidence = export_config(
                report, ram_budget=12000, zp_budget=budget,
                code_base=code, math_io=io, zp_base=zp,
                scratch_base=io+0x40, objective=choice)
            if (config["target"] != "c64" or config["objective"] != "size"
                or set(config["pins"]) != set(mixed3.OPS)
                or evidence["physical_pal_feasibility_claim"] is not False
                or not evidence["cpu_model_only"]
                or evidence["public_calls_per_location"] != mixed3.CALLS
                or evidence["frames_per_location"] != mixed3.FRAMES):
                raise AssertionError("Qualified frame snapshot contract drift")
            if budget == 0 and (
                config["pins"]["MATH_UMUL32"].startswith("link:fast31")
                or config["pins"]["MATH_SMUL32"].startswith("link:fast31")):
                raise AssertionError("Zero-ZP project plan selected FAST31")
            yield i, config, evidence


def check_cli_exact_image(config, evidence, folder: Path):
    """CLI build output, SHA and public symbols must match measured image."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "math-config.json"
    path.write_text(json.dumps(config, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    output = folder / "generated" / "manifest.json"
    proc = subprocess.run(
        [sys.executable, str(ROOT/"tools/math_builder.py"),
         "--config", str(path), "--build", "--out", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=120)
    if proc.returncode:
        raise AssertionError("Pinned CLI rebuild failed: "+proc.stderr[-2000:])
    man = json.loads((output.parent / "selective_manifest.json").read_text(encoding="utf-8"))
    image = (output.parent/"math_selective.prg").read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != evidence["qualified_prg_sha256"]:
        raise AssertionError("Native test PRG differs from measured image")
    code = config["memory"]["code_base"]
    if image[:2] != code.to_bytes(2, "little"):
        raise AssertionError("Wrong code load origin in measured PRG")
    selected = {op["api"]: op["variant"] for op in man["operations"]}
    if selected != config["pins"] or len(man["operations"]) != 3:
        raise AssertionError("Native public API variant selection drift")
    if len(man["link_order"]) != evidence["linked_sources"]:
        raise AssertionError("Shared physical source count changed")
    if man["resource_use"]["zero_page_bytes"] > config["constraints"]["max_zp_bytes"]:
        raise AssertionError("Project output violates ZP constraint")
    if man["resource_use"]["main_ram_total_bytes"] > config["constraints"]["max_ram_bytes"]:
        raise AssertionError("Project output violates main-RAM constraint")
    entries = {op["api"]: int(op["entry"][1:], 16) for op in man["operations"]}
    if set(entries) != {key for key, _ in ORACLES}:
        raise AssertionError("Native entrypoint list incomplete")
    return image, entries, digest


def verify_native(vice: str, root: Path):
    emulator = Path(vice)
    if not emulator.is_file():
        raise RuntimeError("VICE_WRAPPER must be a working native pinned x64sc")
    if N != signed.N or N != sqrt16.N:
        raise AssertionError("Independent native oracle case counts diverge")
    reports = []
    for i, config, evidence in build_native_cases():
        code = config["memory"]["code_base"]
        io = config["memory"]["math_io"]
        choice = evidence["selection"]["objective"]
        folder = root / ("%04x_%s" % (code, choice))
        image, entries, digest = check_cli_exact_image(config, evidence, folder)
        if not (0x7000 <= code < 0x9000 and code+len(image)-2 < 0xb000
                and io >= 0xc000):
            raise AssertionError("Native stub/output maps conflict with math PRG")
        native = {}
        for j, (api, verifier) in enumerate(ORACLES):
            tag = "frame_config_%04x_%s_%s" % (code, choice, api.lower())
            port = 9700 + i*8 + (0 if choice=="peak" else 4) + j
            out_digest = verifier(
                vice, image, entries[api], code, io,
                tag, port, folder)
            native[api] = out_digest
            print("FRAME-CONFIG EXACT-IMAGE NATIVE PASS", hex(code), choice,
                  api, N, out_digest, flush=True)
        reports.append({
            "choice": choice, "code": "$%04X" % code,
            "io": "$%04X" % io,
            "qualified_prg_sha256": digest,
            "public_native_calls": len(ORACLES)*N,
            "public_native_output_sha256": native,
            "pins": config["pins"],
            "retained_frame_cpu_model_evidence": {
                "measured_placements": evidence["locations_tested"],
                "worst_peak_math_cycles": evidence["worst_placement_measured_envelope"][
                    "peak_frame_math_cycles"],
            },
            "physical_pal_timing_measured": False,
            "hardware_reu_qualified": False,
        })
    if len(reports) != 4:
        raise AssertionError("Incomplete frame-selected native build matrix")
    return {"basis": "real x64sc r46284 exact pinned installer PRG ABI, no PAL timing",
            "native_public_calls": sum(x["public_native_calls"] for x in reports),
            "qualified_rebuilds": reports}


def main():
    vice = os.environ.get("VICE_WRAPPER", "")
    if not vice:
        raise RuntimeError("Set VICE_WRAPPER to native pinned x64sc r46284")
    with tempfile.TemporaryDirectory(prefix="native_frame_config_") as temp:
        result = verify_native(vice, Path(temp))
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result["native_public_calls"] == 4*3*N
    print("FRAME-CONFIG EXACT PINNED SOURCE NATIVE PASS",
          result["native_public_calls"], "public calls / 4 PRGs", flush=True)


if __name__ == "__main__":
    main()
