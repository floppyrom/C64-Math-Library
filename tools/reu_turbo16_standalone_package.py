#!/usr/bin/env python3
"""Build an independently loadable, source-only experimental Turbo16 REU PRG.

NOT an operation-first selectable variant: no global mixed-operation allocator,
IRQ/VIC ownership, or native hardware certificate is implied.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from mini6502 import Assembler
import reu_turbo16_swap_experiment as swap
import reu_turbo16_source_tables as tables

ROOT = Path(__file__).resolve().parents[1]
LOADER_SOURCE = ROOT / "relocatable_source/turbo/turbo16_reu_preflight.asm"
BASE, LIMIT = 0x3000, 0x7800
ZP, IO, TABLE, API = 0x3e, 0xc000, 0x6000, 0x3000
CTRL, LOADER, STAGE, STATE = 0x3a00, 0x3b00, 0x3d00, 0x3e00
PROBE = STATE + 2
PUBLIC = ("T16_REU_INSTALL", "T16_REU_BEGIN", "T16_REU_CALL", "T16_REU_END")


class PackageError(ValueError):
    pass


def intersects(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


def check_claims(reu_kib, bank, *, reserved_zp=(), reserved_ram=(),
                 reserved_reu_banks=()):
    if reu_kib not in (512, 16384):
        raise PackageError("Only 512KiB and 16MiB hardware tiers were planned")
    if not isinstance(bank, int) or not 0 <= bank < reu_kib // 64:
        raise PackageError("REU bank outside declared hardware tier")
    if bank in reserved_reu_banks:
        raise PackageError("Selected REU bank is owned by another user")
    if any(intersects((ZP, ZP + 121), x) for x in reserved_zp):
        raise PackageError("122-byte executable zero-page overlay collision")
    if any(intersects((BASE, LIMIT-1), x) or
           intersects((IO, IO+31), x) for x in reserved_ram):
        raise PackageError("Single-file PRG envelope or public math I/O collision")
    alias = bank & 7 if bank >= 8 else None
    if alias is not None and alias in reserved_reu_banks:
        raise PackageError("16MiB alias verification needs ownership of mirror probe byte")
    return {
        "reu_bank_exclusive": [bank * 65536, (bank+1)*65536-1],
        "alias_guard_one_byte": alias*65536+65535 if alias is not None else None,
        "exclusive_zp": [ZP, ZP+121],
        "c64_prg_envelope": [BASE, LIMIT-1],
        "public_io": [IO, IO+31],
        "reu_io2_registers": [0xdf00, 0xdf0a],
    }


def build(reu_kib=512, bank=None, *, reserved_zp=(), reserved_ram=(),
          reserved_reu_banks=()):
    if bank is None:
        bank = 4 if reu_kib == 512 else 200
    claims = check_claims(reu_kib, bank, reserved_zp=reserved_zp,
                          reserved_ram=reserved_ram,
                          reserved_reu_banks=reserved_reu_banks)
    old, pieces, controller, labels = swap.assemble(
        zp=ZP, io=IO, table=TABLE, api=API, ctrl=CTRL, state=STATE,
        bank=bank, reu_bytes=reu_kib*1024)
    table_manifest, planes = tables.materialize()
    source = LOADER_SOURCE.read_text(encoding="utf-8")
    prefix = "\n".join((
        "T16_LOADER_BASE = $%04X" % LOADER,
        "T16_STATE = $%04X" % STATE,
        "T16_READY = $%04X" % (STATE+1),
        "T16_PROBE = $%04X" % PROBE,
        "T16_OVERLAY_STAGE = $%04X" % STAGE,
        "REU_TURBO16_BANK = $%02X" % bank,
        "REU_ALIAS_BANK = $%02X" % (bank & 7),
        "REU_HIGH_BANK = $%02X" % int(bank >= 8),
        "T16_SWAP_BEGIN = $%04X" % labels["begin"],
        "T16_SWAP_CALL = $%04X" % labels["call"],
        "T16_SWAP_END = $%04X" % labels["end"],
    )) + "\n"
    try:
        memory, symbols, _ = Assembler().assemble(prefix+source)
    except (ValueError, KeyError, AssertionError) as exc:
        raise PackageError("Independent REU loader assembly failed: "+str(exc)) from exc
    if not memory or set(memory) != set(range(LOADER, LOADER+len(memory))):
        raise PackageError("Loader did not assemble contiguously")
    if len(memory) > 0x200:
        raise PackageError("Loader overflowed its 512-byte allocation")
    if any(symbols.get(name) is None for name in PUBLIC):
        raise PackageError("One or more public REU exports are absent")
    occupied = set()
    image = bytearray(LIMIT-BASE)

    def insert(name, address, data):
        if not BASE <= address or address+len(data) > LIMIT:
            raise PackageError("Physical segment escaped PRG: "+name)
        region = set(range(address, address+len(data)))
        if occupied & region:
            raise PackageError("Overlapping PRG segments: "+name)
        occupied.update(region)
        image[address-BASE:address-BASE+len(data)] = data

    insert("call binder", API+0x840, pieces["turbo16_call_binder.bin"])
    insert("DMA swap", CTRL, pieces["turbo16_dma_swap_controller.bin"])
    insert("REU installation loader", LOADER,
           bytes(memory[a] for a in range(LOADER, LOADER+len(memory))))
    insert("initial REU executable payload", STAGE, pieces["turbo16_zp_overlay.bin"])
    # Slots $3e00..$3e02 intentionally load as zeros in this single-file PRG.
    for offset, name in zip(tables.OFFSETS, tables.NAMES):
        insert(name, TABLE+offset, planes[name])
    payload = bytes((BASE & 255, BASE >> 8))+bytes(image)
    manifest = {
        "schema": "turbo16-standalone-reu-preflight-package-v1",
        "status": "SOURCE_BUILT_LOADABLE_PRG_NATIVE_REU_NOT_YET_QUALIFIED",
        "public_exports": {name: "$%04X" % symbols[name] for name in PUBLIC},
        "unprotected_legacy_swap_exports_must_not_be_called": True,
        "requires_io2_exclusivity": True,
        "requires_cpu_port_io_visible": True,
        "requires_no_live_irq_users_of_exclusive_zp": True,
        "hardware_minimum_reu_kib": reu_kib,
        "reu_bank": bank,
        "zero_page_restored_after_each_end": True,
        "single_file_loader_prg_bytes": len(payload),
        "prg_load_address": "$%04X" % BASE,
        "prg_sha256": hashlib.sha256(payload).hexdigest(),
        "loader_source_sha256": hashlib.sha256(LOADER_SOURCE.read_bytes()).hexdigest(),
        "controller_source_sha256": old["controller_source_sha256"],
        "quarter_square_source_sha256": table_manifest["reference_sources_sha256"],
        "claimed_resources": claims,
        "reu_mode_selectable_in_operation_first_builder": False,
        "native_vice_qualified": False,
        "known_limits": [
            "Binary contains zero-filled RAM gaps; whole PRG envelope must be reserved",
            "User must exclusively own selected REU bank and alias probe byte",
            "Preflight probe is destructive within explicitly owned REU resources",
            "No IRQ/VIC coexistence or mixed-operation global linker certification",
            "No claim of physical DMA timing or historical parity",
        ],
    }
    return manifest, payload


def parse_range(value):
    try:
        a, b = value.split("-", 1)
        lo, hi = int(a, 0), int(b, 0)
    except (ValueError, AttributeError) as exc:
        raise argparse.ArgumentTypeError("Expected start-end, e.g. 0x20-0x30") from exc
    if not 0 <= lo <= hi <= 0xffff:
        raise argparse.ArgumentTypeError("Out-of-bounds reservation")
    return lo, hi


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--reu-kib", type=int, choices=(512, 16384), default=512)
    parser.add_argument("--bank", type=lambda x: int(x, 0))
    parser.add_argument("--reserved-zp", type=parse_range, action="append", default=[])
    parser.add_argument("--reserved-ram", type=parse_range, action="append", default=[])
    parser.add_argument("--reserved-reu-bank", type=int, action="append", default=[])
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.exit(2, "REU package: output exists; refusing overwrite\n")
    try:
        manifest, payload = build(args.reu_kib, args.bank,
                                  reserved_zp=args.reserved_zp,
                                  reserved_ram=args.reserved_ram,
                                  reserved_reu_banks=args.reserved_reu_bank)
    except (PackageError, swap.SwapError, OSError, ValueError) as exc:
        parser.exit(2, "REU package: "+str(exc)+"\n")
    args.out.mkdir(parents=True)
    (args.out/"turbo16_reu.prg").write_bytes(payload)
    (args.out/"turbo16_reu_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    print("Built source-only experimental Turbo16 standalone REU package.")
    print("Operation-first selectable support and native VICE qualification: pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
