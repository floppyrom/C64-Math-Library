#!/usr/bin/env python3
"""Relocatable source/table assembler for the published stock-C64 ATAN2 kernels.

Uses the library's canonical table generator and executable source, rather
than copying V1/V2 resident bytes. Table start addresses are always page aligned.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1] / "routines" / "atan2"
sys.path.insert(0, str(HERE))
from tables import build_tables, build_sum_tables
from mini6502 import Assembler

KINDS = {
    "compact": {
        "file": "atan2_compact_opt.asm",
        "code_bytes": 94,
        "tables": ("LOGTAB", "ATANTAB"),
    },
    "sum-fast": {
        "file": "atan2_sum_fast.asm",
        "code_bytes": 85,
        "tables": ("LOGX", "LOGY", "QPOS", "QNEG"),
    },
}


def align_page(pc: int) -> int:
    return (pc + 255) & ~255


def layout(kind: str, start: int):
    spec = KINDS[kind]
    cursor = start
    positions = {"KERNEL_CODE": cursor}
    cursor += spec["code_bytes"]
    cursor = align_page(cursor)
    for name in spec["tables"]:
        positions[name] = cursor
        cursor += 256
    return positions, cursor


def render(kind: str, positions: dict, io: int, root: Path):
    path = root / "routines" / "atan2" / KINDS[kind]["file"]
    text = path.read_text(encoding="utf-8")
    if text.count(".org @ORG@") != 1:
        raise ValueError("Missing/ambiguous ATAN2 origin marker")
    text = text.replace(".org @ORG@", "* = $%04X" % positions["KERNEL_CODE"])
    for symbol, dest in (("X0", io), ("Y0", io+4), ("Z0", io+8)):
        old = "%s=$%04X" % (symbol, {"X0":0xC000,"Y0":0xC004,"Z0":0xC008}[symbol])
        if text.count(old) != 1:
            raise ValueError("Missing ATAN2 operand symbol: " + symbol)
        text = text.replace(old, "%s=$%04X" % (symbol, dest))
    for name in KINDS[kind]["tables"]:
        if kind == "compact":
            original = name + "=$" + ("9600" if name == "LOGTAB" else "9700")
        else:
            original = name + "=@" + name + "@"
        if text.count(original) != 1:
            raise ValueError("Missing ATAN2 table symbol: " + name)
        text = text.replace(original, name + "=$%04X" % positions[name])
    return text


def assemble(kind: str, start: int, io: int, root: Path):
    positions, end = layout(kind, start)
    text = render(kind, positions, io, root)
    machine, labels, _ = Assembler().assemble(text)
    expected = set(range(start, start + KINDS[kind]["code_bytes"]))
    if set(machine) != expected or labels.get("atan2") != start:
        raise ValueError("ATAN2 compiled bytes/entry differ from qualified source")
    if kind == "compact":
        log, angle, *_ = build_tables()
        tables = (log, angle)
    else:
        tables = build_sum_tables()
    for name, page in zip(KINDS[kind]["tables"], tables):
        if len(page) != 256 or positions[name] % 256:
            raise ValueError("ATAN2 table page invalid")
        for i, b in enumerate(page):
            addr = positions[name] + i
            if addr in machine:
                raise ValueError("ATAN2 code/table overlap")
            machine[addr] = b
    ranges = [
        {"name": "KERNEL_CODE", "start": "$%04X" % start,
         "bytes": KINDS[kind]["code_bytes"]}
    ]
    ranges.extend(
        {"name": name, "start": "$%04X" % positions[name], "bytes": 256}
        for name in KINDS[kind]["tables"]
    )
    return machine, start, ranges, end


def source_path(kind: str) -> str:
    return "routines/atan2/" + KINDS[kind]["file"]


def source_sha256(kind: str, root: Path) -> str:
    return hashlib.sha256((root / source_path(kind)).read_bytes()).hexdigest()
