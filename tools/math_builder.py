#!/usr/bin/env python3
"""Operation-first selector for the next C64 Math Library builder.

Phase 1 deliberately emits a *plan*, not a PRG. Resident profile mirrors are
not independently linkable and record kernels may have incompatible ABI or
resource ownership. Until selective linking is proven, fail closed.
"""
from __future__ import annotations

import argparse
import csv
import copy
import hashlib
import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "routines" / "SOURCE_CATALOG.csv"
OPERATIONS = ROOT / "routines" / "PUBLIC_OPERATIONS.csv"
STANDALONE = ROOT / "benchmarks" / "STANDALONE_RESULTS.csv"
OBJECTIVES = ("balanced", "speed", "size", "zp")
TARGETS = ("c64", "1541", "1571", "1581")


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
    # The public operation vocabulary is independent of historical V1-V5
    # release profiles. Those profiles contribute source variants only.
    operations: dict[str, dict] = {}
    canonical_to_api: dict[str, str] = {}
    for r in read_csv(root / "routines" / "PUBLIC_OPERATIONS.csv"):
        api = r["api"]
        canonical = r["canonical_name"]
        category = r["category"]
        if not api.startswith("MATH_") or api in operations or not canonical or not category:
            raise SelectionError("Duplicate or invalid public operation: " + api)
        if canonical in canonical_to_api:
            raise SelectionError("Duplicate canonical operation: " + canonical)
        operations[api] = {
            "api": api,
            "canonical_name": canonical,
            "category": category,
            "variants": [],
        }
        canonical_to_api[canonical] = api

    if not operations:
        raise SelectionError("Empty public operation catalog")

    for r in rows:
        if r["scope"] == "shipped-profile":
            api = r["legacy_api"]
            if api not in operations:
                # Hardware-specific additions are not in the portable core set.
                continue
            if r["canonical_name"] != operations[api]["canonical_name"]:
                raise SelectionError("Inconsistent canonical operation for " + api)
            variant_id = "mirror:" + r["source_sha256"][:12]
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
            "historical_provenance": r["profile"] if kind == "resident-source-mirror" else None,
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

    # First independently relocatable arithmetic modules, with explicit source contracts.
    import selective_linker
    for api, variants in selective_linker.available_variants(root).items():
        if api not in operations:
            raise SelectionError("Unknown linkable operation: " + api)
        operations[api]["variants"].extend(variants)
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
    for dependency, expected in source.get("dependency_sha256", {}).items():
        dep = (root / dependency).resolve()
        if not dep.is_relative_to(root.resolve()) or not dep.is_file():
            raise SelectionError("Missing or unsafe dependency: " + dependency)
        if hashlib.sha256(dep.read_bytes()).hexdigest() != expected:
            raise SelectionError("Source dependency checksum mismatch: " + dependency)


def create_plan(
    index: dict[str, dict], names: list[str], *, target: str = "c64",
    objective: str = "balanced", zp_budget: int | None = None,
    ram_budget: int | None = None, pins: dict[str, str] | None = None,
    validate_sources: bool = False, root: Path = ROOT,
    workload_calls: dict[str, int] | None = None,
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
    calls: dict[str, int] = {}
    if workload_calls is not None:
        if objective != "speed" or not isinstance(workload_calls, dict):
            raise SelectionError("Workload calls require the speed objective and a JSON object")
        for name, count in workload_calls.items():
            if not isinstance(name, str):
                raise SelectionError("Workload operation name must be a string")
            api = resolve(name, index)
            if api not in selected or api in calls:
                raise SelectionError("Duplicate or unselected workload operation: " + api)
            if type(count) is not int or not 1 <= count <= 1000000:
                raise SelectionError("Workload calls must be positive integers <= 1000000")
            calls[api] = count
    if objective == "speed":
        if len(selected) == 1 and workload_calls is None:
            calls[selected[0]] = 1
        if set(calls) != set(selected):
            raise SelectionError("Speed selection requires workload calls for every selected operation")
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
        # A plan is a provenance snapshot, never an alias into the catalog.
        # Tests and callers may intentionally tamper with a plan to verify
        # checksum rejection without poisoning later builds.
        variants = copy.deepcopy(op["variants"])
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

    can_link = target == "c64" and all(
        any(v["selective_link_ready"] and target in v.get("build_targets", ["c64"])
            for v in op["available_source_variants"]) for op in output)
    return {
        "schema": "math-selection-plan-v2",
        "status": "planning_only_not_a_loadable_binary",
        "target": target,
        "target_backend_status": ("experimental_selective_linker"
                                  if target == "c64" else "planning_only_no_target_backend"),
        "objective": objective,
        "workload_calls": dict(sorted(calls.items())) if objective == "speed" else None,
        "constraints": {"max_zp_bytes": zp_budget, "max_ram_bytes": ram_budget},
        "operations": output,
        "public_operation_count": len(output),
        "unresolved_dependencies": True,
        "linker_status": ("experimental_subset_available" if can_link else
                          "target_backend_unavailable" if target != "c64" else
                          "operations_unqualified_for_selective_linking"),
        "notes": [
            "Variant cycle means may use different corpora; do not rank across bases.",
            "Per-routine zero-page and memory claims must not be added together.",
            "Resident source mirrors and standalone records are not automatically linkable.",
            "Only the C64 currently has experimental selective executable modules; "
            "other targets accept plans but do not permit binary output.",
            "Build-time compatibility, dependencies, memory ownership and execution "
            "must be verified before producing a selective PRG.",
        ],
    }


def operation_description(api: str) -> str:
    """Readable labels; all technical names still resolve unchanged."""
    tail = api.removeprefix("MATH_")
    for prefix, kind in (("UMULDIV", "Unsigned multiply/divide"),
                         ("SMULDIV", "Signed multiply/divide"),
                         ("UMUL", "Unsigned multiply"), ("SMUL", "Signed multiply"),
                         ("UDIV", "Unsigned divide"), ("SDIV", "Signed divide"),
                         ("UMOD", "Unsigned remainder"), ("SMOD", "Signed remainder")):
        if tail.startswith(prefix):
            return kind + " " + tail[len(prefix):].replace("_", " ")
    names = {
        "SIN8": "8-bit sine", "COS8": "8-bit cosine",
        "SINCOS8": "8-bit sine and cosine", "ATAN2_8": "8-bit vector angle",
        "ISQRT16": "16-bit integer square root",
        "ISQRT32": "32-bit integer square root",
        "URECIP16_Q16": "16-bit reciprocal in Q16",
        "DIST8_FAST": "Fast 8-bit vector distance",
        "DIST8_ACCURATE": "Accurate 8-bit vector distance",
        "VEC2_NORMALIZE_Q8_8": "Normalize 2D Q8.8 vector",
    }
    if tail in names:
        return names[tail]
    if tail.startswith("SEEK"):
        return "Seek/movement " + tail[4:].replace("_", " ")
    return tail.replace("_", " ")


def parse_interactive_choices(raw: str, numbered: list[str]) -> list[str]:
    selected = []
    for part in raw.split(","):
        term = part.strip()
        if not term:
            continue
        if term.isdecimal():
            number = int(term)
            if not 1 <= number <= len(numbered):
                raise SelectionError("Operation number out of range: " + term)
            selected.append(numbered[number - 1])
        elif "-" in term and all(x.strip().isdecimal() for x in term.split("-", 1)):
            first, last = (int(x.strip()) for x in term.split("-", 1))
            if not 1 <= first <= last <= len(numbered):
                raise SelectionError("Invalid operation range: " + term)
            selected.extend(numbered[first-1:last])
        else:
            selected.append(term)
    return selected


def interactive_pick(index: dict[str, dict]) -> list[str]:
    categories: dict[str, list[str]] = {}
    for api, op in index.items():
        categories.setdefault(op["category"], []).append(api)
    numbered = []
    print("C64 Math Library — choose operations (no fixed profile)")
    print("Select by number, range (e.g. 1-3), or operation name.")
    print("Asterisk = selective-linkable source currently available.")
    for category, names in sorted(categories.items()):
        print("\n" + category.title())
        for name in names:
            numbered.append(name)
            ready = any(v["selective_link_ready"] for v in index[name]["variants"])
            print("  {:2d}{} {:25s} {}".format(
                len(numbered), "*" if ready else " ", name, operation_description(name)))
    print("\nOnly starred operations can currently produce a minimal PRG.")
    raw = input("Operations (e.g. 2,5,8-11 or UDIV16,UMOD16): ")
    return parse_interactive_choices(raw, numbered)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plan a minimal math library from operations, budgets and variants."
    )
    parser.add_argument("--list", action="store_true", help="list public operations")
    parser.add_argument("--list-linkable", action="store_true",
                        help="list operations with currently link-ready sources")
    parser.add_argument("--variants", metavar="OP", help="inspect published alternatives")
    parser.add_argument("--operation", action="append", default=[],
                        help="select an API/typed operation (repeat or comma-separate)")
    parser.add_argument("--config", type=Path, help="JSON selection configuration")
    parser.add_argument("--objective", choices=OBJECTIVES + ("frame",))
    parser.add_argument("--target", choices=TARGETS)
    parser.add_argument("--zp-budget", type=int)
    parser.add_argument("--ram-budget", type=int)
    parser.add_argument("--calls", action="append", default=[], metavar="OP=COUNT",
                        help="speed workload: calls of this operation per frame (repeat)")
    parser.add_argument("--frame-report", type=Path,
                        help="source-linked exact mixed frame evidence (frame objective only)")
    parser.add_argument("--frame-max-cycles", type=int,
                        help="max synthetic math-only peak cycles per measured frame")
    parser.add_argument("--frame-optimize", choices=("peak", "ram", "zp"),
                        help="goal within frame-qualified full linked source plans")
    parser.add_argument("--pin", action="append", default=[], metavar="OP=VARIANT",
                        help="pin a catalog variant for subsequent integration")
    parser.add_argument("--out", type=Path,
                        default=Path("build_selective/selection_manifest.json"))
    parser.add_argument("--preview", action="store_true", help="print plan, do not write")
    parser.add_argument("--validate-sources", action="store_true",
                        help="SHA-check referenced source mirrors and records")
    parser.add_argument("--build", action="store_true",
                        help="build a qualified selective source-only subset")
    parser.add_argument("--measure", action="store_true",
                        help="assemble in temporary memory and print exact linked resources")
    args = parser.parse_args(argv)
    try:
        index = operation_index()
        if args.list or args.list_linkable:
            requested_target = args.target or "c64"
            printed = 0
            for api, op in index.items():
                eligible = sum(v["selective_link_ready"] and
                               requested_target in v.get("build_targets", ["c64"])
                               for v in op["variants"])
                if args.list_linkable and not eligible:
                    continue
                print("{:<25} {:<12} {}{}".format(api, op["category"],
                    op["canonical_name"], " [linkable: {}]".format(eligible) if eligible else ""))
                printed += 1
            if args.list_linkable and printed == 0:
                print("No selectively linkable modules for target " +
                      requested_target + "; planning only.", file=sys.stderr)
            return 0
        if args.variants:
            api = resolve(args.variants, index)
            requested_target = args.target or "c64"
            operation = dict(index[api])
            operation["requested_target"] = requested_target
            operation["variants"] = [
                {**v, "target_link_ready": bool(
                    v["selective_link_ready"] and requested_target in
                    v.get("build_targets", ["c64"]))}
                for v in operation["variants"]]
            print(json.dumps(operation, indent=2))
            return 0

        cfg = json.loads(args.config.read_text(encoding="utf-8")) if args.config else {}
        if not isinstance(cfg, dict):
            raise SelectionError("Configuration must be a JSON object")
        if "hardware" in cfg:
            # Saved operation-first project configurations must not silently
            # drop the user's selected REU service on a later rebuild.
            if not (args.build or args.measure) or args.preview:
                raise SelectionError("Hardware REU config requires --build or --measure")
            if (args.operation or args.objective or args.target or args.zp_budget is not None or
                    args.ram_budget is not None or args.pin or args.calls or
                    args.frame_report or args.frame_max_cycles is not None or
                    args.frame_optimize or args.validate_sources):
                raise SelectionError("REU rebuild must use saved project options unchanged")
            import configure_math as user_setup
            if args.measure:
                with tempfile.TemporaryDirectory(prefix="math_reu_measure_") as folder:
                    stock = user_setup.build_checked(cfg,index,Path(folder))
                    combined = json.loads(
                        (Path(folder)/"math_project_manifest.json").read_text())
                print(json.dumps({
                    "stock_operations":[o["api"] for o in stock["operations"]],
                    "combined_resource_use":combined["combined_resource_use"],
                    "hardware":combined["hardware"],
                    "native_mixed_irq_vic_qualified":False,
                },indent=2))
            else:
                result = user_setup.build_checked(cfg,index,args.out.parent)
                print("Built operation-first stock PRG:",args.out.parent/"math_selective.prg")
                print("Built explicit REU Turbo16 companion:",args.out.parent/"turbo16_reu.prg")
                print("Stock operations:",", ".join(o["api"] for o in result["operations"]))
            return 0
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
        workloads = cfg.get("workload_calls", None)
        if args.calls:
            if workloads is None:
                workloads = {}
            if not isinstance(workloads, dict):
                raise SelectionError("workload_calls must be a JSON object")
            workloads = dict(workloads)
            for record in args.calls:
                if "=" not in record:
                    raise SelectionError("Expected --calls OP=COUNT")
                name, value = record.split("=", 1)
                if name in workloads:
                    raise SelectionError("Duplicate workload --calls: " + name)
                if not value.isdecimal():
                    raise SelectionError("Invalid workload call count: " + value)
                workloads[name] = int(value)
        objective_requested = args.objective or cfg.get("objective", "balanced")
        if objective_requested == "frame":
            import frame_builder_mode
            try:
                return frame_builder_mode.run(
                    args, cfg, selected, pins, constraints, workloads, index)
            except (ValueError, KeyError) as error:
                raise SelectionError("frame evidence: " + str(error)) from error
        if args.frame_report is not None or args.frame_max_cycles is not None or args.frame_optimize is not None:
            raise SelectionError("Frame evidence flags require --objective frame")

        plan = create_plan(
            index, selected,
            target=args.target or cfg.get("target", "c64"),
            objective=args.objective or cfg.get("objective", "balanced"),
            zp_budget=args.zp_budget if args.zp_budget is not None
                      else constraints.get("max_zp_bytes"),
            ram_budget=args.ram_budget if args.ram_budget is not None
                       else constraints.get("max_ram_bytes"),
            pins=pins, validate_sources=args.validate_sources,
            workload_calls=workloads,
        )
        if args.measure:
            if args.build or args.preview:
                raise SelectionError("--measure cannot be combined with --build or --preview")
            import selective_linker
            try:
                with tempfile.TemporaryDirectory(prefix="c64_math_measure_") as folder:
                    manifest = selective_linker.build(plan, Path(folder),
                                                      memory=cfg.get("memory", {}))
            except selective_linker.LinkError as exc:
                raise SelectionError(str(exc)) from exc
            print(json.dumps({
                "operations": [x["api"] for x in manifest["operations"]],
                "selected_variants": {x["api"]: x["variant"] for x in manifest["operations"]},
                "resource_use": manifest["resource_use"],
                "memory_map": manifest["memory_map"],
                "note": "Exact assembled bytes, experimental source; no output retained.",
            }, indent=2))
            return 0
        if args.build:
            if args.preview:
                raise SelectionError("--build and --preview are mutually exclusive")
            import selective_linker
            try:
                manifest = selective_linker.build(plan, args.out.parent,
                                                  memory=cfg.get("memory", {}))
            except selective_linker.LinkError as exc:
                raise SelectionError(str(exc)) from exc
            print("Built minimal PRG:", args.out.parent / "math_selective.prg")
            print("Linked operations:", ", ".join(x["api"] for x in manifest["operations"]))
            print("Code bytes:", manifest["resource_use"]["code_and_tables_bytes"])
            return 0
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
