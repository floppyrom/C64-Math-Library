#!/usr/bin/env python3
"""First native operation-first REU *contract* and collision inventory.

This is NOT a REU backend. It verifies frozen V3/V4 entry ownership, models
BEGIN/CALL/END overlay lifetimes and detects incompatible stock zero-page
allocations before anyone transplants DMA or code overlays. No executable
REU code is linked, and legacy PRG/REU pairs remain indispensable.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import export_reu_compat as legacy
from profile_retirement_audit import (
    LEGACY_REU_SERVICE_FAMILIES, SERVICE_PARTS, PROFILE_INCLUDE,
)

ROOT = Path(__file__).resolve().parents[1]
FAMILY_WIDTH = {"UMUL16": 16, "UMUL32": 32, "QS16": 16}
ZP_REFERENCE_EXPORT = {"UMUL16": "TURBO16_ZP_BASE",
                       "UMUL32": "TURBO32_ZP_BASE"}
REU_BANK_REFERENCE_EXPORT = {"UMUL16": "REU_TURBO16_BANK",
                             "UMUL32": "REU_TURBO32_BANK"}
ASSIGN = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=\s*\$([0-9a-fA-F]{2,4})\s*$", re.M)


class REUContractError(ValueError):
    pass


def reference_symbols(profile: str, root: Path = ROOT) -> dict[str, int]:
    path = root / PROFILE_INCLUDE[profile]
    symbols = {}
    for name, value in ASSIGN.findall(path.read_text(encoding="utf-8")):
        if name in symbols:
            raise REUContractError("Duplicated REU reference symbol: " + name)
        symbols[name] = int(value, 16)
    return symbols


def overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


def as_hex(value: int, digits: int = 4) -> str:
    return "$" + format(value, f"0{digits}X")


def zp_owners(manifest: dict) -> list[tuple[str, tuple[int, int]]]:
    """Conservatively account for all stock and application ZP allocations."""
    if manifest.get("target") != "c64":
        raise REUContractError("Requires a stock C64 selective manifest")
    resources, placement = manifest["resource_use"], manifest["memory_map"]
    owners = []
    amount = resources["zero_page_bytes"]
    origin = placement["zp_start"]
    if not isinstance(amount, int) or amount < 0:
        raise REUContractError("Invalid selective ZP byte count")
    if amount:
        if not isinstance(origin, str):
            raise REUContractError("Missing physical ZP origin")
        start = int(origin.removeprefix("$"), 16)
        if start < 0 or start + amount > 256:
            raise REUContractError("Selective ZP range is outside zero page")
        owners.append(("installed_stock_math", (start, start + amount - 1)))
    for item in placement.get("user_zp_reserved", []):
        start = int(item["start"].removeprefix("$"), 16)
        end = int(item["end"].removeprefix("$"), 16)
        if not 0 <= start <= end <= 255:
            raise REUContractError("Invalid application ZP reservation")
        owners.append((item["name"], (start, end)))
    return owners


def plan(profile: str, family: str, *,
         stock_manifest: dict | None = None, root: Path = ROOT) -> dict:
    if profile not in legacy.PROFILES:
        raise REUContractError("Unknown historical REU hardware tier")
    if family not in FAMILY_WIDTH or family not in legacy.PROFILES[profile]["families"]:
        raise REUContractError("REU service unavailable at requested hardware tier")
    contract = LEGACY_REU_SERVICE_FAMILIES[family]
    symbols = reference_symbols(profile, root)
    prefix = "MATH_REU_" + family
    names = tuple(prefix + ("_" + phase if phase else "") for phase in SERVICE_PARTS)
    if not all(name in symbols for name in names):
        raise REUContractError("Missing historical REU lifecycle entry")
    addresses = [symbols[n] for n in names]
    if len(set(addresses)) != 3 or addresses != sorted(addresses):
        raise REUContractError("Invalid BEGIN -> CALL -> END reference placement")
    zp_bytes = contract["exclusive_zp_bytes"]
    zp_base_name = ZP_REFERENCE_EXPORT.get(family)
    base = symbols.get(zp_base_name) if zp_base_name else None
    bank_name = REU_BANK_REFERENCE_EXPORT.get(family)
    bank = symbols.get(bank_name) if bank_name else None
    if zp_base_name and (base is None or base < 2 or base + zp_bytes > 256):
        raise REUContractError("Invalid frozen ZP overlay allocation")
    if bank_name and (bank is None or bank * 65536 >= legacy.PROFILES[profile]["bytes"]):
        raise REUContractError("Invalid REU bank in frozen source contract")
    if family == "QS16" and legacy.PROFILES[profile]["bytes"] < 0x180000:
        raise REUContractError("QS16 table cannot fit the requested REU tier")

    collision_details = []
    if stock_manifest is not None:
        for name, occupied in zp_owners(stock_manifest):
            if base is None:
                # QS16 is not an ordinary free-standing ZP overlay. Its
                # exact 16-byte physical footprint must be extracted from
                # the V4 source; fail closed, even for empty stock ZP.
                collision_details.append({
                    "owner": name, "reason": "QS16 ZP extent not qualified"})
            elif overlap((base, base + zp_bytes - 1), occupied):
                collision_details.append({
                    "owner": name,
                    "occupied": [as_hex(occupied[0], 2),
                                 as_hex(occupied[1], 2)],
                    "reason": "Active REU overlay overwrites application or stock ZP",
                })
    return {
        "schema": "operation-first-reu-module-contract-v1",
        "hardware_reference_profile": profile,
        "hardware_reu_bytes": legacy.PROFILES[profile]["bytes"],
        "family": family,
        "product_bits": FAMILY_WIDTH[family] * 2,
        "lifecycle_reference_entries": {
            name: as_hex(symbols[name]) for name in names
        },
        "zero_page_overlay": {
            "exclusive_bytes": zp_bytes,
            "reference_start": as_hex(base, 2) if base is not None else None,
            "reference_end": as_hex(base + zp_bytes - 1, 2)
            if base is not None else None,
            "not_safe_for_nested_math_calls": True,
        },
        "reference_reu_bank": bank,
        "collision_risks_in_supplied_stock_manifest": collision_details,
        "compatible_with_supplied_zp_placement": (
            not collision_details if base is not None else False
        ),
        "status": "CONTRACT_ONLY_NO_SELECTIVE_REU_BINARY",
        "native_reu_backend_available": False,
        "may_link_legacy_resident_into_stock_prg": False,
        "required_proofs": [
            "independent relocatable DMA and kernel source, with exact source SHA",
            "BEGIN/CALL/END saves and restores caller ZP including repeated batches",
            "qualified exclusive ZP ranges and REU bank/region ownership",
            "same-input whole-call ABI/Q/R/Carry/inputs/stack across two RAM maps",
            "REU-enabled native VICE 512KiB/16MiB and busy VIC DMA checks",
            "simultaneous selective producer/table/IO collision-free linking",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-tier", choices=tuple(legacy.PROFILES),
                        required=True)
    parser.add_argument("--family", choices=tuple(FAMILY_WIDTH), required=True)
    parser.add_argument("--stock-manifest", type=Path,
                        help="Optional generated stock selective_manifest.json to audit")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        installed = (json.loads(args.stock_manifest.read_text("utf-8"))
                     if args.stock_manifest else None)
        data = plan(args.reference_tier, args.family, stock_manifest=installed)
    except (REUContractError, KeyError, ValueError, OSError) as exc:
        parser.exit(2, "REU contract: " + str(exc) + "\n")
    payload = json.dumps(data, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
