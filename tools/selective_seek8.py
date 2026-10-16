#!/usr/bin/env python3
"""Relocatable SEEK8 DDA: the unmodified generated 582-byte standalone kernel.

Keep one physical producer for INIT, STEP, STEP_INT and STEP1; the linker's
separate public exports have distinct entry addresses but share the 160-byte
persistent per-object state. INIT uses 19 bytes of per-call scratch. Inputs
retain their public MATH_X/MATH_Y/MATH_N positions rather than a private IO
block. No additional zero-page bytes, REU or MATH_INIT are required.
"""
from __future__ import annotations
from pathlib import Path
import re
from mini6502 import Assembler

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "routines/movement/seek_u8_u8_dda.asm"
CODE_BYTES = 582
STATE_BYTES = 160
INIT_SCRATCH_BYTES = 19
ENTRIES = ("seek8_init", "seek8_step", "seek8_step_int", "seek8_step1")


def assemble(code: int, io: int, scratch: int, state: int, root: Path = ROOT):
    if state % 8 or not (0x200 <= state <= 0x10000 - STATE_BYTES):
        raise ValueError("SEEK8 persistent state must be 8-byte aligned RAM")
    if scratch + INIT_SCRATCH_BYTES > 0x10000:
        raise ValueError("SEEK8 init scratch exceeds RAM")
    source = (root / SOURCE).read_text(encoding="utf-8")
    symbols = {
        "ORG": code, "ST": state,
        "SEEK_IN_X": io, "SEEK_IN_XH": io + 1,
        "SEEK_IN_Y": io + 4,
        "SEEK_IN_SPL": io + 16, "SEEK_IN_SPH": io + 17,
        "SEEK_T": scratch,
    }
    for label, value in symbols.items():
        pattern = r"(?m)^" + re.escape(label) + r"\s*=\s*(?:\$[0-9a-fA-F]+|IO\+\d+)\s*$"
        source, n = re.subn(pattern, f"{label} = ${value:04X}", source)
        if n != 1:
            raise ValueError("Generated SEEK8 source binding missing or duplicated: " + label)
    image, labels, constants = Assembler().assemble(source)
    if set(image) != set(range(code, code + CODE_BYTES)):
        raise ValueError("SEEK8 generated 582-byte code contract changed")
    if any(label not in labels or labels[label] not in image for label in ENTRIES):
        raise ValueError("SEEK8 public entry or source labels missing")
    if constants["S8_POS_X"] != state or constants["S8_POS_Y"] != state + 8:
        # The source's state field offsets are a public part of the ABI.
        raise ValueError("SEEK8 persistent state layout changed")
    return image, labels, [{"name":"KERNEL_CODE","start":f"${code:04X}",
                            "bytes":CODE_BYTES}], code + CODE_BYTES
