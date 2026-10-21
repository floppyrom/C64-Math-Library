#!/usr/bin/env python3
"""Source-qualified Turbo32 and QS16 ingredients for operation-first REU migration.

These are independently *assembled* and collision-audited source components,
NOT selectable REU services. Neither module is safe to install until hardware
detection, REU memory initialization, lifecycle, native DMA and mixed-project
qualification have passed. No historical resident PRG is used to generate them.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from mini6502 import Assembler
from reu_turbo16_fragment import locked_source
import reu_turbo16_source_tables as quarter_tables

ROOT = Path(__file__).resolve().parents[1]
T32_OVERLAY = Path("relocatable_source/turbo/turbo32_overlay.asm")
T32_RUNTIME = Path("relocatable_source/turbo/turbo32_runtime.asm")
QS_SOURCE = Path("relocatable_source/v4_reu_16m/v4_qs16_relocatable.asm")
QS_RECORDS = 131071
QS_BYTES = QS_RECORDS * 4
QS_BANKS = 8
T32_ZP_BYTES = 135


class REUSourceError(ValueError):
    pass


def _span(name, begin, size):
    if not (isinstance(begin, int) and isinstance(size, int) and
            size > 0 and 0x0200 <= begin <= begin + size - 1 <= 0xffff):
        raise REUSourceError("Invalid C64 RAM extent: " + name)
    end = begin + size - 1
    if begin <= 0xdfff and end >= 0xd000:
        raise REUSourceError("C64 I/O collision: " + name)
    return begin, end


def _disjoint(ranges):
    items = list(ranges.items())
    for i, (name, (begin, end)) in enumerate(items):
        for other, (lo, hi) in items[i + 1:]:
            if begin <= hi and lo <= end:
                raise REUSourceError("Collision: " + name + " / " + other)


def _assemble(source, defines):
    header = "\n".join("%s = $%04X" % (key, value)
                       for key, value in defines.items()) + "\n"
    try:
        return Assembler().assemble(header + source)
    except (ValueError, KeyError, AssertionError) as exc:
        raise REUSourceError("Original source no longer assembles: " + str(exc)) from exc


def _chunks(memory, ranges):
    result = {}
    for name, (lo, hi) in ranges.items():
        addresses = [a for a in memory if lo <= a <= hi]
        if not addresses:
            continue
        if addresses != list(range(lo, lo + len(addresses))):
            raise REUSourceError("Noncontiguous source section: " + name)
        result[name] = bytes(memory[a] for a in addresses)
    return result


def turbo32_fragments(*, zp=0x0a, io=0xc000, table=0x6000,
                      low=0x4000, api=0x3000, root=ROOT):
    """Qualify 135-ZP executable plus binder/summation, no DMA claimed."""
    if type(zp) is not int or not 2 <= zp <= 0x79:
        raise REUSourceError("Turbo32 135-byte executable ZP must fit $02-$FF")
    if type(table) is not int or table % 256:
        raise REUSourceError("Turbo32 quarter-square base must be page aligned")
    ranges = {
        "public_io": _span("public_io", io, 32),
        "low_runtime": _span("low_runtime", low, 512),
        "public_binder": _span("public_binder", api + 0x900, 256),
        "table_planes": _span("table_planes", table + 0x1000, 2048),
    }
    _disjoint(ranges)
    sources, provenance = [], {}
    for path in (T32_OVERLAY, T32_RUNTIME):
        data, sha = locked_source(root, path)
        sources.append(data)
        provenance[path.as_posix()] = sha
    defines = {
        "TURBO32_ZP_BASE": zp, "REG_LOW": low, "REG_API": api,
        "REG_TABLE": table, "MATH_IO": io, "MATH_X": io,
        "MATH_Y": io + 4, "MATH_Z": io + 8,
    }
    memory, labels, _ = _assemble("\n".join(sources), defines)
    actual_zp = {a for a in memory if a < 256}
    if actual_zp != set(range(zp, zp + T32_ZP_BYTES)):
        raise REUSourceError("Source ZP executable is not precisely 135 bytes")
    if labels.get("T32_PUBLIC_CALL") != api + 0x900:
        raise REUSourceError("Turbo32 public ABI symbol was displaced")
    if labels.get("umult32x8_same_x") is None or labels.get("T32_PREP") != low:
        raise REUSourceError("Missing Turbo32 producer or preparer entry")
    for a in memory:
        if a >= 256 and not any(lo <= a <= hi for lo, hi in ranges.values()):
            raise REUSourceError("Turbo32 emitted bytes outside declared regions")
    chunks = {
        "turbo32_executable_zp.bin": bytes(memory[a] for a in
                                            range(zp, zp + T32_ZP_BYTES)),
        **_chunks(memory, {
            "turbo32_low_preparer.bin": (low, low + 0xff),
            "turbo32_low_summation.bin": (low + 0x100, low + 0x1ff),
            "turbo32_public_binder.bin": ranges["public_binder"],
        }),
    }
    table_manifest, planes = quarter_tables.materialize(root)
    return {
        "schema": "turbo32-operation-first-source-fragments-v1",
        "qualification": "SOURCE_ASSEMBLED_ONLY_NOT_REU_INSTALLABLE",
        "source_hashes": provenance,
        "public_entry": "$%04X" % labels["T32_PUBLIC_CALL"],
        "exclusive_zp": ["$%02X" % zp, "$%02X" % (zp + 134)],
        "exclusive_zp_bytes": 135,
        "c64_regions": {k: ["$%04X" % x for x in v] for k, v in ranges.items()},
        "table_source_hashes": table_manifest["reference_sources_sha256"],
        "table_sha256": table_manifest["plane_sha256"],
        "segment_sha256": {n: hashlib.sha256(b).hexdigest()
                           for n, b in sorted(chunks.items())},
        "native_dma_and_hardware_qualified": False,
    }, chunks, planes


def qs16_table():
    """Generate Q(v)=floor(v*v/4), 4 little-endian bytes per entry.

    Q(131070) is 4294836225 and fits exactly in an unsigned 32-bit word.
    This is *new mathematically derived data*, not a copied old REU image.
    """
    return b"".join(((v * v) // 4).to_bytes(4, "little")
                    for v in range(QS_RECORDS))


def qs16_fragments(*, io=0xc000, scratch=0xc020, zp=0x02,
                   api=0x3000, reu_bank=0x10, root=ROOT):
    """Assemble archived QS16 symbolic BEGIN/CALL/END as source fragments.

    This does not create/init a live REU, install the table or implement
    fail-closed DMA capability checking; therefore not selectable.
    """
    if type(zp) is not int or not 2 <= zp <= 0xe2:
        raise REUSourceError("QS16 16-byte ZP range must fit")
    if type(reu_bank) is not int or reu_bank % 8 or not 0 <= reu_bank <= 0xf8:
        raise REUSourceError("QS16 REU tables require eight aligned 64KiB banks")
    ranges = {
        "public_io": _span("public_io", io, 32),
        "reu_scratch": _span("reu_scratch", scratch, 4),
        "qs16_code": _span("qs16_code", api + 0xa80, 0x200),
    }
    _disjoint(ranges)
    source, sha = locked_source(root, QS_SOURCE)
    defines = {"REG_API": api, "MATH_IO": io, "REU_SCRATCH": scratch,
               "ZP_MAIN": zp, "REU_QS16_BASE_BANK": reu_bank}
    memory, labels, _ = _assemble(source, defines)
    if set(memory) - set(range(*[ranges["qs16_code"][0],
                                ranges["qs16_code"][1] + 1])):
        raise REUSourceError("QS16 code extends outside declared range")
    expected = {"MATH_REU_QS16_BEGIN": api + 0xa80,
                "MATH_REU_QS16": api + 0xa8b,
                "MATH_REU_QS16_END": api + 0xb5c}
    if any(labels.get(k) != v for k, v in expected.items()):
        raise REUSourceError("Relocatable QS16 lifecycle ABI changed")
    sources = {
        "qs16_begin.bin": (api + 0xa80, api + 0xa8a),
        "qs16_call.bin": (api + 0xa8b, api + 0xb5b),
        "qs16_end.bin": (api + 0xb5c, api + 0xb66),
    }
    chunks = _chunks(memory, sources)
    if len(chunks) != 3:
        raise REUSourceError("QS16 source has missing lifecycle code")
    data = qs16_table()
    if len(data) != QS_BYTES:
        raise REUSourceError("Generated QS16 table size incorrect")
    return {
        "schema": "qs16-operation-first-source-fragments-v1",
        "qualification": "SOURCE_ASSEMBLED_DATA_GENERATED_NOT_REU_INSTALLABLE",
        "source_hashes": {QS_SOURCE.as_posix(): sha},
        "entrypoints": {n: "$%04X" % v for n, v in expected.items()},
        "exclusive_zp": ["$%02X" % (zp + 0x0e),
                         "$%02X" % (zp + 0x1d)],
        "exclusive_zp_bytes": 16,
        "reu_bank_start": reu_bank,
        "reu_bank_count": 8,
        "table_record_count": QS_RECORDS,
        "table_bytes": QS_BYTES,
        "table_sha256": hashlib.sha256(data).hexdigest(),
        "segment_sha256": {n: hashlib.sha256(b).hexdigest()
                           for n, b in sorted(chunks.items())},
        "native_dma_and_hardware_qualified": False,
    }, chunks, data
