#!/usr/bin/env python3
"""Issue144: source-built release candidates and paired ISQRT32 audit.

Never overwrites frozen PRGs, REUs or PERFORMANCE.md. Output must be external.
6510 CPU-model instruction cycles exclude physical REU/VIC/DMA bus timing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mini6502 import CPU
from assemble_sources import build as build_source
from build_hybrid import build as build_hybrid
from validate_source_build import validate as validate_source

PROFILES = ("v1_balanced", "v2_pareto_fast", "v3_reu_512k",
            "v4_reu_16m", "v5_hybrid_lowzp")
REUS = {
    "v3_reu_512k": ROOT / "v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
    "v4_reu_16m": ROOT / "v4_reu_16m/reu/c64_math_v4_16m_game_math.reu",
}
FROZEN = {p: ROOT / p / "resident" / ("math_" + p + "_game_math.prg")
          for p in PROFILES}
EDGES = (0, 1, 2, 3, 4, 7, 15, 16, 17, 63, 64, 255, 256, 257,
         65535, 65536, 65537, 0x7fffffff, 0x80000000, 0xffffffff)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def frozen_seals():
    expected = dict((name, sha) for sha, name in (
        line.split("  ", 1) for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines()
        if "  " in line))
    paths = list(FROZEN.values()) + list(REUS.values())
    got = {}
    for path in paths:
        name = str(path.relative_to(ROOT))
        value = digest(path)
        assert expected.get(name) == value, ("historical seal changed", name)
        got[name] = value
    return got


def radicands():
    rng = random.Random(0x14432026)
    values = list(EDGES)
    for x in (0, 1, 2, 3, 15, 16, 31, 255, 256, 257, 511,
              1023, 4095, 16383, 32767, 65535):
        for n in (x*x-1, x*x, x*x+1):
            if 0 <= n <= 0xffffffff:
                values.append(n)
    values.extend(rng.getrandbits(32) for _ in range(384))
    return list(dict.fromkeys(values))


def machine(prg, reu):
    data = Path(prg).read_bytes()
    load = int.from_bytes(data[:2], "little")
    assert 0x1000 <= load and load+len(data)-2 <= 0x10000
    mem = bytearray(65536)
    mem[load:load+len(data)-2] = data[2:]
    c = CPU(mem, reu=bytearray(reu.read_bytes()) if reu else None)
    c.d = 0
    c.call(0x3280, 2_000_000)
    return c


def sample(cpu, n):
    for i in range(4):
        cpu.mem[0xc010+i] = (n >> (8*i)) & 255
    original = bytes(cpu.mem[0xc010:0xc014])
    cycles = cpu.call(0x5e30, 2_000_000)
    result = cpu.mem[0xc008] | cpu.mem[0xc009] << 8
    assert result == math.isqrt(n), (hex(n), result)
    assert cpu.c == 0 and bytes(cpu.mem[0xc010:0xc014]) == original
    return cycles


def p95(a):
    s = sorted(a)
    return s[int((len(s)-1)*.95)]


def paired_root(profile, candidate, candidate_reu, inputs):
    old = machine(FROZEN[profile], REUS.get(profile))
    new = machine(candidate, candidate_reu)
    a, b = [], []
    for n in inputs:
        a.append(sample(old, n))
        b.append(sample(new, n))
    saved = [x-y for x, y in zip(a, b)]
    return {"samples": len(inputs),
            "frozen_mean_cycles": statistics.fmean(a),
            "candidate_mean_cycles": statistics.fmean(b),
            "frozen_p95_cycles": p95(a), "candidate_p95_cycles": p95(b),
            "mean_saved_cycles": statistics.fmean(saved),
            "median_saved_cycles": statistics.median(saved),
            "minimum_saved_cycles": min(saved),
            "maximum_saved_cycles": max(saved),
            "slower_calls": sum(x < 0 for x in saved)}


def create(layout, out, benchmark):
    assert layout in ("reference", "alternate")
    out = out.resolve()
    assert not out.is_relative_to(ROOT), "Staging must stay outside checkout"
    out.mkdir(parents=True, exist_ok=True)
    sealed = frozen_seals()
    stage = out / "profiles"
    inputs = radicands()
    inputs_sha = hashlib.sha256(
        b"".join(n.to_bytes(4, "little") for n in inputs)).hexdigest()
    result = []
    for p in PROFILES:
        config = ROOT / "relocatable_source" / p / ("math_config_" + layout + ".inc")
        dest = stage / p
        manifest = (build_hybrid(config, dest) if p == "v5_hybrid_lowzp"
                    else build_source(p, config, dest))
        prg = dest / manifest["output_prg"]
        assert prg.exists() and digest(prg) == manifest["output_sha256"]
        reu = (dest / manifest["reu_image"]["file"]
               if manifest.get("reu_image") else None)
        if reu:
            assert reu.exists() and digest(reu) == manifest["reu_image"]["sha256"]
        api = validate_source(p, stage)
        assert api["status"] == "PASS" and api["public_entries_executed"] == 56, api
        row = {"profile": p, "config": layout,
               "candidate_prg": str(prg.relative_to(out)),
               "candidate_prg_sha256": digest(prg),
               "candidate_reu": str(reu.relative_to(out)) if reu else None,
               "candidate_reu_sha256": digest(reu) if reu else None,
               "source_manifest_sha256": digest(dest / "source_build_manifest.json"),
               "public_abi_entries_executed": api["public_entries_executed"],
               "public_model_calls": api["machine_calls"],
               "frozen_reference_sha256": sealed[str(FROZEN[p].relative_to(ROOT))]}
        if benchmark and layout == "reference":
            row["isqrt32_same_input"] = paired_root(p, prg, reu, inputs)
        result.append(row)
        print(p, layout, "PASS", api["machine_calls"], "public calls", flush=True)
    assert frozen_seals() == sealed, "Historical PRGs/REUs changed"
    report = {
        "status": "PASS_SOURCE_BUILT_CANDIDATE_NOT_SHIPPED",
        "source_commit": os.environ.get("GITHUB_SHA", "local"),
        "map": layout, "profiles": result,
        "same_input_isqrt_corpus_sha256": inputs_sha,
        "same_input_isqrt_samples_per_profile": len(inputs) if benchmark and layout == "reference" else 0,
        "isqrt_cycles_basis": "6502 instruction cycles, public call through RTS",
        "physical_vic_reu_dma_time_measured": False,
        "irq_nmi_reentrancy_certified": False,
        "historical_binaries_unchanged": True,
        "performance_md_unchanged": True,
        "frozen_sha256": sealed,
        "release_state": "source-built candidate, not a shipped binary release"
    }
    (out / "ISSUE144_RELEASE_CANDIDATE.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "map": layout,
                      "profiles": len(result),
                      "report": str(out / "ISSUE144_RELEASE_CANDIDATE.json")}, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--layout", required=True, choices=("reference", "alternate"))
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--skip-benchmark", action="store_true")
    a = p.parse_args()
    create(a.layout, a.out, not a.skip_benchmark)


if __name__ == "__main__":
    main()
