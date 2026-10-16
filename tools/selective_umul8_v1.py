#!/usr/bin/env python3
"""Relocate the *original* 51-byte V1 UMUL8 producer and its two exact tables.

The shipped V1 kernel has a 22-byte $3000 entry and a 29-byte $4700 helper.
Contiguous relocation removes their unused address gap; it does not replace
any instruction or alter the Q(n)=floor(n*n/4) lookup data. No REU required.
"""
from __future__ import annotations

import re
from pathlib import Path
from mini6502 import Assembler

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "routines/multiply/umul8_v1_original.asm"
CODE_BYTES = 51
ENTRIES = 511
STRIDE = 512


def layout(start: int):
    first = (start + CODE_BYTES + 255) & ~255
    return {"KERNEL_CODE": start, "Q_LO": first, "Q_HI": first + STRIDE}, first + STRIDE + ENTRIES


def table_bytes():
    squares = [i * i // 4 for i in range(ENTRIES)]
    return bytes(n & 255 for n in squares), bytes(n >> 8 for n in squares)


def assemble(start: int, io: int, zp: int, root: Path = ROOT):
    if not 2 <= zp <= 252:
        raise ValueError("V1 UMUL8 requires four consecutive private ZP bytes")
    positions, end = layout(start)
    if end > 0x10000:
        raise ValueError("V1 UMUL8 tables overflow address space")
    symbols = {**positions, "INPUT_X": io, "INPUT_Y": io+4,
               "OUTPUT_Z": io+8, "TEMP_ZP": zp, "TEMP_ZP2": zp+2}
    source = (root / SOURCE).read_text(encoding="utf-8")
    for label, value in symbols.items():
        pattern = r"(?m)^" + re.escape(label) + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        source, count = re.subn(pattern, f"{label} = ${value:04X}", source)
        if count != 1:
            raise ValueError("V1 UMUL8 source binding missing or ambiguous: " + label)
    machine, labels, _ = Assembler().assemble(source)
    if set(machine) != set(range(start, start + CODE_BYTES)):
        raise ValueError("V1 UMUL8 assembled byte length differs from the original 51-byte producer")
    if labels.get("FAST_UMUL8_V1") != start:
        raise ValueError("V1 UMUL8 exported entry mismatches source")
    segments = [{"name": "KERNEL_CODE", "start": f"${start:04X}", "bytes": CODE_BYTES}]
    for label, data in zip(("Q_LO", "Q_HI"), table_bytes()):
        address = positions[label]
        if address & 255 or len(data) != ENTRIES:
            raise ValueError("V1 UMUL8 original lookup geometry changed")
        for offset, value in enumerate(data):
            if address + offset in machine:
                raise ValueError("V1 UMUL8 table overlaps executable code")
            machine[address + offset] = value
        segments.append({"name": label, "start": f"${address:04X}", "bytes": ENTRIES})
    return machine, start, segments, end
