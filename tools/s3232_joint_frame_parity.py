#!/usr/bin/env python3
"""Source-linked mixed signed SDIV32_32/SMOD32_32 math-only busiest-frame research.

Compare exact signed truncating full public Q32/R32/C calls from the same 150-call input schedule,
not independent DIV/MOD average cycles or resident register-only benchmarks.
The CPU model is not a physical PAL/VIC/SID/IRQ/REU frame-time oracle.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_s3232 as speed
from frame_cycle_budget import Call, score
from mini6502 import CPU

ROOT = Path(__file__).resolve().parents[1]
OPS = ("MATH_SDIV32_32", "MATH_SMOD32_32")
CHOICES = {
    "signed-portable-shared-zerozp": ("link:portable-zerozp", "link:portable-zerozp"),
    "signed-v2-hybrid-shared": ("link:v2-hybrid-signed", "link:v2-hybrid-signed"),
}
OPTIONS = {label: dict(zip(OPS, pair)) for label, pair in CHOICES.items()}
FRAMES, CALLS = 24, 150
BASIS = "two-operation signed trunc-q32-r32-c same-input source-linked synthetic frames"


def scenario():
    source = speed.corpus()
    calls = []
    for frame in range(FRAMES):
        volume = 24 if frame % 8 == 0 else 8 if frame % 4 == 0 else 3
        for ordinal in range(volume):
            api = OPS[(frame + ordinal) % len(OPS)]
            n, d = source[(frame * 37 + ordinal * 83) % len(source)]
            a, x, y = ((frame * 17 + ordinal * 29) & 255,
                        (frame * 31 + ordinal * 7) & 255,
                        (frame * 13 + ordinal * 23) & 255)
            carry = (frame + ordinal) & 1
            identity = hashlib.sha256(
                ("%s|%d|%d|N=%08x|D=%08x|A=%02x|X=%02x|Y=%02x|C=%d|decimal=0" %
                 (api, frame, ordinal, n, d, a, x, y, carry)
                 ).encode("ascii")).hexdigest()
            calls.append((frame, ordinal, api, n, d, a, x, y, carry, identity))
    if len(calls) != CALLS or len(set(row[-1] for row in calls)) != CALLS:
        raise AssertionError("Mixed signed 32/32 call scenario changed")
    if {row[2] for row in calls} != set(OPS):
        raise AssertionError("One public DIV/MOD operation was omitted")
    return tuple(calls)


def evaluate(label, code=0x8000, io=0xc000, zp=0x50):
    if label not in OPTIONS:
        raise ValueError("Unqualified linked signed DIV/MOD source pair")
    pins = OPTIONS[label]
    for api, variant in pins.items():
        if variant not in linker.MODULES[api]:
            raise AssertionError("Required source variant removed: " + api + ":" + variant)
    index = math_builder.operation_index()
    plan = math_builder.create_plan(
        index, list(OPS), objective="size", zp_budget=12, ram_budget=12000,
        pins={api[5:]: variant for api, variant in pins.items()})
    with tempfile.TemporaryDirectory(prefix="math_u3232_joint_") as temp:
        folder = Path(temp)
        manifest = linker.build(plan, folder, memory={
            "code_base": code, "math_io": io,
            "scratch_base": io + 0x40, "zp_base": zp,
        })
        selected = {x["api"]: x["variant"] for x in manifest["operations"]}
        if selected != pins or len(selected) != len(OPS):
            raise AssertionError("Public source pins were not linked exactly")
        binary = (folder / "math_selective.prg").read_bytes()
        if binary[:2] != code.to_bytes(2, "little"):
            raise AssertionError("Unexpected native PRG origin")
        size = len(binary) - 2
        if not size or code + size >= io or code + size >= 65536:
            raise AssertionError("Relocated source collides with math I/O")
        ram = bytearray(65536)
        ram[code:code + size] = binary[2:]
        cpu = CPU(ram)
        stack = cpu.sp
        entries = {x["api"]: int(x["entry"][1:], 16) for x in manifest["operations"]}
        observations = []
        for frame, ordinal, api, n, d, a, x, y, carry, ident in scenario():
            num = n.to_bytes(4, "little")
            den = d.to_bytes(4, "little")
            ram[io + 16:io + 20] = num
            ram[io + 20:io + 24] = den
            ram[io + 24:io + 28] = b"\x55" * 4
            ram[io + 28:io + 32] = b"\x66" * 4
            cpu.a, cpu.x, cpu.y, cpu.c, cpu.d = a, x, y, carry, 0
            cycles = cpu.call(entries[api], 150000)
            quotient = int.from_bytes(ram[io + 24:io + 28], "little")
            remainder = int.from_bytes(ram[io + 28:io + 32], "little")
            expected_q, expected_r, expected_carry = speed.reference(n, d)
            if (remainder != expected_r or
                api == "MATH_SDIV32_32" and quotient != expected_q or
                cpu.c != expected_carry or cpu.sp != stack or
                ram[io + 16:io + 20] != num or ram[io + 20:io + 24] != den):
                raise AssertionError(("Public Q/R/C/SP/inputs failed", label, api,
                                      hex(code), frame, ordinal, hex(n), hex(d),
                                      hex(quotient), hex(remainder), cpu.c))
            observations.append(Call(frame, ordinal, api, ident, cycles, selected[api]))
        metadata = {"measurement_basis": "cpu-model-public-entry-through-rts",
                    "placement": "$%04X/$%04X" % (code, io),
                    "variants": selected}
        measured = score(observations, metadata, frame_count=FRAMES)
        return {
            "calls": observations, "score": measured, "manifest": manifest,
            "linked_prg_sha256": hashlib.sha256(binary).hexdigest(),
            "source_sha256": {
                api: hashlib.sha256(
                    (ROOT / linker.MODULES[api][variant]["source"]).read_bytes()
                ).hexdigest()
                for api, variant in selected.items()
            },
        }


def compare(code, io, zp):
    results = {label: evaluate(label, code, io, zp) for label in OPTIONS}
    first = results[next(iter(OPTIONS))]["calls"]
    keys = tuple(item.key for item in first)
    if len(set(keys)) != CALLS:
        raise AssertionError("Duplicate signed Q/R public-call identities")
    digest = hashlib.sha256(
        json.dumps(keys, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    report = {
        "code": "$%04X" % code, "io": "$%04X" % io,
        "zp_base": "$%04X" % zp, "scratch_base": "$%04X" % (io + 0x40),
        "frames": FRAMES, "paired_calls": CALLS,
        "cpu_model_only": True, "native_pal_timing": False,
        "input_corpus_sha256": digest, "per_option": {},
    }
    for label, data in results.items():
        if tuple(item.key for item in data["calls"]) != keys:
            raise AssertionError("Candidate measurement used mismatched public-call corpus")
        manifest, measurements = data["manifest"], data["score"]
        resource = manifest["resource_use"]
        report["per_option"][label] = {
            "variant_map": OPTIONS[label],
            "source_sha256": data["source_sha256"],
            "linked_prg_sha256": data["linked_prg_sha256"],
            "linked_source_count": len(manifest["link_order"]),
            "main_ram_total_bytes": resource["main_ram_total_bytes"],
            "zero_page_bytes": resource["zero_page_bytes"],
            "peak_frame_math_cycles": measurements["peak_frame_math_cycles"],
            "p95_frame_math_cycles": measurements["p95_frame_math_cycles"],
            "total_math_cycles": measurements["total_math_cycles"],
            "per_operation": measurements["operations"],
        }
    return report


def complete_report():
    return {"basis": BASIS, "operations": list(OPS),
            "placements": [compare(0x8000, 0xc000, 0x50),
                           compare(0x7123, 0xc040, 0x70)]}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = json.dumps(complete_report(), sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
