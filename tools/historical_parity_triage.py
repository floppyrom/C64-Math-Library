#!/usr/bin/env python3
"""Historical CPU-speed donor triage against operation-first *source* inventory.

The published historical table and selective candidates are measured on
potentially DIFFERENT operand corpora and memory maps. This report never
divides historical cycle figures by unrelated new numbers or certifies
performance parity. It identifies what must be compared on identical inputs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import math_builder
import selective_linker

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = ROOT / "benchmarks" / "BEST_PROFILE_RESULTS.csv"
UNSIGNED = ROOT / "benchmarks" / "UNSIGNED_COMMON_PROFILE_RESULTS.csv"
PROFILES = frozenset({
    "v1_balanced", "v2_pareto_fast", "v3_reu_512k",
    "v4_reu_16m", "v5_hybrid_lowzp"
})


class ParityTriageError(ValueError):
    pass


def records(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ParityTriageError("Missing benchmark records: " + str(path))
    return rows


def source_hash(root: Path, relative: str) -> str:
    source = (root / relative).resolve()
    if not source.is_relative_to(root.resolve()) or not source.is_file():
        raise ParityTriageError("Missing/unsafe historical source: " + relative)
    return hashlib.sha256(source.read_bytes()).hexdigest()


def common_unsigned(root: Path) -> dict:
    """Accept only five-reference, identical-input *historical* comparisons."""
    result = {}
    by_api = {}
    for row in records(root / "benchmarks" /
                       "UNSIGNED_COMMON_PROFILE_RESULTS.csv"):
        by_api.setdefault(row["routine"], []).append(row)
    for api, rows in sorted(by_api.items()):
        if len(rows) != len(PROFILES) or {r["profile"] for r in rows} != PROFILES:
            raise ParityTriageError("Incomplete/duplicate historical common corpus: " + api)
        corpora = {r["same_cases_sha256"] for r in rows}
        cases = {r["cases"] for r in rows}
        basis = {r["cycle_basis"] for r in rows}
        if len(corpora) != 1 or len(cases) != 1 or len(basis) != 1:
            raise ParityTriageError("Historical corpus mismatches: " + api)
        if not all(len(x) == 64 for x in corpora) or not all(
            int(r["cases"]) > 0 and float(r["mean_cycles"]) > 0
            for r in rows
        ):
            raise ParityTriageError("Invalid historical timings: " + api)
        fastest = min(rows, key=lambda r: (float(r["mean_cycles"]), r["profile"]))
        result[api] = {
            "corpus_sha256": fastest["same_cases_sha256"],
            "cases": int(fastest["cases"]),
            "historical_fastest_profile": fastest["profile"],
            "historical_fastest_mean_cycles": float(fastest["mean_cycles"]),
            "historical_fastest_p95_cycles": int(fastest["p95_cycles"]),
            "historical_fastest_max_cycles": int(fastest["max_cycles"]),
            "cross_profile_same_input": True,
            "cross_selective_same_input": False,
        }
    return result


def report(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    if root != ROOT.resolve():
        raise ParityTriageError("Must inspect exactly the installed source root")
    stock = math_builder.operation_index()
    linkable = selective_linker.MODULES
    if len(stock) != 56 or set(stock) != set(linkable):
        raise ParityTriageError("Unexpected 56-operation public ABI/source graph")
    history = records(root / "benchmarks" / "BEST_PROFILE_RESULTS.csv")
    old = {}
    for row in history:
        api = row["routine"]
        if api in old or row["profile"] not in PROFILES:
            raise ParityTriageError("Duplicated API or unknown historical profile: " + api)
        if row["source_sha256"] != source_hash(root, row["source_path"]):
            raise ParityTriageError("Historical published source hash drift: " + api)
        if float(row["mean_cycles"]) <= 0:
            raise ParityTriageError("Invalid historical cycle data: " + api)
        old[api] = row
    missing = set(stock) - set(old)
    if missing:
        raise ParityTriageError("Missing historical benchmark APIs: " +
                                ", ".join(sorted(missing)))
    unsigned = common_unsigned(root)
    if len(unsigned) != 11 or not set(unsigned) <= set(stock):
        raise ParityTriageError("Historical matched-input unsigned corpus count drift")
    output = {}
    exact_source_matches = 0
    for api in sorted(stock):
        baseline = old[api]
        candidates = linkable[api]
        linked = []
        exact = []
        for variant_name, candidate in sorted(candidates.items()):
            relative = candidate["source"]
            checksum = source_hash(root, relative)
            matching = checksum == baseline["source_sha256"]
            if matching:
                exact.append(variant_name)
            linked.append({
                "variant": variant_name,
                "source": relative,
                "source_sha256": checksum,
                "matches_best_historical_source_bytes": matching,
                "source_qualified_for_stock_c64": True,
                "main_code_table_bytes": sum(n for _, n in candidate["segments"]),
                "private_zp_bytes": candidate["zp"],
                "call_scratch_bytes": candidate["scratch"],
                "shared_producer": candidate.get("share_producer"),
            })
        if exact:
            exact_source_matches += 1
        output[api] = {
            "historical_published_leader": {
                "profile": baseline["profile"],
                "mean_cycles": float(baseline["mean_cycles"]),
                "max_cycles": int(baseline["max_cycles"]),
                "cycle_basis": baseline["cycle_basis"],
                "source": baseline["source_path"],
                "source_sha256": baseline["source_sha256"],
                "note": "Published historical record; not directly comparable to selective CPU timing",
            },
            "historical_five_profile_same_input": unsigned.get(api),
            "source_byte_identical_candidates": exact,
            "selective_candidates": linked,
            "required_next_proof": (
                "Run source-assembled historical donor and selected public ABI "
                "on the SAME operand corpus, at two relocations. Compare mean, "
                "p95, maximum and output/carry/input preservation. Then test "
                "worst-case mixed-operation frame separately."
            ),
            "performance_parity_certified": False,
        }
    extra = sorted(set(old) - set(stock))
    return {
        "schema": "operation-first-historical-parity-triage-v1",
        "status": "SOURCE_INVENTORY_ONLY_NOT_SPEED_PARITY",
        "public_operation_count": len(stock),
        "historical_benchmark_rows": len(old),
        "extra_historical_services_not_stock_ops": extra,
        "identical_case_across_five_historical_profiles": len(unsigned),
        "identical_case_across_historical_and_selective": 0,
        "byte_identical_best_historical_source_candidate_apis": exact_source_matches,
        "qualified_full_speed_parity_apis": 0,
        "operation_results": output,
        "disclaimer": (
            "Historical leader labels may derive from unlike corpora; even an "
            "exact source-file SHA does not prove equal ABI wrappers or hardware "
            "cycle costs. Stock REU performance includes hardware requirements."
        ),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, help="Write full reproducible JSON; default stdout")
    args = ap.parse_args(argv)
    try:
        result = report()
    except (ParityTriageError, KeyError, ValueError) as exc:
        ap.exit(2, "historical parity triage: " + str(exc) + "\n")
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
