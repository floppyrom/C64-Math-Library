#!/usr/bin/env python3
"""Build a source-derived Turbo32 standalone REU candidate, not yet an installer.

The package has its own hardware probe, guarded lifecycle, and executable
135-byte ZP overlay. It uses NO frozen resident PRG or preloaded .reu image.
Native x64sc + selective-global-allocation qualification are separate gates.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from mini6502 import Assembler
import reu_turbo16_standalone_package as t16
from reu_turbo16_fragment import locked_source
from reu_remaining_source_modules import turbo32_fragments, REUSourceError

ROOT = Path(__file__).resolve().parents[1]
CTRL_SOURCE = Path("relocatable_source/turbo/turbo16_swap_controller.asm")
LOADER_SOURCE = Path("relocatable_source/turbo/turbo16_reu_preflight.asm")
BASE, LIMIT, ZP, IO = 0x3000, 0x7800, 0x0A, 0xC000
API, LOW, TABLE = 0x3000, 0x4000, 0x6000
CTRL, LOADER, STAGE, STATE = 0x3A00, 0x3B00, 0x3D00, 0x3E00
N = 135
PUBLIC = ("T32_REU_INSTALL", "T32_REU_BEGIN", "T32_REU_CALL", "T32_REU_END")


class Turbo32Error(ValueError):
    pass


def _assemble(src, defines):
    header = "\n".join("%s = $%04X" % (k, v) for k, v in defines.items()) + "\n"
    try:
        return Assembler().assemble(header+src)
    except (ValueError, KeyError, AssertionError) as exc:
        raise Turbo32Error("Turbo32 source/controller assembly failed: "+str(exc)) from exc


def _adapt(source):
    # Source-derived adaptation, not a binary patch: distinct symbols and
    # 135-byte DMA length, preserving original probe and failure contracts.
    return source.replace("TURBO16", "TURBO32").replace("T16_", "T32_").replace(
        "#$7A", "#$87").replace("#$7a", "#$87")


def check_claims(capacity, bank, reserved_zp=(), reserved_ram=(),
                 reserved_reu_banks=()):
    if capacity not in (512, 16384) or type(bank) is not int or not 0 <= bank < capacity//64:
        raise Turbo32Error("Turbo32 needs 512KiB/16MiB REU and a valid bank")
    claims = {"reu_bank_exclusive": (bank*65536,(bank+1)*65536-1),
              "c64_image": (BASE,LIMIT-1), "public_io": (IO,IO+31),
              "exclusive_zp": (ZP,ZP+N-1),
              "alias_probes": [a*65536+65535 for a in t16.alias_banks(bank)]}
    for kind, ranges, allowed in (
        ("reserved_zp",reserved_zp,(0,255)),
        ("reserved_ram",reserved_ram,(0,65535)),
    ):
        for r in ranges:
            if not (isinstance(r,(tuple,list)) and len(r)==2 and
                    all(type(a) is int for a in r) and
                    allowed[0] <= r[0] <= r[1] <= allowed[1]):
                raise Turbo32Error("Invalid "+kind)
            competing = [claims["exclusive_zp"]] if kind=="reserved_zp" else [
                claims["c64_image"],claims["public_io"]]
            if any(t16.intersects(r, pair) for pair in competing):
                raise Turbo32Error("Turbo32 memory ownership collision: "+kind)
    for b in reserved_reu_banks:
        if type(b) is not int or not 0 <= b < capacity//64:
            raise Turbo32Error("Invalid user REU bank")
        if b==bank or b in t16.alias_banks(bank):
            raise Turbo32Error("Reserved bank conflicts with Turbo32 REU/alias probe")
    return claims


def build(capacity=512, bank=None, *, reserved_zp=(), reserved_ram=(),
          reserved_reu_banks=()):
    if bank is None:
        bank = 4 if capacity==512 else 200
    claims = check_claims(capacity, bank, reserved_zp,
                          reserved_ram, reserved_reu_banks)
    frag, chunks, planes = turbo32_fragments(
        zp=ZP, io=IO, table=TABLE, low=LOW, api=API)
    controller_source, ctrl_sha = locked_source(ROOT, CTRL_SOURCE)
    loader_source, loader_sha = locked_source(ROOT, LOADER_SOURCE)
    controller, control_labels, _ = _assemble(_adapt(controller_source), {
        "REU_CTRL_BASE": CTRL, "T32_STATE": STATE,
        "TURBO32_ZP_BASE": ZP, "REU_TURBO32_BANK": bank,
        "T32_PUBLIC_CALL": API+0x900,
    })
    if control_labels.get("T32_SWAP_BEGIN") != CTRL or not controller or (
        set(controller)!=set(range(CTRL,CTRL+len(controller))) or
        len(controller)>128):
        raise Turbo32Error("Turbo32 controller escaped the 128-byte slot")
    alias_data = ",".join("$%02X"%b for b in (t16.alias_banks(bank) or (0,)))
    loader, public, _ = _assemble(
        _adapt(loader_source).replace("!byte T32_ALIAS_BYTES",
                                      "!byte "+alias_data), {
            "T32_LOADER_BASE": LOADER, "T32_STATE": STATE,
            "T32_READY": STATE+1, "T32_PROBE": STATE+2,
            "T32_OVERLAY_STAGE": STAGE, "REU_TURBO32_BANK": bank,
            "T32_ALIAS_COUNT": len(t16.alias_banks(bank)),
            "T32_SWAP_BEGIN": control_labels["T32_SWAP_BEGIN"],
            "T32_SWAP_CALL": control_labels["T32_SWAP_CALL"],
            "T32_SWAP_END": control_labels["T32_SWAP_END"],
        })
    if not loader or set(loader)!=set(range(LOADER,LOADER+len(loader))) or len(loader)>512:
        raise Turbo32Error("Turbo32 installation loader escaped 512-byte slot")
    if any(public.get(name) is None for name in PUBLIC):
        raise Turbo32Error("Turbo32 missing guarded public lifecycle")
    pieces = {
        "turbo32_controller": (CTRL,bytes(controller[x] for x in range(CTRL,CTRL+len(controller)))),
        "turbo32_loader": (LOADER,bytes(loader[x] for x in range(LOADER,LOADER+len(loader)))),
        "turbo32_zp_stage": (STAGE,chunks["turbo32_executable_zp.bin"]),
        "turbo32_preparer": (LOW,chunks["turbo32_low_preparer.bin"]),
        "turbo32_summation": (LOW+0x100,chunks["turbo32_low_summation.bin"]),
        "turbo32_binder": (API+0x900,chunks["turbo32_public_binder.bin"]),
    }
    for offset,name in zip((0x1000,0x1200,0x1400,0x1600),planes):
        pieces["turbo32_"+name]=(TABLE+offset,planes[name])
    data=bytearray(LIMIT-BASE)
    occupied=set()
    for name,(address,blob) in pieces.items():
        new=set(range(address,address+len(blob)))
        if not blob or occupied & new or min(new)<BASE or max(new)>=LIMIT:
            raise Turbo32Error("Turbo32 PRG overlap or escaped segment: "+name)
        occupied.update(new)
        data[address-BASE:address-BASE+len(blob)]=blob
    prg=bytes((BASE&255,BASE>>8))+bytes(data)
    result={
        "schema":"turbo32-standalone-source-built-reu-candidate-v1",
        "status":"CPU_MODEL_PENDING_NATIVE_REU_AND_GLOBAL_BUILDER",
        "public_exports":{name:"$%04X"%public[name] for name in PUBLIC},
        "exclusive_zero_page_restored_by_guarded_end":True,
        "reu_bank":bank,
        "capacity_kib":capacity,
        "source_sha256":{str(CTRL_SOURCE):ctrl_sha,str(LOADER_SOURCE):loader_sha,
                         **frag["source_hashes"]},
        "claims":claims,
        "segments":{name:{"address":"$%04X"%a,"bytes":len(b),
                          "sha256":hashlib.sha256(b).hexdigest()}
                    for name,(a,b) in pieces.items()},
        "prg_sha256":hashlib.sha256(prg).hexdigest(),
        "reu_native_qualified":False,
        "operation_first_allocator_qualified":False,
        "may_use_without_successful_install":False,
        "caller_cannot_use_overlaid_zp_until_end":True,
    }
    return result, prg
