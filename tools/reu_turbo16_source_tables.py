#!/usr/bin/env python3
"""Emit the four Turbo16 lookup planes from SHA-locked *source*, not a PRG.

Historical V3 and V4 relocatable source text each contains explicit physical
REG_TABLE bytes. These are direct source materialization, not a mathematical
re-derivation or a linker-ready REU package. Assert byte-for-byte agreement
across source tiers and (in tests) with the immutable reference PRG.

Turbo16 uses REG_TABLE + $1000/$1200/$1400/$1600, 512 bytes apiece.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    Path("relocatable_source/v3_reu_512k/math_relocatable.asm"),
    Path("relocatable_source/v4_reu_16m/math_relocatable.asm"),
)
REG_TABLE_MARKER = "* = REG_TABLE"
OFFSETS = (0x1000, 0x1200, 0x1400, 0x1600)
PAGE_BYTES = 512
BYTES_REQUIRED = OFFSETS[-1] + PAGE_BYTES
NAMES = ("sqr_lo.bin", "sqr_hi.bin",
         "neg_sqr_lo.bin", "neg_sqr_hi.bin")


class TableError(ValueError):
    pass


def source_manifest(root: Path) -> dict:
    result = {}
    for line in (root / "SHA256SUMS.txt").read_text("utf-8").splitlines():
        if len(line) >= 67 and line[64:66] == "  ":
            result[line[66:]] = line[:64]
    return result


def parse_source(path: Path, root: Path, locked: dict) -> tuple[bytes, str]:
    content = (root / path).read_bytes()
    sha = hashlib.sha256(content).hexdigest()
    if locked.get(path.as_posix()) != sha:
        raise TableError("Historical REU table source drift: " + str(path))
    source = content.decode("utf-8")
    if source.count(REG_TABLE_MARKER) != 1:
        raise TableError("Expected unique REG_TABLE source definition")
    text = source.split(REG_TABLE_MARKER, 1)[1]
    memory = bytearray()
    for raw in text.splitlines()[1:]:
        if len(memory) >= BYTES_REQUIRED:
            break
        data = raw.partition(";")[0].strip()
        if not data:
            continue
        m = re.fullmatch(r"!byte\s+((?:\$[0-9a-fA-F]{2}(?:\s*,\s*)?)+)", data)
        if m is None:
            raise TableError("Unexpected nonliteral REU table source at +" +
                             format(len(memory), "X") + ": " + data)
        values = m.group(1).split(",")
        try:
            memory.extend(int(v.strip()[1:], 16) for v in values)
        except ValueError as exc:
            raise TableError("Malformed historical literal byte") from exc
    if len(memory) != BYTES_REQUIRED:
        raise TableError("Historical quarter-square table region is incomplete")
    return bytes(memory), sha


def materialize(root: Path = ROOT) -> tuple[dict, dict[str, bytes]]:
    """Build four 512-byte source-linked lookup planes; never claim REU readiness."""
    root = root.resolve()
    locked = source_manifest(root)
    sources = {}
    pages = []
    for path in SOURCES:
        original, sha = parse_source(path, root, locked)
        sources[path.as_posix()] = sha
        pages.append(tuple(original[start:start + PAGE_BYTES] for start in OFFSETS))
    if pages[0] != pages[1]:
        raise TableError("V3 and V4 historical Turbo16 source tables disagree")
    chunks = dict(zip(NAMES, pages[0]))
    for name, chunk in chunks.items():
        if len(chunk) != PAGE_BYTES:
            raise TableError("Missing Turbo16 table plane " + name)
    manifest = {
        "schema": "turbo16-source-table-planes-v1",
        "status": "SOURCE_EXTRACTED_ONLY_NOT_INDEPENDENT_MATH_GENERATION",
        "reference_sources_sha256": sources,
        "source_table_offsets": [format(x, "#06x") for x in OFFSETS],
        "plane_names": list(NAMES),
        "plane_sizes": {name: len(chunk) for name, chunk in chunks.items()},
        "plane_sha256": {name: hashlib.sha256(chunk).hexdigest()
                         for name, chunk in chunks.items()},
        "total_bytes": 4 * PAGE_BYTES,
        "requires_math_init": False,
        "byte_identical_v3_v4_source_tables": True,
        "legacy_prg_required_to_materialize": False,
        "independent_math_generated_tables": False,
        "native_reu_backend_available": False,
    }
    return manifest, chunks


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.exit(2, "Turbo16 source tables: destination exists\n")
    try:
        report, planes = materialize()
    except (TableError, OSError) as exc:
        parser.exit(2, "Turbo16 source tables: " + str(exc) + "\n")
    args.out.mkdir(parents=True)
    for name, data in planes.items():
        (args.out / name).write_bytes(data)
    (args.out / "source_table_manifest.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
