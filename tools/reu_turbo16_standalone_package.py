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


def alias_banks(bank):
    """All distinct mirror candidates for smaller power-of-two REUs."""
    return tuple(dict.fromkeys(bank % n for n in (8,16,32,64,128)
                               if bank >= n))


def check_claims(reu_kib, bank, *, reserved_zp=(), reserved_ram=(),
                 reserved_reu_banks=()):
    if reu_kib not in (512, 16384):
        raise PackageError("Only 512KiB and 16MiB hardware tiers were planned")
    if not isinstance(bank, int) or not 0 <= bank < reu_kib // 64:
        raise PackageError("REU bank outside declared hardware tier")
    for label, ranges, maximum in (("zero-page", reserved_zp, 255),
                                    ("RAM", reserved_ram, 65535)):
        for region in ranges:
            if (not isinstance(region, (tuple, list)) or len(region) != 2 or
                    any(type(n) is not int for n in region) or
                    not 0 <= region[0] <= region[1] <= maximum):
                raise PackageError("Invalid user-reserved "+label+" region")
    if any(type(n) is not int or n < 0 or n >= reu_kib//64
           for n in reserved_reu_banks):
        raise PackageError("Invalid user-reserved REU bank")
    if bank in reserved_reu_banks:
        raise PackageError("Selected REU bank is owned by another user")
    if any(intersects((ZP, ZP + 121), x) for x in reserved_zp):
        raise PackageError("122-byte executable zero-page overlay collision")
    if any(intersects((BASE, LIMIT-1), x) or
           intersects((IO, IO+31), x) for x in reserved_ram):
        raise PackageError("Single-file PRG envelope or public math I/O collision")
    aliases = alias_banks(bank)
    if any(a in reserved_reu_banks for a in aliases):
        raise PackageError("16MiB alias verification needs ownership of mirror probe byte")
    return {
        "reu_bank_exclusive": [bank * 65536, (bank+1)*65536-1],
        "alias_guard_one_byte": aliases[0]*65536+65535 if aliases else None,
        "alias_guard_bytes": [a*65536+65535 for a in aliases],
        "exclusive_zp": [ZP, ZP+121],
        "c64_prg_envelope": [BASE, LIMIT-1],
        "public_io": [IO, IO+31],
        "reu_io2_registers": [0xdf00, 0xdf0a],
    }


def stock_manifest_claims(stock):
    """Read actual physical allocations from a successful stock selective build.

    This is an *additional* fail-closed compatibility audit, not global
    allocation, relocation, or source linking. Unknown dimensions must fail.
    """
    try:
        if not isinstance(stock, dict) or stock["target"] != "c64":
            raise PackageError("Expected an operation-first stock C64 manifest")
        memory, use = stock["memory_map"], stock["resource_use"]
        if not isinstance(stock["operations"], list) or not stock["operations"]:
            raise PackageError("Missing selected stock math operations")

        def number(value, name):
            if not isinstance(value, str) or not value.startswith("$"):
                raise PackageError("Missing/invalid stock physical address: " + name)
            number = int(value[1:], 16)
            if not 0 <= number <= 0xffff:
                raise PackageError("Invalid stock address: "+name)
            return number

        def span(start, size, name, *, is_zp=False):
            if type(size) is not int or size < 0:
                raise PackageError("Unqualified stock allocation size: "+name)
            if size == 0:
                return None
            lo = number(start, name)
            hi = lo + size - 1
            if hi > (255 if is_zp else 0xffff):
                raise PackageError("Stock resource extent out of bounds: "+name)
            return (lo, hi)

        ram = []
        zp = []
        cs = number(memory["code_start"], "code_start")
        ce = number(memory["code_end"], "code_end")
        if ce < cs:
            raise PackageError("Stock code end before start")
        ram.append((cs,ce))
        ram.append(span(memory["math_io_start"], use["public_io_bytes"], "math_io_start"))
        if use["private_ram_scratch_bytes"]:
            ram.append(span(memory["scratch_start"], use["private_ram_scratch_bytes"], "scratch_start"))
        if use["zero_page_bytes"]:
            zp.append(span(memory["zp_start"], use["zero_page_bytes"], "zp_start",is_zp=True))
        # Manifest reports family starts and total persistent bytes, but not
        # individual family lengths. Guessing would be unsafe: refuse.
        if memory["persistent_state"] or use.get("persistent_state_bytes",0):
            raise PackageError("Stock persistent state extents not individually reported; cannot audit safely")
        for field,destination,zero in (("user_reserved",ram,False),("user_zp_reserved",zp,True)):
            for item in memory[field]:
                a=number(item["start"],field+".start")
                b=number(item["end"],field+".end")
                if not 0 <= a <= b <= (255 if zero else 0xffff):
                    raise PackageError("Bad stock reserved range: "+field)
                destination.append((a,b))
        if any(item is None for item in ram+zp):
            raise PackageError("Unknown stock RAM or ZP occupancy")
        return {"ram":ram, "zp":zp, "stock_operations":len(stock["operations"])}
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        if isinstance(exc, PackageError):
            raise
        raise PackageError("Incomplete or invalid stock linker resource manifest: "+str(exc)) from exc


def build(reu_kib=512, bank=None, *, reserved_zp=(), reserved_ram=(),
          reserved_reu_banks=(), stock_manifest=None):
    if bank is None:
        bank = 4 if reu_kib == 512 else 200
    stock = stock_manifest_claims(stock_manifest) if stock_manifest is not None else None
    claims = check_claims(reu_kib, bank,
                          reserved_zp=tuple(reserved_zp)+(tuple(stock["zp"]) if stock else ()),
                          reserved_ram=tuple(reserved_ram)+(tuple(stock["ram"]) if stock else ()),
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
        "T16_ALIAS_COUNT = $%02X" % len(alias_banks(bank)),
        "T16_SWAP_BEGIN = $%04X" % labels["begin"],
        "T16_SWAP_CALL = $%04X" % labels["call"],
        "T16_SWAP_END = $%04X" % labels["end"],
    )) + "\n"
    try:
        alias_data = ",".join("$%02X" % a for a in (alias_banks(bank) or (0,)))
        memory, symbols, _ = Assembler().assemble(
            prefix+source.replace("!byte T16_ALIAS_BYTES", "!byte "+alias_data))
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
        "smaller_reu_alias_banks_excluded": list(alias_banks(bank)),
        "zero_page_restored_after_each_end": True,
        "single_file_loader_prg_bytes": len(payload),
        "prg_load_address": "$%04X" % BASE,
        "prg_sha256": hashlib.sha256(payload).hexdigest(),
        "loader_source_sha256": hashlib.sha256(LOADER_SOURCE.read_bytes()).hexdigest(),
        "controller_source_sha256": old["controller_source_sha256"],
        "quarter_square_source_sha256": table_manifest["reference_sources_sha256"],
        "claimed_resources": claims,
        "stock_manifest_collision_check": ("PASSED_FOR_REPORTED_RESOURCES" if stock else "NOT_SUPPLIED"),
        "stock_selected_operations_checked": stock["stock_operations"] if stock else 0,
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
    parser.add_argument("--stock-manifest", type=Path, help="Audit physical resources in an existing operation-first selective_manifest.json; fail closed on incomplete extents")
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.exit(2, "REU package: output exists; refusing overwrite\n")
    try:
        manifest, payload = build(args.reu_kib, args.bank,
                                  reserved_zp=args.reserved_zp,
                                  reserved_ram=args.reserved_ram,
                                  reserved_reu_banks=args.reserved_reu_bank,
                                  stock_manifest=json.loads(args.stock_manifest.read_text("utf-8")) if args.stock_manifest else None)
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
