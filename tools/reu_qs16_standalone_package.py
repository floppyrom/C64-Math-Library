#!/usr/bin/env python3
"""Source-built QS16 REU package; dynamically generates all REU lookup bytes.

This experimental installable *candidate* cannot be selected from the normal
operation-first installer until native VICE and mixed-resource tests pass.
It has no runtime dependency on any historical V4 resident or REU image.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from mini6502 import Assembler
import reu_turbo16_standalone_package as t16
from reu_turbo16_fragment import locked_source
from reu_remaining_source_modules import qs16_fragments, qs16_table

ROOT=Path(__file__).resolve().parents[1]
LOADER_SOURCE=Path("relocatable_source/turbo/turbo16_reu_preflight.asm")
GENERATOR_SOURCE=Path("relocatable_source/turbo/qs16_reu_table_generator.asm")
BASE,LIMIT=0x3000,0x7800
IO,SCRATCH=0xc000,0xc020
ACTIVE,READY,PROBE=0x3801,0x3800,0x3802
SERVICE,LOADER,GENERATOR,API=0x3900,0x3b00,0x4000,0x5000
BUFFER,VERIFY=0x7000,0x7400
ZP_MAIN=0x40
TABLE_BANK=200
PUBLIC=("Q16_REU_INSTALL","Q16_REU_BEGIN","Q16_REU_CALL","Q16_REU_END")


class QS16PackageError(ValueError):
    pass


def check_claims(capacity=16384, bank=TABLE_BANK, reserved_ram=(),
                 reserved_zp=(), reserved_reu_banks=()):
    if capacity!=16384 or type(bank) is not int or bank%8 or bank<128 or bank>248:
        raise QS16PackageError("QS16 requires 16MiB REU and 8 aligned upper-half banks")
    for kind,ranges,maxsize,owned in (
        ("RAM",reserved_ram,65535,((BASE,LIMIT-1),(IO,IO+31),(SCRATCH,SCRATCH+3))),
        ("ZP",reserved_zp,255,((ZP_MAIN+0x0e,ZP_MAIN+0x1d),)),
    ):
        for r in ranges:
            if (not isinstance(r,(tuple,list)) or len(r)!=2 or
                any(type(n) is not int for n in r) or
                not 0<=r[0]<=r[1]<=maxsize):
                raise QS16PackageError("Invalid user "+kind+" range")
            if any(t16.intersects(r,x) for x in owned):
                raise QS16PackageError("QS16 "+kind+" memory reservation collision")
    selected=set(range(bank,bank+8))
    aliases=set()
    for b in selected:
        aliases.update(t16.alias_banks(b))
    if any(type(b) is not int or b<0 or b>255 for b in reserved_reu_banks):
        raise QS16PackageError("Invalid reserved REU bank")
    if selected.intersection(reserved_reu_banks) or aliases.intersection(reserved_reu_banks):
        raise QS16PackageError("QS16 REU bank or mirror-probe resource collision")
    return {
        "c64_prg":[BASE,LIMIT-1], "public_io":[IO,IO+31],
        "reu_scratch":[SCRATCH,SCRATCH+3],
        "exclusive_zero_page":[ZP_MAIN+0x0e,ZP_MAIN+0x1d],
        "reu_banks":list(range(bank,bank+8)),
        "smaller_hardware_probe_bytes":[(a<<16)+65535 for a in sorted(aliases)],
        "requires_io2_reu_register_exclusivity":True,
    }


def _adapt_loader(src):
    src=src.replace("T16_","Q16_").replace(
        "REU_TURBO16_BANK","REU_QS16_BASE_BANK")
    begin=src.find("Q16_INSTALL_UPLOAD:")
    end=src.find("Q16_INSTALL_BAD:")
    if begin<0 or end<begin:
        raise QS16PackageError("Missing audited REU loader install block")
    replacement="""Q16_INSTALL_UPLOAD:
        jsr Q16_GENERATE_TABLE
        bcs Q16_INSTALL_BAD
        lda #$01
        sta Q16_READY
        pla
        tay
        pla
        tax
        plp
        clc
        rts
"""
    return src[:begin]+replacement+src[end:]


def build(capacity=16384, bank=TABLE_BANK, *, reserved_ram=(),reserved_zp=(),
          reserved_reu_banks=()):
    claims=check_claims(capacity,bank,reserved_ram,reserved_zp,reserved_reu_banks)
    runtime, chunks, table=qs16_fragments(
        io=IO,scratch=SCRATCH,zp=ZP_MAIN,api=API,reu_bank=bank)
    loader_src, loader_sha=locked_source(ROOT,LOADER_SOURCE)
    generator_src=(ROOT/GENERATOR_SOURCE).read_text("utf-8")
    generator_sha=hashlib.sha256(generator_src.encode()).hexdigest()
    aliases=t16.alias_banks(bank)
    alias_bytes=",".join("$%02X"%b for b in (aliases or (0,)))
    loader=_adapt_loader(loader_src).replace("!byte Q16_ALIAS_BYTES","!byte "+alias_bytes)
    defines={
        "Q16_LOADER_BASE":LOADER,"Q16_STATE":ACTIVE,"Q16_READY":READY,
        "Q16_PROBE":PROBE,"Q16_OVERLAY_STAGE":0x3d00,
        "REU_QS16_BASE_BANK":bank,"Q16_ALIAS_COUNT":len(aliases),
        "Q16_SWAP_BEGIN":SERVICE,
        "Q16_SWAP_CALL":SERVICE+0x16,
        "Q16_SWAP_END":SERVICE+0x28,
        "Q16_SERVICE_BASE":SERVICE,"Q16_GENERATOR_BASE":GENERATOR,
        "Q16_ACTIVE":ACTIVE,
        "Q16_SCRATCH_ZP":ZP_MAIN+0x0e,
        "Q16_BACKUP":0x3820,
        "Q16_Q0":0x3804,"Q16_Q1":0x3805,"Q16_Q2":0x3806,"Q16_Q3":0x3807,
        "Q16_HALF_LO":0x3808,"Q16_HALF_HI":0x3809,
        "Q16_PARITY":0x380a,"Q16_REU_HIGH":0x380b,
        "Q16_REU_BANK":0x380c,
        "Q16_BLOCK_LO":0x380d,"Q16_BLOCK_HI":0x380e,
        "Q16_DATA_BUFFER":BUFFER,"Q16_VERIFY_BUFFER":VERIFY,
        "Q16_BUF_PTR":ZP_MAIN+0x0e,"Q16_SAVE_PTR0":0x3810,
        "Q16_SAVE_PTR1":0x3811,
        "REU_SCRATCH":SCRATCH,
        "MATH_REU_QS16_BEGIN":int(runtime["entrypoints"]["MATH_REU_QS16_BEGIN"][1:],16),
        "MATH_REU_QS16":int(runtime["entrypoints"]["MATH_REU_QS16"][1:],16),
        "MATH_REU_QS16_END":int(runtime["entrypoints"]["MATH_REU_QS16_END"][1:],16),
    }
    head="\n".join("%s = $%04X"%(k,v) for k,v in defines.items())+"\n"
    try:
        mem,symbols,_=Assembler().assemble(head+loader+"\n"+generator_src)
    except (ValueError,KeyError,AssertionError) as exc:
        raise QS16PackageError("QS16 loader/source assembly failed: "+str(exc)) from exc
    if any(symbols.get(n) is None for n in PUBLIC):
        raise QS16PackageError("Missing guarded QS16 public lifecycle")
    if symbols.get("Q16_SWAP_BEGIN")!=SERVICE or symbols.get("Q16_GENERATE_TABLE")!=GENERATOR:
        raise QS16PackageError("QS16 source relocation escaped assigned entrypoints")
    # The loader's gate symbols are external constants. Validate their
    # independently assembled definition in the new service module.
    for n in ("Q16_SWAP_BEGIN","Q16_SWAP_CALL","Q16_SWAP_END"):
        if symbols.get(n) is None:
            raise QS16PackageError("QS16 dispatcher absent: "+n)
    pieces={
        "loader":bytes(mem[a] for a in sorted(mem) if LOADER<=a<0x4000),
        "generator":bytes(mem[a] for a in sorted(mem) if GENERATOR<=a<0x4800),
        "dispatch":bytes(mem[a] for a in sorted(mem) if SERVICE<=a<0x3a00),
    }
    segments={
        "loader":(LOADER,pieces["loader"]),
        "generator":(GENERATOR,pieces["generator"]),
        "dispatch":(SERVICE,pieces["dispatch"]),
        "qs16_begin":(API+0xa80,chunks["qs16_begin.bin"]),
        "qs16_call":(API+0xa8b,chunks["qs16_call.bin"]),
        "qs16_end":(API+0xb5c,chunks["qs16_end.bin"]),
    }
    if not all(pieces.values()):
        raise QS16PackageError("Incomplete generated runtime code")
    if len(pieces["loader"])>0x500 or len(pieces["generator"])>0x800 or len(pieces["dispatch"])>0x100:
        raise QS16PackageError("QS16 generated source overran declared code")
    occupied=set()
    image=bytearray(LIMIT-BASE)
    for name,(address,blob) in segments.items():
        if not blob or not BASE<=address or address+len(blob)>LIMIT:
            raise QS16PackageError("Illegal PRG segment: "+name)
        span=set(range(address,address+len(blob)))
        if span&occupied:
            raise QS16PackageError("Overlapping QS16 PRG: "+name)
        occupied|=span
        image[address-BASE:address-BASE+len(blob)]=blob
    if len(table)!=524284:
        raise QS16PackageError("QS16 quarter-square table truncated")
    binary=bytes((BASE&255,BASE>>8))+bytes(image)
    report={
        "schema":"qs16-independent-reu-table-generator-candidate-v1",
        "status":"SOURCE_BUILT_REU_GENERATOR_NOT_NATIVE_OR_GLOBAL_LINKER_QUALIFIED",
        "public_exports":{n:"$%04X"%symbols[n] for n in PUBLIC},
        "claims":claims,"capacity_kib":capacity,
        "table_banks":list(range(bank,bank+8)),
        "qs16_record_count":131071,"generated_reu_bytes":524288,
        "expected_table_sha256":hashlib.sha256(table).hexdigest(),
        "source_sha256":{
            str(LOADER_SOURCE):loader_sha,
            str(GENERATOR_SOURCE):generator_sha,
            **runtime["source_hashes"],
        },
        "segments":{n:{"address":"$%04X"%a,"bytes":len(blob),
                       "sha256":hashlib.sha256(blob).hexdigest()}
                    for n,(a,blob) in segments.items()},
        "prg_sha256":hashlib.sha256(binary).hexdigest(),
        "requires_successful_install":True,
        "reu_native_qualified":False,"mixed_selective_qualified":False,
        "legacy_reu_image_needed":False,
    }
    return report,binary
