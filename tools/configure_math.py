#!/usr/bin/env python3
"""One-command, operation-first C64 Math Library configuration and build.

A small front-end to the *existing* math_builder and selective_linker; there
is no second optimizer, no release-profile switch, and no guessed cycle
weights. All output is produced after a successful source-qualified link.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

import math_builder as builder
import selective_linker as linker

OBJECTIVES = builder.OBJECTIVES


def positive_calls(records: list[str], index: dict, operations: list[str]) -> dict:
    """Resolve unambiguous positive workload counts or fail closed."""
    selected = set(operations)
    values = {}
    for item in records:
        if "=" not in item:
            raise builder.SelectionError("Expected OP=COUNT (for example UMUL16=20)")
        raw_name, raw_count = item.split("=", 1)
        api = builder.resolve(raw_name, index)
        if api not in selected or api in values:
            raise builder.SelectionError("Repeated or unselected workload operation: " + api)
        if not raw_count.isdecimal() or not 1 <= int(raw_count) <= 1000000:
            raise builder.SelectionError("Call count must be an integer from 1 to 1000000")
        values[api] = int(raw_count)
    return values


def resolve_pins(records: list[str], index: dict, operations: list[str]) -> dict:
    pins = {}
    for item in records:
        if "=" not in item:
            raise builder.SelectionError("Expected OP=link:VARIANT")
        raw_name, variant = item.split("=", 1)
        api = builder.resolve(raw_name, index)
        if api not in operations or (api in pins and pins[api] != variant):
            raise builder.SelectionError("Conflicting or unselected pinned operation: " + api)
        pins[api] = variant
    return pins


def choice(prompt: str, permitted: tuple[str, ...], default: str) -> str:
    raw = input(prompt + " [" + default + "]: ").strip().lower()
    value = raw or default
    if value not in permitted:
        raise builder.SelectionError(
            "Invalid choice " + repr(value) + "; choose " + ", ".join(permitted))
    return value


def budget(prompt: str) -> int | None:
    raw = input(prompt + " (blank = no specified budget): ").strip()
    if not raw:
        return None
    if not raw.isdecimal():
        raise builder.SelectionError("Budget must be a non-negative decimal integer")
    return int(raw)


def collect(args, index: dict, *, interactive: bool):
    """Return a normalized config; no writes and no hidden defaults."""
    names = args.operation
    if not names:
        if not interactive:
            raise builder.SelectionError(
                "Noninteractive setup requires --operation (repeat for each API)")
        names = builder.interactive_pick(index)
    operations = builder.parse_operations(names, index)

    objective = args.objective
    if objective is None:
        objective = choice(
            "Objective (balanced / speed / size / zp)",
            OBJECTIVES, "balanced") if interactive else "balanced"
    if objective not in OBJECTIVES:
        raise builder.SelectionError("Unknown optimization objective: " + str(objective))
    zp = args.zp_budget
    ram = args.ram_budget
    if interactive:
        if zp is None:
            zp = budget("Available zero-page bytes")
        if ram is None:
            ram = budget("Maximum total library RAM bytes")

    calls = positive_calls(args.calls, index, operations)
    if objective == "speed":
        if interactive:
            for api in operations:
                if api not in calls:
                    raw = input("Expected calls per workload for " + api +
                                " (required positive integer): ").strip()
                    calls.update(positive_calls([api + "=" + raw], index, operations))
        if set(calls) != set(operations):
            missing = ", ".join(sorted(set(operations)-set(calls)))
            raise builder.SelectionError(
                "Speed mode requires --calls for every selected operation; missing " +
                missing)
    elif calls:
        raise builder.SelectionError("--calls is only valid with --objective speed")

    pins = resolve_pins(args.pin, index, operations)
    memory = {}
    if args.memory_config is not None:
        memory = json.loads(args.memory_config.read_text(encoding="utf-8"))
        if not isinstance(memory, dict):
            raise builder.SelectionError("Memory placement must be a JSON object")
    config = {
        "target": "c64",
        "operations": [api.removeprefix("MATH_") for api in operations],
        "objective": objective,
        "constraints": {
            "max_zp_bytes": zp,
            "max_ram_bytes": ram,
        },
    }
    if calls:
        config["workload_calls"] = {
            api.removeprefix("MATH_"): calls[api] for api in operations
        }
    if pins:
        config["pins"] = {
            api.removeprefix("MATH_"): pins[api] for api in sorted(pins)
        }
    if memory:
        config["memory"] = memory
    return config


def build_checked(config: dict, index: dict, folder: Path) -> dict:
    """Re-use the production selector and linker, never a DIY estimator."""
    plan = builder.create_plan(
        index, config["operations"],
        target=config["target"],
        objective=config["objective"],
        zp_budget=config["constraints"]["max_zp_bytes"],
        ram_budget=config["constraints"]["max_ram_bytes"],
        workload_calls=config.get("workload_calls"),
        pins=config.get("pins"),
    )
    return linker.build(plan, folder, memory=config.get("memory", {}))


def destination_is_available(path: Path, label: str) -> None:
    if path.exists():
        raise builder.SelectionError(
            label + " already exists: " + str(path) +
            " (choose a new path; never overwrite an existing project)")
    if not path.parent.is_dir():
        # Missing parents are allowed; created only after qualification passes.
        if any(parent.is_file() for parent in path.parents):
            raise builder.SelectionError(label + " parent is not a directory")


def run(args, index=None, *, interactive: bool | None = None) -> dict:
    if index is None:
        index = builder.operation_index()
    if interactive is None:
        interactive = not args.operation and sys.stdin.isatty()
    config = collect(args, index, interactive=interactive)
    config_out = args.config_out
    build_dir = args.build_dir
    if config_out.resolve() == build_dir.resolve() or config_out.resolve().is_relative_to(build_dir.resolve()):
        raise builder.SelectionError("Configuration file must be outside the build directory")
    destination_is_available(config_out, "Configuration file")
    destination_is_available(build_dir, "Build directory")
    with tempfile.TemporaryDirectory(prefix="math_user_setup_") as work:
        source_dir = Path(work)
        manifest = build_checked(config, index, source_dir)
        names = ("math_selective.prg", "math_api.inc", "selective_manifest.json")
        for name in names:
            if not (source_dir / name).is_file():
                raise builder.SelectionError("Linker did not produce " + name)
        config_contents = json.dumps(config, indent=2) + "\n"
        # Source verification and all budget/address collision checks are now
        # complete. Copy the immutable verified image, not a rebuilt variant.
        build_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_dir, build_dir)
        try:
            config_out.parent.mkdir(parents=True, exist_ok=True)
            config_out.write_text(config_contents, encoding="utf-8")
        except (OSError, ValueError):
            shutil.rmtree(build_dir)
            raise
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Choose C64 operations and constraints, then build an editable project setup")
    parser.add_argument("--operation", action="append", default=[],
                        help="requested operation, repeat or comma-separate; interactive if omitted")
    parser.add_argument("--objective", choices=OBJECTIVES,
                        help="balanced (default), speed, size or zp")
    parser.add_argument("--zp-budget", type=int, help="total zero-page byte limit, 0 permitted")
    parser.add_argument("--ram-budget", type=int, help="total RAM limit including I/O, scratch and tables")
    parser.add_argument("--calls", action="append", default=[], metavar="OP=COUNT",
                        help="required per-operation workload count in speed mode")
    parser.add_argument("--pin", action="append", default=[], metavar="OP=LINK_VARIANT",
                        help="expert override to a specific certified linkable variant")
    parser.add_argument("--memory-config", type=Path,
                        help="optional JSON object defining the linker's memory map and reservations")
    parser.add_argument("--config-out", type=Path, default=Path("my_math.json"),
                        help="write reusable config; refuses to overwrite existing files")
    parser.add_argument("--build-dir", type=Path, default=Path("build_my_math"),
                        help="write verified PRG, include and manifest here; refuses overwrite")
    args = parser.parse_args(argv)
    try:
        manifest = run(args)
        usage = manifest["resource_use"]
        print("Verified project configuration: " + str(args.config_out))
        print("Built source-qualified selective PRG: " +
              str(args.build_dir / "math_selective.prg"))
        print("Assembly exports: " + str(args.build_dir / "math_api.inc"))
        print("Exact placement/variants: " +
              str(args.build_dir / "selective_manifest.json"))
        print("Operations: " + ", ".join(x["api"] for x in manifest["operations"]))
        print("Objective: " + manifest["selection_objective"])
        print("Total main RAM bytes: " + str(usage["main_ram_total_bytes"]))
        print("Total ZP bytes: " + str(usage["zero_page_bytes"]))
        print("No historical V1-V5 profile was installed or replaced.")
        return 0
    except (builder.SelectionError, linker.LinkError, OSError,
            ValueError, TypeError, json.JSONDecodeError, EOFError) as exc:
        parser.exit(2, "configure_math: " + str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
