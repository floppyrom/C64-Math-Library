#!/usr/bin/env python3
"""General multi-operation offline frame frontier for source-qualified plans.

Consumes *measured, fully linked* candidate plans, not isolated operation means.
Resource and frame envelopes are conservative across all included placements.
Fails closed on incomplete/mismatched operation, input and source evidence.
CPU-model arithmetic cycles do NOT prove PAL/VIC/IRQ/SID/REU feasibility.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from mul32_frame_frontier import EvidenceError, FIELDS, frontier, select


def checked_sha(value, label):
    if (not isinstance(value, str) or len(value) != 64 or
            any(c not in "0123456789abcdef" for c in value)):
        raise EvidenceError(label + ": invalid SHA256")
    return value


def integer(value, name, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise EvidenceError(name + ": invalid nonnegative integer")
    return value


def summarize(report):
    if not isinstance(report, dict):
        raise EvidenceError("Expected measured JSON object")
    operations = report.get("operations")
    if (not isinstance(operations, list) or len(operations) < 2 or
            len(set(operations)) != len(operations) or
            any(not isinstance(op, str) or not op.startswith("MATH_") for op in operations)):
        raise EvidenceError("Require explicit distinct public MATH operation list")
    operations_set = set(operations)
    placements = report.get("placements")
    if not isinstance(placements, list) or len(placements) < 2:
        raise EvidenceError("At least two source-linked placements are required")
    sites, candidates = set(), None
    inputs = None
    call_count = None
    observed = {}
    for placement in placements:
        if (not isinstance(placement, dict) or
                placement.get("cpu_model_only") is not True or
                placement.get("native_pal_timing") is not False):
            raise EvidenceError("Unsupported or unqualified timing basis")
        site = (placement.get("code"), placement.get("io"))
        if (site in sites or any(not isinstance(v, str) or not v.startswith("$")
                               for v in site)):
            raise EvidenceError("Bad/duplicate physical origin")
        sites.add(site)
        identity = checked_sha(placement.get("input_corpus_sha256"), "call corpus")
        if inputs is not None and inputs != identity:
            raise EvidenceError("Different input histories across relocations")
        inputs = identity
        count = (integer(placement.get("paired_calls"), "calls", True),
                 integer(placement.get("frames"), "frames", True))
        if call_count is not None and count != call_count:
            raise EvidenceError("Inconsistent public-call and frame counts")
        call_count = count
        choices = placement.get("per_option")
        if (not isinstance(choices, dict) or not choices or
                candidates is not None and candidates != set(choices)):
            raise EvidenceError("Candidate plans differ across placements")
        candidates = set(choices)
        for name, item in choices.items():
            if not isinstance(name, str) or not name or not isinstance(item, dict):
                raise EvidenceError("Invalid linked source plan")
            variants, sources = item.get("variant_map"), item.get("source_sha256")
            if (not isinstance(variants, dict) or set(variants) != operations_set or
                    any(not isinstance(v, str) or not v for v in variants.values()) or
                    not isinstance(sources, dict) or set(sources) != operations_set):
                raise EvidenceError("Missing public API / source variant coverage")
            for op in operations:
                checked_sha(sources[op], name + "." + op)
            checked_sha(item.get("linked_prg_sha256"), name + ".prg")
            links = integer(item.get("linked_source_count"), "physical sources", True)
            if links > len(operations):
                raise EvidenceError("Unqualified producer count")
            vals = {key: integer(item.get(key), name + "." + key) for key in FIELDS}
            if (vals["main_ram_total_bytes"] == 0 or
                    vals["peak_frame_math_cycles"] == 0 or
                    vals["p95_frame_math_cycles"] > vals["peak_frame_math_cycles"]):
                raise EvidenceError("Invalid RAM/peak/p95 math frame envelope")
            # Ensure this really contains calls to all selected operations.
            by_api = item.get("per_operation")
            if (not isinstance(by_api, list) or
                    {line.get("operation") for line in by_api if isinstance(line, dict)}
                    != operations_set or len(by_api) != len(operations) or
                    sum(integer(line.get("calls"), "operation calls", True)
                        for line in by_api) != count[0]):
                raise EvidenceError("Measured call coverage does not match public API list")
            record = observed.setdefault(name, {"identity": (variants, sources),
                                                "placements": []})
            if record["identity"] != (variants, sources):
                raise EvidenceError("Variant/source mismatch between relocations")
            record["placements"].append(vals)

    result = {}
    for name, evidence in sorted(observed.items()):
        rows = evidence["placements"]
        result[name] = {
            key: sum(p[key] for p in rows) if key == "total_math_cycles"
            else max(p[key] for p in rows)
            for key in FIELDS
        }
        result[name]["variant_map"], result[name]["source_sha256"] = evidence["identity"]
    return {
        "operations": operations, "per_option": result,
        "placements": len(placements), "paired_calls": call_count[0],
        "frames": call_count[1], "input_corpus_sha256": inputs,
        "cpu_model_only": True, "physical_pal_feasibility_claim": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in-report", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--ram-budget", type=int)
    parser.add_argument("--zp-budget", type=int)
    parser.add_argument("--max-peak-math-cycles", type=int)
    parser.add_argument("--objective", choices=("peak", "ram", "zp"), default="peak")
    a = parser.parse_args()
    if (a.ram_budget is None) != (a.zp_budget is None):
        parser.error("Provide both RAM and ZP budgets")
    if a.max_peak_math_cycles is not None and a.ram_budget is None:
        parser.error("Peak limit requires RAM and ZP budgets")
    try:
        summary = summarize(json.loads(a.in_report.read_text(encoding="utf-8")))
        result = {"summary": summary, "pareto_source_plans": frontier(summary)}
        if a.ram_budget is not None:
            result["selection"] = select(summary, a.ram_budget, a.zp_budget,
                                         a.max_peak_math_cycles, a.objective)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    document = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(document, encoding="utf-8")
    else:
        print(document, end="")


if __name__ == "__main__":
    main()
