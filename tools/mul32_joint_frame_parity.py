#!/usr/bin/env python3
"""Same-input mixed UMUL32+SMUL32 24-frame code-sharing Pareto measurement.

Compare two compact sources, unified375, two independent FAST31 images and
one shared FAST31 source. Includes full signed/unsigned 64-bit public results,
whole-image RAM/ZP and busiest-frame CPU-model cycles, not PAL/VIC hardware.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_umul32 as u32
from frame_cycle_budget import Call, score
from mini6502 import CPU

ROOT = Path(__file__).resolve().parents[1]
OPS = ("MATH_UMUL32", "MATH_SMUL32")
FRAMES = 24
CALLS = 150
OPTIONS = {
    "compact-pair": ("link:compact-zerozp", "link:compact-zerozp"),
    "unified375": ("link:unified-375", "link:unified-375"),
    "fast31-independent": ("link:fast31-v2-public", "link:fast31-v2-signed"),
    "fast31-shared": ("link:fast31-shared-full64", "link:fast31-shared-full64"),
}
MASK64 = (1 << 64) - 1


def scenario():
    corpus = u32.corpus()
    rows = []
    for frame in range(FRAMES):
        volume = 24 if frame % 8 == 0 else 8 if frame % 4 == 0 else 3
        for ordinal in range(volume):
            operation = OPS[(frame + ordinal) % 2]
            x, y = corpus[(frame * 37 + ordinal * 83) % len(corpus)]
            ra = (frame * 17 + ordinal * 29) & 255
            rx = (frame * 31 + ordinal * 7) & 255
            ry = (frame * 13 + ordinal * 23) & 255
            carry = (frame + ordinal) & 1
            digest = hashlib.sha256(
                ("%s|%08x|%08x|A=%02x|X=%02x|Y=%02x|C=%d|D=0" %
                 (operation, x, y, ra, rx, ry, carry)).encode()).hexdigest()
            rows.append((frame, ordinal, operation, x, y,
                         ra, rx, ry, carry, digest))
    if len(rows) != CALLS:
        raise AssertionError("Mixed full64 frame corpus size changed")
    return tuple(rows)


def evaluate(choice, code=0x8000, io=0xc000, zp=0x50):
    if choice not in OPTIONS:
        raise ValueError("Unqualified signed/unsigned combined source plan")
    variants = OPTIONS[choice]
    for op, ident in zip(OPS, variants):
        if ident not in linker.MODULES[op]:
            raise AssertionError("Missing certified source variant: " + op)
    plan = math_builder.create_plan(
        math_builder.operation_index(), ["UMUL32", "SMUL32"],
        objective="size", zp_budget=31, ram_budget=6400,
        pins={op[5:]: ident for op, ident in zip(OPS, variants)})
    with tempfile.TemporaryDirectory(prefix="mul32_pair_frame_") as td:
        out = Path(td)
        manifest = linker.build(plan, out, memory={
            "code_base": code, "math_io": io,
            "scratch_base": io + 0x40, "zp_base": zp})
        if len(manifest["operations"]) != 2:
            raise AssertionError("Expected both 32x32 full64 public APIs")
        chosen = {v["api"]: v["variant"] for v in manifest["operations"]}
        if chosen != dict(zip(OPS, variants)):
            raise AssertionError("Multiplication public source pins drifted")
        want_links = 1 if choice in ("unified375", "fast31-shared") else 2
        if len(manifest["link_order"]) != want_links:
            raise AssertionError("Unexpected code/tables producer sharing")
        resources = manifest["resource_use"]
        expected_zp = 31 if choice.startswith("fast31") else 0
        if resources["zero_page_bytes"] != expected_zp:
            raise AssertionError("32x32 shared source ZP usage changed")
        binary = (out / "math_selective.prg").read_bytes()
        if binary[:2] != code.to_bytes(2, "little"):
            raise AssertionError("Linked multiplication PRG origin mismatch")
        size = len(binary) - 2
        if code + size >= io or code + size >= 0x10000:
            raise AssertionError("32x32 code/tables collide with public I/O")
        mem = bytearray(65536)
        mem[code:code+size] = binary[2:]
        before = bytes(mem[code:code+size])
        cpu = CPU(mem)
        sp = cpu.sp
        entries = {x["api"]: int(x["entry"][1:], 16)
                   for x in manifest["operations"]}
        observations = []
        for frame, ordinal, api, x, y, ra, rx, ry, carry, identity in scenario():
            xb, yb = x.to_bytes(4, "little"), y.to_bytes(4, "little")
            mem[io:io+4] = xb
            mem[io+4:io+8] = yb
            mem[io+8:io+16] = b"\xa5" * 8
            cpu.a, cpu.x, cpu.y = ra, rx, ry
            cpu.c, cpu.d = carry, 0
            ticks = cpu.call(entries[api], 125000)
            if api == "MATH_UMUL32":
                expected = x * y
            else:
                sx = x - (1 << 32) if x & 0x80000000 else x
                sy = y - (1 << 32) if y & 0x80000000 else y
                expected = (sx * sy) & MASK64
            actual = int.from_bytes(mem[io+8:io+16], "little")
            if (actual != expected or bytes(mem[io:io+4]) != xb
                or bytes(mem[io+4:io+8]) != yb or cpu.sp != sp or cpu.c != 0):
                raise AssertionError(("Mixed signed/unsigned public ABI drift",
                                      choice, api, frame, ordinal, x, y, actual, expected))
            observations.append(Call(frame, ordinal, api, identity, ticks, chosen[api]))
        if choice in ("compact-pair", "unified375") and bytes(mem[code:code+size]) != before:
            raise AssertionError("Compact multiply unexpectedly modified executable bytes")
        meta = {"measurement_basis": "cpu-model-public-entry-through-rts",
                "placement": "$%04X/$%04X" % (code, io), "variants": chosen}
        return {
            "variant_map": chosen,
            "source_sha256": {op: hashlib.sha256(
                (ROOT / linker.MODULES[op][chosen[op]]["source"]).read_bytes()
            ).hexdigest() for op in OPS},
            "linked_prg_sha256": hashlib.sha256(binary).hexdigest(),
            "linked_source_count": len(manifest["link_order"]),
            "resource_use": resources,
            "calls": observations,
            "scored": score(observations, meta, frame_count=FRAMES),
        }


def compare(code, io, zp=0x50):
    data = {choice: evaluate(choice, code, io, zp) for choice in OPTIONS}
    reference = data["compact-pair"]["calls"]
    keys = tuple(x.key for x in reference)
    if len(keys) != CALLS or len(set(keys)) != CALLS:
        raise AssertionError("Paired full64 call keys changed")
    baseline = data["compact-pair"]["scored"]
    result = {"code": "$%04X" % code, "io": "$%04X" % io,
              "paired_calls": CALLS, "frames": FRAMES, "cpu_model_only": True,
              "input_corpus_sha256": hashlib.sha256(
                  json.dumps(keys, separators=(",", ":")).encode("utf-8")).hexdigest(),
              "native_pal_timing": False, "per_option": {}}
    for choice, option in data.items():
        calls = option["calls"]
        if tuple(x.key for x in calls) != keys:
            raise AssertionError("Mixed full64 source input identities diverged")
        sc = option["scored"]
        diffs = [new.cycles - old.cycles for old, new in zip(reference, calls)]
        fdelta = [new - old for new, old in zip(
            sc["frame_math_cycles"], baseline["frame_math_cycles"])]
        res = option["resource_use"]
        result["per_option"][choice] = {
            "linked_source_count": option["linked_source_count"],
            "variant_map": option["variant_map"],
            "source_sha256": option["source_sha256"],
            "linked_prg_sha256": option["linked_prg_sha256"],
            "main_ram_total_bytes": res["main_ram_total_bytes"],
            "image_span_bytes": res["image_span_bytes"],
            "zero_page_bytes": res["zero_page_bytes"],
            "mean_call_cycles": sum(v.cycles for v in calls) / CALLS,
            "peak_frame_math_cycles": sc["peak_frame_math_cycles"],
            "p95_frame_math_cycles": sc["p95_frame_math_cycles"],
            "total_math_cycles": sc["total_math_cycles"],
            "regressed_calls_vs_compact": sum(d > 0 for d in diffs),
            "worst_call_regression_vs_compact": max((0, *diffs)),
            "regressed_frames_vs_compact": sum(d > 0 for d in fdelta),
            "worst_frame_regression_vs_compact": max((0, *fdelta)),
        }
    return result


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    result = {"basis": "same-input mixed signed unsigned full64 source-model frame",
              "placements": [compare(0x8000, 0xc000),
                             compare(0x7123, 0xc040, 0x70)]}
    text = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
