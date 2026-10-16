#!/usr/bin/env python3
"""Issue144 D: public-entry SEEK16 V1/V5 normal-resident batch qualification.

Compare frozen shipped reference PRGs to *source-built*, current-branch
normal-resident candidates. Paired corpus and native VICE never overwrite
released reference images or claim native cycle accounting. All 248 bytes of
SEEK16 object state, public X/C/SP, and subsequent STEP modes are checked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from benchmark_seek_profiles import api, corpus, load
from mini6502 import CPU

PROFILES = ("v1_balanced", "v5_hybrid_lowzp")
SPEEDS = (0x0080, 0x0100, 0x0180, 0x0200, 0x0300, 0x0400,
          0x8080, 0x8100, 0x8180, 0x8200, 0x8300, 0x8400)
STATE = (0x1988, 0x1A80)
BATCH = (0x3599, 0x35C6)  # half-open; verified against reference zero island


def build(out: Path) -> dict[str, Path]:
    def run(*args: str) -> None:
        p = subprocess.run([sys.executable, *args], cwd=ROOT,
                           text=True, capture_output=True)
        if p.returncode:
            raise RuntimeError((args, p.returncode, p.stdout[-1800:], p.stderr[-2500:]))
    run("tools/assemble_sources.py", "--profile", "v1_balanced",
        "--config-kind", "reference", "--out", str(out))
    run("tools/build_hybrid.py", "--config-kind", "reference", "--out", str(out))
    result = {}
    for profile in PROFILES:
        folder = out / "reference" / profile
        manifest = json.loads((folder / "source_build_manifest.json").read_text())
        result[profile] = folder / manifest["output_prg"]
        assert result[profile].is_file(), result[profile]
    return result


def machine(path: Path, A: dict) -> CPU:
    b = path.read_bytes()
    origin = int.from_bytes(b[:2], "little")
    assert origin == 0x1000
    mem = bytearray(65536)
    mem[origin:origin + len(b) - 2] = b[2:]
    c = CPU(mem)
    c.d = 0
    c.call(A["MATH_INIT"], 2_000_000)
    return c


def feed(cpu: CPU, A: dict, move: tuple, speed: int, slot: int) -> None:
    x0, y0, x1, y1 = move
    mem = cpu.mem
    mem[A["MATH_SEEK16_POS_XL"] + slot] = x0 & 255
    mem[A["MATH_SEEK16_POS_XH"] + slot] = x0 >> 8
    mem[A["MATH_SEEK16_POS_Y"] + slot] = y0
    mem[A["MATH_X"]] = x1 & 255
    mem[A["MATH_X"] + 1] = x1 >> 8
    mem[A["MATH_Y"]] = y1
    mem[A["MATH_N"]] = speed & 255
    mem[A["MATH_N"] + 1] = speed >> 8
    cpu.x = slot


def equal(cpu_a: CPU, cpu_b: CPU, label: str) -> None:
    assert cpu_a.mem[STATE[0]:STATE[1]] == cpu_b.mem[STATE[0]:STATE[1]], label + ": state"
    assert cpu_a.c == cpu_b.c, label + ": carry"
    assert cpu_a.x == cpu_b.x, label + ": X"
    assert cpu_a.sp == cpu_b.sp, label + ": SP"


def profile_check(profile: str, candidate_prg: Path, moves: int) -> dict:
    orig, A = load(profile)
    candidate = machine(candidate_prg, A)
    raw_old = next((ROOT / profile / "resident").glob("math_*_game_math.prg")).read_bytes()
    raw_new = candidate_prg.read_bytes()
    assert not any(raw_old[2 + a - 0x1000] for a in range(*BATCH)), "reference gap occupied"
    assert any(raw_new[2 + a - 0x1000] for a in range(*BATCH)), "batch helper missing"
    assert raw_old[:2] == raw_new[:2] == bytes((0, 16))
    gains = {}
    calls = 0
    followups = 0
    for i, move in enumerate(corpus(320)[:moves]):
        for si, speed in enumerate(SPEEDS):
            for step_mode in ("STEP", "STEP_INT", "STEP1"):
                if step_mode == "STEP_INT" and (speed & 0x8000 or speed & 255):
                    continue
                if step_mode == "STEP1" and speed != 0x0100:
                    continue
                slot = (i * 3 + si) & 7
                for c in (orig, candidate):
                    feed(c, A, move, speed, slot)
                before = orig.call(A["MATH_SEEK16_INIT"], 500_000)
                after = candidate.call(A["MATH_SEEK16_INIT"], 500_000)
                label = f"{profile}/{i}/{speed:04X}/{step_mode}"
                equal(orig, candidate, label + "/INIT")
                gains.setdefault(f"{speed:04X}:{step_mode}", []).append(before - after)
                calls += 1
                for j in range(24):
                    orig.x = candidate.x = slot
                    orig.call(A["MATH_SEEK16_" + step_mode], 500_000)
                    candidate.call(A["MATH_SEEK16_" + step_mode], 500_000)
                    equal(orig, candidate, label + f"/STEP/{j}")
                    followups += 1
    values = [x for row in gains.values() for x in row]
    def stats(x):
        s = sorted(x)
        return dict(n=len(x), mean=round(statistics.fmean(x), 6),
                    median=statistics.median(x), p95=s[int(0.95 * (len(s) - 1))],
                    worst=min(x), best=max(x), slower=sum(v < 0 for v in x))
    result = dict(profile=profile, status="PASS_PAIRED_PUBLIC_MODEL",
                  candidate_sha256=hashlib.sha256(raw_new).hexdigest(),
                  old_sha256=hashlib.sha256(raw_old).hexdigest(),
                  init_calls=calls, followup_calls=followups,
                  saved_cycles=stats(values),
                  speed_classes={k: stats(v) for k, v in gains.items()})
    assert result["saved_cycles"]["worst"] >= -4, result
    assert max(values) >= 24, "no material high-integer-speed benefit"
    print(profile, "paired INIT", calls, "STEP", followups,
          "mean saved", result["saved_cycles"]["mean"],
          "min", min(values), "max", max(values), flush=True)
    return result


def native(profiles: dict, vice: str) -> dict:
    import native_issue39_seek_all_modes as n
    import hashlib
    old_reader = n.resident
    result = {}
    try:
        with tempfile.TemporaryDirectory(prefix="seek_v15_native_") as td:
            for idx, profile in enumerate(PROFILES):
                old_path = next((ROOT / profile / "resident").glob("math_*_game_math.prg"))
                old = old_path.read_bytes()
                new = profiles[profile].read_bytes()
                n.resident = lambda p, data=old: data
                a, _, _ = n.native(profile, 27340 + 2 * idx, Path(td), vice)
                n.verify(profile, a)
                n.resident = lambda p, data=new: data
                b, _, _ = n.native(profile, 27341 + 2 * idx, Path(td), vice)
                n.verify(profile, b)
                assert a == b, profile + ": real VICE output or state differs"
                result[profile] = dict(status="PASS_NATIVE_X64SC_ALL_SEEK_MODES",
                                       output_sha256=hashlib.sha256(a).hexdigest())
    finally:
        n.resident = old_reader
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--moves", type=int, default=48)
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    assert 8 <= args.moves <= 408
    with tempfile.TemporaryDirectory(prefix="seek_v15_models_") as td:
        built = build(Path(td))
        results = {p: profile_check(p, built[p], args.moves) for p in PROFILES}
        out = {"status": "PASS_MODEL_AND_NATIVE" if args.native else "PASS_MODEL_ONLY",
               "source_built_not_reference_release": True, "profiles": results}
        if args.native:
            vice = os.getenv("VICE_WRAPPER")
            if not vice:
                raise RuntimeError("--native requires VICE_WRAPPER")
            out["native"] = native(built, vice)
        if args.write:
            path = ROOT / "validation/review/ISSUE144_SEEK16_V15_NORMAL_BATCH_2026-10-16.json"
            path.write_text(json.dumps(out, indent=2) + "\n")
        print("ISSUE144 V1/V5 NORMAL RESIDENT SEEK16 QUALIFICATION", out["status"], flush=True)


if __name__ == "__main__":
    main()
