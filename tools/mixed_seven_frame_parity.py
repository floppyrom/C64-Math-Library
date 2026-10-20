#!/usr/bin/env python3
"""Seven-operation linked C64 arithmetic project: synthetic busiest-frame evidence.

This benchmark evaluates whole linked images containing both full64 32x32
multipliers, ISQRT16, unsigned and signed 32/32 quotient/remainder APIs.
It tests complete public-call correctness, relocation, source integrity and
shared resource costs, NOT physical PAL/VIC/IRQ/SID/REU execution timing.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from math import isqrt
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_umul32 as multiplication
import selective_speed_u3232 as unsigned_division
import selective_speed_s3232 as signed_division
from frame_cycle_budget import Call, score
from mini6502 import CPU

ROOT = Path(__file__).resolve().parents[1]
OPS = (
    "MATH_UMUL32", "MATH_SMUL32", "MATH_ISQRT16",
    "MATH_UDIV32_32", "MATH_UMOD32_32", "MATH_SDIV32_32", "MATH_SMOD32_32",
)
FRAMES = 24
CALLS = 150
MASK64 = (1 << 64) - 1
BASIS = "seven-operation-source-linked-mul-sqrt-signed-unsigned-divmod-synthetic-frames"

COMPACT_MUL = ("link:compact-zerozp", "link:compact-zerozp")
FAST_MUL = ("link:fast31-shared-full64", "link:fast31-shared-full64")
COMPACT_DIV = ("link:shared-aligned-zerozp", "link:shared-aligned-zerozp",
               "link:portable-zerozp", "link:portable-zerozp")
FAST_DIV = ("link:v2-lowdivisor-hybrid", "link:v2-lowdivisor-hybrid",
            "link:v2-hybrid-signed", "link:v2-hybrid-signed")
CHOICES = {
    "compact-everywhere": COMPACT_MUL + ("link:radix4-zerozp",) + COMPACT_DIV,
    "fast-mul-compact-div": FAST_MUL + ("link:square-table",) + COMPACT_DIV,
    "compact-mul-fast-div": COMPACT_MUL + ("link:radix4-zerozp",) + FAST_DIV,
    "fast-everywhere": FAST_MUL + ("link:square-table",) + FAST_DIV,
}
OPTIONS = {name: dict(zip(OPS, variants)) for name, variants in CHOICES.items()}


def scenario():
    mul_inputs = multiplication.corpus()
    udiv_inputs = unsigned_division.corpus()
    sdiv_inputs = signed_division.corpus()
    calls = []
    for frame in range(FRAMES):
        count = 24 if frame % 8 == 0 else 8 if frame % 4 == 0 else 3
        for ordinal in range(count):
            api = OPS[(frame + ordinal) % len(OPS)]
            offset = (frame * 37 + ordinal * 83)
            if api in OPS[:3]:
                x, y = mul_inputs[offset % len(mul_inputs)]
                n = (x ^ y) & 0xffff
            elif api in OPS[3:5]:
                x, y = udiv_inputs[offset % len(udiv_inputs)]
                n = 0
            else:
                x, y = sdiv_inputs[offset % len(sdiv_inputs)]
                n = 0
            a = (frame * 17 + ordinal * 29) & 255
            rx = (frame * 31 + ordinal * 7) & 255
            ry = (frame * 13 + ordinal * 23) & 255
            carry = (frame + ordinal) & 1
            identity = hashlib.sha256(
                (f"{api}|{frame}|{ordinal}|X={x:08x}|Y={y:08x}|"
                 f"N={n:04x}|A={a:02x}|RX={rx:02x}|RY={ry:02x}|"
                 f"C={carry}|D=0").encode("ascii")
            ).hexdigest()
            calls.append((frame, ordinal, api, x, y, n, a, rx, ry, carry, identity))
    if len(calls) != CALLS or len({row[-1] for row in calls}) != CALLS:
        raise AssertionError("Seven-API synthetic call history changed")
    if {row[2] for row in calls} != set(OPS):
        raise AssertionError("Seven-API public operation omitted from workload")
    return tuple(calls)


def evaluate(name: str, code=0x8000, io=0xc000, zp=0x50, *, candidates=None):
    choices = OPTIONS if candidates is None else candidates
    if name not in choices:
        raise ValueError("Unqualified seven-operation candidate plan")
    pins = choices[name]
    for api, variant in pins.items():
        if variant not in linker.MODULES[api]:
            raise AssertionError("Linked public variant missing " + api + " " + variant)
    plan = math_builder.create_plan(
        math_builder.operation_index(), list(OPS), objective="size",
        zp_budget=64, ram_budget=16000,
        pins={api[5:]: variant for api, variant in pins.items()})
    with tempfile.TemporaryDirectory(prefix="math_seven_frame_") as tmp:
        folder = Path(tmp)
        manifest = linker.build(
            plan, folder,
            memory={"code_base": code, "math_io": io,
                    "scratch_base": io + 0x40, "zp_base": zp})
        real_pins = {op["api"]: op["variant"] for op in manifest["operations"]}
        if real_pins != pins:
            raise AssertionError("Source-linked candidate variant pins changed")
        image = (folder / "math_selective.prg").read_bytes()
        if image[:2] != code.to_bytes(2, "little"):
            raise AssertionError("Wrong relocated PRG origin")
        size = len(image) - 2
        if not size or code + size >= io or code + size > 65536:
            raise AssertionError("Seven-API code and tables collide with public math I/O")
        ram = bytearray(65536)
        ram[code:code + size] = image[2:]
        cpu = CPU(ram)
        entry = {op["api"]: int(op["entry"][1:], 16) for op in manifest["operations"]}
        sp = cpu.sp
        measurements = []
        for frame, ordinal, api, x, y, n, a, rx, ry, carry, key in scenario():
            cpu.a, cpu.x, cpu.y, cpu.c, cpu.d = a, rx, ry, carry, 0
            if api in OPS[:3]:
                xb, yb, nb = (x.to_bytes(4, "little"), y.to_bytes(4, "little"),
                              n.to_bytes(2, "little"))
                ram[io:io + 4] = xb
                ram[io + 4:io + 8] = yb
                ram[io + 8:io + 16] = b"\xa5" * 8
                ram[io + 16:io + 18] = nb
            else:
                xb, yb = x.to_bytes(4, "little"), y.to_bytes(4, "little")
                ram[io + 16:io + 20] = xb
                ram[io + 20:io + 24] = yb
                ram[io + 24:io + 28] = b"\x55" * 4
                ram[io + 28:io + 32] = b"\x66" * 4
            cycles = cpu.call(entry[api], 160000)
            if api == "MATH_ISQRT16":
                valid = (int.from_bytes(ram[io + 8:io + 10], "little") == isqrt(n)
                         and ram[io + 16:io + 18] == nb and cpu.c == 0)
            elif api in OPS[:2]:
                sx = x - (1 << 32) if x & 0x80000000 else x
                sy = y - (1 << 32) if y & 0x80000000 else y
                expected = (x * y if api == "MATH_UMUL32" else
                            (sx * sy) & MASK64)
                valid = (
                    int.from_bytes(ram[io + 8:io + 16], "little") == expected
                    and ram[io:io + 4] == xb and ram[io + 4:io + 8] == yb
                    and cpu.c == 0
                )
            else:
                if api in OPS[5:]:
                    q, remainder, c = signed_division.reference(x, y)
                else:
                    q, remainder, c = (x // y if y else 0,
                                       x % y if y else 0, int(y == 0))
                actual_q = int.from_bytes(ram[io + 24:io + 28], "little")
                actual_r = int.from_bytes(ram[io + 28:io + 32], "little")
                valid = (actual_r == remainder and cpu.c == c
                         and (api not in (OPS[3], OPS[5]) or actual_q == q)
                         and ram[io + 16:io + 20] == xb
                         and ram[io + 20:io + 24] == yb)
            if not valid or cpu.sp != sp:
                raise AssertionError(("Complete public arithmetic ABI mismatch",
                                      name, api, hex(code), frame, ordinal,
                                      hex(x), hex(y), hex(n)))
            measurements.append(Call(frame, ordinal, api, key, cycles, real_pins[api]))
        result = score(
            measurements,
            {"measurement_basis": "cpu-model-public-entry-through-rts",
             "placement": "$%04X/$%04X" % (code, io), "variants": real_pins},
            frame_count=FRAMES,
        )
        return {
            "calls": measurements, "score": result, "manifest": manifest,
            "linked_prg_sha256": hashlib.sha256(image).hexdigest(),
            "source_sha256": {
                api: hashlib.sha256(
                    (ROOT / linker.MODULES[api][variant]["source"]).read_bytes()
                ).hexdigest()
                for api, variant in real_pins.items()
            },
        }


def compare(code, io, zp, *, candidates=None):
    choices = OPTIONS if candidates is None else candidates
    variants = {label: evaluate(label, code, io, zp, candidates=choices)
                for label in choices}
    first = tuple(c.key for c in next(iter(variants.values()))["calls"])
    if len(first) != CALLS or len(set(first)) != CALLS:
        raise AssertionError("Invalid matched seven-operation public-call history")
    digest = hashlib.sha256(
        json.dumps(first, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    result = {
        "code": "$%04X" % code, "io": "$%04X" % io,
        "zp_base": "$%04X" % zp, "scratch_base": "$%04X" % (io + 0x40),
        "frames": FRAMES, "paired_calls": CALLS,
        "cpu_model_only": True, "native_pal_timing": False,
        "input_corpus_sha256": digest, "per_option": {},
    }
    for label, data in variants.items():
        if tuple(c.key for c in data["calls"]) != first:
            raise AssertionError("Candidate implementations used unequal public calls")
        use = data["manifest"]["resource_use"]
        scored = data["score"]
        result["per_option"][label] = {
            "variant_map": choices[label],
            "source_sha256": data["source_sha256"],
            "linked_prg_sha256": data["linked_prg_sha256"],
            "linked_source_count": len(data["manifest"]["link_order"]),
            "main_ram_total_bytes": use["main_ram_total_bytes"],
            "zero_page_bytes": use["zero_page_bytes"],
            "peak_frame_math_cycles": scored["peak_frame_math_cycles"],
            "p95_frame_math_cycles": scored["p95_frame_math_cycles"],
            "total_math_cycles": scored["total_math_cycles"],
            "per_operation": scored["operations"],
        }
    return result


def complete_report():
    return {"basis": BASIS, "operations": list(OPS),
            "placements": [compare(0x2000, 0xc000, 0x50),
                           compare(0x4123, 0xc040, 0x70)]}


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    output = json.dumps(complete_report(), sort_keys=True, indent=2) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
