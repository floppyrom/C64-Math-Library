#!/usr/bin/env python3
"""Generate *measured* operation-first per-routine variant performance and footprints.

No historical-profile cycle figures are imported. For each of 56 stock C64
operations, run the same-input public-ABI speed benchmark over all link-ready
variants, then independently build every pinned variant with the real linker
to obtain actual physical resource use. Never sum isolated footprints.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile

import math_builder as builder
import selective_linker as linker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "routines/PUBLIC_OPERATIONS.csv"
MD = ROOT / "docs/OPERATION_FIRST_ROUTINE_METRICS.md"
CSV = ROOT / "benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv"
META = ROOT / "validation/OPERATION_FIRST_VARIANT_METRICS.json"
RESOURCE_KEYS = (
    "code_and_tables_bytes", "image_span_bytes", "shared_table_bytes",
    "alignment_padding_bytes", "public_io_bytes",
    "private_ram_scratch_bytes", "persistent_state_bytes",
    "state_alignment_padding_bytes", "main_ram_total_bytes",
    "zero_page_bytes", "persistent_stack_page_bytes",
)
FIELDS = (
    "operation", "category", "typed_name", "variant",
    "mean_cpu_cycles", "corpus_cases", "corpus_sha256", "cycle_basis",
    *RESOURCE_KEYS, "source_path", "source_sha256",
    "linked_prg_sha256", "code_origin", "io_origin", "zp_origin",
)


def index_and_operations():
    index = builder.operation_index(ROOT)
    with CATALOG.open(newline="", encoding="utf-8") as stream:
        operations = list(csv.DictReader(stream))
    names = [entry["api"] for entry in operations]
    if len(names) != len(set(names)) or len(names) != 56 or set(names) != set(index):
        raise AssertionError("Operation-first 56-public-API catalog changed")
    if set(names) != set(linker.MODULES):
        raise AssertionError("The linkable stock C64 module set changed")
    return index, operations


def measure(index, operations):
    result = []
    per_api = {}
    # Standard linker placement, used by the current speed objective.
    # These are isolated source footprints, not a recommendation for games.
    for ordinal, op in enumerate(operations, 1):
        api = op["api"]
        variants = linker.MODULES[api]
        with tempfile.TemporaryDirectory(prefix="math_metric_" + api.lower() + "_") as td:
            temp = Path(td)
            speed = builder.create_plan(
                index, [api], objective="speed", zp_budget=254,
                ram_budget=65536, workload_calls={api: 1}, root=ROOT,
            )
            sm = linker.build(speed, temp / "speed", root=ROOT)
            benchmark = sm.get("cycle_model_benchmark")
            if not benchmark or benchmark.get("cpu_model_only") is not True:
                raise AssertionError(api + ": no qualified CPU-model speed benchmark")
            corpus_sha = benchmark.get("corpus_sha256", "")
            if len(corpus_sha) != 64:
                raise AssertionError(api + ": missing corpus SHA")
            means = benchmark.get("mean_cycles", {})
            if set(means) != set(variants):
                raise AssertionError(api + ": incomplete same-input variant cycle data")
            source_hashes = benchmark.get("source_sha256", {})
            for variant in sorted(variants):
                mean = float(means[variant])
                if not math.isfinite(mean) or mean <= 0:
                    raise AssertionError(api + "/" + variant + ": invalid cycle mean")
                plan = builder.create_plan(
                    index, [api], objective="size", pins={api: variant},
                    zp_budget=254, ram_budget=65536, root=ROOT,
                )
                pm = linker.build(plan, temp / "pinned", root=ROOT)
                if len(pm["operations"]) != 1 or pm["operations"][0]["variant"] != variant:
                    raise AssertionError(api + ": wrong pinned source was linked")
                resources = pm["resource_use"]
                if resources["main_ram_total_bytes"] < resources["code_and_tables_bytes"] + 32:
                    raise AssertionError(api + ": incomplete physical RAM accounting")
                if resources["persistent_stack_page_bytes"] != 0:
                    # This script reports persistent ownership only, not peak transient SP.
                    raise AssertionError(api + ": unexpected persistent stack reservation")
                src = variants[variant]["source"]
                sha = hashlib.sha256((ROOT / src).read_bytes()).hexdigest()
                if variant in source_hashes and source_hashes[variant] != sha:
                    raise AssertionError(api + "/" + variant + ": speed/source hash mismatch")
                row = {
                    "operation": api, "category": op["category"],
                    "typed_name": op["canonical_name"], "variant": variant,
                    "mean_cpu_cycles": format(mean, ".9f").rstrip("0").rstrip("."),
                    "corpus_cases": benchmark.get("cases", ""),
                    "corpus_sha256": corpus_sha, "cycle_basis": benchmark.get("basis", ""),
                    **{k: resources.get(k, 0) for k in RESOURCE_KEYS},
                    "source_path": src, "source_sha256": sha,
                    "linked_prg_sha256": pm["prg_sha256"],
                    "code_origin": pm["memory_map"]["code_start"],
                    "io_origin": pm["memory_map"]["math_io_start"],
                    "zp_origin": pm["memory_map"]["zp_start"] or "",
                }
                result.append(row)
            per_api[api] = {
                "corpus_sha256": corpus_sha,
                "basis": benchmark.get("basis", ""),
                "variants": len(variants),
                "source_benchmark_code_origin": benchmark.get("code_origin", "$8000"),
                "source_benchmark_io_origin": benchmark.get("io_origin", "$C000"),
                "note": benchmark.get("note", ""),
            }
        print(f"[{ordinal:02d}/56] {api}: {len(variants)} source variants", flush=True)
    return result, per_api


def contents(rows, per_api):
    if len({row["operation"] for row in rows}) != 56:
        raise AssertionError("Not every operation measured")
    if not all(row["cycle_basis"] and row["corpus_sha256"] for row in rows):
        raise AssertionError("Every measurement needs its complete benchmark basis")
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    csv_text = out.getvalue()
    groups = {}
    for row in rows:
        groups.setdefault(row["operation"], []).append(row)
    lines = [
        "# Operation-first routine metrics: cycles, RAM, zero page and stack",
        "",
        "**Current stock-C64 operation-first system.** Measurements are taken",
        "from the **real qualified selective builder**, not historical V1–V5",
        "resident averages. Every one of the 56 public APIs has an isolated",
        "fully assembled source-linked footprint. Each variant's cycle mean",
        "uses the **same input corpus as the other variants of that operation**.",
        "Different operations can have different corpora; cross-operation means",
        "are therefore not a calibrated mixed-application speed ranking.",
        "",
        "## One-row-per-operation reference (fastest measured isolated variant)",
        "",
        "This is a lookup convenience, **not the universal fastest combined",
        "project**: globally shared kernels, budgets, origins, requested variants",
        "and call frequency can change an actual multi-operation build.",
        "",
        "| Operation | Fastest measured linkable variant | Mean CPU cycles/call | Code + tables B | Total isolated RAM B | ZP B | Persistent stack-page B |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for api in sorted(groups):
        best = min(groups[api], key=lambda r: (
            float(r["mean_cpu_cycles"]),
            int(r["main_ram_total_bytes"]),
            int(r["zero_page_bytes"]),
            r["variant"],
        ))
        lines.append(
            f'| \`{api}\` | \`{best["variant"]}\` | '
            f'{float(best["mean_cpu_cycles"]):.6f} | '
            f'{best["code_and_tables_bytes"]} | '
            f'{best["main_ram_total_bytes"]} | '
            f'{best["zero_page_bytes"]} | '
            f'{best["persistent_stack_page_bytes"]} |'
        )
    lines.extend([
        "",
        "## All selectable source variants (complete numeric data)",
        "",
        f"**{len(rows)} separately source-linked variant observations covering 56",
        "operations** are available in",
        "[\`benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv\`](../benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv).",
        "That detailed file includes each source's exact mean CPU-model cycles,",
        "code-and-tables size, full isolated RAM total, alignment/image span,",
        "shared tables, scratch, persistent object state, ZP and persistent",
        "stack-page reservation, benchmark case count/basis/input SHA,",
        "source SHA and linked PRG SHA. Filter its \`operation\` column to",
        "compare only like-for-like input corpora.",
        "",
        "### What the columns mean",
        "",
        "- **Mean CPU cycles/call:** public entry through RTS, as measured by",
        "  that operation's original source-qualified Mini6502 benchmark;",
        "  not a physical PAL frame or REU-inclusive elapsed time. Benchmark",
        "  source functions record each input corpus SHA in the CSV.",
        "- **Code + tables B:** independently source-assembled executable",
        "  and owned lookup-table bytes; padding is separately represented",
        "  by \`image_span_bytes\` and \`alignment_padding_bytes\` in the CSV.",
        "- **Total isolated RAM B:** the actual physical one-operation linker",
        "  charge, including 32 B of public I/O, scratch, persistent state",
        "  and alignment. This is **not additive** across APIs: code and",
        "  tables may be shared in a real combined library.",
        "- **ZP B:** bytes required by the linked standalone variant; this",
        "  is an ownership reservation, not a sum of simultaneous per-call",
        "  touches. A combined build can share call-exclusive scratch.",
        "- **Persistent stack-page B:** hardware stack page $0100–$01FF",
        "  *reserved for persistent library storage*. Stock selective",
        "  variants currently reserve zero such bytes. **Transient JSR/RTS,",
        "  PHA/PLA or interrupt stack high-water is NOT measured here.**",
        "  Zero does not mean zero runtime stack usage.",
        "",
        "## Get your exact installed project footprint and speed choice",
        "",
        "\`\`\`sh",
        "python3 tools/math_builder.py --variants UMUL16",
        "",
        "python3 tools/configure_math.py \\",
        "  --operation UMUL16 --objective speed --calls UMUL16=1 \\",
        "  --zp-budget 120 --ram-budget 16000 \\",
        "  --config-out umul16-speed.json --build-dir build_umul16_speed",
        "",
        "# Actual selected source, total RAM/ZP, source hashes and measured cycle basis:",
        "python3 -m json.tool build_umul16_speed/selective_manifest.json",
        "\`\`\`",
        "",
        "For multiple operations, the **combined** \`selective_manifest.json\`",
        "overrides the isolated per-row memory figures. The optional Turbo16",
        "REU service uses **additional** independently reserved executable",
        "ZP and C64/REU memory and is not included in these stock-only rows.",
        "There is no verified DMA-inclusive speed ranking for the optional REU",
        "service. See [REU integration](OPERATION_FIRST_REU_TURBO16.md).",
        "",
        "## Reproduce and audit",
        "",
        "The report generator calls the current real single-operation speed",
        "selector for **every candidate variant on its common inputs**, and",
        "then independently assembles **each pinned variant** for the physical",
        "resource measurements at the default stock linker origin. Any",
        "cycle-benchmark omission, changed source hash, missing operation or",
        "failed binary link aborts publication; numerical guesses and",
        "historical profile speed exports are never used.",
        "",
        "\`\`\`sh",
        "python3 tools/report_operation_first_metrics.py",
        "python3 tools/report_operation_first_metrics.py --verify",
        "\`\`\`",
        "",
        "This report is a **generated, reproducible reference** for the",
        "particular source revision and standard isolated placement. The",
        "per-operation corpus basis and full SHA provenance are in",
        "[the machine-readable validation record](../validation/OPERATION_FIRST_VARIANT_METRICS.json).",
        "",
    ])
    md_text = "\n".join(lines)
    meta = {
        "schema": "c64-operation-first-isolated-variant-metrics-v1",
        "target": "stock C64 operation-first source linker",
        "operations": 56,
        "measured_variants": len(rows),
        "cycle_units": "Mini6502 public entry through RTS, per-operation matched input corpus",
        "memory_units": "bytes of isolated fully linked source image + I/O/scratch/state",
        "persistent_stack_page_only": True,
        "transient_runtime_stack_peak_measured": False,
        "reu_dma_included": False,
        "reported_standard_placement": {
            "code": "$8000", "io": "$C000", "zp": "$50", "scratch": "$C020"
        },
        "operation_bases": per_api,
        "csv_sha256": hashlib.sha256(csv_text.encode()).hexdigest(),
        "markdown_sha256": hashlib.sha256(md_text.encode()).hexdigest(),
        "generator_sha256": hashlib.sha256(
            (ROOT / "tools/report_operation_first_metrics.py").read_bytes()).hexdigest(),
    }
    return md_text, csv_text, json.dumps(meta, indent=2, sort_keys=True) + "\n"


def verify(md_path=MD, csv_path=CSV, meta_path=META):
    index, ops = index_and_operations()
    csv_txt = csv_path.read_text(encoding="utf-8")
    md_txt = md_path.read_text(encoding="utf-8")
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    with io.StringIO(csv_txt) as stream:
        rows = list(csv.DictReader(stream))
    if (metadata["operations"] != len(ops) or
        metadata["measured_variants"] != len(rows) or
        hashlib.sha256(csv_txt.encode()).hexdigest() != metadata["csv_sha256"] or
        hashlib.sha256(md_txt.encode()).hexdigest() != metadata["markdown_sha256"] or
        hashlib.sha256((ROOT / "tools/report_operation_first_metrics.py").read_bytes()).hexdigest() != metadata["generator_sha256"]):
        raise AssertionError("Published chart/CSV/generator SHA, count or metadata drift")
    grouped = {}
    for row in rows:
        api, ident = row["operation"], row["variant"]
        if api not in index or ident not in linker.MODULES[api]:
            raise AssertionError("Unknown/obsolete variant " + api + "/" + ident)
        mod = linker.MODULES[api][ident]
        sha = hashlib.sha256((ROOT / mod["source"]).read_bytes()).hexdigest()
        if sha != row["source_sha256"] or row["source_path"] != mod["source"]:
            raise AssertionError(api + "/" + ident + ": source SHA no longer matches")
        if not row["corpus_sha256"] or not row["cycle_basis"]:
            raise AssertionError(api + ": missing benchmark basis")
        for field in RESOURCE_KEYS:
            if not row[field] or int(row[field]) < 0:
                raise AssertionError(api + "/" + ident + ": bad memory number " + field)
        if not math.isfinite(float(row["mean_cpu_cycles"])) or float(row["mean_cpu_cycles"]) <= 0:
            raise AssertionError(api + ": invalid cycles")
        if int(row["persistent_stack_page_bytes"]) != 0:
            raise AssertionError("Persistent stack reservation unexpectedly changed")
        grouped.setdefault(api, []).append(row)
    if set(grouped) != set(index):
        raise AssertionError("Incomplete 56-API benchmark")
    if any(set(linker.MODULES[api]) != {r["variant"] for r in group}
           for api, group in grouped.items()):
        raise AssertionError("An individually linkable variant is missing")
    if "Transient JSR/RTS" not in md_txt:
        raise AssertionError("Missing stack safety disclaimer")
    for api, group in grouped.items():
        best = min(group, key=lambda r: (
            float(r["mean_cpu_cycles"]),
            int(r["main_ram_total_bytes"]),
            int(r["zero_page_bytes"]),
            r["variant"],
        ))
        expected = (f'| \`{api}\` | \`{best["variant"]}\` | '
                    f'{float(best["mean_cpu_cycles"]):.6f} | '
                    f'{best["code_and_tables_bytes"]} | '
                    f'{best["main_ram_total_bytes"]} | '
                    f'{best["zero_page_bytes"]} | '
                    f'{best["persistent_stack_page_bytes"]} |')
        if expected not in md_txt:
            raise AssertionError(api + ": summary no longer equals detailed CSV")
    print("PASS: %d operations, %d variants, published numeric and source integrity" %
          (len(grouped), len(rows)), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true",
                        help="verify published data and source provenance without recomputing")
    args = parser.parse_args()
    if args.verify:
        verify()
    else:
        index, ops = index_and_operations()
        rows, api_meta = measure(index, ops)
        md, csv_text, manifest = contents(rows, api_meta)
        for path, content in ((MD, md), (CSV, csv_text), (META, manifest)):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        verify()


if __name__ == "__main__":
    main()
