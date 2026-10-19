#!/usr/bin/env python3
"""Stock-C64 reciprocal fast path from the historical V3/V4 threshold strategy.

V3/V4 solve reciprocal quotients 1..15 with signed-free 16-bit threshold
comparisons before their REU-backed small-divisor continuation. This module
preserves that arithmetic strategy but reuses the certified 0-ZP restoring
source for D<=4096 instead of introducing an REU hardware dependency.
Not a literal relocation of the V3/V4 REU implementation.

The entire public API is unchanged: D=0 sets carry and returns Q24=0,
otherwise Q24=floor(65536/D), C=0; Q3, R0..R3 and divisor are untouched.
The executable contains writable-RAM-free stock 6510 instructions and does
not require INIT, REU, zero-page state, or SMC.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from mini6502 import Assembler

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "routines/fixed/urecip16_q16_zerozp.asm"
HISTORICAL_DONOR = "v3_reu_512k/standalone/recip_u16_u24_q16.asm"
ENTRY = "FAST_URECIP16_Q16_THRESH"
REFERENCE = "FAST_URECIP16_Q16_ZEROZP"
IMAGE_BYTES = 448


def render(code: int, io: int, scratch: int, root: Path = ROOT) -> str:
    original = (root / SOURCE).read_text(encoding="utf-8")
    if original.count("* = KERNEL_CODE\n") != 1 or (
            original.count("FAST_URECIP16_Q16_ZEROZP:") != 1):
        raise ValueError("Canonical compact reciprocal source changed")
    prefix, body = original.split("* = KERNEL_CODE\n", 1)
    bindings = {
        "KERNEL_CODE = $8000": "KERNEL_CODE = $%04X" % code,
        "INPUT_NUM = $C010": "INPUT_NUM = $%04X" % (io + 16),
        "INPUT_DIV = $C014": "INPUT_DIV = $%04X" % (io + 20),
        "OUTPUT_QUOT = $C018": "OUTPUT_QUOT = $%04X" % (io + 24),
        "OUTPUT_REM = $C01C": "OUTPUT_REM = $%04X" % (io + 28),
        "TEMP_RAM = $C020": "TEMP_RAM = $%04X" % scratch,
    }
    for old, new in bindings.items():
        if prefix.count(old) != 1:
            raise ValueError("Source address binding changed: " + old)
        prefix = prefix.replace(old, new)

    # Exact integer threshold: floor(65536 / D) <= q iff
    # D >= floor(65536/(q+1)) + 1. The historical V3/V4 donor
    # uses this same 1..15 decision ladder; use explicit full-16 tests.
    gate = [ENTRY + ":", "    ldx INPUT_DIV+1"]
    for q in range(1, 16):
        minimum = 65536 // (q + 1) + 1
        low, high = minimum & 255, minimum >> 8
        gate += [
            "    cpx #$%02X" % high,
            "    bcc RECIP_NEXT_%02d" % q,
            "    bne RECIP_TAKE_%02d" % q,
            "    lda INPUT_DIV",
            "    cmp #$%02X" % low,
            "    bcc RECIP_NEXT_%02d" % q,
            "RECIP_TAKE_%02d:" % q,
            "    lda #$%02X" % q,
            "    jmp RECIP_FAST_OUTPUT",
            "RECIP_NEXT_%02d:" % q,
        ]
    gate += [
        "    jmp " + REFERENCE,
        "RECIP_FAST_OUTPUT:",
        "    sta OUTPUT_QUOT",
        "    lda #$00",
        "    sta OUTPUT_QUOT+1",
        "    sta OUTPUT_QUOT+2",
        "    clc",
        "    rts",
    ]
    return prefix + "* = KERNEL_CODE\n" + "\n".join(gate) + "\n" + body


def assemble_image(code: int, io: int, scratch: int, root: Path = ROOT):
    if not 0x0200 <= code < 0x10000-IMAGE_BYTES:
        raise ValueError("Invalid reciprocal code origin")
    if not 0x0200 <= io <= 0x10000-32:
        raise ValueError("Invalid reciprocal public I/O")
    if not 0x0200 <= scratch < 0x10000:
        raise ValueError("Invalid reciprocal temporary scratch")
    source = render(code, io, scratch, root)
    image, labels, _ = Assembler().assemble(source)
    if (labels.get(ENTRY) != code or
            REFERENCE not in labels or
            not image or min(image) != code or
            max(image) >= code + IMAGE_BYTES):
        raise ValueError("Reciprocal historical-threshold source exceeds image")
    if set(image) != set(range(code, max(image)+1)):
        raise ValueError("Reciprocal candidate assembled non-contiguous bytes")
    packed = {addr: 0xea for addr in range(code, code+IMAGE_BYTES)}
    packed.update(image)
    return (packed, labels,
            [{"name":"KERNEL_CODE","start":"$%04X"%code,
              "bytes":IMAGE_BYTES}],
            code+IMAGE_BYTES)


def provenance(root: Path = ROOT):
    return {
        "restoring_source": hashlib.sha256((root/SOURCE).read_bytes()).hexdigest(),
        "historical_threshold": hashlib.sha256((root/HISTORICAL_DONOR).read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    for code, io, scratch in ((0x8000,0xc000,0xc020),
                               (0x7123,0xc040,0xc080)):
        image, labels, _, end = assemble_image(code,io,scratch)
        print("RECIP16 THRESHOLD STOCK",hex(code),"image",len(image),
              "fast",hex(labels[ENTRY]),"fallback",hex(labels[REFERENCE]),
              "end",hex(end),flush=True)
