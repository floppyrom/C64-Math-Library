#!/usr/bin/env python3
"""Operation-first selector for the next C64 Math Library builder.

Phase 1 deliberately emits a *plan*, not a PRG. Resident profile mirrors are
not independently linkable and record kernels may have incompatible ABI or
resource ownership. Until selective linking is proven, fail closed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "routines" / "SOURCE_CATALOG.csv"
STANDALONE = ROOT / "benchmarks" / "STANDALONE_RESULTS.csv"
OBJECTIVES = ("balanced", "speed", "size", "zp")
TARGETS = ("c64",)


class SelectionError(ValueError):
    pass


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def operation_index(root: Path = ROOT) -> dict[str, dict]:
    """Find public operations from the certified resident catalog, not a hardcoded list."""
    rows = read_csv(root / "routines" / "SOURCE_CATALOG.csv")
    extras = {
        (r["canonical_name"], r["variant"], r["source_path"]): r
        for r in read_csv(root / "benchmarks" / "STANDALONE_RESULTS.csv")
    }
    operations: dict[str, dict] = {}
    canonical_to_api: dict[str, str] = {}
    for r in rows:
        if r["scope"] != "shipped-profile" or r["profile"] != "v1_balanced":
            continue
        api = r["legacy_api"]
        if not api or api in operations:
            raise SelectionError("Duplicate or missing stable public API: " + api)
        operations[api] = {
            "api": api,
            "canonical_name": r["canonical_name"],
            "category": r["category"],
            "variants": [],
        }
        canonical_to_api[r["canonical_name"]] = api

    if not operations:
        raise SelectionError("No stable operations in the source catalog")

    for r in rows:
        if r["scope"] == "shipped-profile":
            api = r["legacy_api"]
            if api not in operations:
                # Hardware-specific additions are not in the portable core set.
                continue
            if r["canonical_name"] != operations[api]["canonical_name"]:
                raise SelectionError("Inconsistent canonical operation for " + api)
            variant_id = "resident:" + r["profile"]
            kind = "resident-source-mirror"
            resource = {}
        elif r["scope"] == "standalone-alternative":
            api = canonical_to_api.get(r["canonical_name"])
            if api is None:
                continue
            variant_id = "standalone:" + r["variant"]
            kind = "standalone-requires-integration"
            extra = extras.get(
                (r["canonical_name"], r["variant"], r["source_path"]), {}
            )
            resource = {
                k: int(extra[k]) for k in ("code_bytes", "table_bytes", "occupied_bytes")
                if extra.get(k, "").strip().isdigit()
            }
        else:
            continue

        v = {
            "id": variant_id,
            "kind": kind,
            "source_path": r["source_path"],
            "source_sha256": r["source_sha256"],
            "mean_cycles_reported": r["mean_cycles"],
            "zp_bytes_reported": r["zp_bytes"],
            "stack_page_bytes_reported": r["stack_page_reserved_bytes"],
            "validation_path": r["validation_path"],
            "qualification": r["status"],
            "notes": r["notes"],
            "resources_reported": resource,
            "selective_link_ready": False,
        }
        options = operations[api]["variants"]
        if any(p["id"] == variant_id for p in options):
            raise SelectionError("Variant ID collision for " + api + ": " + variant_id)
        options.append(v)

    return dict(sorted(operations.items()))


def resolve(token: str, index: dict[str, dict]) -> str:
    name = token.strip()
    if not name:
        raise SelectionError("Empty operation name")
    api = name.upper()
    if not api.startswith("MATH_"):
        api = "MATH_" + api
    if api in index:
        return api
    typed = [key for key, value in index.items()
             if value["canonical_name"].casefold() == name.casefold()]
    if len(typed) == 1:
        return typed[0]
    raise SelectionError("Unknown operation: " + token)


def parse_operations(names: list[str], index: dict[str, dict]) -> list[str]:
    selected: list[str] = []
    for item in names:
        for name in item.split(","):
            if not name.strip():
                continue
            api = resolve(name, index)
            if api not in selected:
                selected.append(api)
    if not selected:
        raise SelectionError("Select at least one operation")
    return sorted(selected)


def validate_sha(root: Path, source: dict) -> None:
    path = (root / source["source_path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise SelectionError("Missing or unsafe source path: " + source["source_path"])
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != source["source_sha256"]:
        raise SelectionError("Source checksum mismatch: " + source["source_path"])


def create_plan(
    index: dict[str, dict], names: list[str], *, target: str = "c64",
    objective: str = "balanced", zp_budget: int | None = None,
    ram_budget: int | None = None, pins: dict[str, str] | None = None,
    validate_sources: bool = False, root: Path = ROOT,
) -> dict:
    if target not in TARGETS:
        raise SelectionError("Unsupported target: " + target)
    if objective not in OBJECTIVES:
        raise SelectionError("Unsupported objective: " + objective)
    if zp_budget is not None and not 0 <= zp_budget <= 254:
        raise SelectionError("ZP budget must be in [0, 254]")
    if ram_budget is not None and not 0 <= ram_budget <= 65536:
        raise SelectionError("RAM budget must be in [0, 65536]")
    selected = parse_operations(names, index)
    requested_pins = pins or {}
    resolved_pins: dict[str, str] = {}
    for operation, variant_id in requested_pins.items():
        api = resolve(operation, index)
        if api not in selected:
            raise SelectionError("Pin refers to unselected operation: " + api)
        if api in resolved_pins and resolved_pins[api] != variant_id:
            raise SelectionError("Conflicting variants pinned for " + api)
        if not any(v["id"] == variant_id for v in index[api]["variants"]):
            raise SelectionError("Unknown variant for " + api + ": " + variant_id)
        resolved_pins[api] = variant_id

    output = []
    for api in selected:
        op = index[api]
        variants = op["variants"]
        if validate_sources:
            for v in variants:
                validate_sha(root, v)
        output.append({
            "api": api,
            "canonical_name": op["canonical_name"],
            "category": op["category"],
            "pinned_variant": resolved_pins.get(api),
            "available_source_variants": variants,
            "chosen_linkable_variant": None,
        })

    return {
        "schema": "c64-math-selection-plan-v1",
        "status": "planning_only_not_a_loadable_binary",
        "target": target,
        "objective": objective,
        "constraints": {"max_zp_bytes": zp_budget, "max_ram_bytes": ram_budget},
        "operations": output,
        "public_operation_count": len(output),
        "unresolved_dependencies": True,
        "linker_status": "not_implemented",
        "notes": [
            "Variant cycle means may use different corpora; do not rank across bases.",
            "Per-routine zero-page and memory claims must not be added together.",
            "Resident source mirrors and standalone records are not automatically linkable.",
            "Build-time compatibility, dependencies, memory ownership and execution "
            "must be verified before producing a selective PRG.",
        ],
    }


def interactive_pick(index: dict[str, dict]) -> list[str]:
    categories: dict[str, list[str]] = {}
    for api, op in index.items():
        categories.setdefault(op["category"], []).append(api)
    print("C64 Math Library — select operations (no fixed profile required)")
    for category, names in sorted(categories.items()):
        print("\n" + category.title())
        for name in names:
            print("  {:23s} {}".format(name, index[name]["canonical_name"]))
    print("\nEnter operation names, separated by commas.")
    raw = input("Operations: ")
    return [raw]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plan a minimal math library from operations, budgets and variants."
    )
    parser.add_argument("--list", action="store_true", help="list public operations")
    parser.add_argument("--variants", metavar="OP", help="inspect published alternatives")
    parser.add_argument("--operation", action="append", default=[],
                        help="select an API/typed operation (repeat or comma-separate)")
    parser.add_argument("--config", type=Path, help="JSON selection configuration")
    parser.add_argument("--objective", choices=OBJECTIVES)
    parser.add_argument("--target", choices=TARGETS)
    parser.add_argument("--zp-budget", type=int)
    parser.add_argument("--ram-budget", type=int)
    parser.add_argument("--pin", action="append", default=[], metavar="OP=VARIANT",
                        help="pin a catalog variant for subsequent integration")
    parser.add_argument("--out", type=Path,
                        default=Path("build_selective/selection_manifest.json"))
    parser.add_argument("--preview", action="store_true", help="print plan, do not write")
    parser.add_argument("--validate-sources", action="store_true",
                        help="SHA-check referenced source mirrors and records")
    parser.add_argument("--build", action="store_true",
                        help="request a PRG (currently refused until linker qualification)")
    args = parser.parse_args(argv)
    try:
        index = operation_index()
        if args.list:
            for api, op in index.items():
                print("{:<25} {:<12} {}".format(api, op["category"], op["canonical_name"]))
            return 0
        if args.variants:
            api = resolve(args.variants, index)
            print(json.dumps(index[api], indent=2))
            return 0

        cfg = json.loads(args.config.read_text(encoding="utf-8")) if args.config else {}
        if not isinstance(cfg, dict):
            raise SelectionError("Configuration must be a JSON object")
        selected = cfg.get("operations", []) + args.operation
        if not selected:
            if not sys.stdin.isatty():
                raise SelectionError("Supply --operation or --config in noninteractive mode")
            selected = interactive_pick(index)
        if not isinstance(selected, list) or not all(isinstance(s, str) for s in selected):
            raise SelectionError("operations must be a list of strings")
        pins = dict(cfg.get("pins", {}))
        for value in args.pin:
            if "=" not in value:
                raise SelectionError("Expected --pin OP=VARIANT")
            name, variant = value.split("=", 1)
            if name in pins and pins[name] != variant:
                raise SelectionError("Conflicting --pin for " + name)
            pins[name] = variant

        constraints = cfg.get("constraints", {})
        plan = create_plan(
            index, selected,
            target=args.target or cfg.get("target", "c64"),
            objective=args.objective or cfg.get("objective", "balanced"),
            zp_budget=args.zp_budget if args.zp_budget is not None
                      else constraints.get("max_zp_bytes"),
            ram_budget=args.ram_budget if args.ram_budget is not None
                       else constraints.get("max_ram_bytes"),
            pins=pins, validate_sources=args.validate_sources,
        )
        if args.build:
            raise SelectionError(
                "Selective PRG linking is not qualified yet; plan only. "
                "The current complete-image builder remains unchanged."
            )
        payload = json.dumps(plan, indent=2) + "\n"
        if args.preview:
            print(payload, end="")
        else:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(payload, encoding="utf-8")
            print("Wrote selection plan: " + str(args.out))
            print("Selected {} operations; no binary was built.".format(len(plan["operations"])))
        return 0
    except (SelectionError, OSError, json.JSONDecodeError, TypeError) as exc:
        parser.exit(2, "math_builder: {}\n".format(exc))


if __name__ == "__main__":
    raise SystemExit(main())
