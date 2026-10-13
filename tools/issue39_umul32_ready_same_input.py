#!/usr/bin/env python3
"""Issue #39: same-input UMUL32 versus UMUL32_READY public-entry audit.

Published legacy means used different 2,409- and 1,024-pair corpora.
This audits both APIs on the *same* 2,409 operand pairs. READY remains a
distinct state/usage contract, even when public results and cycles match.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from benchmark_multiply_refresh import CORPORA, PROFILES, load, rd, wr

EXPECTED = {
    "v1_balanced": 22,
    "v2_pareto_fast": 0,
    "v3_reu_512k": 0,
    "v4_reu_16m": 0,
    "v5_hybrid_lowzp": 22,
}


def paired_profile(profile, pairs, check_shape):
    cpu, api = load(profile)
    hist = {}
    sums = [0, 0]
    for i, (x, y) in enumerate(pairs):
        values = []
        cycles = []
        for which, name in enumerate(("MATH_UMUL32", "MATH_UMUL32_READY")):
            wr(cpu.mem, 0xC000, x, 4)
            wr(cpu.mem, 0xC004, y, 4)
            input_before = bytes(cpu.mem[0xC000:0xC008])
            cyc = cpu.call(api[name], 2_000_000)
            got = rd(cpu.mem, 0xC008, 8)
            if (got != x * y or cpu.c != 0 or
                    bytes(cpu.mem[0xC000:0xC008]) != input_before):
                raise AssertionError(
                    f"{profile} {name} index={i} x={x:08x} y={y:08x} "
                    f"got={got:016x} expected={x*y:016x} carry={cpu.c}")
            values.append(got)
            cycles.append(cyc)
            sums[which] += cyc
        if values[0] != values[1]:
            raise AssertionError(f"{profile}: output discrepancy at {i}")
        saving = cycles[0] - cycles[1]
        hist[str(saving)] = hist.get(str(saving), 0) + 1
    if check_shape and hist != {str(EXPECTED[profile]): len(pairs)}:
        raise AssertionError(f"{profile}: unexpected paired cycle histogram {hist}")
    n = len(pairs)
    return {
        "profile": profile, "paired_cases": n,
        "ordinary_mean_cycles": sums[0] / n,
        "ready_mean_cycles": sums[1] / n,
        "mean_ready_saving_cycles": (sums[0] - sums[1]) / n,
        "paired_saving_histogram": hist,
        "product_carry_and_input_preservation": "PASS",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", choices=PROFILES, action="append")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--output", type=Path)
    p.add_argument("--no-assert-shape", action="store_true")
    args = p.parse_args()
    pairs = CORPORA[32][:args.limit] if args.limit else CORPORA[32]
    if not pairs:
        p.error("empty corpus")
    data = b"".join(
        x.to_bytes(4, "little") + y.to_bytes(4, "little") for x, y in pairs)
    profiles = args.profile or PROFILES
    rows = []
    for profile in profiles:
        row = paired_profile(profile, pairs, not args.no_assert_shape)
        print(profile, "PASS", len(pairs), row["paired_saving_histogram"], flush=True)
        rows.append(row)
    result = {
        "status": "PASS",
        "scope": "CPU-model public-entry including RTS, excluding caller JSR / stores",
        "legacy_warning": "UMUL32 and READY published averages used different corpora; do not directly compare those published means",
        "corpus": "benchmark_multiply_refresh.CORPORA[32]",
        "corpus_sha256_le32x2": hashlib.sha256(data).hexdigest(),
        "input_pairs": len(pairs), "full_corpus": len(pairs) == len(CORPORA[32]),
        "profiles": rows,
        "ready_contract": "Distinct READY state prerequisites; equality of mathematical outputs is not interchangeability proof",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("ISSUE39 UMUL32/READY SAME-INPUT PASS", len(rows), "profiles")


if __name__ == "__main__":
    main()
