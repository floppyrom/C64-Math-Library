#!/usr/bin/env python3
"""Fail-closed stock-C64 profile-retirement evidence inventory.

This is an *inventory* of source qualification, historical Pareto alternatives
and the nine extra REU/Turbo/QS16 public lifecycle exports. It does NOT
certify V1-V5 speed parity, 50Hz frame time or replacement REU hardware.
"""
from __future__ import annotations

import argparse
import ast
import inspect
import json
from pathlib import Path
import re
import sys

import math_builder
import selective_linker

ROOT = Path(__file__).resolve().parents[1]
PROFILE_INCLUDE = {
    "v1_balanced": "v1_balanced/resident/math_api.inc",
    "v2_pareto_fast": "v2_pareto_fast/resident/math_api.inc",
    "v3_reu_512k": "v3_reu_512k/resident/math_api.inc",
    "v4_reu_16m": "v4_reu_16m/resident/math_api.inc",
    "v5_hybrid_lowzp": "v5_hybrid_lowzp/resident/math_api.inc",
}
LEGACY_REU_SERVICE_FAMILIES = {
    "UMUL16": {"profiles": ("v3_reu_512k", "v4_reu_16m"),
               "exclusive_zp_bytes": 122, "hardware": "REU 512KiB+"},
    "UMUL32": {"profiles": ("v3_reu_512k", "v4_reu_16m"),
               "exclusive_zp_bytes": 135, "hardware": "REU 512KiB+"},
    "QS16": {"profiles": ("v4_reu_16m",),
              "exclusive_zp_bytes": 16, "hardware": "REU 16MiB"},
}
SERVICE_PARTS = ("BEGIN", "", "END")
ASSIGNMENT = re.compile(r"^(MATH_[A-Z0-9_]+)\s*=\s*\$[0-9A-Fa-f]{4}\b", re.M)


class RetirementAuditError(ValueError):
    pass


def source_speed_keys():
    """Static source declaration only, NOT an executed timing certification."""
    module = ast.parse(inspect.getsource(selective_linker.build))
    keys = []
    for node in ast.walk(module):
        if (isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "measured"
                    for t in node.targets)
            and isinstance(node.value, ast.Dict)):
            keys.extend(key.value for key in node.value.keys
                        if isinstance(key, ast.Constant) and isinstance(key.value, str))
    if not keys or len(keys) != len(set(keys)):
        raise RetirementAuditError("No unique source speed-model keys")
    return set(keys)


def profile_symbols(root: Path):
    result = {}
    for profile, source in PROFILE_INCLUDE.items():
        filename = root / source
        if not filename.is_file():
            raise RetirementAuditError("Historical profile symbol file absent: "+source)
        symbols = ASSIGNMENT.findall(filename.read_text(encoding="utf-8"))
        if len(symbols) != len(set(symbols)):
            raise RetirementAuditError("Duplicate historical public symbols: "+source)
        result[profile] = set(symbols)
    return result


def audit(root: Path = ROOT):
    if root.resolve() != ROOT.resolve():
        raise RetirementAuditError("Audit imports must match source root")
    catalog = math_builder.operation_index()
    linked = selective_linker.MODULES
    speed = source_speed_keys()
    if len(catalog) != 56 or set(catalog) != set(linked):
        raise RetirementAuditError("56-operation canonical/linked catalog mismatch")
    if speed != set(catalog):
        raise RetirementAuditError("One or more stock APIs lack declared speed models: "
                                   +repr(sorted(set(catalog)^speed)))
    symbols = profile_symbols(root)
    by_api = {}
    for api in sorted(linked):
        variants = linked[api]
        if not variants:
            raise RetirementAuditError("Empty linkable source variants: "+api)
        source_details = []
        for name, variant in sorted(variants.items()):
            if not name.startswith("link:") or not variant.get("source"):
                raise RetirementAuditError("Invalid linkable source lineage: "+api)
            if not (root / variant["source"]).is_file():
                raise RetirementAuditError("Source missing for "+api+" / "+name)
            source_details.append({
                "variant": name,
                "source": variant["source"],
                "code_and_tables_bytes": sum(n for _,n in variant["segments"]),
                "private_zp_bytes": variant["zp"],
                "scratch_bytes": variant["scratch"],
                "shared_producer": variant.get("share_producer"),
                "persistent_state_bytes": variant.get("persistent_state", 0),
                "requires_writable_code": bool(variant.get("requires_writable_code")),
                "requires_reu": bool(variant.get("requires_reu")),
            })
        by_api[api] = {
            "linkable_stock_c64": True,
            "source_cycle_model_declared": True,
            "native_profile_parity_certified_by_this_audit": False,
            "candidate_variants": source_details,
            "historical_profile_mirror_records": sum(
                v["kind"] == "resident-source-mirror"
                for v in catalog[api]["variants"]),
            "standalone_donor_records_not_automatically_linkable": sum(
                v["kind"] == "standalone-requires-integration"
                for v in catalog[api]["variants"]),
        }
        if any(api not in exported for exported in symbols.values()):
            raise RetirementAuditError("Reference profile missing stable API "+api)
    reu_services = {}
    expected_reu = set()
    for family, contract in sorted(LEGACY_REU_SERVICE_FAMILIES.items()):
        for suffix in SERVICE_PARTS:
            name = "MATH_REU_"+family+("_"+suffix if suffix else "")
            expected_reu.add(name)
            profiles = [p for p,v in symbols.items() if name in v]
            if set(profiles) != set(contract["profiles"]):
                raise RetirementAuditError(
                    "Historical REU service/capability map mismatch: "+name)
            if name in linked or name in speed:
                raise RetirementAuditError(
                    "REU lifecycle entry silently folded into stock API: "+name)
            reu_services[name] = {
                "legacy_profiles": sorted(profiles),
                "stock_operation_first_available": False,
                "legacy_compatibility_required": True,
                "exclusive_mode_zp_bytes": contract["exclusive_zp_bytes"],
                "hardware": contract["hardware"],
                "lifecycle_phase": suffix or "CALL",
            }
    unexpected = (symbols["v3_reu_512k"]|symbols["v4_reu_16m"])-set(catalog)-{"MATH_INIT"}-expected_reu
    if unexpected:
        raise RetirementAuditError("Uncatalogued additional REU service: "
                                   +repr(sorted(unexpected)))
    counts = {}
    for a in by_api.values():
        n = len(a["candidate_variants"])
        counts[n] = counts.get(n, 0)+1
    outstanding = [
        "No cross-profile identical-public-ABI fastest-donor and worst-frame parity certificate for all 56 APIs",
        "Nine REU/Turbo/QS16 lifecycle exports still require V3/V4 legacy compatibility packages or a qualified feature backend",
        "Real-game native PAL VIC-II/IRQ/SID and REU DMA busy-frame timing is not qualified",
    ]
    return {
        "schema": "c64-profile-retirement-evidence-v1",
        "scope": "stock NMOS C64 operation-first source inventory; not full release parity",
        "stock_public_operations": len(by_api),
        "source_cycle_model_declarations": len(speed),
        "selectable_variants_per_operation": {str(k): counts[k] for k in sorted(counts)},
        "stock_operations": by_api,
        "legacy_hardware_services": reu_services,
        "legacy_profile_symbol_sources": PROFILE_INCLUDE,
        "hardware_backend_status": {
            "c64": "stock-source-link-ready; historical performance parity pending",
            "1541": "planning_only", "1571": "planning_only", "1581": "planning_only",
            "reu_512k": "legacy_profile_compatibility_only",
            "reu_16m": "legacy_profile_compatibility_only",
        },
        "ready_to_retire_all_v1_v5_profiles": False,
        "blocking_gates": outstanding,
        "disclaimer": ("Counts and source provenance are inspected, but this audit "
                       "does not itself compare historical full-call speed, prove "
                       "full PAL frame time, or certify a REU backend."),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, help="Save reproducible JSON report")
    ap.add_argument("--require-retirement-ready", action="store_true",
                    help="Fail closed until independent retirement gates qualify")
    args = ap.parse_args(argv)
    result = audit()
    rendered = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if args.require_retirement_ready and not result["ready_to_retire_all_v1_v5_profiles"]:
        print("V1-V5 retirement BLOCKED: missing hardware/performance certificates",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
