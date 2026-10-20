#!/usr/bin/env python3
"""Native x64sc validation of the *same exact* seven-API frame-selected PRGs.

Independent existing VICE public-call harnesses validate all seven public
exports in the complete seven-operation linked project. Only the $4123
qualified relocation is exercised: the other qualified relocation ($2000)
overlaps the independent native oracle's $2000-$405F RAM harness and buffers.
This validates native result/ABI correctness, NOT physical PAL frame timing.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import mixed_seven_frame_parity as seven

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "routines/standalone_lab/portable"))

import native_selective_umul32 as umul
import native_selective_smul32 as smul
import native_selective_isqrt16 as sqrt
import native_selective_sdiv32_32 as signed
from native_vice import N as UNSIGNED_N, VICE, check as unsigned_check

CODE, IO, ZP = 0x4123, 0xc040, 0x70
ORIGINS = ((0x2000, 0xc000, 0x50), (CODE, IO, ZP))
BUDGETS = (("peak", 64), ("ram", 0))
N = 96
OPS = tuple(seven.OPS)


def qualified_cases():
    """Return the report without pretending the native oracle timed PAL frames."""
    result = seven.complete_report()
    if (result["basis"] != seven.BASIS or result["operations"] != list(OPS)
            or result["placements"][1]["code"] != "$4123"
            or result["placements"][1]["io"] != "$C040"
            or result["placements"][1]["zp_base"] != "$0070"
            or len(result["placements"]) != 2
            or result["placements"][0]["input_corpus_sha256"]
               != result["placements"][1]["input_corpus_sha256"]):
        raise AssertionError("Source-qualified seven-API two-relocation report drift")
    return result


def build_exact_frame_prg(report: dict, destination: Path,
                          *, zp_budget: int):
    """Rebuild using the *production frame CLI*, not a hand-picked native source."""
    from frame_qualified_config import export_config

    destination.mkdir(parents=True, exist_ok=True)
    config, expected = export_config(
        report, ram_budget=16000, zp_budget=zp_budget,
        code_base=CODE, math_io=IO, zp_base=ZP, scratch_base=IO + 0x40,
        objective="peak" if zp_budget else "ram")
    if set(config["pins"]) != set(OPS):
        raise AssertionError("Seven native exports missing in pinned source plan")
    project = {
        "target": "c64", "objective": "frame",
        "operations": list(OPS),
        "constraints": {"max_ram_bytes": 16000, "max_zp_bytes": zp_budget},
        "memory": {"code_base": CODE, "math_io": IO,
                   "zp_base": ZP, "scratch_base": IO+0x40},
        "frame_optimize": "peak" if zp_budget else "ram",
    }
    path = destination / "project.json"
    path.write_text(json.dumps(project, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    raw = destination / "source_report.json"
    raw.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    out = destination / "generated" / "selection_manifest.json"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools/math_builder.py"),
         "--objective", "frame", "--config", str(path),
         "--frame-report", str(raw), "--build", "--out", str(out)],
        cwd=ROOT, capture_output=True, text=True, timeout=300)
    if proc.returncode:
        raise AssertionError("Seven-API source-qualified CLI failed: " + proc.stderr[-2500:])
    folder = out.parent
    binary = (folder / "math_selective.prg").read_bytes()
    manifest = json.loads((folder / "selective_manifest.json").read_text(encoding="utf-8"))
    proof = json.loads((folder / "frame_qualified_evidence.json").read_text(encoding="utf-8"))
    pins = json.loads((folder / "frame_qualified_config.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(binary).hexdigest()
    selected = {entry["api"]: entry["variant"] for entry in manifest["operations"]}
    entries = {entry["api"]: int(entry["entry"][1:], 16) for entry in manifest["operations"]}
    if (digest != proof["qualified_prg_sha256"]
            or digest != expected["qualified_prg_sha256"]
            or selected != pins["pins"] or selected != config["pins"]
            or set(entries) != set(OPS) or set(manifest["link_exports"]) != set(OPS)
            or binary[:2] != CODE.to_bytes(2, "little")
            or not binary[2:] or CODE + len(binary) - 2 >= 0xc000
            or manifest["resource_use"]["main_ram_total_bytes"] > 16000
            or manifest["resource_use"]["zero_page_bytes"] > zp_budget
            or proof["cpu_model_only"] is not True
            or proof["physical_pal_feasibility_claim"] is not False):
        raise AssertionError("Native verification image differs from source-proved installer")
    if zp_budget == 0 and proof["choice"] != "compact-everywhere":
        raise AssertionError("Unqualified zero-ZP candidate selected")
    return binary, entries, proof


def check_native_map(binary: bytes):
    """Check legacy oracle data areas do not overlap this exact measured PRG."""
    from native_vice import H, INPUT, OUTPUT, STRIDE
    end = CODE + len(binary) - 2
    # Old independent harness uses these areas; do NOT silently test
    # the measured $2000 image with the same native test stub.
    assert H == 0x2000 and INPUT == 0x3000 and OUTPUT == 0x3800
    assert STRIDE == 0x80
    if CODE <= OUTPUT + 16*STRIDE + N-1 or end >= 0xc000:
        raise AssertionError("Native harness/PRG overlap")
    return end


def verify_native(vice: str, directory: Path):
    if not os.environ.get("VICE_WRAPPER") or not Path(vice).is_file() or VICE != Path(vice):
        raise RuntimeError("VICE_WRAPPER must point to pinned, functioning x64sc")
    if not (N == umul.N == smul.N == sqrt.N == signed.N == UNSIGNED_N):
        raise AssertionError("Native independent public oracle counts differ")
    report = qualified_cases()
    rows = []
    for ordinal, (objective, limit) in enumerate(BUDGETS):
        folder = directory / objective
        binary, entries, proof = build_exact_frame_prg(report, folder, zp_budget=limit)
        end = check_native_map(binary)
        native = {}
        for j, api in enumerate(OPS):
            tag = "seven_exact_%s_%s" % (objective, api.lower())
            port = 11000 + ordinal*8 + j
            entry = entries[api]
            if api == "MATH_UMUL32":
                digest = umul.run_native(vice, binary, entry, CODE, IO, tag, port, folder)
            elif api == "MATH_SMUL32":
                digest = smul.run_native(vice, binary, entry, CODE, IO, tag, port, folder)
            elif api == "MATH_ISQRT16":
                digest = sqrt.verify(vice, binary, entry, CODE, IO, tag, port, folder)
            elif api in ("MATH_UDIV32_32", "MATH_UMOD32_32"):
                ram = bytearray(65536)
                ram[CODE:CODE+len(binary)-2] = binary[2:]
                mapping = {"INPUT_NUM": IO+16, "INPUT_DIV": IO+20,
                           "OUTPUT_QUOT": IO+24, "OUTPUT_REM": IO+28}
                native_result = unsigned_check(
                    ram, entry, 32, mapping, tag, port, folder, False)
                if native_result["cases"] != N:
                    raise AssertionError("Incomplete unsigned native call output")
                digest = native_result["output_sha256"]
            else:
                digest = signed.verify(vice, binary, entry, CODE, IO, tag, port, folder)
            native[api] = digest
            print("NATIVE SEVEN EXACT PASS", objective, api, N, digest, flush=True)
        rows.append({
            "selected_plan": proof["choice"], "objective": objective,
            "code": "$%04X" % CODE, "io": "$%04X" % IO,
            "code_end": "$%04X" % end,
            "qualified_prg_sha256": proof["qualified_prg_sha256"],
            "linked_ram_bytes": proof["worst_placement_measured_envelope"]["main_ram_total_bytes"],
            "linked_zp_bytes": proof["worst_placement_measured_envelope"]["zero_page_bytes"],
            "public_native_calls": len(OPS)*N,
            "public_native_output_sha256": native,
            "cpu_model_timing_only": True,
            "physical_pal_frame_cycles_measured": False,
            "hardware_reu_qualified": False,
        })
    if len(rows) != len(BUDGETS) or len({r["qualified_prg_sha256"] for r in rows}) != 2:
        raise AssertionError("Did not qualify two distinct exact project binaries")
    return {"basis": "native pinned x64sc public ABI for exact 7-API frame installer PRGs",
            "emulator_calls": sum(x["public_native_calls"] for x in rows),
            "native_builds": rows, "physical_pal_timing_measured": False}


def main():
    vice = os.environ.get("VICE_WRAPPER", "")
    if not vice:
        raise RuntimeError("Set VICE_WRAPPER to pinned native x64sc")
    with tempfile.TemporaryDirectory(prefix="native_seven_frame_") as temp:
        result = verify_native(vice, Path(temp))
    print(json.dumps(result, sort_keys=True, indent=2))
    assert result["emulator_calls"] == 2 * 7 * N
    print("NATIVE EXACT SEVEN FRAME 1344 API CALLS PASS", flush=True)


if __name__ == "__main__":
    main()
