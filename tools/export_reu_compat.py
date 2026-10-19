#!/usr/bin/env python3
"""Export exact standalone V3/V4 REU compatibility, never a selectable kernel."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from profile_retirement_audit import (
    LEGACY_REU_SERVICE_FAMILIES, SERVICE_PARTS, STOCK_NON_OPERATION_SYMBOLS,
    profile_symbols,
)
ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    "v3_reu_512k": {
        "resident": "v3_reu_512k/resident/math_v3_reu_512k_game_math.prg",
        "reu": "v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
        "bytes": 524288,
        "families": ("UMUL16", "UMUL32"),
    },
    "v4_reu_16m": {
        "resident": "v4_reu_16m/resident/math_v4_reu_16m_game_math.prg",
        "reu": "v4_reu_16m/reu/c64_math_v4_16m_game_math.reu",
        "bytes": 16777216,
        "families": ("UMUL16", "UMUL32", "QS16"),
    },
}
LINE = re.compile(r"^([0-9a-f]{64})  (\S+)$")

class LegacyREUError(ValueError):
    pass

def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()

def manifest_hashes(root: Path) -> dict[str, str]:
    values = {}
    for line in (root / "SHA256SUMS.txt").read_text("utf-8").splitlines():
        m = LINE.fullmatch(line)
        if not m or m[2] in values:
            raise LegacyREUError("Invalid/duplicate locked SHA256 manifest entry")
        values[m[2]] = m[1]
    return values

def service_symbols(profile: str) -> dict:
    out = {}
    for family in PROFILES[profile]["families"]:
        contract = LEGACY_REU_SERVICE_FAMILIES[family]
        if profile not in contract["profiles"]:
            raise LegacyREUError("Hardware service ownership drift")
        for phase in SERVICE_PARTS:
            name = "MATH_REU_" + family + ("_" + phase if phase else "")
            out[name] = {
                "phase": phase if phase else "CALL",
                "exclusive_zp_bytes": contract["exclusive_zp_bytes"],
                "hardware": contract["hardware"],
            }
    return out

def export(profile: str, destination: Path, root: Path = ROOT) -> dict:
    if profile not in PROFILES:
        raise LegacyREUError("Unsupported historical hardware profile")
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise LegacyREUError("Destination already exists: refusing overwrite")
    if destination == root or destination in {
        (root / p).resolve() for p in PROFILES
    }:
        raise LegacyREUError("Will not overwrite source profile")
    spec = PROFILES[profile]
    sources = {
        "math_legacy.prg": spec["resident"],
        "math_legacy.reu": spec["reu"],
        "math_api.inc": profile + "/resident/math_api.inc",
        "REFERENCE_README.md": profile + "/README.md",
        "LICENSE_NOTES.md": profile + "/LICENSE_NOTES.md",
    }
    hashes = manifest_hashes(root)
    locked = {}
    for name, rel in sources.items():
        path = root / rel
        if rel not in hashes or not path.is_file() or path.is_symlink():
            raise LegacyREUError("Unqualified reference source file: " + rel)
        size = path.stat().st_size
        if name == "math_legacy.prg" and size != 49042:
            raise LegacyREUError("Historical resident PRG length drift")
        if name == "math_legacy.reu" and size != spec["bytes"]:
            raise LegacyREUError("Historical REU image length drift")
        sha = digest(path)
        if sha != hashes[rel]:
            raise LegacyREUError("Historical reference checksum drift: " + rel)
        locked[name] = {"source_path": rel, "sha256": sha, "bytes": size}
    symbols = profile_symbols(root)[profile]
    services = service_symbols(profile)
    if not set(services).issubset(symbols):
        raise LegacyREUError("Missing historical REU public entry")
    if not STOCK_NON_OPERATION_SYMBOLS.issubset(symbols):
        raise LegacyREUError("Missing historical public data/INIT symbol")
    if {x for x in symbols if x.startswith("MATH_REU_")} != set(services):
        raise LegacyREUError("Unexpected extra/missing REU public lifecycle entries")
    result = {
        "schema": "c64-legacy-reu-exclusive-compat-v1",
        "profile": profile,
        "reu_bytes": spec["bytes"],
        "sources": locked,
        "public_reu_lifecycle": services,
        "public_stock_nonoperation_symbols": sorted(STOCK_NON_OPERATION_SYMBOLS),
        "exclusive_whole_resident_image": True,
        "may_mix_with_operation_first_prg": False,
        "new_reu_backend_implemented": False,
        "physical_pal_timing_certified_by_export": False,
    }
    note = (
        "STANDALONE HISTORICAL REU COMPATIBILITY\n\n"
        "This is the unchanged, checksum-locked " + profile + " complete resident.\n"
        "Load its matching REU image alongside its legacy PRG and use its\n"
        "original math_api.inc. Never link this whole resident into an\n"
        "operation-first math_selective.prg or merge their public addresses/ZP.\n"
        "Turbo16, Turbo32 and QS16 require their BEGIN/CALL/END ownership\n"
        "contracts and exclusive ZP overlays. Original README/LICENSE included.\n"
        "This copy is NOT a new hardware backend or a PAL timing certificate.\n"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".stage_reu_compat_", dir=destination.parent
    ) as td:
        stage = Path(td)
        for name, rel in sources.items():
            shutil.copyfile(root / rel, stage / name)
            if digest(stage / name) != locked[name]["sha256"]:
                raise LegacyREUError("Corrupt staged reference copy: " + rel)
        (stage / "COMPATIBILITY.txt").write_text(note, encoding="utf-8")
        (stage / "compat_manifest.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if destination.exists():
            raise LegacyREUError("Refusing destination overwrite during stage")
        os.replace(stage, destination)
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", choices=tuple(PROFILES), required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    try:
        result = export(args.profile, args.out)
    except (LegacyREUError, OSError) as error:
        p.error(str(error))
    print("SEALED REU COMPAT", result["profile"], result["reu_bytes"],
          len(result["public_reu_lifecycle"]))

if __name__ == "__main__":
    main()
