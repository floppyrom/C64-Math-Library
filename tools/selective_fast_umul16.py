#!/usr/bin/env python3
"""Relocatable zero-ZP 16x16 quarter-square emitter.

Four 8x8 partial products share the same two 511-byte quarter-square planes.
All symbol addresses are explicit and the generated table bytes are taken
from the established UMUL8 quarter-square generator.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

from mini6502 import Assembler
import selective_fast_umul8 as fast8

SOURCE = "routines/multiply/umul16_quartersquare.asm"
CODE_BYTES = 233
TABLE_BYTES = 511


def layout(start: int, code_bytes: int = CODE_BYTES):
    addresses = {
        "KERNEL_CODE": start,
        "Q_LO": start + code_bytes,
        "Q_HI": start + code_bytes + TABLE_BYTES,
    }
    return addresses, start + code_bytes + 2 * TABLE_BYTES


def render(addresses: dict, io: int, scratch: int, root: Path,
           source_path: str = SOURCE):
    source = (root / source_path).read_text(encoding="utf-8")
    values = {
        **addresses,
        "INPUT_X": io,
        "INPUT_Y": io + 4,
        "OUTPUT_Z": io + 8,
        "TEMP_RAM": scratch,
    }
    for symbol, value in values.items():
        regex = r"(?m)^" + re.escape(symbol) + r"\s*=\s*\$[0-9A-Fa-f]+\s*$"
        source, count = re.subn(regex, f"{symbol} = ${value:04X}", source)
        if count != 1:
            raise ValueError("Missing or ambiguous UMUL16 source binding: " + symbol)
    return source


def assemble(start: int, io: int, scratch: int, root: Path,
             *, source_path: str = SOURCE, code_bytes: int = CODE_BYTES,
             entry_label: str = "FAST_UMUL16_QUARTERSQUARE"):
    positions, end = layout(start, code_bytes)
    machine, labels, _ = Assembler().assemble(
        render(positions, io, scratch, root, source_path))
    expected = set(range(start, start + code_bytes))
    if set(machine) != expected or entry_label not in labels:
        raise ValueError("UMUL16 quarter-square code size or entry mismatch")
    lower, upper = fast8.tables()
    if len(lower) != TABLE_BYTES or len(upper) != TABLE_BYTES:
        raise ValueError("UMUL16 quarter-square table-size mismatch")
    for name, table in (("Q_LO", lower), ("Q_HI", upper)):
        begin = positions[name]
        for offset, value in enumerate(table):
            address = begin + offset
            if address in machine:
                raise ValueError("UMUL16 quarter-square source/data collision")
            machine[address] = value
    segments = [
        {"name": "KERNEL_CODE", "start": f"${start:04X}", "bytes": code_bytes},
        {"name": "Q_LO", "start": f"${positions['Q_LO']:04X}", "bytes": TABLE_BYTES},
        {"name": "Q_HI", "start": f"${positions['Q_HI']:04X}", "bytes": TABLE_BYTES},
    ]
    return machine, labels[entry_label], segments, end


def source_sha256(root: Path):
    return hashlib.sha256((root / SOURCE).read_bytes()).hexdigest()
