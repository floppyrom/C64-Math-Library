#!/usr/bin/env python3
"""Relocatable, three-table ISQRT16 based on the certified resident lookup kernel.

No REU or setup is needed.  The maximum candidate for high byte h is
isqrt((h << 8) | 255); the descending comparison finds isqrt(n) exactly.
Every byte of all three tables is deterministically derived from integer math.
"""
from __future__ import annotations

from math import isqrt
from pathlib import Path
import re
from mini6502 import Assembler

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "routines/roots/isqrt16_square_table.asm"
CODE_BYTES = 38
TABLE_NAMES = ("SQ_LO", "SQ_HI", "SEED")


def align_page(address: int) -> int:
    return (address + 255) & ~255


def layout(start: int):
    pages = align_page(start + CODE_BYTES)
    positions = {"KERNEL_CODE": start}
    positions.update({name: pages + 256*i for i, name in enumerate(TABLE_NAMES)})
    return positions, pages + 3*256


def tables() -> tuple[bytes, bytes, bytes]:
    squares = [x*x for x in range(256)]
    return (bytes(n & 255 for n in squares),
            bytes(n >> 8 for n in squares),
            bytes(isqrt((h << 8) | 255) for h in range(256)))


def render(positions: dict, io: int, root: Path = ROOT):
    source = (root / SOURCE).read_text(encoding="utf-8")
    bindings = {**positions, "INPUT_NUM": io + 16, "OUTPUT_Z": io + 8}
    for label, value in bindings.items():
        pattern = r"(?m)^" + re.escape(label) + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        source, count = re.subn(pattern, label + " = $%04X" % value, source)
        if count != 1:
            raise ValueError("ISQRT16 source binding missing or ambiguous: " + label)
    return source


def assemble(start: int, io: int, root: Path = ROOT):
    positions, end = layout(start)
    code, labels, _ = Assembler().assemble(render(positions, io, root))
    expected = set(range(start, start + CODE_BYTES))
    if set(code) != expected or labels.get("FAST_ISQRT16_TABLE") != start:
        raise ValueError("ISQRT16 compiled size/entry mismatch")
    regions = [{"name": "KERNEL_CODE", "start": "$%04X" % start,
                "bytes": CODE_BYTES}]
    for name, table in zip(TABLE_NAMES, tables()):
        beginning = positions[name]
        assert len(table) == 256 and beginning % 256 == 0
        for i, b in enumerate(table):
            addr = beginning + i
            if addr in code:
                raise ValueError("ISQRT16 source/table overlap")
            code[addr] = b
        regions.append({"name": name, "start": "$%04X" % beginning,
                        "bytes": len(table)})
    return code, start, regions, end
