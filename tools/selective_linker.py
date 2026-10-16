#!/usr/bin/env python3
"""Source-only linker for a deliberately small, qualified 16-bit arithmetic subset.

Only published independently relocatable sources are eligible; no full-profile
image, fixed-address source mirror or unverified record is linked.
"""
from __future__ import annotations
import hashlib
import os
import tempfile
import itertools
import json
from pathlib import Path
import re
from mini6502 import Assembler
import selective_atan2 as atan2
import selective_fast_umul8 as fast8
import selective_fast_umul16 as fast16
import selective_umul8_v1 as v1umul8
import selective_seek8 as seek8
import selective_seek16 as seek16
import selective_speed
import selective_speed_umul16
import selective_speed_umod8
import selective_speed_udiv8
import selective_isqrt16 as sqrt16
import selective_trig8 as trig8
import selective_dist8_accurate as dist8tab
import selective_smul8 as smul8tab

ROOT = Path(__file__).resolve().parents[1]
MODULES = {
    "MATH_SEEK16_INIT": {
        "link:generated-dda": {
            "source": "routines/movement/seek_u16_u8_dda.asm",
            "segments": (("KERNEL_CODE", 898),),
            "entry": "seek16_init", "zp": 0, "scratch": 19,
            "persistent_state": 248, "state_family": "seek16",
            "share_producer": "seek16-dda", "multi_entry": True,
            "seek16": True, "operand_layout": "seek16",
            "provenance": "RAM-input relocation of eight-slot, 16-bit-X SEEK16 DDA engine with four entry points",
        },
    },
    "MATH_SEEK16_STEP": {
        "link:generated-dda": {
            "source": "routines/movement/seek_u16_u8_dda.asm",
            "segments": (("KERNEL_CODE", 898),),
            "entry": "seek16_step", "zp": 0, "scratch": 19,
            "persistent_state": 248, "state_family": "seek16",
            "share_producer": "seek16-dda", "multi_entry": True,
            "seek16": True, "operand_layout": "seek16",
            "provenance": "RAM-input relocation of eight-slot, 16-bit-X SEEK16 DDA engine with four entry points",
        },
    },
    "MATH_SEEK16_STEP_INT": {
        "link:generated-dda": {
            "source": "routines/movement/seek_u16_u8_dda.asm",
            "segments": (("KERNEL_CODE", 898),),
            "entry": "seek16_step_int", "zp": 0, "scratch": 19,
            "persistent_state": 248, "state_family": "seek16",
            "share_producer": "seek16-dda", "multi_entry": True,
            "seek16": True, "operand_layout": "seek16",
            "provenance": "RAM-input relocation of eight-slot, 16-bit-X SEEK16 DDA engine with four entry points",
        },
    },
    "MATH_SEEK16_STEP1": {
        "link:generated-dda": {
            "source": "routines/movement/seek_u16_u8_dda.asm",
            "segments": (("KERNEL_CODE", 898),),
            "entry": "seek16_step1", "zp": 0, "scratch": 19,
            "persistent_state": 248, "state_family": "seek16",
            "share_producer": "seek16-dda", "multi_entry": True,
            "seek16": True, "operand_layout": "seek16",
            "provenance": "RAM-input relocation of eight-slot, 16-bit-X SEEK16 DDA engine with four entry points",
        },
    },
    "MATH_SEEK8_INIT": {
        "link:generated-dda": {
            "source": "routines/movement/seek_u8_u8_dda.asm",
            "segments": (("KERNEL_CODE", 651),),
            "entry": "seek8_init", "zp": 0, "scratch": 19,
            "persistent_state": 160, "state_family": "seek8",
            "share_producer": "seek8-dda", "multi_entry": True,
            "seek8": True, "operand_layout": "seek8",
            "provenance": "RAM-input relocation of generated eight-slot SEEK8 engine; four distinct exported entry points",
        },
    },
    "MATH_SEEK8_STEP": {
        "link:generated-dda": {
            "source": "routines/movement/seek_u8_u8_dda.asm",
            "segments": (("KERNEL_CODE", 651),),
            "entry": "seek8_step", "zp": 0, "scratch": 19,
            "persistent_state": 160, "state_family": "seek8",
            "share_producer": "seek8-dda", "multi_entry": True,
            "seek8": True, "operand_layout": "seek8",
            "provenance": "RAM-input relocation of generated eight-slot SEEK8 engine; four distinct exported entry points",
        },
    },
    "MATH_SEEK8_STEP_INT": {
        "link:generated-dda": {
            "source": "routines/movement/seek_u8_u8_dda.asm",
            "segments": (("KERNEL_CODE", 651),),
            "entry": "seek8_step_int", "zp": 0, "scratch": 19,
            "persistent_state": 160, "state_family": "seek8",
            "share_producer": "seek8-dda", "multi_entry": True,
            "seek8": True, "operand_layout": "seek8",
            "provenance": "RAM-input relocation of generated eight-slot SEEK8 engine; four distinct exported entry points",
        },
    },
    "MATH_SEEK8_STEP1": {
        "link:generated-dda": {
            "source": "routines/movement/seek_u8_u8_dda.asm",
            "segments": (("KERNEL_CODE", 651),),
            "entry": "seek8_step1", "zp": 0, "scratch": 19,
            "persistent_state": 160, "state_family": "seek8",
            "share_producer": "seek8-dda", "multi_entry": True,
            "seek8": True, "operand_layout": "seek8",
            "provenance": "RAM-input relocation of generated eight-slot SEEK8 engine; four distinct exported entry points",
        },
    },
    "MATH_UMOD8": {
        "link:v1-fast-fallback": {
            "source": "routines/modulo/umod8_v1_hybrid.asm",
            "segments": (("KERNEL_CODE", 157),),
            "entry": "FAST_UMOD8_V1", "zp": 2, "scratch": 0,
            "requires_writable_code": True, "umod8_v1": True,
            "provenance": "Original V1 fast >=32 divide and small-divisor SMC fallback, Q preserved",
        },
        "link:v2-unrolled-fallback": {
            "source": "routines/modulo/umod8_v2_fast.asm",
            "segments": (("KERNEL_CODE", 229),),
            "entry": "FAST_UMOD8_V2", "zp": 2, "scratch": 0,
            "requires_writable_code": True, "umod8_extra": True,
            "provenance": "Original V2 >=24 fast subtraction and 15-step SMC small-divisor fallback; Q preserved",
        },
        "link:v5-unrolled-hybrid": {
            "source": "routines/modulo/umod8_v5_hybrid.asm",
            "segments": (("KERNEL_CODE", 205),),
            "entry": "FAST_UMOD8_V5", "zp": 2, "scratch": 0,
            "requires_writable_code": True, "umod8_extra": True,
            "provenance": "Original V5 >=32 fast subtraction and 15-step SMC small-divisor fallback; Q preserved",
        },
    },
    "MATH_SMUL8": {
        "link:v1-resident-smc": {
            "source": "routines/multiply/smul8_v1_smc.asm",
            "segments": (("KERNEL_CODE", 46),),
            "entry": "FAST_SMUL8_V1", "zp": 0, "scratch": 0,
            "operand_layout": "xyz", "smul8_v1": True,
            "requires_writable_code": True,
            "provenance": "46-byte original V1-V5 SMC producer; exact four 511-entry table pages",
        },
    },
    "MATH_SDIV8": {
        "link:v1-shared-producer": {
            "source": "routines/divide/sdiv8_v1_resident.asm",
            "segments": (("KERNEL_CODE", 530),),
            "entry": "FAST_SDIV8_V1", "zp": 1, "scratch": 0,
            "share_producer": "v1-signed-division8",
            "provenance": "Exact V1 shared SDIV8/SMOD8 producer with zero stub",
            "sdiv8_v1": True,
        },
    },
    "MATH_SMOD8": {
        "link:v1-shared-producer": {
            "source": "routines/divide/sdiv8_v1_resident.asm",
            "segments": (("KERNEL_CODE", 530),),
            "entry": "FAST_SDIV8_V1", "zp": 1, "scratch": 0,
            "share_producer": "v1-signed-division8",
            "provenance": "Exact V1 alias of SDIV8 public producer; Q and R both written",
            "sdiv8_v1": True,
        },
    },
    "MATH_SIN8": {
        "link:resident-shared-table": {
            "source": "routines/trig/sin8_shared.asm",
            "segments": (("KERNEL_CODE", 11),),
            "entry": "FAST_SIN8", "zp": 0, "scratch": 0,
            "trig8": True, "operand_layout": "trig-xz",
            "provenance": "V1-V5 exact 256-byte shared sine table, original 11-byte kernel",
        },
    },
    "MATH_COS8": {
        "link:resident-shared-table": {
            "source": "routines/trig/cos8_shared.asm",
            "segments": (("KERNEL_CODE", 15),),
            "entry": "FAST_COS8", "zp": 0, "scratch": 0,
            "trig8": True, "operand_layout": "trig-xz",
            "provenance": "V1-V5 identical lookup table, original 15-byte quarter-cycle phase shift",
        },
    },
    "MATH_SINCOS8": {
        "link:resident-shared-table": {
            "source": "routines/trig/sincos8_shared.asm",
            "segments": (("KERNEL_CODE", 22),),
            "entry": "FAST_SINCOS8", "zp": 0, "scratch": 0,
            "trig8": True, "operand_layout": "trig-xz",
            "provenance": "V1-V5 identical lookup table, original 22-byte dual-output kernel",
        },
    },
    "MATH_UDIV8": {
        "link:v1-resident-fast": {
            "source": "routines/divide/udiv8_v1_resident.asm",
            "segments": (("KERNEL_CODE", 294),),
            "entry": "FAST_UDIV8_V1", "zp": 1, "scratch": 0,
            "provenance": "Exact V1 125-instruction UDIV8 fast chain, trampoline omitted",
            "udiv8_v1": True,
        },
        "link:v2-v5-fast": {
            "source": "routines/divide/udiv8_v2v5_fast.asm",
            "segments": (("KERNEL_CODE", 430),),
            "entry": "FAST_UDIV8_V2V5", "zp": 1, "scratch": 0,
            "udiv8_v2v5": True,
            "provenance": "Byte-identical V2 and V5 original 430-byte branch-chain producer; no REU",
        },
    },
    "MATH_UDIV16": {
        "link:biased": {
            "source": "routines/standalone_lab/portable/div_u16_biased.asm",
            "segments": (("KERNEL_CODE", 323),),
            "entry": "FAST_UDIV16_BIASED", "zp": 2, "scratch": 0,
        },
    },
    "MATH_UMUL8": {
        "link:v1-resident-fast": {
            "source": "routines/multiply/umul8_v1_original.asm",
            "segments": (("KERNEL_CODE", 51), ("Q_LO", 511), ("Q_HI", 511)),
            "entry": "FAST_UMUL8_V1", "zp": 4, "scratch": 0,
            "operand_layout": "xyz", "umul8_v1": True,
            "provenance": "Original V1 22-byte entry plus 29-byte helper, identical 511-entry quarter-square lookup pages",
        },
        "link:compact-zerozp": {
            "source": "routines/multiply/umul8_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 60),),
            "entry": "FAST_UMUL8_COMPACT", "zp": 0, "scratch": 3,
            "operand_layout": "xyz",
        },
        "link:quarter-square": {
            "source": "routines/multiply/umul8_quartersquare.asm",
            "segments": (("KERNEL_CODE", 73), ("Q_LO", 511), ("Q_HI", 511)),
            "entry": "FAST_UMUL8_QUARTERSQUARE", "zp": 0, "scratch": 2,
            "operand_layout": "xyz", "fast_umul8": True,
        },
    },
    "MATH_UMUL16": {
        "link:compact-zerozp": {
            "source": "routines/multiply/umul16_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 108),),
            "entry": "FAST_UMUL16_COMPACT", "zp": 0, "scratch": 6,
            "operand_layout": "xyz",
        },
        "link:quarter-square": {
            "source": "routines/multiply/umul16_quartersquare.asm",
            "segments": (("KERNEL_CODE", 233), ("Q_LO", 511), ("Q_HI", 511)),
            "entry": "FAST_UMUL16_QUARTERSQUARE", "zp": 0, "scratch": 4,
            "operand_layout": "xyz", "fast_umul16": True,
        },
    },
    "MATH_UMOD16": {
        "link:biased": {
            "source": "routines/standalone_lab/portable/mod_u16_biased_carry.asm",
            "segments": (("KERNEL_CODE", 244), ("KERNEL_ADAPTER", 18)),
            "entry": "FAST_UMOD16_PUBLIC", "zp": 2, "scratch": 0,
        },
        "link:direct-zerozp": {
            "source": "routines/standalone_lab/portable/mod_u16_direct_zerozp.asm",
            "segments": (("KERNEL_TABLE", 16), ("KERNEL_CODE", 945),
                         ("KERNEL_ADAPTER", 15)),
            "entry": "FAST_UMOD16_DIRECT_PUBLIC", "zp": 0, "scratch": 2,
        },
    },
    "MATH_UDIV32_32": {
        "link:zptail": {
            "source": "routines/standalone_lab/portable/div_u32_zptail.asm",
            "segments": (("KERNEL_CODE", 325), ("KERNEL_AUX", 219)),
            "entry": "FAST_UDIV32_PUBLIC", "zp": 4, "scratch": 0,
        },
        "link:aligned-zerozp": {
            "source": "routines/standalone_lab/portable/div_u32_aligned_nozp.asm",
            "segments": (("KERNEL_CODE", 325), ("KERNEL_AUX", 251)),
            "entry": "FAST_UDIV32_PUBLIC", "zp": 0, "scratch": 4,
        },
    },
    "MATH_ATAN2_8": {
        "link:compact": {
            "source": "routines/atan2/atan2_compact_opt.asm",
            "segments": (("KERNEL_CODE", 94), ("LOGTAB", 256),
                         ("ATANTAB", 256)),
            "entry": "atan2", "zp": 0, "scratch": 0, "atan2": "compact",
        },
        "link:sum-fast": {
            "source": "routines/atan2/atan2_sum_fast.asm",
            "segments": (("KERNEL_CODE", 85), ("LOGX", 256),
                         ("LOGY", 256), ("QPOS", 256), ("QNEG", 256)),
            "entry": "atan2", "zp": 0, "scratch": 0, "atan2": "sum-fast",
        },
    },
    "MATH_DIST8_ACCURATE": {
        "link:v1-ram-tables": {
            "source": "routines/game/dist8_accurate_v1_ram.asm",
            "segments": (("KERNEL_CODE", 66),),
            "entry": "FAST_DIST8_ACCURATE", "zp": 0, "scratch": 2,
            "operand_layout": "xyz", "dist8_accurate": True,
            "provenance": "Original V1 accurate-distance two-table lookup with RAM abs/sort",
        },
        "link:v2-zp-tables": {
            "source": "routines/game/dist8_accurate_v2_zp.asm",
            "segments": (("KERNEL_CODE", 58),),
            "entry": "FAST_DIST8_ACCURATE", "zp": 2, "scratch": 0,
            "operand_layout": "xyz", "dist8_accurate": True,
            "provenance": "Original V2 accurate-distance two-table lookup with ZP abs/sort",
        },
    },
    "MATH_DIST8_FAST": {
        "link:resident-approx": {
            "source": "routines/game/dist8_fast.asm",
            "segments": (("KERNEL_CODE", 61),),
            "entry": "FAST_DIST8_FAST", "zp": 0, "scratch": 2,
            "operand_layout": "xyz", "dist8": True,
            "provenance": "V1 fast signed-8 abs/max/min approximation; resident trampoline removed",
        },
    },
    "MATH_ISQRT16": {
        "link:square-table": {
            "source": "routines/roots/isqrt16_square_table.asm",
            "segments": (("KERNEL_CODE", 38), ("SQ_LO", 256),
                         ("SQ_HI", 256), ("SEED", 256)),
            "entry": "FAST_ISQRT16_TABLE", "zp": 0, "scratch": 0,
            "isqrt16": True, "operand_layout": "nz",
            "provenance": "V1/V2/V5 16-bit square-lookup kernel; tables regenerated",
        },
    },
    "MATH_UMOD32_32": {
        "link:aligned-zerozp": {
            "source": "routines/standalone_lab/portable/mod_u32_aligned_carry.asm",
            "segments": (("KERNEL_CODE", 250), ("KERNEL_AUX", 225),
                         ("KERNEL_ADAPTER", 21)),
            "entry": "FAST_UMOD32_ALIGNED_PUBLIC", "zp": 0, "scratch": 4,
        },
    },
}

class LinkError(ValueError):
    pass


def available_variants(root=ROOT):
    result = {}
    for api, variants in MODULES.items():
        result[api] = []
        for ident, mod in variants.items():
            result[api].append({
                "id": ident, "kind": "selective-source-module",
                "build_targets": ["c64"],
                "source_path": mod["source"],
                "source_sha256": hashlib.sha256(
                    (root / mod["source"]).read_bytes()).hexdigest(),
                "dependency_sha256": ({
                    "routines/atan2/tables.py": hashlib.sha256(
                        (root / "routines/atan2/tables.py").read_bytes()).hexdigest()
                } if "atan2" in mod else {
                    "tools/selective_fast_umul8.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul8.py").read_bytes()).hexdigest()
                } if mod.get("fast_umul8") else {
                    "tools/selective_umul8_v1.py": hashlib.sha256(
                        (root / "tools/selective_umul8_v1.py").read_bytes()).hexdigest(),
                } if mod.get("umul8_v1") else {
                    "tools/selective_seek8.py": hashlib.sha256(
                        (root / "tools/selective_seek8.py").read_bytes()).hexdigest(),
                    "tools/seek_kernel.py": hashlib.sha256(
                        (root / "tools/seek_kernel.py").read_bytes()).hexdigest(),
                } if mod.get("seek8") else {
                    "tools/selective_seek16.py": hashlib.sha256(
                        (root / "tools/selective_seek16.py").read_bytes()).hexdigest(),
                    "tools/seek_kernel.py": hashlib.sha256(
                        (root / "tools/seek_kernel.py").read_bytes()).hexdigest(),
                } if mod.get("seek16") else {
                    "tools/selective_fast_umul8.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul8.py").read_bytes()).hexdigest(),
                    "tools/selective_fast_umul16.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul16.py").read_bytes()).hexdigest(),
                } if mod.get("fast_umul16") else {
                    "tools/selective_isqrt16.py": hashlib.sha256(
                        (root / "tools/selective_isqrt16.py").read_bytes()).hexdigest()
                } if mod.get("isqrt16") else {
                    "tools/selective_trig8.py": hashlib.sha256(
                        (root / "tools/selective_trig8.py").read_bytes()).hexdigest()
                } if mod.get("trig8") else {
                    "tools/selective_dist8_accurate.py": hashlib.sha256(
                        (root / "tools/selective_dist8_accurate.py").read_bytes()).hexdigest()
                } if mod.get("dist8_accurate") else {
                    "tools/selective_smul8.py": hashlib.sha256(
                        (root / "tools/selective_smul8.py").read_bytes()).hexdigest(),
                } if mod.get("smul8_v1") else {}),
                "historical_provenance": mod.get("provenance"),
                "requires_writable_code": bool(mod.get("requires_writable_code")),
                "mean_cycles_reported": "",
                "zp_bytes_reported": mod["zp"],
                "stack_page_bytes_reported": 0,
                "validation_path": (
                    "tools/test_selective_umod8_variants.py" if mod.get("umod8_extra") else
                    "tools/test_selective_umod8.py" if mod.get("umod8_v1") else
                    "tools/test_selective_smul8.py" if mod.get("smul8_v1") else
                    "tools/test_selective_fast_umul16.py" if mod.get("fast_umul16") else
                    "tools/test_selective_dist8_accurate.py" if mod.get("dist8_accurate") else
                    "tools/test_selective_trig8.py" if mod.get("trig8") else
                    "tools/test_selective_sdiv8.py" if mod.get("sdiv8_v1") else
                    "tools/test_selective_udiv8_v2v5.py" if mod.get("udiv8_v2v5") else
                    "tools/test_selective_udiv8.py" if mod.get("udiv8_v1") else
                    "tools/test_selective_dist8.py" if mod.get("dist8") else
                    "tools/test_selective_isqrt16.py" if mod.get("isqrt16") else
                    "tools/test_selective_seek16.py" if mod.get("seek16") else
                    "tools/test_selective_seek8.py" if mod.get("seek8") else
                    "tools/test_selective_umul8_v1.py" if mod.get("umul8_v1") else
                    "tools/test_selective_fast_umul8.py" if mod.get("fast_umul8") else
                    "tools/test_selective_multiply.py"
                    if mod.get("operand_layout") == "xyz" else
                    "routines/atan2/validate_optimized.py" if "atan2" in mod else
                    "routines/standalone_lab/portable/verify.py"),
                "qualification": ("historical fast source port; CPU and native VICE gates"
                                  if (mod.get("umod8_v1") or mod.get("umod8_extra")) or mod.get("smul8_v1") or mod.get("umul8_v1") or mod.get("seek8") or mod.get("seek16") or mod.get("sdiv8_v1") or mod.get("dist8_accurate") or mod.get("trig8") or mod.get("udiv8_v2v5") or mod.get("udiv8_v1") or mod.get("dist8") or mod.get("isqrt16") else
                                  "experimental compact source; CPU and native validation"
                                  if mod.get("operand_layout") == "xyz" else
                                  "portable source; mixed-call qualification"),
                "notes": ("Original byte-identical V2/V5 430-byte unrestricted UDIV8 Q/R fast producer; no REU, 1 ZP byte"
                          if mod.get("udiv8_v2v5") else
                          "Original V2/V5 unrolled fast/fallback U8 remainder producer, "
                          "two zero-page bytes and writable immediate operands; Q untouched"
                          if mod.get("umod8_extra") else
                          "Original V1 157-byte UMOD8 fast/low-divisor fallback; "
                          "2 zero-page scratch and two writable immediate operands, Q untouched"
                          if (mod.get("umod8_v1") or mod.get("umod8_extra")) else
                          "Original 46-byte writable-RAM self-modifying signed 8x8; "
                          "four exact V1-V5 511-byte table pages, zero ZP/scratch"
                          if mod.get("smul8_v1") else
                          "Original V1 signed 8-bit Q/R producer; two APIs share a single 530-byte kernel, one ZP byte"
                          if mod.get("sdiv8_v1") else
                          "Historical V1/V2 max/min lookup with one shared 512-byte table pair; "
                          "variant-dependent 2 scratch RAM or 2 ZP bytes"
                          if mod.get("dist8_accurate") else
                          "Original 8-bit trig code with one page-aligned 256-byte exact sine table; "
                          "shared across SIN8/COS8/SINCOS8 in one binary, zero scratch/ZP"
                          if mod.get("trig8") else
                          "294-byte V1 8-bit quotient/remainder chain, one ZP byte, no table"
                          if mod.get("udiv8_v1") else
                          "61-byte trampoline-free V1 signed-distance approximation, "
                          "two private scratch bytes and zero ZP"
                          if mod.get("dist8") else
                          "38-byte V1/V2/V5 ISQRT16 descending square-lookup kernel, "
                          "768 generated aligned table bytes and zero ZP"
                          if mod.get("isqrt16") else
                          "73-byte quarter-square 8x8 code and 1022 exact table bytes; 2 RAM scratch, 0 ZP"
                          if mod.get("fast_umul8") else
                          "Original V1 unsigned 8x8 51-byte entry/core and two exact 511-byte lookup pages; 4 ZP, no REU"
                          if mod.get("umul8_v1") else
                          "Generated 651-byte RAM-operand SEEK8 engine; four entries share 160 persistent RAM bytes and 19 init scratch bytes"
                          if mod.get("seek8") else
                          "Generated 898-byte RAM-operand SEEK16 DDA engine; 248 persistent object RAM and 19-byte shared init scratch"
                          if mod.get("seek16") else
                          "Compact portable shift-add multiply; not performance-ranked against table variants"
                          if mod.get("operand_layout") == "xyz" else
                          "Complete page-aligned ATAN2 lookup tables, exhaustive stock-C64 phase certification"
                          if "atan2" in mod else
                          "Standalone source with checked public carry semantics"),
                "resources_reported": {
                    "code_and_table_bytes": sum(s for _, s in mod["segments"]),
                    "scratch_bytes": mod["scratch"],
                    "persistent_state_bytes": mod.get("persistent_state", 0),
                },
                "selective_link_ready": True,
            })
    return result


def address(value, name):
    if isinstance(value, str):
        try:
            value = int(value[1:], 16) if value.startswith("$") else int(value, 0)
        except ValueError as e:
            raise LinkError(name + ": invalid address") from e
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 65535:
        raise LinkError(name + ": invalid 16-bit address")
    return value


def region(name, start, count, zp=False):
    end = start + count - 1
    if count <= 0 or start < 0 or end > (255 if zp else 65535):
        raise LinkError(name + ": region exceeds address space")
    if zp:
        if start < 2:
            raise LinkError(name + ": 6510 processor port collision")
    else:
        if start <= 0x01ff:
            raise LinkError(name + ": overlaps system zero/stack page")
        if start <= 0xdfff and end >= 0xd000:
            raise LinkError(name + ": overlaps I/O region")
        if start <= 0xbfff and end >= 0xa000:
            raise LinkError(name + ": BASIC ROM RAM underlay not supported")
        if end >= 0xe000:
            raise LinkError(name + ": KERNAL ROM RAM underlay not supported")
    return (name, start, end)


def check_nonoverlap(regions):
    for i, (name, start, end) in enumerate(regions):
        for other, a, b in regions[i+1:]:
            if max(start, a) <= min(end, b):
                raise LinkError(name + " overlaps " + other)


def custom_reserved(data, key, zp=False):
    raw = data.get(key, [])
    if not isinstance(raw, list):
        raise LinkError(key + ": expected a list")
    result = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict) or "start" not in item or "end" not in item:
            raise LinkError(key + ": expected objects with start/end")
        first = address(item["start"], key + ".start")
        last = address(item["end"], key + ".end")
        if not first <= last <= (255 if zp else 65535):
            raise LinkError(key + ": inverted or out-of-range reservation")
        name = item.get("name", "reserved_" + str(i))
        if not isinstance(name, str) or not name.strip():
            raise LinkError(key + ": invalid reservation label")
        result.append((name, first, last))
    return result


def shared_identity(item):
    """Identical share-eligible code/data contract; other items are never coalesced."""
    _, ident, spec = item
    key = spec.get("share_producer")
    if not key:
        return None
    return (key, ident, spec["source"], tuple(spec["segments"]),
            None if spec.get("multi_entry") else spec["entry"],
            spec["zp"], spec["scratch"], spec.get("persistent_state", 0))


def unique_code_modules(items):
    """Count/emit genuinely shared producer once while retaining all API exports."""
    physical, seen = [], set()
    for item in items:
        key = shared_identity(item)
        if key is not None and key in seen:
            continue
        if key is not None:
            seen.add(key)
        physical.append(item)
    return physical


def projected_end(start, items):
    """Actual compact PRG span, including aligned table data and trig sharing."""
    cursor = start
    shared_trig = any(mod.get("trig8") for _, _, mod in items)
    shared_dist8 = any(mod.get("dist8_accurate") for _, _, mod in items)
    shared_smul8 = any(mod.get("smul8_v1") for _, _, mod in items)
    for _, _, mod in items:
        if "atan2" in mod:
            _, cursor = atan2.layout(mod["atan2"], cursor)
        elif mod.get("isqrt16"):
            _, cursor = sqrt16.layout(cursor)
        elif mod.get("umul8_v1"):
            _, cursor = v1umul8.layout(cursor)
        else:
            cursor += sum(length for _, length in mod["segments"])
    if shared_trig:
        cursor = trig8.align_page(cursor) + len(trig8.SINE_BYTES)
    if shared_dist8:
        cursor = trig8.align_page(cursor) + len(dist8tab.MAJOR_BYTES) + len(dist8tab.MINOR_BYTES)
    if shared_smul8:
        cursor = smul8tab.align_page(cursor) + smul8tab.ALIGNED_SPAN
    return cursor


def place_modules(items, start):
    """Minimize ATAN2 alignment waste over all attainable modulo-256 offsets.

    One table-aligned module is currently supported. Ordinary kernels have
    unconstrained placement. A 256-state subset-sum DP identifies the globally
    minimum padding at the aligned module's code/table boundary. This remains
    O(256 * number_of_modules), not factorial when the catalog expands.
    """
    aligned = [item for item in items if "atan2" in item[2] or item[2].get("isqrt16") or item[2].get("umul8_v1")]
    ordinary = [item for item in items if "atan2" not in item[2] and not item[2].get("isqrt16") and not item[2].get("umul8_v1")]
    if not aligned:
        return ordinary
    if len(aligned) != 1:
        # Deterministic conservative layout for multiple table-aligned kernels.
        # Exact span is still budgeted; optimal multi-aligned ordering is future work.
        return ordinary + sorted(aligned, key=lambda item: item[0])
    atan = aligned[0]
    code_bytes = (atan2.KINDS[atan[2]["atan2"]]["code_bytes"]
                  if "atan2" in atan[2] else sqrt16.CODE_BYTES
                  if atan[2].get("isqrt16") else v1umul8.CODE_BYTES)
    # Track one deterministic set of indices per possible prefix address.
    # Item order remains stable within the selected prefix and suffix.
    states = {start % 256: ()}
    for i, item in enumerate(ordinary):
        nbytes = sum(length for _, length in item[2]["segments"])
        expanded = dict(states)
        for residue, indices in states.items():
            new_residue = (residue + nbytes) % 256
            candidate = indices + (i,)
            if (new_residue not in expanded or
                    candidate < expanded[new_residue]):
                expanded[new_residue] = candidate
        states = expanded
    best = min(states, key=lambda residue: (
        -(residue + code_bytes) % 256, states[residue]))
    before_indices = set(states[best])
    before = [item for i, item in enumerate(ordinary) if i in before_indices]
    after = [item for i, item in enumerate(ordinary) if i not in before_indices]
    return before + [atan] + after

def pareto_resource_variants(variants):
    """Prune memory-dominated variants only for automatic selection.

    An algorithm using no more code/table bytes, scratch RAM, or zero page
    always has a memory layout no worse after page-padding optimization.
    Performance ranking is intentionally outside this resource-only rule.
    """
    candidates = list(sorted(variants.items()))
    sizes = {
        key: (sum(length for _, length in spec["segments"]),
              spec["scratch"], spec["zp"])
        for key, spec in candidates
    }
    # Pruning is sound only across identical layout classes. All current
    # ATAN2 data segments are full pages, but future emitters may impose
    # other code/table alignment or placement constraints.
    layout_classes = {
        key: (("page-aligned", len(spec["segments"]) - 1)
              if "atan2" in spec or spec.get("isqrt16") or spec.get("umul8_v1")
              else ("contiguous", 0))
        for key, spec in candidates
    }
    keep = {}
    for key, variant in candidates:
        mine = sizes[key]
        dominated = any(
            other != key and
            layout_classes[other] == layout_classes[key] and
            all(a <= b for a, b in zip(sizes[other], mine)) and
            (any(a < b for a, b in zip(sizes[other], mine)) or other < key)
            for other, _ in candidates
        )
        if not dominated:
            keep[key] = variant
    return keep


def state_requirements(modules):
    """Persistent state is neither reusable call scratch nor per-entry duplication."""
    regions = {}
    for mod in modules:
        family = mod.get("state_family")
        if not family:
            continue
        claimed = mod.get("persistent_state")
        if not isinstance(claimed, int) or claimed <= 0:
            raise LinkError("Invalid persistent state requirement")
        if family in regions and regions[family] != claimed:
            raise LinkError("Conflicting persistent state resource contract")
        regions[family] = claimed
    return dict(sorted(regions.items()))


def place_state(state_families, scratch_start, scratch_size):
    cursor = scratch_start + scratch_size
    allocation = {}
    for family, count in state_families.items():
        # Eight sprite slots are indexed by X; 8-byte alignment preserves
        # their documented no-page-cross layout within each field.
        cursor = (cursor + 7) & ~7
        allocation[family] = cursor
        cursor += count
    return allocation, cursor - (scratch_start + scratch_size)


def choose(names, pins, objective, zp_budget, ram_budget=None, code_base=0x8000, cycle_metrics=None, scratch_base=0xc020):
    """Optimize *the whole selection*, sharing nonreentrant scratch ownership."""
    options = []
    for api in names:
        if api not in MODULES:
            raise LinkError(api + ": no qualified selective source yet")
        variants = MODULES[api]
        if api in pins:
            if pins[api] not in variants:
                raise LinkError(api + ": selected variant is not link-ready")
            # An expert pin can select a memory-dominated algorithm for other
            # benefits (e.g. ATAN2 sum-fast's published speed improvement).
            variants = {pins[api]: variants[pins[api]]}
        elif objective != "speed":
            variants = pareto_resource_variants(variants)
        options.append([(api, ident, mod) for ident, mod in sorted(variants.items())])

    if objective == "speed" and not cycle_metrics:
        raise LinkError("Speed selection requires an authenticated same-corpus cycle model")
    best_score = None
    best = None
    for combination in itertools.product(*options):
        zp = max(mod["zp"] for _, _, mod in combination)
        scratch = max(mod["scratch"] for _, _, mod in combination)
        code = projected_end(code_base, place_modules(unique_code_modules(combination), code_base)) - code_base
        _, state_allocated = place_state(
            state_requirements(spec for _, _, spec in combination),
            scratch_base, scratch)
        ram = code + 32 + scratch + state_allocated
        if zp_budget is not None and zp > zp_budget:
            continue
        if ram_budget is not None and ram > ram_budget:
            continue
        # Never combine unrelated benchmark corpora into a fake speed score.
        if objective == "speed":
            try:
                measured_cycles = sum(
                    cycle_metrics[api][ident] for api, ident, _ in combination)
            except KeyError as exc:
                raise LinkError("Selected variants lack a comparable cycle model") from exc
            metric = (measured_cycles, ram, zp)
        elif objective == "zp":
            metric = (zp, ram, code)
        elif objective == "balanced":
            metric = (ram + 8 * zp, ram, zp)
        else:  # size, exactly measured RAM footprint
            metric = (ram, zp, code)
        fingerprint = tuple(ident for _, ident, _ in combination)
        score = (*metric, fingerprint)
        if best_score is None or score < best_score:
            best_score = score
            best = {api: (ident, mod) for api, ident, mod in combination}
    if best is None:
        raise LinkError("No certified variant combination fits RAM/ZP budgets")
    return best

def relocate_source(mod, locations, root):
    src = (root / mod["source"]).read_text(encoding="utf-8")
    used = {k for k, _ in mod["segments"]}
    if (mod.get("umod8_v1") or mod.get("umod8_extra")):
        used |= {"INPUT_NUM", "INPUT_DIV", "OUTPUT_REM"}
    elif mod.get("smul8_v1"):
        used |= {"INPUT_X", "INPUT_Y", "OUTPUT_Z",
                 "SMUL_LOW_SUM", "SMUL_HIGH_SUM", "SMUL_LOW_COMP", "SMUL_HIGH_COMP"}
    elif mod.get("trig8"):
        used |= {"INPUT_X", "OUTPUT_Z", "SINE_TAB"}
    elif mod.get("dist8_accurate"):
        used |= {"INPUT_X", "INPUT_Y", "OUTPUT_Z", "DIST_MAJOR", "DIST_MINOR"}
    elif mod.get("operand_layout") == "xyz":
        used |= {"INPUT_X", "INPUT_Y", "OUTPUT_Z"}
    else:
        used |= {"INPUT_NUM", "INPUT_DIV", "OUTPUT_QUOT", "OUTPUT_REM"}
    if mod["zp"]:
        used.add("TEMP_ZP")
    if mod["scratch"]:
        used.add("TEMP_RAM")
    for key in used:
        if key not in locations:
            raise LinkError("Missing address symbol: " + key)
        pattern = r"(?m)^" + re.escape(key) + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        src, n = re.subn(pattern, key + " = $%04X" % locations[key], src)
        if n != 1:
            raise LinkError(mod["source"] + ": cannot safely patch " + key)
    return src


def build(plan, outdir, memory=None, root=ROOT):
    if plan.get("schema") != "math-selection-plan-v2":
        raise LinkError("Unsupported selection plan schema; regenerate with current math_builder")
    if plan["target"] != "c64":
        raise LinkError("No qualified selective modules for requested hardware")
    names = [op["api"] for op in plan["operations"]]
    if not names or len(set(names)) != len(names):
        raise LinkError("Selected operations must be nonempty and unique")
    pins = {op["api"]: op["pinned_variant"] for op in plan["operations"]
            if op["pinned_variant"]}
    constraints = plan["constraints"]
    zp_budget = constraints["max_zp_bytes"]
    ram_budget = constraints["max_ram_bytes"]
    memory = memory or {}
    if not isinstance(memory, dict):
        raise LinkError("memory: expected a map")
    supported = {"code_base", "math_io", "zp_base", "scratch_base",
                 "reserved", "zp_reserved"}
    unknown = set(memory) - supported
    if unknown:
        raise LinkError("Unknown memory parameters: " + ", ".join(sorted(unknown)))
    code = address(memory.get("code_base", 0x8000), "code_base")
    io = address(memory.get("math_io", 0xc000), "math_io")
    zb = address(memory.get("zp_base", 0x50), "zp_base")
    sb = address(memory.get("scratch_base", io + 32), "scratch_base")
    cycle_model = None
    per_operation_cycles = None
    if plan["objective"] == "speed":
        if names not in (["MATH_UMUL8"], ["MATH_UMUL16"],
                         ["MATH_UMOD8"], ["MATH_UDIV8"]):
            raise LinkError(
                "Measured automatic speed selection supports UMUL8, UMUL16, "
                "UMOD8 or UDIV8 alone; mixed operations need comparable "
                "certified cycle corpora")
        api = names[0]
        if api == "MATH_UMUL8":
            benchmark, scratch_address = selective_speed.bench_umul8, sb
        elif api == "MATH_UMUL16":
            benchmark, scratch_address = selective_speed_umul16.bench_umul16, sb
        elif api == "MATH_UMOD8":
            benchmark, scratch_address = selective_speed_umod8.bench_umod8, zb
        else:
            benchmark, scratch_address = selective_speed_udiv8.bench_udiv8, zb
        try:
            if api == "MATH_UMUL8":
                cycle_model = benchmark(MODULES[api], code, io, scratch_address, root, zp=zb)
            else:
                cycle_model = benchmark(MODULES[api], code, io, scratch_address, root)
        except (ValueError, OSError, RuntimeError) as exc:
            raise LinkError(api + " cycle-model measurement failed: " + str(exc)) from exc
        per_operation_cycles = {api: cycle_model["mean_cycles"]}
    modules = choose(names, pins, plan["objective"], zp_budget, ram_budget,
                     code_base=code, cycle_metrics=per_operation_cycles,
                     scratch_base=sb)
    zp_bytes = max(mod["zp"] for _, mod in modules.values())
    scratch = max(mod["scratch"] for _, mod in modules.values())
    selected = [(api, ident, mod) for api, (ident, mod) in modules.items()]
    build_order = place_modules(unique_code_modules(selected), code)
    size = projected_end(code, build_order) - code
    states, persistent_allocated = place_state(
        state_requirements(mod for _, mod in modules.values()), sb, scratch)
    occupied_ram = size + 32 + scratch + persistent_allocated
    if zp_budget is not None and zp_bytes > zp_budget:
        raise LinkError("ZP budget too small")
    if ram_budget is not None and occupied_ram > ram_budget:
        raise LinkError("RAM budget too small (including alignment padding and I/O)")
    blocks = [region("code", code, size), region("public I/O", io, 32)]
    if scratch:
        blocks.append(region("scratch", sb, scratch))
    for family, state_start in states.items():
        blocks.append(region("persistent " + family, state_start,
                             state_requirements(mod for _, mod in modules.values())[family]))
    main_reserved = custom_reserved(memory, "reserved")
    zp_reserved = custom_reserved(memory, "zp_reserved", zp=True)
    check_nonoverlap(blocks + main_reserved)
    if zp_bytes:
        check_nonoverlap([region("scratch ZP", zb, zp_bytes, zp=True)] + zp_reserved)

    constants = {
        "INPUT_NUM": io + 16, "INPUT_DIV": io + 20,
        "OUTPUT_QUOT": io + 24, "OUTPUT_REM": io + 28,
        "INPUT_X": io, "INPUT_Y": io + 4, "OUTPUT_Z": io + 8,
    }
    # Source-locked tables are shared per family and placed after all code.
    # DIST8's two pages follow the (optional) one-page sine table.
    has_trig = any(mod.get("trig8") for _, mod in modules.values())
    has_dist8 = any(mod.get("dist8_accurate") for _, mod in modules.values())
    has_smul8 = any(mod.get("smul8_v1") for _, mod in modules.values())
    smul8_span = smul8tab.ALIGNED_SPAN if has_smul8 else 0
    smul8_start = code + size - smul8_span if has_smul8 else None
    dist_table_bytes = (len(dist8tab.MAJOR_BYTES) + len(dist8tab.MINOR_BYTES)
                        if has_dist8 else 0)
    shared_dist_page = code + size - smul8_span - dist_table_bytes if has_dist8 else None
    shared_trig_page = (code + size - smul8_span - dist_table_bytes - len(trig8.SINE_BYTES)
                        if has_trig else None)
    if has_trig:
        if shared_trig_page & 255:
            raise LinkError("Trig shared table was not placed on a page boundary")
        constants["SINE_TAB"] = shared_trig_page
    if has_dist8:
        if shared_dist_page & 255:
            raise LinkError("DIST8 shared table pages were not aligned")
        constants["DIST_MAJOR"] = shared_dist_page
        constants["DIST_MINOR"] = shared_dist_page + len(dist8tab.MAJOR_BYTES)
    if has_smul8:
        if smul8_start & 255:
            raise LinkError("SMUL8 self-modifying operand tables must start at page boundary")
        constants.update({
            "SMUL_LOW_SUM": smul8_start,
            "SMUL_HIGH_SUM": smul8_start + smul8tab.PAGE_STRIDE,
            "SMUL_LOW_COMP": smul8_start + 2*smul8tab.PAGE_STRIDE,
            "SMUL_HIGH_COMP": smul8_start + 3*smul8tab.PAGE_STRIDE,
        })
    if zp_bytes:
        constants["TEMP_ZP"] = zb
    if scratch:
        constants["TEMP_RAM"] = sb
    binary = {}
    entries, detail = {}, []
    physical_labels = {}
    pc = code
    for api, ident, module in build_order:
        operation = next(op for op in plan["operations"] if op["api"] == api)
        link_sources = [v for v in operation["available_source_variants"]
                        if v["id"] == ident and v["selective_link_ready"]]
        if len(link_sources) != 1:
            raise LinkError(api + ": selected source not authorized by plan")
        source_path = (root / module["source"]).resolve()
        if not source_path.is_relative_to(root.resolve()):
            raise LinkError(api + ": source escapes repository")
        exact_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if exact_digest != link_sources[0]["source_sha256"]:
            raise LinkError(api + ": source changed since selection plan")
        dep_provenance = []
        for dep, digest in link_sources[0].get("dependency_sha256", {}).items():
            dep_path = (root / dep).resolve()
            if not dep_path.is_relative_to(root.resolve()) or not dep_path.is_file():
                raise LinkError(api + ": missing/unsafe source dependency")
            actual_dep_sha = hashlib.sha256(dep_path.read_bytes()).hexdigest()
            if actual_dep_sha != digest:
                raise LinkError(api + ": source dependency changed since selection plan")
            dep_provenance.append({"source_path": dep, "sha256": actual_dep_sha})
        if "atan2" in module and [x["source_path"] for x in dep_provenance] != [
                "routines/atan2/tables.py"]:
            raise LinkError(api + ": ATAN2 table generator provenance missing")
        if module.get("fast_umul8") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_fast_umul8.py"]:
            raise LinkError(api + ": quarter-square table generator provenance missing")
        if module.get("fast_umul16") and set(x["source_path"] for x in dep_provenance) != {
                "tools/selective_fast_umul8.py", "tools/selective_fast_umul16.py"}:
            raise LinkError(api + ": 16-bit quarter-square emitter provenance missing")
        if module.get("isqrt16") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_isqrt16.py"]:
            raise LinkError(api + ": integer-root table generator provenance missing")
        if module.get("trig8") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_trig8.py"]:
            raise LinkError(api + ": shared sine table provenance missing")
        if module.get("dist8_accurate") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_dist8_accurate.py"]:
            raise LinkError(api + ": accurate-distance lookup provenance missing")
        if module.get("umul8_v1") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_umul8_v1.py"]:
            raise LinkError(api + ": V1 unsigned multiply source provenance missing")
        if module.get("seek8") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_seek8.py", "tools/seek_kernel.py"]:
            raise LinkError(api + ": SEEK8 source generator/emitter provenance missing")
        if module.get("seek16") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_seek16.py", "tools/seek_kernel.py"]:
            raise LinkError(api + ": SEEK16 source generator/emitter provenance missing")
        if module.get("smul8_v1") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_smul8.py"]:
            raise LinkError(api + ": signed multiplication table provenance missing")
        locations = dict(constants)
        expected = set()
        ranges = []
        try:
            if "atan2" in module or module.get("fast_umul8") or module.get("fast_umul16") or module.get("isqrt16") or module.get("umul8_v1") or module.get("seek8") or module.get("seek16"):
                if "atan2" in module:
                    machine, entry, ranges, end = atan2.assemble(
                        module["atan2"], pc, io, root)
                elif module.get("isqrt16"):
                    machine, entry, ranges, end = sqrt16.assemble(pc, io, root)
                elif module.get("umul8_v1"):
                    machine, entry, ranges, end = v1umul8.assemble(pc, io, zb, root)
                elif module.get("seek8"):
                    machine, labels, ranges, end = seek8.assemble(
                        pc, io, sb, states["seek8"], root)
                    entry = labels[module["entry"]]
                elif module.get("seek16"):
                    machine, labels, ranges, end = seek16.assemble(
                        pc, io, sb, states["seek16"], root)
                    entry = labels[module["entry"]]
                elif module.get("fast_umul16"):
                    machine, entry, ranges, end = fast16.assemble(pc, io, sb, root)
                else:
                    machine, entry, ranges, end = fast8.assemble(pc, io, sb, root)
                expected = set()
                for seg in ranges:
                    start = int(seg["start"][1:], 16)
                    expected.update(range(start, start + seg["bytes"]))
                if not module.get("seek8") and not module.get("seek16"):
                    labels = {module["entry"]: entry}
                pc = end
            else:
                for seg, length in module["segments"]:
                    locations[seg] = pc
                    ranges.append({"name": seg, "start": "$%04X" % pc, "bytes": length})
                    expected.update(range(pc, pc + length))
                    pc += length
                machine, labels, _ = Assembler().assemble(
                    relocate_source(module, locations, root))
        except Exception as e:
            raise LinkError("Assembly failed for " + api + ": " + str(e)) from e
        if set(machine) != expected:
            raise LinkError(api + ": assembled segment sizes differ from contract")
        if module["entry"] not in labels or labels[module["entry"]] not in machine:
            raise LinkError(api + ": entry label not in assembled image")
        if set(machine) & set(binary):
            raise LinkError(api + ": module overlaps existing code")
        binary.update(machine)
        if shared_identity((api, ident, module)) is not None:
            physical_labels[shared_identity((api, ident, module))] = labels
        entries[api] = labels[module["entry"]]
        detail.append({
            "api": api, "variant": ident, "entry": "$%04X" % entries[api],
            "dependencies": dep_provenance, "scratch_lifetime": "exclusive_call",
            "source": module["source"],
            "sha256": hashlib.sha256((root / module["source"]).read_bytes()).hexdigest(),
            "segments": ranges, "zp_bytes": module["zp"], "scratch_bytes": module["scratch"],
            "persistent_state_bytes": module.get("persistent_state", 0),
            "operand_layout": module.get("operand_layout", "ndqr"),
        })
    # Public API aliases can point at one physically linked historical producer.
    # Every virtual export is separately source/hash-authorized by its own plan.
    shared_owners = {shared_identity(item): item[0] for item in build_order
                     if shared_identity(item) is not None}
    for api, ident, module in selected:
        if api in entries:
            continue
        identity = shared_identity((api, ident, module))
        if identity is None or identity not in shared_owners:
            raise LinkError(api + ": missing shared physical producer")
        owner = shared_owners[identity]
        op = next(op for op in plan["operations"] if op["api"] == api)
        authorized = [v for v in op["available_source_variants"]
                      if v["id"] == ident and v["selective_link_ready"]]
        if len(authorized) != 1:
            raise LinkError(api + ": aliased source not authorized by plan")
        source = (root / module["source"]).read_bytes()
        if authorized[0]["source_sha256"] != hashlib.sha256(source).hexdigest():
            raise LinkError(api + ": aliased source changed since selection plan")
        parent = next(d for d in detail if d["api"] == owner)
        original = next(op for op in plan["operations"] if op["api"] == owner)
        source_qual = next(v for v in original["available_source_variants"]
                           if v["id"] == ident and v["selective_link_ready"])
        if authorized[0].get("dependency_sha256", {}) != source_qual.get("dependency_sha256", {}):
            raise LinkError(api + ": alias dependency provenance differs")
        owner_entries = physical_labels[identity]
        if module["entry"] not in owner_entries:
            raise LinkError(api + ": distinct shared entry missing from linked producer")
        entries[api] = owner_entries[module["entry"]]
        detail.append({**parent, "api": api, "entry": "$%04X" % entries[api],
                       "shared_kernel_of": owner})
    shared_tables = []
    if has_trig:
        if pc > shared_trig_page:
            raise LinkError("Shared sine table overlaps kernel bytes")
        shared_data = trig8.emit(shared_trig_page)
        if set(shared_data) & set(binary):
            raise LinkError("Shared sine table overlaps linked module")
        binary.update(shared_data)
        shared_tables.append({
            "name": "SINE8_SHARED", "start": "$%04X" % shared_trig_page,
            "bytes": len(shared_data),
            "users": sorted(api for api, (ident, mod) in modules.items()
                            if mod.get("trig8")),
        })
        shared_tables[-1]["sha256"] = hashlib.sha256(trig8.SINE_BYTES).hexdigest()
        pc = shared_trig_page + len(shared_data)
    if has_dist8:
        if pc > shared_dist_page:
            raise LinkError("DIST8 shared table pair overlaps previous data")
        shared_data = dist8tab.emit(shared_dist_page)
        if set(shared_data) & set(binary):
            raise LinkError("DIST8 lookup overlaps linked module")
        binary.update(shared_data)
        shared_tables.append({
            "name": "DIST8_ACCURATE_SHARED", "start": "$%04X" % shared_dist_page,
            "bytes": len(shared_data),
            "users": sorted(api for api, (ident, mod) in modules.items()
                            if mod.get("dist8_accurate")),
            "sha256": hashlib.sha256(
                dist8tab.MAJOR_BYTES + dist8tab.MINOR_BYTES).hexdigest(),
        })
        pc = shared_dist_page + len(shared_data)
    if has_smul8:
        if pc > smul8_start:
            raise LinkError("SMUL8 tables overlap linked code or other tables")
        data = smul8tab.emit(smul8_start)
        if set(data) & set(binary):
            raise LinkError("SMUL8 lookup tables overlap other modules")
        binary.update(data)
        shared_tables.append({
            "name": "SMUL8_V1_ORIGINAL_PAGES",
            "start": "$%04X" % smul8_start, "bytes": len(data),
            "users": sorted(api for api, (ident, mod) in modules.items()
                            if mod.get("smul8_v1")),
            "sha256": hashlib.sha256(smul8tab.digest_data()).hexdigest(),
        })
        pc = smul8_start + smul8tab.ALIGNED_SPAN
    if pc != code + size:
        raise LinkError("Incorrect linked image span")
    # ATAN2 lookup pages need page alignment. Gaps are explicit zero-filled
    # PRG padding and are counted in RAM usage, not silently reusable memory.
    padding = size - len(binary)
    if padding < 0 or any(a < code or a >= pc for a in binary):
        raise LinkError("Linked image outside declared span")
    prg = bytes((code & 255, code >> 8)) + bytes(
        binary.get(addr, 0) for addr in range(code, code + size))
    exports = [
        "; Generated selective C64 math library (CLD required; non-reentrant)",
        "; All public inputs preserved; A/X/Y and processor flags may be volatile.",
        "; DIV/MOD: unsigned N/D in MATH_N/MATH_D, quotient/remainder Q/R;",
        "; UDIV8: low byte N/D => low byte Q/R; high bytes unchanged; C=1 on D=0.",
        "; UMOD8: low byte N/D => low byte R ONLY; Q untouched, C=1 if D=0.",
        "; UMOD8 V1 fast/fallback uses two writable immediate operands in RAM.",
        "; SDIV8/SMOD8: signed low byte N/D => signed low Q/R, both outputs written.",
        "; carry set iff D=0. UMOD leaves quotient untouched.",
        "; UMUL8: unsigned 8-bit MATH_X/Y => unsigned 16-bit MATH_Z;",
        "; UMUL16: unsigned 16-bit MATH_X/Y => unsigned 32-bit MATH_Z;",
        "; SMUL8: signed 8-bit X/Y => signed 16-bit Z low/next, C=0.",
        "; SMUL8 uses self-modifying instructions: load into writable RAM, non-reentrant.",
        "; ISQRT16: unsigned MATH_N 16-bit => floor(sqrt(N)) in MATH_Z 16-bit, C=0.",
        "; SIN8: phase in MATH_X low => sine signed byte in MATH_Z low, C=0.",
        "; COS8: phase in MATH_X low => cosine signed byte in MATH_Z low, C=0.",
        "; SINCOS8: phase in MATH_X low => sin/cos in MATH_Z low/next, C=0.",
        "; DIST8_ACCURATE: signed MATH_X/Y low => lookup[max] +",
        "; lookup[min] mod 256 in MATH_Z low, C=0 (exact resident tables).",
        "; DIST8_FAST: signed MATH_X/Y low bytes => max(abs(X),abs(Y)) +",
        "; floor(min(abs(X),abs(Y))/2) mod 256 in MATH_Z low byte, C=0.",
        "; ATAN2_8: signed 8-bit MATH_X/Y low bytes => phase MATH_Z low byte",
        "; and A, C clear. Initial carry ignored.",
        "MATH_X = $%04X" % io, "MATH_Y = $%04X" % (io + 4),
        "MATH_Z = $%04X" % (io + 8),
        "MATH_N = $%04X" % (io + 16), "MATH_D = $%04X" % (io + 20),
        "MATH_Q = $%04X" % (io + 24), "MATH_R = $%04X" % (io + 28),
    ]
    if "seek8" in states:
        exports += [
            "; SEEK8: X=slot 0..7; INIT target MATH_X/MATH_Y, speed MATH_N/N+1.",
            "; Eight persistent object positions, targets and velocities; keep RAM live.",
            "MATH_SEEK8_POS_X = $%04X" % states["seek8"],
            "MATH_SEEK8_POS_Y = $%04X" % (states["seek8"] + 8),
        ]
    if "seek16" in states:
        exports += [
            "; SEEK16: X=slot 0..7; 16-bit target MATH_X, 8-bit Y, speed MATH_N.",
            "; Eight persistent 16-bit X/Y object coordinates; keep RAM live.",
            "MATH_SEEK16_POS_XL = $%04X" % states["seek16"],
            "MATH_SEEK16_POS_XH = $%04X" % (states["seek16"] + 8),
            "MATH_SEEK16_POS_Y = $%04X" % (states["seek16"] + 16),
        ]
    exports += [api + " = $%04X" % addr for api, addr in entries.items()]
    # Preserve the stable typed ABI aliases when generating a tiny library.
    for operation in plan["operations"]:
        canonical = operation["canonical_name"]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", canonical):
            raise LinkError("Unsafe typed operation alias: " + canonical)
        exports.append(canonical + " = " + operation["api"])
    toolchain_paths = ("tools/math_builder.py", "tools/selective_linker.py",
                       "tools/selective_atan2.py", "tools/selective_fast_umul8.py",
                       "tools/selective_speed.py", "tools/selective_isqrt16.py",
                       "tools/selective_fast_umul16.py", "tools/selective_speed_umul16.py",
                       "tools/selective_speed_umod8.py", "tools/selective_speed_udiv8.py",
                       "tools/selective_trig8.py", "tools/selective_dist8_accurate.py",
                       "tools/selective_smul8.py",
                       "tools/selective_seek8.py", "tools/selective_seek16.py",
                       "tools/seek_kernel.py",
                       "tools/mini6502.py")
    toolchain_hashes = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in toolchain_paths
    }
    manifest = {
        "schema": "c64-math-selective-binary-v1",
        "toolchain_sha256": toolchain_hashes,
        "status": "selective_binary_emitted",
        "target": "c64",
        "selection_objective": plan["objective"],
        "selection_basis": ("same-corpus measured CPU-model cycles for " + names[0]
                            if cycle_model else
                            "global code/RAM/ZP resource optimization; cycle-speed not certified"),
        "cycle_model_benchmark": cycle_model,
        "operations": detail,
        "shared_tables": shared_tables,
        "link_order": [api for api, _, _ in build_order],
        "link_exports": sorted(entries),
        "typed_exports": sorted(x["canonical_name"] for x in plan["operations"]),
        "resource_use": {
            "code_and_tables_bytes": len(binary), "image_span_bytes": size,
            "shared_table_bytes": sum(t["bytes"] for t in shared_tables),
            "alignment_padding_bytes": padding, "public_io_bytes": 32,
            "private_ram_scratch_bytes": scratch,
            **({"persistent_state_bytes": sum(state_requirements(
                mod for _, mod in modules.values()).values()),
                "state_alignment_padding_bytes": persistent_allocated - sum(
                state_requirements(mod for _, mod in modules.values()).values())}
               if states else {}),
            "main_ram_total_bytes": occupied_ram, "zero_page_bytes": zp_bytes,
            "persistent_stack_page_bytes": 0,
        },
        "memory_map": {
            "code_start": "$%04X" % code,
            "code_end": "$%04X" % (pc - 1),
            "math_io_start": "$%04X" % io,
            "scratch_start": "$%04X" % sb if scratch else None,
            "persistent_state": {family:"$%04X" % addr for family, addr in states.items()},
            "zp_start": "$%02X" % zb if zp_bytes else None,
            "user_reserved": [dict(name=n, start="$%04X" % a, end="$%04X" % b)
                              for n, a, b in main_reserved],
            "user_zp_reserved": [dict(name=n, start="$%02X" % a, end="$%02X" % b)
                                 for n, a, b in zp_reserved],
        },
        "nonreentrant": True, "rom_underlay_enabled": False,
        "prg_sha256": hashlib.sha256(prg).hexdigest(),
        "note": "New selective binaries require full CPU/native qualification before general release.",
    }
    # All assembly, resource and provenance checks must succeed before any
    # publication. Stage all outputs first; commit the manifest last, as a
    # completion marker for consumers of this experimental build directory.
    outdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".math_stage_", dir=outdir) as temp:
        stage = Path(temp)
        (stage / "math_selective.prg").write_bytes(prg)
        (stage / "math_api.inc").write_text("\n".join(exports) + "\n")
        (stage / "selective_manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n")
        if hashlib.sha256((stage / "math_selective.prg").read_bytes()).hexdigest() != manifest["prg_sha256"]:
            raise LinkError("Staged PRG checksum mismatch")
        for name in ("math_selective.prg", "math_api.inc",
                     "selective_manifest.json"):
            os.replace(stage / name, outdir / name)
    return manifest
