#!/usr/bin/env python3
"""Relocatable quarter-square UMUL8 emitter; no resident profile dependency.

Q(n)=floor(n*n/4), 0<=n<=510. Since x+y and x-y have equal parity,
Q(x+y)-Q(abs(x-y)) = x*y exactly, including all unsigned 8-bit edges.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

from mini6502 import Assembler

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "routines/multiply/umul8_quartersquare.asm"
CODE_BYTES = 73
TABLE_ENTRIES = 511


def tables() -> tuple[bytes, bytes]:
    values = [n * n // 4 for n in range(TABLE_ENTRIES)]
    assert max(values) <= 0xffff
    return (bytes(v & 255 for v in values),
            bytes(v >> 8 for v in values))


def layout(start: int):
    return {
        "KERNEL_CODE": start,
        "Q_LO": start + CODE_BYTES,
        "Q_HI": start + CODE_BYTES + TABLE_ENTRIES,
    }, start + CODE_BYTES + 2 * TABLE_ENTRIES


def render(layout_map: dict, io: int, scratch: int, root: Path):
    source = (root / SOURCE).read_text(encoding="utf-8")
    bindings = {
        **layout_map,
        "INPUT_X": io,
        "INPUT_Y": io + 4,
        "OUTPUT_Z": io + 8,
        "TEMP_RAM": scratch,
    }
    for label, value in bindings.items():
        pattern = r"(?m)^" + re.escape(label) + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        source, n = re.subn(pattern, label + " = $%04X" % value, source)
        if n != 1:
            raise ValueError("Missing or duplicated source binding: " + label)
    return source


def assemble(start: int, io: int, scratch: int, root: Path = ROOT):
    addresses, end = layout(start)
    source = render(addresses, io, scratch, root)
    code, labels, _ = Assembler().assemble(source)
    if set(code) != set(range(start, start + CODE_BYTES)):
        raise ValueError("UMUL8 quarter-square code length/relocation mismatch")
    if labels.get("FAST_UMUL8_QUARTERSQUARE") != start:
        raise ValueError("UMUL8 quarter-square public entry mismatch")
    lower, upper = tables()
    for label, contents in (("Q_LO", lower), ("Q_HI", upper)):
        begin = addresses[label]
        if len(contents) != TABLE_ENTRIES:
            raise ValueError("Unexpected quarter-square table length")
        for i, byte in enumerate(contents):
            loc = begin + i
            if loc in code:
                raise ValueError("UMUL8 quarter-square code/table collision")
            code[loc] = byte
    geometry = [
        {"name": "KERNEL_CODE", "start": "$%04X" % start, "bytes": CODE_BYTES},
        {"name": "Q_LO", "start": "$%04X" % addresses["Q_LO"], "bytes": TABLE_ENTRIES},
        {"name": "Q_HI", "start": "$%04X" % addresses["Q_HI"], "bytes": TABLE_ENTRIES},
    ]
    return code, start, geometry, end


def source_sha256(root: Path = ROOT) -> str:
    return hashlib.sha256((root / SOURCE).read_bytes()).hexdigest()
