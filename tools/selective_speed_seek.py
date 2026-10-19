#!/usr/bin/env python3
"""Authenticated full-public cycle models for the original shared SEEK8/SEEK16 DDA.

Measure INIT separately from STEP, STEP_INT and STEP1, on deterministic,
bounded eight-slot movement traces. INIT costs must not be charged to frame
steppers. Arrival/post-arrival and both major-axis and Euclidean modes are
included. These are 6510 CPU-model cycles, not physical PAL frame timing.
No alternate or slower arithmetic kernel is introduced.
"""
from __future__ import annotations

import hashlib
import random
from pathlib import Path

from mini6502 import CPU, load_sparse
import selective_seek8 as seek8
import selective_seek16 as seek16

ROOT = Path(__file__).resolve().parents[1]
VARIANT = "link:generated-dda"
SUFFIXES = ("INIT", "STEP", "STEP_INT", "STEP1")
BASIS = "original-shared-seek-dda-complete-public-movement-v1"
FIXTURES = 80
SPECS = {
    "SEEK8": (seek8, 651, 160, "routines/movement/seek_u8_u8_dda.asm",
              "4a94cb656a5893183cee9416828e5e97d3f5118d6799d2678d7983d22299f6f0"),
    "SEEK16": (seek16, 898, 248, "routines/movement/seek_u16_u8_dda.asm",
               "da4f4113a93da195c491a1c1247c101c1d1620ada48c8ddc0d3375adbdf15144"),
}
INIT_SPEEDS = ((0, 1), (128, 1), (0, 2), (128, 129),
               (128, 0), (0, 4), (0, 1), (0, 2))


def fixtures(family):
    """Fixed movement corpus; all routes have <= 40 pixels major-axis length."""
    rng = random.Random(0x5EE82026 + (16 if family == "SEEK16" else 8))
    result = []
    maximum = 639 if family == "SEEK16" else 255
    for i in range(FIXTURES):
        slot = i % 8
        x = rng.randrange(40, maximum - 39)
        y = rng.randrange(40, 160)
        dx = rng.randrange(-36, 37)
        dy = rng.randrange(-36, 37)
        if i % 10 == 0:
            dx = dy = 0
        elif i % 10 == 1:
            dx, dy = 1, 0
        elif i % 10 == 2:
            dx, dy = 0, -1
        elif i % 10 == 3:
            dx, dy = 0, 36
        elif i % 10 == 4:
            dx, dy = -36, 0
        elif i % 10 == 5:
            dx, dy = 36, 36
        result.append((slot, x, y, x + dx, y + dy))
    return result


def benchmark(api, modules, code, io, scratch, root=ROOT):
    family = api[5:].split("_")[0]
    suffix = api[5 + len(family) + 1:]
    if family not in SPECS or suffix not in SUFFIXES:
        raise ValueError("Unqualified SEEK public name: " + api)
    emitter, image_size, state_size, path, locked_sha = SPECS[family]
    if set(modules) != {VARIANT}:
        raise ValueError("SEEK candidate set changed; source qualification required")
    mod = modules[VARIANT]
    if (mod["source"] != path
        or mod["segments"] != (("KERNEL_CODE", image_size),)
        or mod["entry"] != family.lower() + "_" + suffix.lower()
        or mod["zp"] != 0 or mod["scratch"] != 19
        or mod.get("persistent_state") != state_size
        or mod.get("state_family") != family.lower()
        or mod.get("share_producer") != family.lower() + "-dda"
        or not mod.get(family.lower())
        or not mod.get("multi_entry")
        or mod.get("requires_reu") or mod.get("requires_writable_code")):
        raise ValueError("SEEK original code/resource/public entry contract drift")
    source_digest = hashlib.sha256((root / path).read_bytes()).hexdigest()
    if source_digest != locked_sha:
        raise ValueError("Historical SEEK generated source SHA changed")
    state = (scratch + 19 + 7) & ~7
    if (not 0x200 <= state or state + state_size > 0x10000
        or code + image_size > 0x10000 or io + 32 > 0x10000
        or not (code + image_size <= io or io + 32 <= code)
        or not (io + 32 <= scratch)
        or not (scratch + 19 <= state)
        or not (code + image_size <= scratch or state + state_size <= code)):
        raise ValueError("SEEK source model placement overlaps RAM or crosses address space")
    image, labels, segments, end = emitter.assemble(code, io, scratch, state, root)
    if (end != code + image_size
        or set(image) != set(range(code, end))
        or len(labels) < 4
        or any(e not in labels for e in emitter.ENTRIES)):
        raise ValueError("SEEK generated source geometry/exports changed")
    original_code = bytes(image[a] for a in range(code, end))
    cpu = CPU(load_sparse(image))
    mem = cpu.mem
    sp = cpu.sp
    cases = fixtures(family)
    ticks = []
    digest = hashlib.sha256()
    entry = labels[mod["entry"]]
    init_entry = labels[family.lower() + "_init"]
    for i, (slot, sx, sy, tx, ty) in enumerate(cases):
        if suffix == "INIT":
            low, high = INIT_SPEEDS[i % len(INIT_SPEEDS)]
        elif suffix == "STEP":
            low, high = ((128, 1), (128, 129), (0, 2))[i % 3]
        elif suffix == "STEP_INT":
            low, high = 0, 2
        else:
            low, high = 0, 1
        digest.update(bytes((slot, sy, ty, low, high)))
        digest.update(sx.to_bytes(2, "little") + tx.to_bytes(2, "little"))
        # Inputs and other object slots are sentinels, not temporary storage.
        if family == "SEEK8":
            mem[state + slot] = sx
            mem[state + 8 + slot] = sy
            mem[io] = tx
        else:
            mem[state + slot] = sx & 255
            mem[state + 8 + slot] = sx >> 8
            mem[state + 16 + slot] = sy
            mem[io:io + 2] = tx.to_bytes(2, "little")
        mem[io + 4] = ty
        mem[io + 16] = low
        mem[io + 17] = high
        inputs = bytes(mem[io:io + 32])
        others = bytes(mem[state:state + state_size])
        cpu.a = (i * 17 + sx) & 255
        cpu.y = (i * 5 + ty) & 255
        cpu.x = slot
        cpu.d = 0
        cpu.c = i & 1
        cycles = cpu.call(init_entry, 140000)
        if (cpu.sp != sp or cpu.x != slot or bytes(mem[io:io + 32]) != inputs
            or cpu.c != int(sx == tx and sy == ty)):
            raise ValueError("SEEK INIT public ABI/arrival drift " + repr((api, i)))
        if any(mem[state + j] != before for j, before in enumerate(others)
               if (j % 8) != slot):
            raise ValueError("SEEK INIT clobbered a different object slot")
        if suffix == "INIT":
            ticks.append(cycles)
            continue

        def position():
            if family == "SEEK8":
                return mem[state + slot], mem[state + 8 + slot]
            return (mem[state + slot] | (mem[state + 8 + slot] << 8),
                    mem[state + 16 + slot])

        arrived = False
        for frame in range(96):
            cpu.x = slot
            cpu.a = (frame + i) & 255
            cpu.y = (frame ^ i) & 255
            cpu.d = 0
            cpu.c = (frame + i) & 1
            cycles = cpu.call(entry, 140000)
            ticks.append(cycles)
            if cpu.sp != sp or cpu.x != slot or bytes(mem[io:io + 32]) != inputs:
                raise ValueError("SEEK step public input/X/SP drift " + repr((api, i, frame)))
            if cpu.c:
                if position() != (tx, ty):
                    raise ValueError("SEEK step arrival coordinates mismatch")
                cpu.x = slot
                cpu.d = 0
                ticks.append(cpu.call(entry, 140000))
                if (not cpu.c or cpu.sp != sp or cpu.x != slot
                    or position() != (tx, ty)
                    or bytes(mem[io:io + 32]) != inputs):
                    raise ValueError("SEEK post-arrival/public ABI mismatch")
                arrived = True
                break
        if not arrived:
            raise ValueError("SEEK fixture never arrived " + repr((api, i)))
        if any(mem[state + j] != before for j, before in enumerate(others)
               if (j % 8) != slot):
            raise ValueError("SEEK step clobbered a different object slot")
    if bytes(mem[code:end]) != original_code:
        raise ValueError("SEEK source mutated executable code")
    ordered = sorted(ticks)
    return {
        "basis": BASIS, "operation": api, "cases": len(ticks),
        "fixtures": len(cases), "corpus_sha256": digest.hexdigest(),
        "cpu_model_only": True, "native_hardware_timing": False,
        "mean_cycles": {VARIANT: sum(ticks) / len(ticks)},
        "p95_cycles": {VARIANT: ordered[(len(ordered) * 95 - 1) // 100]},
        "maximum_cycles": {VARIANT: ordered[-1]},
        "source_sha256": {VARIANT: source_digest},
        "generator_sha256": hashlib.sha256(
            (root / "tools/seek_kernel.py").read_bytes()).hexdigest(),
        "code_origin": "$%04X" % code, "io_origin": "$%04X" % io,
        "state_origin": "$%04X" % state,
        "note": "One original shared multi-entry DDA producer; INIT and each stepper measured separately including arrival and post-arrival; CPU-model cycles, not PAL/IRQ timings",
    }


def bench_seek8_init(modules, code, io, scratch, root):
    return benchmark("MATH_SEEK8_INIT", modules, code, io, scratch, root)


def bench_seek8_step(modules, code, io, scratch, root):
    return benchmark("MATH_SEEK8_STEP", modules, code, io, scratch, root)


def bench_seek8_step_int(modules, code, io, scratch, root):
    return benchmark("MATH_SEEK8_STEP_INT", modules, code, io, scratch, root)


def bench_seek8_step1(modules, code, io, scratch, root):
    return benchmark("MATH_SEEK8_STEP1", modules, code, io, scratch, root)


def bench_seek16_init(modules, code, io, scratch, root):
    return benchmark("MATH_SEEK16_INIT", modules, code, io, scratch, root)


def bench_seek16_step(modules, code, io, scratch, root):
    return benchmark("MATH_SEEK16_STEP", modules, code, io, scratch, root)


def bench_seek16_step_int(modules, code, io, scratch, root):
    return benchmark("MATH_SEEK16_STEP_INT", modules, code, io, scratch, root)


def bench_seek16_step1(modules, code, io, scratch, root):
    return benchmark("MATH_SEEK16_STEP1", modules, code, io, scratch, root)
