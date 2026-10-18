#!/usr/bin/env python3
"""Measure historical V1-V5 signed-wide public calls on one reproducible frame corpus.

CPU-model observations, NOT VICE wall-clock and NOT isolated historical means.
Resident profile images are executable donor evidence, not relocatable variants.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path

from export_wide_frame_trace import OPS, operands, signed
from frame_cycle_budget import COLUMNS, load_trace, score
from validate_signed_division import PROFILES, REU, ROOT, load_profile

WIDE_OPS = OPS + ("SDIV24", "SMOD24")
MEMORY_IO = 0xC000
SEED = 0xC643232


def operands24(rng, frame, ordinal):
    # Mirror the signed24 extension to export_wide_frame_trace.py.
    k = (31 * frame + ordinal) % 12
    numerators = (0, 1, 2, 3, 0x7fffff, 0x800000, 0x800001, 0xffffff)
    denominators = (0, 1, 2, 3, 0x7fffff, 0x800000, 0xffffff)
    return (numerators[k] if k < 8 else rng.getrandbits(24),
            denominators[k] if k < 7 else rng.getrandbits(24))


def reference_div(nraw, draw, bits):
    n = signed(nraw, 24 if bits == 24 else 32)
    d = signed(draw, bits)
    if not d:
        return 0, 0, 1
    q = abs(n) // abs(d)
    if (n < 0) != (d < 0):
        q = -q
    r = n - q * d
    return q & ((1 << (24 if bits == 24 else 32)) - 1), r & ((1 << bits) - 1), 0


def source_manifest(profile, api):
    resident = ROOT / profile / "resident"
    prg_path = resident / ("math_" + profile + "_game_math.prg")
    prg = prg_path.read_bytes()
    origin = int.from_bytes(prg[:2], "little")
    inc = resident / "math_api.inc"
    return {
        "profile": profile, "initialized_by_math_init": True,
        "resident_prg": str(prg_path.relative_to(ROOT)),
        "resident_prg_sha256": hashlib.sha256(prg).hexdigest(),
        "resident_load_address": "$%04X" % origin,
        "math_api_sha256": hashlib.sha256(inc.read_bytes()).hexdigest(),
        "public_entries": {key: "$%04X" % api[key] for key in ("MATH_" + op for op in WIDE_OPS)},
        "reu": ({"path": str(REU[profile].relative_to(ROOT)),
                 "sha256": hashlib.sha256(REU[profile].read_bytes()).hexdigest()}
                if profile in REU else None),
    }


def export(profile, out, frames=24):
    if profile not in PROFILES:
        raise ValueError("Unknown historical profile: " + str(profile))
    if not 1 <= frames <= 2000:
        raise ValueError("frames must be 1..2000")
    rng = random.Random(SEED)
    cpu, api = load_profile(profile)
    info = source_manifest(profile, api)
    io = MEMORY_IO
    sp = cpu.sp
    observations = []
    for frame in range(frames):
        volume = 24 if frame % 8 == 0 else 8 if frame % 4 == 0 else 3
        for ordinal in range(volume):
            op = "MATH_" + WIDE_OPS[(3 * frame + 5 * ordinal) % len(WIDE_OPS)]
            carry_in = (frame + ordinal) & 1
            n, d = (operands24(rng, frame, ordinal) if op in ("MATH_SDIV24", "MATH_SMOD24")
                    else operands(rng, frame, ordinal, 16 if op.endswith("32_16") else 32))
            if "MUL" in op:
                before_n = n.to_bytes(4, "little")
                before_d = d.to_bytes(4, "little")
                cpu.mem[io:io + 4] = before_n
                cpu.mem[io + 4:io + 8] = before_d
                cpu.mem[io + 8:io + 16] = bytes([0xA5] * 8)
            else:
                bits = 24 if op in ("MATH_SDIV24", "MATH_SMOD24") else (
                    16 if op.endswith("32_16") else 32)
                width = bits // 8
                before_n = n.to_bytes(3 if bits == 24 else 4, "little")
                before_d = d.to_bytes(width, "little")
                cpu.mem[io + 16:io + 16 + len(before_n)] = before_n
                cpu.mem[io + 20:io + 20 + len(before_d)] = before_d
                cpu.mem[io + 24:io + 32] = bytes([0xA5] * 8)
            # Make the entire caller register/flag state repeatable across all
            # profile executions: different MATH_INIT routines may return
            # different register values, which must not bias first calls.
            cpu.a = (frame * 17 + ordinal * 29) & 255
            cpu.x = (frame * 31 + ordinal * 7) & 255
            cpu.y = (frame * 13 + ordinal * 23) & 255
            start_regs = (cpu.a, cpu.x, cpu.y)
            cpu.c, cpu.d = carry_in, 0
            cycles = cpu.call(api[op], 150000)
            if cpu.sp != sp:
                raise ValueError("Historical profile stack changed: " + op)
            if "MUL" in op:
                result_width = 6 if "SHR16" in op else 8
                prod = (signed(n, 32) * signed(d, 32)) & ((1 << 64) - 1)
                expected = prod >> 16 if result_width == 6 else prod
                actual = int.from_bytes(cpu.mem[io + 8:io + 8 + result_width], "little")
                if (actual, cpu.c) != (expected, 0):
                    raise ValueError("Historical multiply result mismatch: " + profile + " " + op)
                if bytes(cpu.mem[io:io + 4]) != before_n or bytes(cpu.mem[io + 4:io + 8]) != before_d:
                    raise ValueError("Historical multiply operands modified: " + op)
            else:
                qlen = 3 if bits == 24 else 4
                got_q = int.from_bytes(cpu.mem[io + 24:io + 24 + qlen], "little")
                got_r = int.from_bytes(cpu.mem[io + 28:io + 28 + width], "little")
                if (got_q, got_r, cpu.c) != reference_div(n, d, bits):
                    raise ValueError("Historical signed division mismatch: %s %s %06x/%06x got %r" %
                                     (profile, op, n, d, (got_q, got_r, cpu.c)))
                if (bytes(cpu.mem[io + 16:io + 16 + len(before_n)]) != before_n
                    or bytes(cpu.mem[io + 20:io + 20 + width]) != before_d):
                    raise ValueError("Historical division operands modified: " + op)
            identity = hashlib.sha256(
                ("%s|%08x|%08x|A=%02x|X=%02x|Y=%02x|C=%d|D=0" %
                 (op, n, d, *start_regs, carry_in)).encode()).hexdigest()
            observations.append({
                "frame": frame, "call": ordinal, "operation": op, "input_id": identity,
                "cycles": cycles, "variant": "resident:" + profile,
                "measurement_basis": "cpu-model-public-entry-through-rts",
                "placement": "%s/$C000" % info["resident_load_address"],
            })
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(observations)
    info.update({
        "synthetic_not_real_game": True, "seed": "0x%X" % SEED,
        "frames": frames, "calls": len(observations),
        "timing_basis": "Mini6502 public-entry through RTS; no caller JSR, IRQ, VIC or REU transport added",
        "trace_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "limitations": "Resident historical binary, fixed placement; not an independently linked kernel or a proof of transplant compatibility",
    })
    out.with_suffix(".manifest.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    calls, metadata = load_trace(out)
    report = score(calls, metadata, frame_count=frames)
    return {
        "profile": profile, "calls": report["calls"],
        "mean_frame_math_cycles": report["mean_frame_math_cycles"],
        "p95_frame_math_cycles": report["p95_frame_math_cycles"],
        "peak_frame": report["peak_frame"],
        "peak_frame_math_cycles": report["peak_frame_math_cycles"],
        "over_budget_frames": report["over_budget_frames"],
        "operations": report["operations"],
        "placement": metadata["placement"],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", required=True, choices=PROFILES)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--frames", type=int, default=24)
    args = p.parse_args()
    print(json.dumps(export(args.profile, args.out, args.frames), indent=2))


if __name__ == "__main__":
    main()
