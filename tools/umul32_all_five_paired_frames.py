#!/usr/bin/env python3
"""Same-placement 24-frame public-call comparison of five historical UMUL32 kernels.

This is deterministic 6510 instruction-cycle model arithmetic time, not actual
PAL/VIC-II/IRQ or DMA frame time. All five sources remain selectable; the
comparison does not substitute a compact fallback with a slower new kernel.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import math_builder
import selective_linker as linker
import selective_speed_umul32 as speed
from frame_cycle_budget import Call, score
from mini6502 import CPU, Assembler
import selective_fast31_umul32 as fast31

ROOT = Path(__file__).resolve().parents[1]
API = "MATH_UMUL32"
VARIANTS = tuple(sorted(speed.EXPECTED))
FRAMES = 24
CALL_COUNT = 150
MASK64 = (1 << 64) - 1


def scenario():
    pairs = speed.corpus()
    calls = []
    for frame in range(FRAMES):
        volume = 24 if frame % 8 == 0 else 8 if frame % 4 == 0 else 3
        for ordinal in range(volume):
            x, y = pairs[(frame * 37 + ordinal * 83) % len(pairs)]
            register_a = (frame * 17 + ordinal * 29) & 255
            register_x = (frame * 31 + ordinal * 7) & 255
            register_y = (frame * 13 + ordinal * 23) & 255
            carry = (frame + ordinal) & 1
            identity = hashlib.sha256(
                ("%s|%08x|%08x|A=%02x|X=%02x|Y=%02x|C=%d|D=0" %
                 (API, x, y, register_a, register_x, register_y, carry)
                ).encode("ascii")).hexdigest()
            calls.append((frame, ordinal, x, y, register_a,
                          register_x, register_y, carry, identity))
    assert len(calls) == CALL_COUNT
    return tuple(calls)


def evaluate(variant, code=0x8000, io=0xc000, zp=0x50):
    if variant not in speed.EXPECTED:
        raise ValueError("UMUL32 source variant is not authenticated: " + str(variant))
    if io < 0x200 or io + 0x80 >= 0x10000 or zp + 31 > 0xff:
        raise ValueError("UMUL32 I/O/ZP placement is out of bounds")
    plan = math_builder.create_plan(
        math_builder.operation_index(), ["UMUL32"], objective="size",
        zp_budget=31, ram_budget=3200, pins={"UMUL32": variant})
    with tempfile.TemporaryDirectory(prefix="umul32_paired_frame_") as td:
        path = Path(td)
        manifest = linker.build(plan, path, memory={
            "code_base": code, "math_io": io, "zp_base": zp,
            "scratch_base": io + 0x40})
        operations = manifest["operations"]
        if len(operations) != 1 or operations[0]["api"] != API or operations[0]["variant"] != variant:
            raise AssertionError("UMUL32 variant pin/source-link drift")
        used = manifest["resource_use"]
        want_code, want_zp, want_scratch = speed.EXPECTED_RESOURCES[variant]
        if (used["zero_page_bytes"] != want_zp or
            used["private_ram_scratch_bytes"] != want_scratch or
            used["image_span_bytes"] < want_code):
            raise AssertionError("UMUL32 RAM/ZP/source geometry drift")
        binary = (path / "math_selective.prg").read_bytes()
        if binary[:2] != code.to_bytes(2, "little"):
            raise AssertionError("UMUL32 linked PRG load base mismatch")
        length = len(binary) - 2
        if code + length >= io or code + length >= 0x10000:
            raise AssertionError("UMUL32 code overlaps public input region")
        mem = bytearray(65536)
        mem[code:code+length] = binary[2:]
        before = bytes(mem[code:code+length])
        mod = linker.MODULES[API][variant]
        # Shared FAST31 adds a signed export in the same physical image.
        # Assemble the exact variant-specific donor source, not the standalone
        # FAST31 default from the per-operation speed helper.
        if variant in ("link:fast31-shared-full64", "link:fast31-v2-public"):
            source_image, source_entry, _, source_end = fast31.assemble(
                code, io, zp, ROOT, source_path=mod["source"])
            layout, end = fast31.layout(code)
            if source_end != end:
                raise AssertionError("FAST31 original table/code layout drift")
            rendered = fast31.render(layout, io, zp, ROOT, mod["source"])
            _, labels, _ = Assembler().assemble(rendered)
            mutable = {addr + 1 for key, addr in labels.items()
                       if key.startswith("SMC_")}
            if len(mutable) != 10:
                raise AssertionError("FAST31 original ten SMC operands changed")
        else:
            source_image, source_entry, mutable = speed.source_assemble(
                variant, mod, code, io, io + 0x40, ROOT, zp)
        entry = int(operations[0]["entry"][1:], 16)
        if entry != source_entry or any(
            mem[addr] != val for addr, val in source_image.items()):
            raise AssertionError("UMUL32 source-assembled bytes do not match linked PRG")
        cpu = CPU(mem)
        sp = cpu.sp
        observations = []
        for frame, ordinal, x, y, a, rx, ry, carry, identity in scenario():
            xb, yb = x.to_bytes(4, "little"), y.to_bytes(4, "little")
            mem[io:io+4] = xb
            mem[io+4:io+8] = yb
            mem[io+8:io+16] = bytes((0xa5,)) * 8
            cpu.a, cpu.x, cpu.y = a, rx, ry
            cpu.c, cpu.d = carry, 0
            ticks = cpu.call(entry, 125000)
            actual = int.from_bytes(mem[io+8:io+16], "little")
            if (actual != (x * y) & MASK64 or
                bytes(mem[io:io+4]) != xb or bytes(mem[io+4:io+8]) != yb or
                cpu.c != 0 or cpu.sp != sp):
                raise AssertionError(
                    ("UMUL32 full64/public ABI drift", variant, frame, ordinal, x, y, actual))
            observations.append(Call(frame, ordinal, API, identity, ticks, variant))
        modified = {code+i for i, (old, new) in enumerate(
            zip(before, mem[code:code+length])) if old != new}
        if not modified.issubset(mutable):
            raise AssertionError(
                ("UMUL32 unexpected executable/table mutation", variant,
                 sorted(modified - mutable)))
        metadata = {
            "measurement_basis": "cpu-model-public-entry-through-rts",
            "placement": "$%04X/$%04X" % (code, io),
            "variants": {API: variant},
        }
        budget = score(observations, metadata, frame_count=FRAMES)
        return {
            "variant": variant, "code": "$%04X" % code, "io": "$%04X" % io,
            "zp": zp, "source_sha256": hashlib.sha256(
                (ROOT / mod["source"]).read_bytes()).hexdigest(),
            "linked_prg_sha256": hashlib.sha256(binary).hexdigest(),
            "resources": used, "calls": observations, "scored": budget,
        }


def compare(code, io, zp=0x50):
    evidence = {variant: evaluate(variant, code, io, zp)
                for variant in VARIANTS}
    reference = evidence["link:compact-zerozp"]["calls"]
    keys = tuple(v.key for v in reference)
    if len(keys) != CALL_COUNT or len(set(keys)) != CALL_COUNT:
        raise AssertionError("UMUL32 paired corpus count/uniqueness changed")
    baseline = evidence["link:compact-zerozp"]["scored"]
    output = {
        "code": "$%04X" % code, "io": "$%04X" % io,
        "frames": FRAMES, "paired_calls": CALL_COUNT,
        "cpu_model_only": True, "native_pal_timing": False,
        "baseline_variant": "link:compact-zerozp",
        "per_variant": {},
    }
    for variant, result in evidence.items():
        calls = result["calls"]
        if tuple(v.key for v in calls) != keys:
            raise AssertionError("UMUL32 candidate public operand/caller corpus drift")
        b = result["scored"]
        delta_calls = [n.cycles - o.cycles for o, n in zip(reference, calls)]
        old_frames = baseline["frame_math_cycles"]
        new_frames = b["frame_math_cycles"]
        output["per_variant"][variant] = {
            "source_sha256": result["source_sha256"],
            "linked_prg_sha256": result["linked_prg_sha256"],
            "zero_page_bytes": result["resources"]["zero_page_bytes"],
            "code_span_bytes": result["resources"]["image_span_bytes"],
            "main_ram_total_bytes": result["resources"]["main_ram_total_bytes"],
            "mean_public_cycles": sum(v.cycles for v in calls) / CALL_COUNT,
            "peak_frame_math_cycles": b["peak_frame_math_cycles"],
            "p95_frame_math_cycles": b["p95_frame_math_cycles"],
            "total_math_cycles": b["total_math_cycles"],
            "peak_savings_vs_compact": baseline["peak_frame_math_cycles"] -
                                       b["peak_frame_math_cycles"],
            "total_savings_vs_compact": baseline["total_math_cycles"] -
                                        b["total_math_cycles"],
            "regressed_calls_vs_compact": sum(x > 0 for x in delta_calls),
            "worst_call_regression_vs_compact": max((0, *delta_calls)),
            "regressed_frames_vs_compact": sum(
                n > o for o, n in zip(old_frames, new_frames)),
            "worst_frame_regression_vs_compact": max(
                (0, *(n - o for o, n in zip(old_frames, new_frames)))),
        }
    return output


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    report = {
        "basis": "source-linked same-public-call 24-frame UMUL32 all-five",
        "placements": [compare(0x8000, 0xc000), compare(0x7123, 0xc040, 0x70)],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
