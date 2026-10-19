#!/usr/bin/env python3
"""Three-operation source-linked frame comparison: UMUL32, SMUL32, ISQRT16.

The complete mixed public-call trace uses the same 150 operands and caller
states for all eight independently linked choices, at two relocations.
Only stock 6510 CPU-model arithmetic cycles are measured, never PAL/VIC/IRQ.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from math import isqrt
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_umul32 as u32
from frame_cycle_budget import Call, score
from mini6502 import CPU

ROOT = Path(__file__).resolve().parents[1]
OPS = ("MATH_UMUL32", "MATH_SMUL32", "MATH_ISQRT16")
MUL_PAIRS = {
    "compact-pair": ("link:compact-zerozp", "link:compact-zerozp"),
    "unified375": ("link:unified-375", "link:unified-375"),
    "fast31-independent": ("link:fast31-v2-public", "link:fast31-v2-signed"),
    "fast31-shared": ("link:fast31-shared-full64", "link:fast31-shared-full64"),
}
ROOT_VARIANTS = {"table": "link:square-table", "tableless": "link:radix4-zerozp"}
OPTIONS = {
    name + "+" + label: dict(zip(OPS, pair + (root,)))
    for name, pair in MUL_PAIRS.items()
    for label, root in ROOT_VARIANTS.items()
}
FRAMES = 24
CALLS = 150
MASK64 = (1 << 64) - 1


def scenario():
    corpus = u32.corpus()
    calls = []
    for frame in range(FRAMES):
        volume = 24 if frame % 8 == 0 else 8 if frame % 4 == 0 else 3
        for ordinal in range(volume):
            api = OPS[(frame + ordinal) % len(OPS)]
            x, y = corpus[(frame * 37 + ordinal * 83) % len(corpus)]
            n = (x ^ y) & 65535
            a, rx, ry = ((frame * 17 + ordinal * 29) & 255,
                          (frame * 31 + ordinal * 7) & 255,
                          (frame * 13 + ordinal * 23) & 255)
            carry = (frame + ordinal) & 1
            identity = hashlib.sha256(
                ("%s|%d|%d|X=%08x|Y=%08x|N=%04x|A=%02x|RX=%02x|RY=%02x|C=%d|D=0" %
                 (api, frame, ordinal, x, y, n, a, rx, ry, carry)
                ).encode("ascii")).hexdigest()
            calls.append((frame, ordinal, api, x, y, n, a, rx, ry, carry, identity))
    if len(calls) != CALLS or len({row[-1] for row in calls}) != CALLS:
        raise AssertionError("Deterministic mixed call corpus changed")
    return tuple(calls)


def evaluate(choice, code=0x8000, io=0xc000, zp=0x50):
    if choice not in OPTIONS:
        raise ValueError("Unknown qualified source combination")
    variants = OPTIONS[choice]
    if any(variant not in linker.MODULES[api] for api, variant in variants.items()):
        raise AssertionError("Missing independent linked source")
    plan = math_builder.create_plan(
        math_builder.operation_index(),
        ["UMUL32", "SMUL32", "ISQRT16"],
        objective="size", zp_budget=31, ram_budget=12000,
        pins={api[5:]: variant for api, variant in variants.items()})
    with tempfile.TemporaryDirectory(prefix="math_mixed3_") as temp:
        out = Path(temp)
        manifest = linker.build(plan, out, memory={
            "code_base": code, "math_io": io,
            "scratch_base": io + 0x40, "zp_base": zp})
        chosen = {item["api"]: item["variant"] for item in manifest["operations"]}
        if chosen != variants or len(chosen) != 3:
            raise AssertionError("The linker did not use exact source pins")
        resources = manifest["resource_use"]
        image = (out / "math_selective.prg").read_bytes()
        if image[:2] != code.to_bytes(2, "little"):
            raise AssertionError("Wrong executable origin")
        size = len(image) - 2
        if code + size >= io or code + size >= 65536:
            raise AssertionError("Code/table versus I/O collision")
        mem = bytearray(65536)
        mem[code:code + size] = image[2:]
        cpu = CPU(mem)
        entry = {item["api"]: int(item["entry"][1:], 16)
                 for item in manifest["operations"]}
        sp = cpu.sp
        observations = []
        for frame, ordinal, api, x, y, n, a, rx, ry, carry, identity in scenario():
            xb, yb, nb = (x.to_bytes(4, "little"), y.to_bytes(4, "little"),
                          n.to_bytes(2, "little"))
            mem[io:io + 4] = xb
            mem[io + 4:io + 8] = yb
            mem[io + 8:io + 16] = b"\xa5" * 8
            mem[io + 16:io + 18] = nb
            cpu.a, cpu.x, cpu.y, cpu.c, cpu.d = a, rx, ry, carry, 0
            cycles = cpu.call(entry[api], 125000)
            if api == "MATH_ISQRT16":
                correct = (int.from_bytes(mem[io + 8:io + 10], "little") == isqrt(n)
                           and bytes(mem[io + 16:io + 18]) == nb)
            else:
                sx = x - (1 << 32) if x & 0x80000000 else x
                sy = y - (1 << 32) if y & 0x80000000 else y
                expected = (x * y if api == "MATH_UMUL32"
                            else (sx * sy) & MASK64)
                correct = (int.from_bytes(mem[io + 8:io + 16], "little") == expected
                           and bytes(mem[io:io + 4]) == xb
                           and bytes(mem[io + 4:io + 8]) == yb)
            if not correct or cpu.c != 0 or cpu.sp != sp:
                raise AssertionError(("Public call failed", choice, api,
                                      hex(code), frame, ordinal, x, y, n))
            observations.append(Call(frame, ordinal, api, identity, cycles, chosen[api]))
        metadata = {"measurement_basis": "cpu-model-public-entry-through-rts",
                    "placement": "$%04X/$%04X" % (code, io), "variants": chosen}
        result = score(observations, metadata, frame_count=FRAMES)
        return {"calls": observations, "scored": result, "manifest": manifest,
                "source_sha256": {
                    api: hashlib.sha256(
                        (ROOT / linker.MODULES[api][variant]["source"]).read_bytes()
                    ).hexdigest() for api, variant in chosen.items()},
                "linked_prg_sha256": hashlib.sha256(image).hexdigest()}


def compare(code, io, zp):
    samples = {key: evaluate(key, code, io, zp) for key in OPTIONS}
    original = samples[next(iter(OPTIONS))]["calls"]
    keys = tuple(call.key for call in original)
    if len(set(keys)) != CALLS:
        raise AssertionError("Duplicate public-call identity")
    fingerprint = hashlib.sha256(
        json.dumps(keys, separators=(",", ":")).encode("utf-8")).hexdigest()
    report = {"code": "$%04X" % code, "io": "$%04X" % io,
              "paired_calls": CALLS, "frames": FRAMES,
              "cpu_model_only": True, "native_pal_timing": False,
              "input_corpus_sha256": fingerprint, "per_option": {}}
    for key, data in samples.items():
        if tuple(call.key for call in data["calls"]) != keys:
            raise AssertionError("Variants used different public input histories")
        resources = data["manifest"]["resource_use"]
        cycles = data["scored"]
        report["per_option"][key] = {
            "variant_map": OPTIONS[key],
            "source_sha256": data["source_sha256"],
            "linked_prg_sha256": data["linked_prg_sha256"],
            "linked_source_count": len(data["manifest"]["link_order"]),
            "main_ram_total_bytes": resources["main_ram_total_bytes"],
            "zero_page_bytes": resources["zero_page_bytes"],
            "peak_frame_math_cycles": cycles["peak_frame_math_cycles"],
            "p95_frame_math_cycles": cycles["p95_frame_math_cycles"],
            "total_math_cycles": cycles["total_math_cycles"],
            "per_operation": cycles["operations"],
        }
    return report


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    report = {"basis": "three-operation same-input linked source math-only frames",
              "operations": list(OPS),
              "placements": [compare(0x8000, 0xc000, 0x50),
                             compare(0x7123, 0xc040, 0x70)]}
    contents = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(contents, encoding="utf-8")
    else:
        print(contents, end="")


if __name__ == "__main__":
    main()
