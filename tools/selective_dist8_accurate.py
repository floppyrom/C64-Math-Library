#!/usr/bin/env python3
"""Relocatable V1 DIST8_ACCURATE with exact resident-derived lookup tables.

The 512 table bytes below are byte-identical to the immutable released V1
resident PRG pages $9A00 and $9B00. They are embedded in this text emitter,
so generating a selective build NEVER loads the full resident image.
The independent CPU regression compares them to that released PRG again.
"""
from __future__ import annotations
from pathlib import Path
import re

from mini6502 import Assembler

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "routines/game/dist8_accurate.asm"
CODE_BYTES = 66
MAX_HEX = (
    "00010203040506070809090a0b0c0d0e0f101112131415161718191a1b1c1c1d"
    "1e1f202122232425262728292a2b2c2d2e2f2f303132333435363738393a3b3c"
    "3d3e3f40414142434445464748494a4b4c4d4e4f50515253545455565758595a"
    "5b5c5d5e5f60616263646566676768696a6b6c6d6e6f70717273747576777879"
    "7a7a7b7c7d7e7f808182838485868788898a8b8c8c8d8e8f9091929394959697"
    "98999a9b9c9d9e9f9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b2b3b4b5"
    "b6b7b8b9babbbcbdbebfc0c1c2c3c4c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4"
    "d5d6d7d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaeaebecedeeeff0f1f2"
)
MIN_HEX = (
    "00000101020203030304040505050606070708080809090a0a0a0b0b0c0c0d0d"
    "0d0e0e0f0f0f1010111112121213131414141515161617171718181919191a1a"
    "1b1b1c1c1c1d1d1e1e1f1f1f2020212121222223232424242525262626272728"
    "282929292a2a2b2b2b2c2c2d2d2e2e2e2f2f3030303131323233333334343535"
    "363636373738383839393a3a3b3b3b3c3c3d3d3d3e3e3f3f4040404141424242"
    "434344444545454646474747484849494a4a4a4b4b4c4c4c4d4d4e4e4f4f4f50"
    "50515152525253535454545555565657575758585959595a5a5b5b5c5c5c5d5d"
    "5e5e5e5f5f6060616161626263636364646565666666676768686869696a6a6b"
)


def tables():
    a, b = bytes.fromhex(MAX_HEX), bytes.fromhex(MIN_HEX)
    assert len(a) == len(b) == 256
    return a, b


def layout(start):
    pages = (start + CODE_BYTES + 255) & ~255
    return {"KERNEL_CODE": start, "DIST_MAX": pages,
            "DIST_MIN": pages + 256}, pages + 512


def render(locations, io, scratch, root=ROOT):
    source = (root / SOURCE).read_text(encoding="utf-8")
    constants = {**locations, "INPUT_X": io, "INPUT_Y": io+4,
                 "OUTPUT_Z": io+8, "TEMP_RAM": scratch}
    for label, value in constants.items():
        pattern = r"(?m)^" + re.escape(label) + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        source, count = re.subn(pattern, label+" = $%04X" % value, source)
        if count != 1:
            raise ValueError("DIST8_ACCURATE source binding missing: " + label)
    return source


def assemble(start, io, scratch, root=ROOT):
    locations, end = layout(start)
    code, labels, _ = Assembler().assemble(render(locations, io, scratch, root))
    if set(code) != set(range(start, start+CODE_BYTES)):
        raise ValueError("DIST8_ACCURATE assembled code size mismatch")
    if labels.get("FAST_DIST8_ACCURATE") != start:
        raise ValueError("DIST8_ACCURATE public entry mismatch")
    regions = [{"name": "KERNEL_CODE", "start": "$%04X" % start,
                "bytes": CODE_BYTES}]
    for name, table in zip(("DIST_MAX", "DIST_MIN"), tables()):
        address = locations[name]
        if address & 255:
            raise ValueError("DIST8_ACCURATE table not aligned")
        for idx, value in enumerate(table):
            absolute = address + idx
            if absolute in code:
                raise ValueError("DIST8_ACCURATE code/table overlap")
            code[absolute] = value
        regions.append({"name": name, "start": "$%04X" % address,
                        "bytes": len(table)})
    return code, start, regions, end
