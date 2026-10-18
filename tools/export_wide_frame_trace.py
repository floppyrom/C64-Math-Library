#!/usr/bin/env python3
"""Measure a synthetic mixed signed-wide workload with source-linked Mini6502."""
import argparse
import csv
import hashlib
import json
import random
import tempfile
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker
from frame_cycle_budget import COLUMNS, load_trace, score

OPS = ("SMUL32", "SMUL32_SHR16", "SDIV32_16", "SMOD32_16", "SDIV32_32", "SMOD32_32")


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def operands(rng, frame, ordinal, bits):
    k = (31 * frame + ordinal) % 12
    numerators = (0, 1, 2, 3, 0x7fffffff, 0x80000000, 0x80000001, 0xffffffff)
    denominators = ((0, 1, 2, 3, 0x7fff, 0x8000, 0xffff) if bits == 16
                    else (0, 1, 2, 3, 0x7fffffff, 0x80000000, 0xffffffff))
    return ((numerators[k] if k < 8 else rng.getrandbits(32)),
            (denominators[k] if k < 7 else rng.getrandbits(bits)))


def divmod_reference(n, d, bits):
    n, d = signed(n, 32), signed(d, bits)
    if d == 0:
        return 0, 0, 1
    q = abs(n) // abs(d)
    q = -q if (n < 0) != (d < 0) else q
    return q & 0xffffffff, (n - q * d) & ((1 << bits) - 1), 0


def export(out, frames=40, code=0x8000, io=0xc000):
    if not 1 <= frames <= 2000:
        raise ValueError("frames must be in 1..2000")
    rng = random.Random(0xC643232)
    plan = math_builder.create_plan(math_builder.operation_index(), list(OPS),
                                    objective="size", zp_budget=0, ram_budget=8192)
    with tempfile.TemporaryDirectory() as temp:
        manifest = selective_linker.build(plan, Path(temp), memory={
            "code_base": code, "math_io": io, "scratch_base": io + 0x40})
        prg = (Path(temp) / "math_selective.prg").read_bytes()
        if int.from_bytes(prg[:2], "little") != code:
            raise ValueError("Bad assembled load address")
        mem = bytearray(65536)
        mem[code:code + len(prg) - 2] = prg[2:]
        image_before = bytes(mem[code:code + len(prg) - 2])
        cpu = CPU(mem)
        sp = cpu.sp
        entries = {e["api"]: int(e["entry"][1:], 16) for e in manifest["operations"]}
        variants = {e["api"]: e["variant"] for e in manifest["operations"]}
        if set(entries) != {"MATH_" + op for op in OPS}:
            raise ValueError("Incomplete operation link")
        observations = []
        for frame in range(frames):
            volume = 24 if frame % 8 == 0 else 8 if frame % 4 == 0 else 3
            for ordinal in range(volume):
                operation = "MATH_" + OPS[(3 * frame + 5 * ordinal) % len(OPS)]
                carry_in = (frame + ordinal) & 1
                if "MUL" in operation:
                    x, y = operands(rng, frame, ordinal, 32)
                    mem[io:io + 4] = x.to_bytes(4, "little")
                    mem[io + 4:io + 8] = y.to_bytes(4, "little")
                    mem[io + 8:io + 16] = bytes([0xA5] * 8)
                else:
                    bits = 16 if operation.endswith("32_16") else 32
                    x, y = operands(rng, frame, ordinal, bits)
                    mem[io + 16:io + 20] = x.to_bytes(4, "little")
                    mem[io + 20:io + 24] = y.to_bytes(4, "little")
                    mem[io + 24:io + 32] = bytes([0xA5] * 8)
                cpu.d, cpu.c = 0, carry_in
                cycles = cpu.call(entries[operation], 150000)
                if "MUL" in operation:
                    result_width = 6 if "SHR16" in operation else 8
                    actual = int.from_bytes(mem[io + 8:io + 8 + result_width], "little")
                    p = (signed(x, 32) * signed(y, 32)) & ((1 << 64) - 1)
                    expected = p >> 16 if result_width == 6 else p
                    if actual != expected or cpu.c:
                        raise ValueError("Incorrect multiply result: " + operation)
                else:
                    q = int.from_bytes(mem[io + 24:io + 28], "little")
                    r = int.from_bytes(mem[io + 28:io + 28 + bits // 8], "little")
                    if (q, r, cpu.c) != divmod_reference(x, y, bits):
                        raise ValueError("Incorrect divide/mod result: " + operation)
                if cpu.sp != sp:
                    raise ValueError("Stack not preserved: " + operation)
                identity = hashlib.sha256(
                    f"{operation}|{x:08x}|{y:08x}|C={carry_in}|D=0".encode()).hexdigest()
                observations.append({"frame": frame, "call": ordinal,
                                     "operation": operation, "input_id": identity,
                                     "cycles": cycles, "variant": variants[operation],
                                     "measurement_basis": "cpu-model-public-entry-through-rts",
                                     "placement": "$%04X/$%04X" % (code, io)})
        if bytes(mem[code:code + len(prg) - 2]) != image_before:
            raise ValueError("Public source unexpectedly self-modified")
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(observations)
        out.with_suffix(".manifest.json").write_text(
            json.dumps({"synthetic_not_real_game": True, "seed": "0xC643232",
                        "manifest": manifest,
                        "trace_sha256": hashlib.sha256(out.read_bytes()).hexdigest()},
                       indent=2) + "\n", encoding="utf-8")
    calls, meta = load_trace(out)
    scored = score(calls, meta, frame_count=frames)
    return {key: scored[key] for key in ("calls", "peak_frame",
                                       "peak_frame_math_cycles", "p95_frame_math_cycles",
                                       "peak_hotspots")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--frames", type=int, default=40)
    parser.add_argument("--code-base", type=lambda x: int(x, 0), default=0x8000)
    parser.add_argument("--io-base", type=lambda x: int(x, 0), default=0xc000)
    args = parser.parse_args()
    print(json.dumps(export(args.out, args.frames, args.code_base, args.io_base), indent=2))
