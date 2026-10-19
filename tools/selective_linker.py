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
import math
from functools import lru_cache
import json
from pathlib import Path
import re
from mini6502 import Assembler
import selective_atan2 as atan2
import selective_fast_umul8 as fast8
import selective_smul8_qs_readonly as smul8qs
import selective_fast_umul16 as fast16
import selective_umuldiv16_qs_v2 as muldiv16qs
import selective_smuldiv16_qs_v2 as signed_muldiv16qs
import selective_smul16_quartersquare as qs16signed
import selective_smul16_shr8_quartersquare as qs16shr
import selective_fast31_umul32 as fast31
import selective_v2_fast_umul24 as v2umul24
import selective_umul8_v1 as v1umul8
import selective_seek8 as seek8
import selective_seek16 as seek16
import selective_speed
import selective_speed_smul8 as speed_smul8
import selective_speed_umul16
import selective_speed_umuldiv16_qsv2 as speed_umuldiv16
import selective_speed_smuldiv16_qsv2 as speed_smuldiv16
import selective_speed_smul16 as speed_smul16
import selective_speed_smul16_shr8 as speed_smul16_shr8
import selective_speed_sdiv8_shared as speed_sdiv8_shared
import selective_speed_umul24 as speed_umul24
import selective_speed_smul24 as speed_smul24
import selective_speed_umul16_shr8
import selective_speed_umod8
import selective_speed_udiv8
import selective_speed_isqrt32
import selective_speed_umul32
import selective_speed_smul32
import selective_speed_mul32_ready_shr16 as speed32extras
import selective_speed_u3216 as speed_u3216
import selective_speed_udiv16_shl8 as speed_shl8
import selective_speed_sdiv16_shl8 as speed_signedshl8
import selective_speed_sdiv16_shared as speed_sdiv16shared
import selective_speed_recip16 as speed_recip16
import selective_speed_s3216 as speed_s3216
import selective_speed_s3232 as speed_s3232
import selective_speed_u3232 as speed_u3232
import selective_speed_u24 as speed_u24
import selective_speed_s24 as speed_s24
import selective_speed_umod16 as speed_umod16
import selective_speed_dist8_accurate as speed_dist8_accurate
import selective_speed_dist8_fast as speed_dist8_fast
import selective_speed_atan2 as speed_atan2
import selective_speed_udiv16 as speed_udiv16
import selective_speed_isqrt16 as speed_isqrt16
import selective_hybrid_u3232 as hybrid_u3232
import selective_signed_hybrid_u3232 as signed_u3232
import selective_v2_fast_u3216 as v2u3216
import selective_v2_shifted_u3216 as v2shifted
import selective_v2_signed_shifted16 as signedshift
import selective_v2_signed16_shared as v2signed16
import selective_recip16_threshold as recip_threshold
import selective_recip16_table as recip_table
import research_signed_v2_u3216 as signedv2u3216
import selective_isqrt16 as sqrt16
import selective_trig8 as trig8
import selective_speed_vec2_stock as speed_vec2_stock
import selective_speed_trig8 as speed_trig8
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
        "link:qs-readonly": {
            "source": "routines/multiply/umul8_quartersquare.asm",
            "segments": (("KERNEL_CODE", 73),("Q_LO", 511),("Q_HI", 511),
                         ("SIGNED8_ADAPTER", 64)),
            "entry": "FAST_SMUL8_QS_READONLY", "zp": 0, "scratch": 2,
            "operand_layout": "xyz", "smul8_qs": True,
            "provenance": "Canonical 73-byte unsigned quarter-square 8x8 source, two 511-entry exact Q planes and fixed signed high-byte correction; stock NMOS 6510, read-only, no ZP, two RAM scratch bytes.",
        },
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
    "MATH_SDIV32_32": {
        "link:portable-zerozp": {
            "source": "routines/divide/sdiv32_smod32_zerozp.asm",
            "segments": (("KERNEL_CODE", 412),),
            "entry": "FAST_SDIV32_32_ZEROZP", "zp": 0, "scratch": 9,
            "share_producer": "signed-32by32-portable-zerozp",
            "multi_entry": True, "sdiv32_32_portable": True,
            "provenance": "Portable sign-normalized 32/32 restoring shared Q32/R32 producer, 412 code bytes, 9 ordinary RAM scratch, 0 ZP. Exact signed truncating quotient and N-sign remainder.",
        },
        "link:v2-hybrid-signed": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2880),),
            "entry": "FAST_SDIV32_32_V2MAG", "zp": 12, "scratch": 0,
            "share_producer": "signed-32by32-v2-hybrid-qr",
            "multi_entry": True, "signed_hybrid_u3232": True,
            "provenance": "Signed Q32/R32/C producer composed around the qualified unrestricted V2 low-divisor hybrid, 2880 source-linked executable bytes, 12 call-exclusive ZP, no RAM scratch or tables. Includes 384-byte signed wrapper slot, stable original source hashes, non-reentrant.",
        },
    },
    "MATH_SMOD32_32": {
        "link:portable-zerozp": {
            "source": "routines/divide/sdiv32_smod32_zerozp.asm",
            "segments": (("KERNEL_CODE", 412),),
            "entry": "FAST_SMOD32_32_ZEROZP", "zp": 0, "scratch": 9,
            "share_producer": "signed-32by32-portable-zerozp",
            "multi_entry": True, "sdiv32_32_portable": True,
            "provenance": "Signed SMOD32_32 alias of shared SDIV32_32 Q32/R32 restoring producer; full-width exact R, N/D untouched, no duplicate image.",
        },
        "link:v2-hybrid-signed": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2880),),
            "entry": "FAST_SMOD32_32_V2MAG", "zp": 12, "scratch": 0,
            "share_producer": "signed-32by32-v2-hybrid-qr",
            "multi_entry": True, "signed_hybrid_u3232": True,
            "provenance": "SMOD32_32 aliases the same composed signed hybrid Q32/R32/C public producer; no duplicated code, 12 shared ZP bytes.",
        },
    },
    "MATH_SDIV32_16": {
        "link:portable-zerozp": {
            "source": "routines/divide/sdiv32_16_smod32_16_zerozp.asm",
            "segments": (("KERNEL_CODE", 260),),
            "entry": "FAST_SDIV32_16_ZEROZP", "zp": 0, "scratch": 3,
            "share_producer": "signed-32by16-portable-zerozp",
            "multi_entry": True, "sdiv32_16_portable": True,
            "provenance": "Shared signed N32/D16 exact Q32 signed/R16 numerator-signed, zero-D carry; 260 code/3 scratch/0 ZP, N/D preserved, high R unchanged.",
        },
        "link:v2-signed-magnitude": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2880),),
            "entry": "FAST_SDIV32_16_V2MAG", "zp": 12, "scratch": 0,
            "share_producer": "signed-32by16-v2-magnitude",
            "multi_entry": True, "signed_v2_u3216": True,
            "provenance": "Relocated original V2 unsigned magnitude donor with signed numerator/divisor normalization and correction; complete Q32/R16/C ABI, 2880B code + 12 call-exclusive ZP, NMOS illegal opcodes, non-reentrant.",
        },
    },
    "MATH_SMOD32_16": {
        "link:portable-zerozp": {
            "source": "routines/divide/sdiv32_16_smod32_16_zerozp.asm",
            "segments": (("KERNEL_CODE", 260),),
            "entry": "FAST_SMOD32_16_ZEROZP", "zp": 0, "scratch": 3,
            "share_producer": "signed-32by16-portable-zerozp",
            "multi_entry": True, "sdiv32_16_portable": True,
            "provenance": "SMOD32_16 aliases signed 32/16 public Q32/R16 producer; no duplicated image or N/D clobber.",
        },
        "link:v2-signed-magnitude": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2880),),
            "entry": "FAST_SMOD32_16_V2MAG", "zp": 12, "scratch": 0,
            "share_producer": "signed-32by16-v2-magnitude",
            "multi_entry": True, "signed_v2_u3216": True,
            "provenance": "One canonical signed V2 magnitude Q32/R16/C producer shared by DIV and MOD without a second code island; 12 ZP.",
        },
    },
    "MATH_SDIV24": {
        "link:v3-signed-magnitude": {
            "source": "routines/divide/sdiv24_v3_relocated.asm",
            "segments": (("KERNEL_CODE", 1897),),
            "entry": "FAST_SDIV24_V3", "zp": 9, "scratch": 0,
            "share_producer": "v3-signed24-magnitude-relocated",
            "multi_entry": True, "requires_writable_code": True,
            "sdiv24_v3_relocated": True,
            "provenance": "Exact V3 signed24 magnitude body compacted from three executable islands, 9 private ZP, one relocated SMC opcode, original two public Q/R aliases, no tables/INIT/REU; historical SHA256 c34456837b5f9bd24265d7b3108d71ddb1d7a9575402ef49a58a82fb831ca11c",
        },
        "link:abs-qzero-guard": {
            "source": "routines/divide/sdiv24_smod24_qzero_zerozp.asm",
            "segments": (("KERNEL_CODE", 387),),
            "entry": "FAST_SDIV24_QZERO", "zp": 0, "scratch": 7,
            "share_producer": "signed-24by24-abs-qzero-zerozp",
            "multi_entry": True, "sdiv24_qzero": True,
            "provenance": "Independent signed 24/24 Q32/R32 public producer; early exact |N|<|D| quotient-zero exit and portable 24-round fallback; 387 B code, 7 RAM scratch, zero ZP.",
        },
        "link:portable-zerozp": {
            "source": "routines/divide/sdiv24_smod24_zerozp.asm",
            "segments": (("KERNEL_CODE", 325),),
            "entry": "FAST_SDIV24_ZEROZP", "zp": 0, "scratch": 7,
            "share_producer": "signed-24by24-portable-zerozp",
            "multi_entry": True, "sdiv24_portable": True,
            "provenance": "Shared signed 24/24 quotient and modulo exact wrap/truncation, signed R; 325 code, 7 ordinary RAM scratch, zero ZP, input and high Q/R preserved.",
        },
    },
    "MATH_SMOD24": {
        "link:v3-signed-magnitude": {
            "source": "routines/divide/sdiv24_v3_relocated.asm",
            "segments": (("KERNEL_CODE", 1897),),
            "entry": "FAST_SMOD24_V3", "zp": 9, "scratch": 0,
            "share_producer": "v3-signed24-magnitude-relocated",
            "multi_entry": True, "requires_writable_code": True,
            "sdiv24_v3_relocated": True,
            "provenance": "Exact V3 signed24 magnitude body compacted from three executable islands, 9 private ZP, one relocated SMC opcode, original two public Q/R aliases, no tables/INIT/REU; historical SHA256 c34456837b5f9bd24265d7b3108d71ddb1d7a9575402ef49a58a82fb831ca11c",
        },
        "link:abs-qzero-guard": {
            "source": "routines/divide/sdiv24_smod24_qzero_zerozp.asm",
            "segments": (("KERNEL_CODE", 387),),
            "entry": "FAST_SMOD24_QZERO", "zp": 0, "scratch": 7,
            "share_producer": "signed-24by24-abs-qzero-zerozp",
            "multi_entry": True, "sdiv24_qzero": True,
            "provenance": "Independent signed 24/24 Q32/R32 public producer; early exact |N|<|D| quotient-zero exit and portable 24-round fallback; 387 B code, 7 RAM scratch, zero ZP.",
        },
        "link:portable-zerozp": {
            "source": "routines/divide/sdiv24_smod24_zerozp.asm",
            "segments": (("KERNEL_CODE", 325),),
            "entry": "FAST_SMOD24_ZEROZP", "zp": 0, "scratch": 7,
            "share_producer": "signed-24by24-portable-zerozp",
            "multi_entry": True, "sdiv24_portable": True,
            "provenance": "SMOD24 alias to the signed 24/24 quotient+remainder kernel; code shares with SDIV24 and writes public R/Q.",
        },
    },
    "MATH_SDIV16_SHL8": {
        "link:v2-signed-shifted-public": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2624),),
            "entry": "FAST_SDIV16_SHL8_V2", "zp": 12, "scratch": 0,
            "v2_signed_shifted16": True,
            "provenance": "Historical native V2 unsigned 32/16 producer plus direct signed N16<<8 magnitude adapter; signed Q24/R16/C, unchanged inputs/sentinels, 12 non-port ZP, no generic bitloop; D=0 and signed overflow wraps.",
        },
        "link:portable-zerozp": {
            "source": "routines/divide/sdiv16_shl8_zerozp.asm",
            "segments": (("KERNEL_CODE", 237),),
            "entry": "FAST_SDIV16_SHL8_ZEROZP", "zp": 0, "scratch": 3,
            "sdiv16_shl8_portable": True,
            "provenance": "Signed fixed-point (N16<<8)/D16 => signed Q24/R16, truncation to zero and numerator-signed remainder; 237B code, 3 RAM scratch, 0 ZP, no writable code.",
        },
    },
    "MATH_SDIV16": {
        "link:v2-signed-shared": {
            "source": "routines/divide/udiv16_v2_zerozp.asm",
            "segments": (("KERNEL_CODE", 1481),("SIGNED_ADAPTER", 224)),
            "entry": "FAST_SDIV16_V2_SHARED", "zp": 0, "scratch": 8,
            "share_producer": "signed-16by16-v2-direct", "multi_entry": True,
            "signed16_v2_shared": True,
            "provenance": "Historical canonical V2 direct 16/16 source with signed Q/R/C adapter and one physical shared producer; zero ZP, no REU/SMC/INIT.",
        },
        "link:portable-zerozp": {
            "source": "routines/divide/sdiv16_smod16_zerozp.asm",
            "segments": (("KERNEL_CODE", 206),),
            "entry": "FAST_SDIV16_ZEROZP", "zp": 0, "scratch": 3,
            "share_producer": "signed-16by16-portable-zerozp",
            "multi_entry": True, "sdiv16_portable": True,
            "provenance": "Signed 16/16 quotient+remainder producer: truncate Q toward zero, R signed as N, D=0 sets C, sign-extended domain includes -32768/-1 wrap. Legal 6510 zero-ZP 206-byte source, 3 RAM scratch.",
        },
    },
    "MATH_SMOD16": {
        "link:v2-signed-shared": {
            "source": "routines/divide/udiv16_v2_zerozp.asm",
            "segments": (("KERNEL_CODE", 1481),("SIGNED_ADAPTER", 224)),
            "entry": "FAST_SMOD16_V2_SHARED", "zp": 0, "scratch": 8,
            "share_producer": "signed-16by16-v2-direct", "multi_entry": True,
            "signed16_v2_shared": True,
            "provenance": "Historical canonical V2 direct 16/16 source with signed Q/R/C adapter and one physical shared producer; zero ZP, no REU/SMC/INIT.",
        },
        "link:portable-zerozp": {
            "source": "routines/divide/sdiv16_smod16_zerozp.asm",
            "segments": (("KERNEL_CODE", 206),),
            "entry": "FAST_SMOD16_ZEROZP", "zp": 0, "scratch": 3,
            "share_producer": "signed-16by16-portable-zerozp",
            "multi_entry": True, "sdiv16_portable": True,
            "provenance": "Signed remainder public entry shares signed 16/16 quotient/remainder producer; no duplicated code, exact N-sign R16, unchanged N/D/Q2+/R2+.",
        },
    },
    "MATH_UDIV16": {
        "link:biased": {
            "source": "routines/standalone_lab/portable/div_u16_biased.asm",
            "segments": (("KERNEL_CODE", 323),),
            "entry": "FAST_UDIV16_BIASED", "zp": 2, "scratch": 0,
        },
        "link:v2-zerozp": {
            "source": "routines/divide/udiv16_v2_zerozp.asm",
            "segments": (("KERNEL_CODE", 1481),),
            "entry": "DU16F_div_u16", "zp": 0, "scratch": 0,
            "udiv16_v2": True,
            "provenance": "Original V2 direct size-fast 16/16 Q/R/C producer, canonical source alias and public stubs removed; 1481 bytes, 0 ZP, 0 scratch, NMOS 6510 LAX/ANC; historical V2 donor preserved unchanged.",
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
    "MATH_UMUL16_SHR8": {
        "link:compact-zerozp": {
            "source": "routines/multiply/umul16_shr8_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 126),),
            "entry": "FAST_UMUL16_SHR8_COMPACT", "zp": 0, "scratch": 6,
            "operand_layout": "xyz",
            "provenance": "Standalone 16x16 product shifted right eight, 24-bit result; no ZP, all public inputs preserved; reference rather than historical speed",
        },
        "link:quarter-square": {
            "source": "routines/multiply/umul16_shr8_quartersquare.asm",
            "segments": (("KERNEL_CODE", 256), ("Q_LO", 511), ("Q_HI", 511)),
            "entry": "FAST_UMUL16_SHR8_QUARTERSQUARE", "zp": 0, "scratch": 4,
            "operand_layout": "xyz", "fast_umul16": True,
            "fast_umul16_shr8": True,
            "provenance": "Independent zero-ZP 16x16 quarter-square shared-table kernel plus 24-bit SHR8 adapter; 256 B code, 1022 B tables, 4 B scratch",
        },
    },
    "MATH_VEC2_NORMALIZE_Q8_8": {
        "link:certified-stock": {
            "source": "routines/vector/vec2_normalize_q8_8_source.asm",
            "segments": (("KERNEL_CODE", 3587),),
            "entry": "VEC2_NORMALIZE_Q8_8_NATIVE", "zp": 4, "scratch": 0,
            "operand_layout": "vec2", "vec2_stock": True,
            "requires_writable_code": True,
            "provenance": "Canonical V1/V5 4-quadrant signed Q8.8 normalizer and exact 2560B ratio/log/component stock tables; 865 code bytes plus 162 page gaps, 3587 aligned RAM image span, 4 volatile ZP, NMOS LAX abs and self-modifying operand; unchanged full-domain precision certificate <=0.3621 degrees / <=202 LSB.",
        },
    },
    "MATH_UMULDIV16": {
        "link:qs-v2-fused": {
            "source": "routines/multiply/umul16_quartersquare.asm",
            "segments": (("KERNEL_CODE", 3655),),
            "entry": "FAST_UMULDIV16_QS_V2", "zp": 12, "scratch": 4,
            "operand_layout": "muldiv16", "umuldiv16_qsv2": True,
            "provenance": "Original 233-byte unsigned quarter-square 16x16 with two 511-byte immutable planes, canonical V2 12-ZP 32/16 split-tail producer and a 32-byte direct compound public adapter; exact Q32/R16/C, preserves X/Y/D.",
        },
        "link:portable-zerozp": {
            "source": "routines/muldiv16/umuldiv16_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 288),),
            "entry": "FAST_UMULDIV16_PORTABLE", "zp": 0, "scratch": 6,
            "operand_layout": "muldiv16",
            "provenance": "Private compact UMUL16 full32 product followed by restoring UDIV32_16, 288 code/6 ordinary scratch/zero ZP. D=0 C=1.",
        },
    },
    "MATH_SMULDIV16": {
        "link:signed-qs-v2-fused": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 4263),),
            "entry": "FAST_SMULDIV16_SIGNED_QS_V2", "zp": 12, "scratch": 4,
            "operand_layout": "muldiv16", "smuldiv16_qsv2": True,
            "provenance": "Independent source fusion of certified signed QS16 full32, canonical V2 signed 32/16 quotient and direct signed muldiv public adapter. Preserves X/Y/D, Z32 and volatile N32, trunc-toward-zero Q32/R16/C, 12 ZP, 4 ordinary scratch.",
        },
        "link:portable-zerozp": {
            "source": "routines/muldiv16/smuldiv16_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 439),),
            "entry": "FAST_SMULDIV16_PORTABLE", "zp": 0, "scratch": 6,
            "operand_layout": "muldiv16",
            "provenance": "Private compact SMUL16 signed full32 product followed by signed SDIV32_16, 439 code/6 ordinary scratch/zero ZP. D=0 C=1.",
        },
    },
    "MATH_SMUL32_SHR16": {
        "link:fast31-shared-full64": {
            "source": "routines/multiply/mul32_fast31_shared_public.asm",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_SMUL32_SHR16_FAST31", "zp": 31, "scratch": 0,
            "operand_layout": "xyz", "fast31_umul32": True,
            "fast31_shared": True,
            "share_producer": "fast31-dual-public-full64", "multi_entry": True,
            "requires_writable_code": True,
            "provenance": "Signed 32x32 Q48 SHR16 ABI; one six-export shared V2 FAST31 512-byte code island, four 512-byte page-aligned lookup slots, 31 call-exclusive ZP bytes, zero ordinary scratch, writable RAM, D=0, no persistent READY state.",
        },
        "link:compact-zerozp": {
            "source": "routines/multiply/smul32_shr16_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 334),),
            "entry": "FAST_SMUL32_SHR16_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "smul32_shr16": True,
            "provenance": "Standalone signed 32x32 full64 source plus 41-byte arithmetic SHR16 Q48 adapter; 334 code / 12 RAM scratch / zero ZP.",
        },
        "link:unified-375": {
            "source": "routines/multiply/mul32_unified_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 375),),
            "entry": "FAST_SMUL32_SHR16_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "mul32-six-entry-unified375",
            "multi_entry": True,
            "provenance": "Combined state-independent signed/unsigned full64 and SHR16 Q48 shared source: six public APIs, 375 bytes code and 12 reusable ordinary scratch bytes; no ZP/REU/SMC/READY state.",
        },
    },
    "MATH_SMUL32_READY": {
        "link:fast31-shared-full64": {
            "source": "routines/multiply/mul32_fast31_shared_public.asm",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_SMUL32_FAST31", "zp": 31, "scratch": 0,
            "operand_layout": "xyz", "fast31_umul32": True,
            "fast31_shared": True,
            "share_producer": "fast31-dual-public-full64", "multi_entry": True,
            "requires_writable_code": True,
            "provenance": "Signed 32x32 READY full64 ABI, state-independent; one six-export shared V2 FAST31 512-byte code island, four 512-byte page-aligned lookup slots, 31 call-exclusive ZP bytes, zero ordinary scratch, writable RAM, D=0, no persistent READY state.",
        },
        "link:compact-zerozp": {
            "source": "routines/multiply/smul32_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 293),),
            "entry": "FAST_SMUL32_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "smul32-safe-core",
            "provenance": "State-independent signed full64 READY-compatible fallback; deduplicated with SMUL32, zero ZP, 12 RAM scratch, correctness-first rather than faster resident READY ABI",
        },
        "link:unified-375": {
            "source": "routines/multiply/mul32_unified_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 375),),
            "entry": "FAST_SMUL32_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "mul32-six-entry-unified375",
            "multi_entry": True,
            "provenance": "Combined state-independent signed/unsigned full64 and SHR16 Q48 shared source: six public APIs, 375 bytes code and 12 reusable ordinary scratch bytes; no ZP/REU/SMC/READY state.",
        },
    },
    "MATH_SMUL32": {
        "link:fast31-shared-full64": {
            "source": "routines/multiply/mul32_fast31_shared_public.asm",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_SMUL32_FAST31", "zp": 31, "scratch": 0,
            "operand_layout": "xyz", "fast31_umul32": True,
            "fast31_smul32": True, "fast31_shared": True,
            "share_producer": "fast31-dual-public-full64", "multi_entry": True,
            "requires_writable_code": True,
            "provenance": "Historical V2 31-ZP FAST31 single arithmetic kernel and four aligned lookup pages shared by unsigned/signed public full64 API; exact signed upper-half correction, retained X32/Y32, CLD and writable code; 512B code + 2048B table slots, 31 exclusive ZP.",
        },
        "link:fast31-v2-signed": {
            "source": "routines/multiply/smul32_fast31_public.asm",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_SMUL32_FAST31", "zp": 31, "scratch": 0,
            "operand_layout": "xyz", "fast31_umul32": True, "fast31_smul32": True,
            "requires_writable_code": True,
            "provenance": "Signed 32x32 full64 public adapter using certified V2 31-ZP unsigned FAST31 native producer and sign-correct upper 32 bits. 512 code slot, four exact 512-byte-aligned quarter-square table slots, 31 volatile ZP, no RAM scratch, REU or stack reservation, SMC kernel RAM and D=0 required.",
        },
        "link:compact-zerozp": {
            "source": "routines/multiply/smul32_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 293),),
            "entry": "FAST_SMUL32_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "smul32-safe-core", "smul32": True,
            "provenance": "Compact 32x32 signed full64: source-local unsigned shift-add plus upper32 two's complement correction, 293 code / 12 ordinary scratch / 0 ZP, not historical faster resident source.",
        },
        "link:unified-375": {
            "source": "routines/multiply/mul32_unified_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 375),),
            "entry": "FAST_SMUL32_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "mul32-six-entry-unified375",
            "multi_entry": True,
            "provenance": "Combined state-independent signed/unsigned full64 and SHR16 Q48 shared source: six public APIs, 375 bytes code and 12 reusable ordinary scratch bytes; no ZP/REU/SMC/READY state.",
        },
    },
    "MATH_SMUL24": {
        "link:compact-zerozp": {
            "source": "routines/multiply/smul24_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 227),),
            "entry": "FAST_SMUL24_COMPACT", "zp": 0, "scratch": 9,
            "operand_layout": "xyz", "smul24": True,
            "provenance": "Exact signed24x24 -> signed48 via source-private unsigned 156B core + 24-bit high correction, 227B code/9B RAM/0 ZP; original fast resident algorithms retained.",
        },
        "link:v2-quarter-square": {
            "source": "v2_pareto_fast/resident/modules/pareto_umul24.a",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_SMUL24_V2_QS", "zp": 24, "scratch": 0,
            "operand_layout": "xyz", "v2_umul24": True,
            "share_producer": "v2-biased-dual-mul24", "multi_entry": True,
            "requires_writable_code": True,
            "provenance": "Signed 24x24 modulo-2^48 high-word correction on the exact same historical V2 $CA-biased UMUL24 producer and four 512-byte quarter-square planes; one 512-byte dual-entry code island, 24 call-exclusive ZP, source-linked nonreentrant.",
        },
    },
    "MATH_UMUL32_SHR16": {
        "link:fast31-shared-full64": {
            "source": "routines/multiply/mul32_fast31_shared_public.asm",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_UMUL32_SHR16_FAST31", "zp": 31, "scratch": 0,
            "operand_layout": "xyz", "fast31_umul32": True,
            "fast31_shared": True,
            "share_producer": "fast31-dual-public-full64", "multi_entry": True,
            "requires_writable_code": True,
            "provenance": "Unsigned 32x32 Q48 SHR16 ABI; one six-export shared V2 FAST31 512-byte code island, four 512-byte page-aligned lookup slots, 31 call-exclusive ZP bytes, zero ordinary scratch, writable RAM, D=0, no persistent READY state.",
        },
        "link:compact-zerozp": {
            "source": "routines/multiply/umul32_shr16_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 245),),
            "entry": "FAST_UMUL32_SHR16_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "umul32_shr16": True,
            "provenance": "Standalone compact 32x32 unsigned source returning exact 48-bit (X*Y)>>16 in Z0..5, 245B code/12B ordinary scratch/0 ZP; high Z volatile and historical fastest remains available in resident profiles.",
        },
        "link:unified-375": {
            "source": "routines/multiply/mul32_unified_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 375),),
            "entry": "FAST_UMUL32_SHR16_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "mul32-six-entry-unified375",
            "multi_entry": True,
            "provenance": "Combined state-independent signed/unsigned full64 and SHR16 Q48 shared source: six public APIs, 375 bytes code and 12 reusable ordinary scratch bytes; no ZP/REU/SMC/READY state.",
        },
    },
    "MATH_UMUL32_READY": {
        "link:fast31-shared-full64": {
            "source": "routines/multiply/mul32_fast31_shared_public.asm",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_UMUL32_FAST31", "zp": 31, "scratch": 0,
            "operand_layout": "xyz", "fast31_umul32": True,
            "fast31_shared": True,
            "share_producer": "fast31-dual-public-full64", "multi_entry": True,
            "requires_writable_code": True,
            "provenance": "Unsigned 32x32 READY full64 ABI, state-independent; one six-export shared V2 FAST31 512-byte code island, four 512-byte page-aligned lookup slots, 31 call-exclusive ZP bytes, zero ordinary scratch, writable RAM, D=0, no persistent READY state.",
        },
        "link:compact-zerozp": {
            "source": "routines/multiply/umul32_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 204),),
            "entry": "FAST_UMUL32_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "umul32-safe-core",
            "provenance": "State-independent unsigned full64 READY-compatible fallback; deduplicated with UMUL32, zero ZP, 12 RAM scratch, correctness-first rather than faster resident READY ABI",
        },
        "link:unified-375": {
            "source": "routines/multiply/mul32_unified_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 375),),
            "entry": "FAST_UMUL32_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "mul32-six-entry-unified375",
            "multi_entry": True,
            "provenance": "Combined state-independent signed/unsigned full64 and SHR16 Q48 shared source: six public APIs, 375 bytes code and 12 reusable ordinary scratch bytes; no ZP/REU/SMC/READY state.",
        },
    },
    "MATH_UMUL32": {
        "link:fast31-shared-full64": {
            "source": "routines/multiply/mul32_fast31_shared_public.asm",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_UMUL32_FAST31", "zp": 31, "scratch": 0,
            "operand_layout": "xyz", "fast31_umul32": True,
            "fast31_shared": True,
            "share_producer": "fast31-dual-public-full64", "multi_entry": True,
            "requires_writable_code": True,
            "provenance": "Historical V2 31-ZP FAST31 single arithmetic kernel and four aligned lookup pages shared by unsigned/signed public full64 API; exact signed upper-half correction, retained X32/Y32, CLD and writable code; 512B code + 2048B table slots, 31 exclusive ZP.",
        },
        "link:fast31-v2-public": {
            "source": "routines/multiply/umul32_fast31_public.asm",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_UMUL32_FAST31", "zp": 31, "scratch": 0,
            "operand_layout": "xyz", "fast31_umul32": True,
            "requires_writable_code": True,
            "provenance": "V2 31-ZP certified native unsigned kernel plus a public X32/Y32 -> Z64 adapter; 512 code-slot bytes, four exact 511-entry lookup tables in 512-byte aligned slots, 31 volatile ZP bytes, zero private RAM scratch, no REU/stack reservation. Rebinds table pointer highs per call; writable kernel RAM and CLD required.",
        },
        "link:quarter-square-32": {
            "source": "routines/multiply/umul32_quartersquare.asm",
            "segments": (("KERNEL_CODE", 1028), ("Q_LO", 511), ("Q_HI", 511)),
            "entry": "FAST_UMUL32_QUARTERSQUARE", "zp": 0, "scratch": 4,
            "operand_layout": "xyz", "fast_umul16": True, "fast_umul32": True,
            "provenance": "Unsigned 32x32 16-term base-256 quarter-square convolution using certified UMUL16 511-entry tables; zero ZP, preserved inputs, no init/SMC/REU.",
        },
        "link:compact-zerozp": {
            "source": "routines/multiply/umul32_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 204),),
            "entry": "FAST_UMUL32_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "umul32-safe-core", "umul32": True,
            "provenance": "Portable standalone exact unsigned 32x32->64, 204 code/12 RAM scratch/0 ZP, untouched X/Y, legal NMOS; not historical 600-cycle fast source.",
        },
        "link:unified-375": {
            "source": "routines/multiply/mul32_unified_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 375),),
            "entry": "FAST_UMUL32_COMPACT", "zp": 0, "scratch": 12,
            "operand_layout": "xyz", "share_producer": "mul32-six-entry-unified375",
            "multi_entry": True,
            "provenance": "Combined state-independent signed/unsigned full64 and SHR16 Q48 shared source: six public APIs, 375 bytes code and 12 reusable ordinary scratch bytes; no ZP/REU/SMC/READY state.",
        },
    },
    "MATH_UMUL24": {
        "link:compact-zerozp": {
            "source": "routines/multiply/umul24_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 156),),
            "entry": "FAST_UMUL24_COMPACT", "zp": 0, "scratch": 9,
            "operand_layout": "xyz", "umul24": True,
            "provenance": "Portable unsigned 24x24 -> 48-bit source; zero ZP, nine RAM scratch bytes, preserved operands, output Z0..5, no REU/SMC/lookup. Not historical fastest.",
        },
        "link:v2-quarter-square": {
            "source": "v2_pareto_fast/resident/modules/pareto_umul24.a",
            "segments": (("KERNEL_CODE", 512), ("Q_SQR_LO", 512),
                         ("Q_SQR_HI", 512), ("Q_NEG_LO", 512),
                         ("Q_NEG_HI", 512)),
            "entry": "FAST_UMUL24_V2_QS", "zp": 24, "scratch": 0,
            "operand_layout": "xyz", "v2_umul24": True,
            "share_producer": "v2-biased-dual-mul24", "multi_entry": True,
            "requires_writable_code": True,
            "provenance": "Historical V2 $CA-biased source-shared unsigned/signed 24x24 quarter-square producer: 512-byte code island with signed correction, four 512-byte aligned tables, 24 private ZP bytes. Both entries share one image, require writable code and are non-reentrant; no INIT/REU.",
        },
    },
    "MATH_SMUL16_SHR8": {
        "link:qs-signed-shr8-public": {
            "source": "routines/multiply/umul16_quartersquare.asm",
            "segments": (("KERNEL_CODE", 233), ("Q_LO", 511), ("Q_HI", 511),
                         ("SIGNED_ADAPTER", 96), ("SHR8_ADAPTER", 32)),
            "entry": "FAST_SMUL16_SHR8_QUARTERSQUARE", "zp": 0, "scratch": 4,
            "operand_layout": "xyz", "smul16_shr8_qs": True,
            "provenance": "Stock C64 canonical quarter-square signed full32 producer with bounded high24 arithmetic byte-slice entry; exact signed X16*Y16>>8, 0 ZP and 4 scratch; no REU/SMC.",
        },
        "link:compact-zerozp": {
            "source": "routines/multiply/smul16_shr8_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 184),),
            "entry": "FAST_SMUL16_SHR8_COMPACT", "zp": 0, "scratch": 6,
            "operand_layout": "xyz", "smul16_shr8": True,
            "provenance": "Independent source-private signed16 producer plus arithmetic high-byte slice: exact signed (X16*Y16)>>8 in Z24, 184 code and 6 ordinary scratch, zero ZP; not resident speed champion.",
        },
    },
    "MATH_SMUL16": {
        "link:qs-signed-public": {
            "source": "routines/multiply/umul16_quartersquare.asm",
            "segments": (("KERNEL_CODE", 233), ("Q_LO", 511), ("Q_HI", 511), ("SIGNED_ADAPTER", 96)),
            "entry": "FAST_SMUL16_QUARTERSQUARE", "zp": 0, "scratch": 4,
            "operand_layout": "xyz", "smul16_qs": True,
            "provenance": "Canonical unsigned 16x16 quarter-square 233-byte producer and two 511-byte tables with a separate signed high-word correction public entry; exact full signed32 result, 0 ZP, four ordinary scratch, no REU, SMC or INIT.",
        },
        "link:compact-zerozp": {
            "source": "routines/multiply/smul16_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 161),),
            "entry": "FAST_SMUL16_COMPACT", "zp": 0, "scratch": 6,
            "operand_layout": "xyz", "smul16": True,
            "provenance": "Two's-complement 16x16->32: original 108-byte unsigned shift-add plus sign correction of upper word, six call-exclusive RAM bytes, zero ZP; not historical performance winner.",
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
    "MATH_UDIV24": {
        "link:v2-repose-fast": {
            "source": "routines/divide/u24_v2_repose_selective.asm",
            "segments": (("KERNEL_CODE", 1244), ("KERNEL_AUX", 217)),
            "entry": "DU24F_div_u24", "zp": 3, "scratch": 0,
            "share_producer": "unsigned-24by24-v2-repose", "multi_entry": True,
            "requires_writable_code": True, "udiv24_v2": True,
            "provenance": "Canonical historical V2 high-speed Repose 24-bit shared quotient/remainder; two relocated code islands, three scratch ZP, self-modifying tail immediate",
        },
        "link:portable-restoring": {
            "source": "routines/divide/u24_by_u24_restoring_selective.asm",
            "segments": (("KERNEL_CODE", 190),),
            "entry": "FAST_UDIV24_RESTORING", "zp": 0, "scratch": 4,
            "share_producer": "unsigned-24by24-restoring", "multi_entry": True,
            "provenance": "Full-domain zero-ZP portable 24/24 DIV+MOD correctness source, not historical speed champion",
        },
    },
    "MATH_UMOD24": {
        "link:v2-repose-fast": {
            "source": "routines/divide/u24_v2_repose_selective.asm",
            "segments": (("KERNEL_CODE", 1244), ("KERNEL_AUX", 217)),
            "entry": "DU24F_div_u24", "zp": 3, "scratch": 0,
            "share_producer": "unsigned-24by24-v2-repose", "multi_entry": True,
            "requires_writable_code": True, "udiv24_v2": True,
            "provenance": "Canonical historical V2 high-speed Repose 24-bit shared quotient/remainder; two relocated code islands, three scratch ZP, self-modifying tail immediate",
        },
        "link:portable-restoring": {
            "source": "routines/divide/u24_by_u24_restoring_selective.asm",
            "segments": (("KERNEL_CODE", 190),),
            "entry": "FAST_UMOD24_RESTORING", "zp": 0, "scratch": 4,
            "share_producer": "unsigned-24by24-restoring", "multi_entry": True,
            "provenance": "Shared 24/24 unsigned DIV+MOD producer: both outputs, divisor-zero carry and preserved N/D",
        },
    },
    "MATH_URECIP16_Q16": {
        "link:threshold-tables-zerozp": {
            "source": "tools/selective_recip16_table.py",
            "segments": (("KERNEL_CODE", 1544),),
            "entry": "FAST_URECIP16_Q16_TABLE", "zp": 0, "scratch": 0,
            "recip16_table": True,
            "provenance": "Stock 6510 exact 256-entry Q24 low-divisor table and V3/V4-inspired eight-step 16-bit threshold bisection for D>=257; no zero-page, REU, writable code, SMC or initialization; complete public Q24/C contract.",
        },
        "link:threshold-zerozp": {
            "source": "routines/fixed/urecip16_q16_zerozp.asm",
            "segments": (("KERNEL_CODE", 448),),
            "entry": "FAST_URECIP16_Q16_THRESH", "zp": 0, "scratch": 1,
            "recip16_threshold": True,
            "provenance": "Stock 6510 historical V3/V4 1..15 integer reciprocal threshold gate with exact compact fallback for D<=4096; zero ZP, no REU, one byte scratch; preserves Q3, R and all public input bytes.",
        },
        "link:compact-zerozp": {
            "source": "routines/fixed/urecip16_q16_zerozp.asm",
            "segments": (("KERNEL_CODE", 99),),
            "entry": "FAST_URECIP16_Q16_ZEROZP", "zp": 0, "scratch": 1,
            "urecip16": True,
            "provenance": "Standalone 24-step fixed-numerator unsigned 65536/D16 Q24, 99 B code and one RAM byte. Inputs intact, D=0 signals carry. Portable reference, not historical 66-cycle speed variant.",
        },
    },
    "MATH_UDIV16_SHL8": {
        "link:v2-shifted-public": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2368),),
            "entry": "FAST_UDIV16_SHL8_V2", "zp": 12, "scratch": 0,
            "v2_shifted_u3216": True,
            "provenance": "Canonical historical V2 32/16 split-tail source; shifted N16 staging without touching N+2/N+3, full Q24/R16/C ABI; independent 2368-byte code and 12 call-exclusive ZP bytes; NMOS LAX/ANC and D=0 required.",
        },
        "link:accumulator-remainder": {
            "source": "routines/divide/u16_shl8_accum_selective.asm",
            "segments": (("KERNEL_CODE", 129),),
            "entry": "FAST_UDIV16_SHL8_ACCUM", "zp": 0, "scratch": 1,
            "udiv16_shl8": True,
            "provenance": "Portable shifted N16<<8 / D16 using one ordinary remainder byte, 32 iterations; Q24 and R16, preserved N/D, zero-divisor carry; no ZP/REU/SMC",
        },
    },
    "MATH_UDIV32_16": {
        "link:v2-sizefast-public": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2368),),
            "entry": "FAST_UDIV32_16_V2", "zp": 12, "scratch": 0,
            "share_producer": "unsigned-32by16-v2-sizefast",
            "multi_entry": True, "v2_sizefast_u3216": True,
            "provenance": "Relocated canonical V2 12-ZP size-fast high-word 16-bit divider + 16 unrolled low-word quotient bits; public Q32/R16 ABI staging and carry preservation, 2368B image including hole padding, NMOS LAX/ANC, D=0, non-reentrant scratch.",
        },
        "link:accum-unrolled-32": {
            "source": "routines/divide/u32_by_u16_accum_unrolled_selective.asm",
            "segments": (("KERNEL_CODE", 1771),),
            "entry": "FAST_UDIV32_16_ACCUM", "zp": 0, "scratch": 1,
            "share_producer": "unsigned-32by16-accum-unrolled",
            "multi_entry": True,
            "provenance": "Statically unrolled 32-round 32/16 public Q32+R16; zero ZP, one ordinary scratch byte, 1771B executable, no SMC/tables; D=0 prerequisite and C=1/Q=R=0 on divisor zero; research source qualified independently and native VICE tested.",
        },
        "link:accumulator-remainder": {
            "source": "routines/divide/u32_by_u16_accum_selective.asm",
            "segments": (("KERNEL_CODE", 131),),
            "entry": "FAST_UDIV32_16_ACCUM", "zp": 0, "scratch": 1,
            "share_producer": "unsigned-32by16-accum", "multi_entry": True,
            "provenance": "131-byte accumulator-high restoring unsigned 32/16 kernel; independently verified zero-ZP candidate",
        },
        "link:portable-restoring": {
            "source": "routines/divide/u32_by_u16_restoring_selective.asm",
            "segments": (("KERNEL_CODE", 162),),
            "entry": "FAST_UDIV32_16_PORTABLE", "zp": 0, "scratch": 3,
            "share_producer": "unsigned-32by16-restoring", "multi_entry": True,
            "provenance": "Portable standalone restoring reference; shared public DIV/MOD producer, NOT a V1-V5 speed replacement",
        },
    },
    "MATH_UMOD32_16": {
        "link:v2-sizefast-public": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2368),),
            "entry": "FAST_UMOD32_16_V2", "zp": 12, "scratch": 0,
            "share_producer": "unsigned-32by16-v2-sizefast",
            "multi_entry": True, "v2_sizefast_u3216": True,
            "provenance": "Relocated canonical V2 12-ZP size-fast high-word 16-bit divider + 16 unrolled low-word quotient bits; public Q32/R16 ABI staging and carry preservation, 2368B image including hole padding, NMOS LAX/ANC, D=0, non-reentrant scratch.",
        },
        "link:accum-unrolled-32": {
            "source": "routines/divide/u32_by_u16_accum_unrolled_selective.asm",
            "segments": (("KERNEL_CODE", 1771),),
            "entry": "FAST_UMOD32_16_ACCUM", "zp": 0, "scratch": 1,
            "share_producer": "unsigned-32by16-accum-unrolled",
            "multi_entry": True,
            "provenance": "Statically unrolled 32-round 32/16 public Q32+R16; zero ZP, one ordinary scratch byte, 1771B executable, no SMC/tables; D=0 prerequisite and C=1/Q=R=0 on divisor zero; research source qualified independently and native VICE tested.",
        },
        "link:accumulator-remainder": {
            "source": "routines/divide/u32_by_u16_accum_selective.asm",
            "segments": (("KERNEL_CODE", 131),),
            "entry": "FAST_UMOD32_16_ACCUM", "zp": 0, "scratch": 1,
            "share_producer": "unsigned-32by16-accum", "multi_entry": True,
            "provenance": "131-byte accumulator-high restoring unsigned 32/16 kernel; independently verified zero-ZP candidate",
        },
        "link:portable-restoring": {
            "source": "routines/divide/u32_by_u16_restoring_selective.asm",
            "segments": (("KERNEL_CODE", 162),),
            "entry": "FAST_UMOD32_16_PORTABLE", "zp": 0, "scratch": 3,
            "share_producer": "unsigned-32by16-restoring", "multi_entry": True,
            "provenance": "Portable standalone restoring reference; writes both Q32 and R16 like the existing resident alias",
        },
    },
    "MATH_UDIV32_32": {
        "link:v2-lowdivisor-hybrid": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2496),),
            "entry": "FAST_UDIV32_32_HYBRID", "zp": 12, "scratch": 0,
            "share_producer": "unsigned-32by32-v2-lowdivisor-public-qr",
            "multi_entry": True, "hybrid_u3232": True,
            "provenance": "Source-authenticated unrestricted Q32/R32/C using canonical V2 12-ZP low-D 32/16 public kernel and qualified 4-ZP full-D 32/32 tail; shared 2496B caller-RAM image, 12 call-exclusive ZP, no tables/SMC/REU/scratch, D=0 prerequisite. Preserves N32/D32 and C=1 on D=0.",
        },
        "link:shared-aligned-zerozp": {
            "source": "routines/standalone_lab/portable/div_u32_aligned_nozp.asm",
            "segments": (("KERNEL_CODE", 325), ("KERNEL_AUX", 251)),
            "entry": "FAST_UDIV32_PUBLIC", "zp": 0, "scratch": 4,
            "share_producer": "unsigned-32by32-aligned-public-qr",
            "multi_entry": True,
            "provenance": "Source-qualified public unsigned 32/32 shared Q32/R32 restoring producer: same 576-byte two-island machine image and 4B ordinary scratch for DIV and MOD; 0 ZP; both outputs and divide-zero C flag, caller operands preserved. Uses the existing independently native-qualified aligned DIV source.",
        },
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
    "MATH_ISQRT32": {
        "link:v2-highword-source": {
            "source": "routines/roots/isqrt32_v2_highword_selective.asm",
            "segments": (("KERNEL_CODE", 192), ("SQ_SQUARE_LO", 256),
                         ("SQ_SQUARE_HI", 256), ("SQ_GUESS", 256)),
            "entry": "LCB40", "zp": 7, "scratch": 0,
            "operand_layout": "nz", "isqrt32_v2": True,
            "provenance": "Original V2 highword seed and 4+4 radix-4 refinement, 192 code and three exact 256-byte tables, seven ZP; portable all-domain source-derived specialist",
        },
        "link:radix4-zerozp": {
            "source": "routines/roots/isqrt32_restoring_zerozp.asm",
            "segments": (("KERNEL_CODE", 204),),
            "entry": "FAST_ISQRT32_RESTORING", "zp": 0, "scratch": 10,
            "operand_layout": "nz",
            "provenance": "Exact full-domain restoring ISQRT32; 204 bytes / 10 RAM / 0 ZP; V1–V5 optimized fast producers retained for follow-on transplant",
        },
    },
    "MATH_ISQRT16": {
        "link:radix4-zerozp": {
            "source": "routines/roots/isqrt16_radix4_zerozp.asm",
            "segments": (("KERNEL_CODE", 137),),
            "entry": "FAST_ISQRT16_RESTORING", "zp": 0, "scratch": 6,
            "operand_layout": "nz", "isqrt16_radix4": True,
            "provenance": "Exhaustive all-65536 unsigned floor-sqrt restoring 137B code +6B RAM scratch, 0 ZP, no tables or SMC; C=0, N preserved",
        },
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
        "link:v2-lowdivisor-hybrid": {
            "source": "v2_pareto_fast/resident/modules/pareto_udiv32_16.a",
            "segments": (("KERNEL_CODE", 2496),),
            "entry": "FAST_UMOD32_32_HYBRID", "zp": 12, "scratch": 0,
            "share_producer": "unsigned-32by32-v2-lowdivisor-public-qr",
            "multi_entry": True, "hybrid_u3232": True,
            "provenance": "Source-authenticated unrestricted Q32/R32/C using canonical V2 12-ZP low-D 32/16 public kernel and qualified 4-ZP full-D 32/32 tail; shared 2496B caller-RAM image, 12 call-exclusive ZP, no tables/SMC/REU/scratch, D=0 prerequisite. Preserves N32/D32 and C=1 on D=0.",
        },
        "link:shared-aligned-zerozp": {
            "source": "routines/standalone_lab/portable/div_u32_aligned_nozp.asm",
            "segments": (("KERNEL_CODE", 325), ("KERNEL_AUX", 251)),
            "entry": "FAST_UDIV32_PUBLIC", "zp": 0, "scratch": 4,
            "share_producer": "unsigned-32by32-aligned-public-qr",
            "multi_entry": True,
            "provenance": "Source-qualified public unsigned 32/32 shared Q32/R32 restoring producer: same 576-byte two-island machine image and 4B ordinary scratch for DIV and MOD; 0 ZP; both outputs and divide-zero C flag, caller operands preserved. Uses the existing independently native-qualified aligned DIV source.",
        },
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
                    "tools/selective_fast_umul8.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul8.py").read_bytes()).hexdigest(),
                    "tools/selective_smul8_qs_readonly.py": hashlib.sha256(
                        (root / "tools/selective_smul8_qs_readonly.py").read_bytes()).hexdigest(),
                } if mod.get("smul8_qs") else {
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
                    "tools/selective_fast_umul8.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul8.py").read_bytes()).hexdigest(),
                    "tools/selective_fast_umul16.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul16.py").read_bytes()).hexdigest(),
                    "tools/selective_v2_fast_u3216.py": hashlib.sha256(
                        (root / "tools/selective_v2_fast_u3216.py").read_bytes()).hexdigest(),
                    "tools/selective_umuldiv16_qs_v2.py": hashlib.sha256(
                        (root / "tools/selective_umuldiv16_qs_v2.py").read_bytes()).hexdigest(),
                    "v2_pareto_fast/resident/modules/pareto_udiv32_16.a": hashlib.sha256(
                        (root / "v2_pareto_fast/resident/modules/pareto_udiv32_16.a").read_bytes()).hexdigest(),
                } if mod.get("umuldiv16_qsv2") else {
                    "tools/selective_fast_umul8.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul8.py").read_bytes()).hexdigest(),
                    "tools/selective_fast_umul16.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul16.py").read_bytes()).hexdigest(),
                    "tools/selective_smul16_quartersquare.py": hashlib.sha256(
                        (root / "tools/selective_smul16_quartersquare.py").read_bytes()).hexdigest(),
                    "tools/selective_v2_fast_u3216.py": hashlib.sha256(
                        (root / "tools/selective_v2_fast_u3216.py").read_bytes()).hexdigest(),
                    "tools/research_signed_v2_u3216.py": hashlib.sha256(
                        (root / "tools/research_signed_v2_u3216.py").read_bytes()).hexdigest(),
                    "tools/selective_smuldiv16_qs_v2.py": hashlib.sha256(
                        (root / "tools/selective_smuldiv16_qs_v2.py").read_bytes()).hexdigest(),
                } if mod.get("smuldiv16_qsv2") else {
                    "tools/selective_fast_umul8.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul8.py").read_bytes()).hexdigest(),
                    "tools/selective_fast_umul16.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul16.py").read_bytes()).hexdigest(),
                    "tools/selective_smul16_quartersquare.py": hashlib.sha256(
                        (root / "tools/selective_smul16_quartersquare.py").read_bytes()).hexdigest(),
                } if mod.get("smul16_qs") else {
                    "tools/selective_fast_umul8.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul8.py").read_bytes()).hexdigest(),
                    "tools/selective_fast_umul16.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul16.py").read_bytes()).hexdigest(),
                    "tools/selective_smul16_quartersquare.py": hashlib.sha256(
                        (root / "tools/selective_smul16_quartersquare.py").read_bytes()).hexdigest(),
                    "tools/selective_smul16_shr8_quartersquare.py": hashlib.sha256(
                        (root / "tools/selective_smul16_shr8_quartersquare.py").read_bytes()).hexdigest(),
                } if mod.get("smul16_shr8_qs") else {
                    "tools/selective_fast31_umul32.py": hashlib.sha256(
                        (root / "tools/selective_fast31_umul32.py").read_bytes()).hexdigest(),
                    "v2_pareto_fast/resident/modules/pareto_umul32.a": hashlib.sha256(
                        (root / "v2_pareto_fast/resident/modules/pareto_umul32.a").read_bytes()).hexdigest(),
                } if mod.get("fast31_umul32") else {
                    "tools/selective_v2_fast_umul24.py": hashlib.sha256(
                        (root / "tools/selective_v2_fast_umul24.py").read_bytes()).hexdigest(),
                } if mod.get("v2_umul24") else {
                    "tools/selective_v2_shifted_u3216.py": hashlib.sha256(
                        (root / "tools/selective_v2_shifted_u3216.py").read_bytes()).hexdigest(),
                    "tools/selective_v2_fast_u3216.py": hashlib.sha256(
                        (root / "tools/selective_v2_fast_u3216.py").read_bytes()).hexdigest(),
                } if mod.get("v2_shifted_u3216") else {
                    "tools/selective_v2_signed_shifted16.py": hashlib.sha256(
                        (root / "tools/selective_v2_signed_shifted16.py").read_bytes()).hexdigest(),
                    "tools/selective_v2_fast_u3216.py": hashlib.sha256(
                        (root / "tools/selective_v2_fast_u3216.py").read_bytes()).hexdigest(),
                } if mod.get("v2_signed_shifted16") else {
                    "tools/selective_v2_signed16_shared.py": hashlib.sha256(
                        (root / "tools/selective_v2_signed16_shared.py").read_bytes()).hexdigest(),
                    "relocatable_source/v2_pareto_fast/udiv16_direct_fast.inc": hashlib.sha256(
                        (root / "relocatable_source/v2_pareto_fast/udiv16_direct_fast.inc").read_bytes()).hexdigest(),
                } if mod.get("signed16_v2_shared") else {
                    "tools/selective_recip16_threshold.py": hashlib.sha256(
                        (root / "tools/selective_recip16_threshold.py").read_bytes()).hexdigest(),
                    "v3_reu_512k/standalone/recip_u16_u24_q16.asm": hashlib.sha256(
                        (root / "v3_reu_512k/standalone/recip_u16_u24_q16.asm").read_bytes()).hexdigest(),
                } if mod.get("recip16_threshold") else {
                    "v3_reu_512k/standalone/recip_u16_u24_q16.asm": hashlib.sha256(
                        (root / "v3_reu_512k/standalone/recip_u16_u24_q16.asm").read_bytes()).hexdigest(),
                } if mod.get("recip16_table") else {
                    "tools/selective_v2_fast_u3216.py": hashlib.sha256(
                        (root / "tools/selective_v2_fast_u3216.py").read_bytes()).hexdigest(),
                } if mod.get("v2_sizefast_u3216") else {
                    "tools/research_signed_v2_u3216.py": hashlib.sha256(
                        (root / "tools/research_signed_v2_u3216.py").read_bytes()).hexdigest(),
                    "tools/selective_v2_fast_u3216.py": hashlib.sha256(
                        (root / "tools/selective_v2_fast_u3216.py").read_bytes()).hexdigest(),
                } if mod.get("signed_v2_u3216") else {
                    "tools/selective_hybrid_u3232.py": hashlib.sha256(
                        (root / "tools/selective_hybrid_u3232.py").read_bytes()).hexdigest(),
                    "tools/selective_v2_fast_u3216.py": hashlib.sha256(
                        (root / "tools/selective_v2_fast_u3216.py").read_bytes()).hexdigest(),
                    "routines/standalone_lab/portable/div_u32_zptail.asm": hashlib.sha256(
                        (root / "routines/standalone_lab/portable/div_u32_zptail.asm").read_bytes()).hexdigest(),
                } if mod.get("hybrid_u3232") else {
                    "tools/selective_signed_hybrid_u3232.py": hashlib.sha256(
                        (root / "tools/selective_signed_hybrid_u3232.py").read_bytes()).hexdigest(),
                    "tools/selective_hybrid_u3232.py": hashlib.sha256(
                        (root / "tools/selective_hybrid_u3232.py").read_bytes()).hexdigest(),
                    "tools/selective_v2_fast_u3216.py": hashlib.sha256(
                        (root / "tools/selective_v2_fast_u3216.py").read_bytes()).hexdigest(),
                    "routines/standalone_lab/portable/div_u32_zptail.asm": hashlib.sha256(
                        (root / "routines/standalone_lab/portable/div_u32_zptail.asm").read_bytes()).hexdigest(),
                } if mod.get("signed_hybrid_u3232") else {
                    "tools/selective_isqrt16.py": hashlib.sha256(
                        (root / "tools/selective_isqrt16.py").read_bytes()).hexdigest()
                } if mod.get("isqrt16") else {
                    "relocatable_source/v2_pareto_fast/isqrt32_direct_highword_normal.inc":
                        hashlib.sha256((root / "relocatable_source/v2_pareto_fast/isqrt32_direct_highword_normal.inc").read_bytes()).hexdigest(),
                    "relocatable_source/v2_pareto_fast/math_relocatable.asm":
                        hashlib.sha256((root / "relocatable_source/v2_pareto_fast/math_relocatable.asm").read_bytes()).hexdigest(),
                } if mod.get("isqrt32_v2") else {
                    "relocatable_source/v2_pareto_fast/udiv24_direct_repose.inc":
                        hashlib.sha256((root / "relocatable_source/v2_pareto_fast/udiv24_direct_repose.inc").read_bytes()).hexdigest(),
                    "tools/selective_udiv24_v2.py":
                        hashlib.sha256((root / "tools/selective_udiv24_v2.py").read_bytes()).hexdigest(),
                } if mod.get("udiv24_v2") else {
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
                    "tools/test_selective_smul8_qs_readonly.py" if mod.get("smul8_qs") else
                    "tools/test_selective_smul8.py" if mod.get("smul8_v1") else
                    "tools/test_selective_fast_umul16_shr8.py" if mod.get("fast_umul16_shr8") else
                    "tools/test_selective_fast31_shared.py" if mod.get("fast31_shared") else
                    "tools/test_selective_fast31_smul32_builder.py" if mod.get("fast31_smul32") else
                    "tools/test_selective_umul32_fast31_builder.py" if mod.get("fast31_umul32") else
                    "tools/test_selective_u3232_hybrid_builder.py" if mod.get("hybrid_u3232") else
                    "tools/test_selective_umul32_quartersquare.py" if mod.get("fast_umul32") else
                    "tools/test_selective_fast_umul16.py" if mod.get("fast_umul16") else
                    "tools/test_selective_dist8_accurate.py" if mod.get("dist8_accurate") else
                    "tools/test_selective_trig8.py" if mod.get("trig8") else
                    "tools/test_selective_sdiv8.py" if mod.get("sdiv8_v1") else
                    "tools/test_selective_udiv8_v2v5.py" if mod.get("udiv8_v2v5") else
                    "tools/test_selective_udiv8.py" if mod.get("udiv8_v1") else
                    "tools/test_selective_dist8.py" if mod.get("dist8") else
                    "tools/test_selective_urecip16_q16.py" if mod.get("urecip16") else
                    "tools/test_selective_sdiv32_32.py" if mod.get("sdiv32_32_portable") else
                    "tools/test_selective_sdiv32_16.py" if mod.get("sdiv32_16_portable") else
                    "tools/test_selective_sdiv24_v3.py" if mod.get("sdiv24_v3_relocated") else
                    "tools/test_selective_sdiv24_qzero.py" if mod.get("sdiv24_qzero") else
                    "tools/test_selective_sdiv24.py" if mod.get("sdiv24_portable") else
                    "tools/test_selective_sdiv16_shl8.py" if mod.get("sdiv16_shl8_portable") else
                    "tools/test_selective_sdiv16.py" if mod.get("sdiv16_portable") else
                    "tools/test_selective_udiv16_shl8.py" if mod.get("udiv16_shl8") else
                    "tools/test_selective_udiv24_v2.py" if mod.get("udiv24_v2") else
                    "tools/test_selective_isqrt32_v2.py" if mod.get("isqrt32_v2") else
                    "tools/test_selective_isqrt16_radix4.py" if mod.get("isqrt16_radix4") else
                    "tools/test_selective_isqrt16.py" if mod.get("isqrt16") else
                    "tools/test_selective_seek16.py" if mod.get("seek16") else
                    "tools/test_selective_seek8.py" if mod.get("seek8") else
                    "tools/test_selective_umul8_v1.py" if mod.get("umul8_v1") else
                    "tools/test_selective_fast_umul8.py" if mod.get("fast_umul8") else
                    "tools/test_selective_smul16_shr8.py" if mod.get("smul16_shr8") else
                    "tools/test_selective_smul16.py" if mod.get("smul16") else
                    "tools/test_selective_smul32.py" if mod.get("smul32") else
                    "tools/test_selective_umul32_shr16.py" if mod.get("umul32_shr16") else
                    "tools/test_selective_umul32.py" if mod.get("umul32") else
                    "tools/test_selective_smul24.py" if mod.get("smul24") else
                    "tools/test_selective_umul24.py" if mod.get("umul24") else
                    "tools/test_selective_multiply.py"
                    if mod.get("operand_layout") == "xyz" else
                    "routines/atan2/validate_optimized.py" if "atan2" in mod else
                    "routines/standalone_lab/portable/verify.py"),
                "qualification": ("historical fast source port; CPU and native VICE gates"
                                  if mod.get("udiv24_v2") or (mod.get("umod8_v1") or mod.get("umod8_extra")) or mod.get("smul8_v1") or mod.get("umul8_v1") or mod.get("seek8") or mod.get("seek16") or mod.get("sdiv8_v1") or mod.get("dist8_accurate") or mod.get("trig8") or mod.get("udiv8_v2v5") or mod.get("udiv8_v1") or mod.get("dist8") or mod.get("isqrt16") else
                                  "experimental compact source; CPU and native validation"
                                  if mod.get("operand_layout") == "xyz" else
                                  "portable source; mixed-call qualification"),
                "notes": ("Canonical V2 highword root32 seed with source-derived 4+4 radix-4 refinement, exact 3-page generated tables; 192 code, 768 table, 7 ZP, no writable code"
                          if mod.get("isqrt32_v2") else
                          "Certified historical V2 1244+217-byte direct Repose 24/24 DIV/MOD fast chain, 3 ZP bytes and writable tail-bias instruction; explicit opt-in until common-corpus speed ranking"
                          if mod.get("udiv24_v2") else
                          "Original byte-identical V2/V5 430-byte unrestricted UDIV8 Q/R fast producer; no REU, 1 ZP byte"
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
                          "Signed FAST31 native 32x32 product with exact high-word sign corrections; 512-byte code slot and four 512-byte aligned table slots, 31 ZP, writable code"
                          if mod.get("fast31_smul32") else
                          "FAST31 historical 277-byte native producer wrapped for public ABI; 512 code slot and four 512-byte aligned table slots, 31 ZP, writable code, zero ordinary scratch"
                          if mod.get("fast31_umul32") else
                          "1028-byte unsigned 32x32 quarter-square convolution and 1022 generated table bytes; 4 RAM scratch, 0 ZP"
                          if mod.get("fast_umul32") else
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
        elif mod.get("vec2_stock"):
            cursor = ((cursor + 255) & ~255) + 3587
        elif mod.get("fast31_umul32"):
            _, cursor = fast31.layout(cursor)
        elif mod.get("v2_umul24"):
            _, cursor = v2umul24.layout(cursor)
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
    aligned = [item for item in items if "atan2" in item[2] or item[2].get("isqrt16") or item[2].get("umul8_v1") or item[2].get("vec2_stock") or item[2].get("fast31_umul32") or item[2].get("v2_umul24")]
    ordinary = [item for item in items if "atan2" not in item[2] and not item[2].get("isqrt16") and not item[2].get("umul8_v1") and not item[2].get("vec2_stock") and not item[2].get("fast31_umul32") and not item[2].get("v2_umul24")]
    if not aligned:
        return ordinary
    if len(aligned) != 1:
        # Deterministic conservative layout for multiple table-aligned kernels.
        # Exact span is still budgeted; optimal multi-aligned ordering is future work.
        return ordinary + sorted(aligned, key=lambda item: item[0])
    atan = aligned[0]
    code_bytes = (atan2.KINDS[atan[2]["atan2"]]["code_bytes"]
                  if "atan2" in atan[2] else sqrt16.CODE_BYTES
                  if atan[2].get("isqrt16") else 0
                   if atan[2].get("vec2_stock") else fast31.CODE_SLOT
                  if atan[2].get("fast31_umul32") else v2umul24.CODE_SLOT
                  if atan[2].get("v2_umul24") else v1umul8.CODE_BYTES)
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

    Do not prune an individually dominated *shared producer*: two API entries
    can link the same physical image once. A larger producer may therefore
    reduce global RAM compared with a locally smaller independent kernel.
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
              if "atan2" in spec or spec.get("isqrt16") or spec.get("umul8_v1") or spec.get("vec2_stock") or spec.get("fast31_umul32")
              else ("contiguous", 0))
        for key, spec in candidates
    }
    keep = {}
    for key, variant in candidates:
        if variant.get("share_producer"):
            # Dominance in isolation says nothing about combined cost when
            # another selected operation exports this physical producer.
            keep[key] = variant
            continue
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


def choose(names, pins, objective, zp_budget, ram_budget=None, code_base=0x8000, cycle_metrics=None, scratch_base=0xc020, workload_calls=None):
    """Optimize *the whole selection*, sharing nonreentrant scratch ownership."""
    if objective == "speed":
        if not isinstance(workload_calls, dict) or set(workload_calls) != set(names):
            raise LinkError("Speed selection requires positive workload calls for all selected operations")
        if any(type(n) is not int or not 1 <= n <= 1000000
               for n in workload_calls.values()):
            raise LinkError("Invalid speed workload call count")
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
    if objective == "speed":
        # The ordinary Cartesian product grows prohibitively with sixteen
        # measured APIs. Use an exact branch-and-bound search instead: cycle
        # minima and packed, unaligned source sizes are *lower bounds* (never
        # claims of realistic physical placement or shared table padding).
        # Final candidates still use the original full resource/score model.
        weighted_options = []
        for variants in options:
            api = variants[0][0]
            measured = cycle_metrics.get(api)
            if measured is None or set(measured) != set(MODULES[api]):
                raise LinkError(api + ": missing or incomplete comparable cycle model")
            candidates = []
            for item in variants:
                _, ident, spec = item
                try:
                    mean = measured[ident]
                except KeyError as exc:
                    raise LinkError(api + ": selected variants lack a comparable cycle model") from exc
                if type(mean) not in (float, int) or not math.isfinite(mean) or mean <= 0:
                    raise LinkError(api + ": invalid comparable cycle measurement")
                if zp_budget is not None and spec["zp"] > zp_budget:
                    continue
                # Even with unlimited cross-API sharing, a single source
                # requires its own raw code/data bytes and 32 public I/O B.
                raw_size = sum(n for _, n in spec["segments"])
                if ram_budget is not None and raw_size + 32 + spec["scratch"] > ram_budget:
                    continue
                candidates.append((item, workload_calls[api] * mean, raw_size))
            if not candidates:
                raise LinkError("No certified variant combination fits RAM/ZP budgets")
            candidates.sort(key=lambda c: (c[1], c[2], c[0][2]["zp"], c[0][1]))
            weighted_options.append(candidates)

        # Explore the most discriminating workloads first. A tight cycle
        # lower bound permits pruning entire shared-producer combinations.
        order = sorted(range(len(options)), key=lambda i: (
            -(max(c[1] for c in weighted_options[i]) -
              min(c[1] for c in weighted_options[i])),
            len(weighted_options[i]), i))
        suffix_min = [0.0] * (len(order) + 1)
        for depth in range(len(order) - 1, -1, -1):
            suffix_min[depth] = (suffix_min[depth+1] +
                                 min(c[1] for c in weighted_options[order[depth]]))
        # Only use RAM tie pruning when the primary score is provably
        # unchanged (all candidate values equal), or every weighted mean is
        # an exactly represented integer with an exactly summable total.
        # Fractional CPU means may round differently in API order, and a
        # tolerance-based RAM tie would incorrectly discard a faster result.
        uniform_cycles = all(len({c[1] for c in group}) == 1
                             for group in weighted_options)
        integer_cycles = (sum(max(c[1] for c in group)
                              for group in weighted_options) < 2**53 and
                          all(float(c[1]).is_integer() for group in weighted_options
                              for c in group))
        best_score = None
        best = None
        chosen = {}
        shared_seen = set()
        state_families = {}

        def search(depth, cycles, raw, zp, scratch):
            nonlocal best_score, best
            if zp_budget is not None and zp > zp_budget:
                return
            _, state_bytes = place_state(state_families, scratch_base, scratch)
            minimum_ram = raw + 32 + scratch + state_bytes
            if ram_budget is not None and minimum_ram > ram_budget:
                return
            if best_score is not None:
                floor = cycles + suffix_min[depth]
                # Pessimistic rounding safety: a lower bound must never
                # exclude a genuinely faster combination due to float noise.
                tolerance = 1e-12 * max(1.0, abs(floor), abs(best_score[0]))
                if floor > best_score[0] + tolerance:
                    return
                if minimum_ram > best_score[1] and (
                    uniform_cycles or (integer_cycles and floor >= best_score[0])):
                    return
            if depth == len(order):
                # Run the exact same layout, shared-state accounting and
                # lexicographic tie-break as the historical exhaustive loop.
                combination = tuple(chosen[api] for api in names)
                code = projected_end(code_base, place_modules(
                    unique_code_modules(combination), code_base)) - code_base
                _, state_allocated = place_state(
                    state_requirements(spec for _, _, spec in combination),
                    scratch_base, scratch)
                ram = code + 32 + scratch + state_allocated
                if ram_budget is not None and ram > ram_budget:
                    return
                actual_cycles = sum(workload_calls[api] * cycle_metrics[api][ident]
                                    for api, ident, _ in combination)
                fingerprint = tuple(ident for _, ident, _ in combination)
                score = (actual_cycles, ram, zp, fingerprint)
                if best_score is None or score < best_score:
                    best_score = score
                    best = {api: (ident, spec) for api, ident, spec in combination}
                return
            for item, contribution, size in weighted_options[order[depth]]:
                api, ident, spec = item
                key = shared_identity(item)
                additional = 0 if key is not None and key in shared_seen else size
                family = spec.get("state_family")
                if family:
                    count = spec.get("persistent_state")
                    if not isinstance(count, int) or count <= 0:
                        raise LinkError("Invalid persistent state requirement")
                    if family in state_families and state_families[family] != count:
                        raise LinkError("Conflicting persistent state resource contract")
                added_family = family is not None and family not in state_families
                if added_family:
                    state_families[family] = count
                if key is not None:
                    shared_seen.add(key)
                chosen[api] = item
                search(depth + 1, cycles + contribution, raw + additional,
                       max(zp, spec["zp"]), max(scratch, spec["scratch"]))
                del chosen[api]
                if key is not None and not any(
                    shared_identity(previous) == key for previous in chosen.values()):
                    shared_seen.remove(key)
                if added_family:
                    del state_families[family]

        search(0, 0.0, 0, 0, 0)
    else:
        # The full 56-operation resource frontier has over 143 million
        # combinations even after independent Pareto filtering. Search it
        # exactly without creating its Cartesian product. Partial code sizes
        # are raw unaligned *lower bounds*, never a substitute for the final
        # full page-aligned, shared-producer-aware physical linker layout.
        group_parent = list(range(len(options)))

        def find_group(i):
            while group_parent[i] != i:
                group_parent[i] = group_parent[group_parent[i]]
                i = group_parent[i]
            return i

        first_owner = {}
        for i, variants in enumerate(options):
            for item in variants:
                key = shared_identity(item)
                if key is not None:
                    if key in first_owner:
                        group_parent[find_group(i)] = find_group(first_owner[key])
                    else:
                        first_owner[key] = i
        groups = {i: find_group(i) for i in range(len(options))}
        resource_options = []
        for variants in options:
            ranked = []
            for item in variants:
                _, ident, spec = item
                # Any individual ZP demand above the global ceiling is
                # impossible in a feasible solution. Removing it before
                # lower-bound calculation tightens the exact search without
                # changing its admissible candidate set.
                if zp_budget is not None and spec["zp"] > zp_budget:
                    continue
                size = sum(n for _, n in spec["segments"])
                ranked.append((item, size, shared_identity(item)))
            if not ranked:
                raise LinkError("No certified variant combination fits RAM/ZP budgets")
            ranked.sort(key=lambda c: (
                (c[0][2]["zp"], c[1], c[0][2]["scratch"], c[0][1])
                if objective == "zp" else
                (c[1] + 8*c[0][2]["zp"] if objective == "balanced" else c[1],
                 c[1], c[0][2]["zp"], c[0][1])))
            resource_options.append(ranked)
        # Forced operations are assigned first: their code and shared keys
        # improve lower bounds immediately. Ties are deterministic.
        order = sorted(range(len(options)), key=lambda i: (
            len(resource_options[i]),
            -min(c[1] for c in resource_options[i]), i))
        best_score = None
        best = None
        chosen = {}
        state_families = {}

        # Integer bit identities avoid hashing producer tuples during search.
        keys = {key for candidates in resource_options
                for _, _, key in candidates if key is not None}
        key_bits = {key: 1 << i for i, key in enumerate(sorted(keys, key=repr))}
        bit_options = [[(item, size, key_bits.get(key, 0))
                        for item, size, key in candidates]
                       for candidates in resource_options]

        # Each shared producer appears in exactly one connected component.
        # Unlike the old per-component MAX(min API bytes), the dynamic
        # programme below proves the minimum *union* of source bytes needed
        # by all still-unassigned operations in that component. This is an
        # exact raw-code lower bound; table alignment can only add bytes.
        suffix_groups = []
        group_bits = {}
        for i, variants in enumerate(bit_options):
            mask = group_bits.get(groups[i], 0)
            for _, _, bit in variants:
                mask |= bit
            group_bits[groups[i]] = mask
        for depth in range(len(order) + 1):
            remaining = {}
            for i in order[depth:]:
                remaining.setdefault(groups[i], []).append(i)
            suffix_groups.append(tuple(
                (group, tuple(indices))
                for group, indices in sorted(remaining.items())))

        @lru_cache(maxsize=65536)
        def minimum_shared_bytes(indices, seen_mask):
            if not indices:
                return 0
            i, rest = indices[0], indices[1:]
            return min(
                (0 if bit and seen_mask & bit else size) +
                minimum_shared_bytes(rest, seen_mask | bit)
                for _, size, bit in bit_options[i])

        def consider_candidate(combination):
            nonlocal best_score, best
            z = max(spec["zp"] for _, _, spec in combination)
            temp = max(spec["scratch"] for _, _, spec in combination)
            if zp_budget is not None and z > zp_budget:
                return
            code = projected_end(code_base, place_modules(
                unique_code_modules(combination), code_base)) - code_base
            _, permanent = place_state(
                state_requirements(spec for _, _, spec in combination),
                scratch_base, temp)
            ram = code + 32 + temp + permanent
            if ram_budget is not None and ram > ram_budget:
                return
            if objective == "zp":
                metric = (z, ram, code)
            elif objective == "balanced":
                metric = (ram + 8*z, ram, z)
            else:
                metric = (ram, z, code)
            score = (*metric, tuple(ident for _, ident, _ in combination))
            if best_score is None or score < best_score:
                best_score = score
                best = {api: (ident, spec) for api, ident, spec in combination}

        # A feasible greedy layout is only an incumbent upper bound. Search
        # still runs to exact completion and can replace it, so a heuristic
        # can never silently replace resource-optimal selection.
        consider_candidate(tuple(group[0][0] for group in resource_options))

        def bound_prunes(low_ram, min_zp):
            if ram_budget is not None and low_ram > ram_budget:
                return True
            if zp_budget is not None and min_zp > zp_budget:
                return True
            if best_score is None:
                return False
            if objective == "zp":
                return ((min_zp > best_score[0]) or
                        (min_zp == best_score[0] and low_ram > best_score[1]))
            if objective == "balanced":
                floor = low_ram + 8 * min_zp
                return ((floor > best_score[0]) or
                        (floor == best_score[0] and low_ram > best_score[1]))
            return ((low_ram > best_score[0]) or
                    (low_ram == best_score[0] and min_zp > best_score[1]))

        def resource_search(depth, raw, zp, scratch, seen_mask):
            nonlocal best_score, best
            min_zp = zp
            min_scratch = scratch
            cheap = {}
            for i in order[depth:]:
                candidates = resource_options[i]
                min_zp = max(min_zp, min(item[2]["zp"] for item, _, _ in candidates))
                min_scratch = max(min_scratch,
                                  min(item[2]["scratch"] for item, _, _ in candidates))
                # Cheap legacy max-of-minima prunes first. Use the stronger
                # exact group DP only on branches that might improve the
                # incumbent, avoiding unnecessary memoization overhead.
                extra = min(0 if bit and seen_mask & bit else size
                            for _, size, bit in bit_options[i])
                group = groups[i]
                cheap[group] = max(cheap.get(group, 0), extra)
            _, persistent = place_state(state_families, scratch_base, min_scratch)
            quick_ram = raw + sum(cheap.values()) + 32 + min_scratch + persistent
            if bound_prunes(quick_ram, min_zp):
                return
            required_code = sum(
                minimum_shared_bytes(indices, seen_mask & group_bits[group])
                for group, indices in suffix_groups[depth])
            low_ram = raw + required_code + 32 + min_scratch + persistent
            if bound_prunes(low_ram, min_zp):
                return
            if depth == len(order):
                consider_candidate(tuple(chosen[api] for api in names))
                return
            for item, size, bit in bit_options[order[depth]]:
                api, _, spec = item
                family = spec.get("state_family")
                if family:
                    count = spec.get("persistent_state")
                    if not isinstance(count, int) or count <= 0:
                        raise LinkError("Invalid persistent state requirement")
                    if family in state_families and state_families[family] != count:
                        raise LinkError("Conflicting persistent state resource contract")
                added_family = family is not None and family not in state_families
                if added_family:
                    state_families[family] = count
                chosen[api] = item
                resource_search(depth + 1, raw + (0 if bit and seen_mask & bit else size),
                                max(zp, spec["zp"]), max(scratch, spec["scratch"]),
                                seen_mask | bit)
                del chosen[api]
                if added_family:
                    del state_families[family]

        resource_search(0, 0, 0, 0, 0)
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
    elif mod.get("operand_layout") == "nz":
        used |= {"INPUT_NUM", "OUTPUT_Z"}
    elif mod.get("operand_layout") == "muldiv16":
        used |= {"INPUT_X", "INPUT_Y", "OUTPUT_Z", "INPUT_NUM",
                 "INPUT_DIV", "OUTPUT_QUOT", "OUTPUT_REM"}
    elif mod.get("operand_layout") == "vec2":
        used |= {"INPUT_X"}
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
    workload_calls = None
    if plan["objective"] == "speed":
        workload_calls = plan.get("workload_calls")
        # Permit legacy single-operation plans without an explicit workload;
        # never infer equal call frequencies for multi-operation projects.
        if workload_calls is None and len(names) == 1:
            workload_calls = {names[0]: 1}
        if (not isinstance(workload_calls, dict) or set(workload_calls) != set(names)
            or any(type(x) is not int or not 1 <= x <= 1000000
                   for x in workload_calls.values())):
            raise LinkError("Speed builds require positive workload calls for every operation")
        measured = {
            "MATH_VEC2_NORMALIZE_Q8_8": (speed_vec2_stock.bench_vec2_normalize, "scratch", True),
            "MATH_DIST8_FAST": (speed_dist8_fast.bench_dist8_fast, "scratch", False),
            "MATH_SDIV8": (speed_sdiv8_shared.bench_sdiv8, "zp", False),
            "MATH_SMOD8": (speed_sdiv8_shared.bench_smod8, "zp", False),
            "MATH_SIN8": (speed_trig8.bench_sin8, "scratch", False),
            "MATH_COS8": (speed_trig8.bench_cos8, "scratch", False),
            "MATH_SINCOS8": (speed_trig8.bench_sincos8, "scratch", False),
            "MATH_UMUL8": (selective_speed.bench_umul8, "scratch", True),
            "MATH_SMUL8": (speed_smul8.bench_smul8, "scratch", False),
            "MATH_UMUL16": (selective_speed_umul16.bench_umul16, "scratch", False),
            "MATH_UMULDIV16": (speed_umuldiv16.bench_umuldiv16, "scratch", True),
            "MATH_SMULDIV16": (speed_smuldiv16.bench_smuldiv16, "scratch", True),
            "MATH_SMUL16": (speed_smul16.bench_smul16, "scratch", False),
            "MATH_SMUL16_SHR8": (speed_smul16_shr8.bench_smul16_shr8, "scratch", False),
            "MATH_UMUL24": (speed_umul24.bench_umul24, "scratch", True),
            "MATH_SMUL24": (speed_smul24.bench_smul24, "scratch", True),
            "MATH_UMUL16_SHR8": (selective_speed_umul16_shr8.bench_umul16_shr8, "scratch", False),
            "MATH_UMOD8": (selective_speed_umod8.bench_umod8, "zp", False),
            "MATH_UDIV8": (selective_speed_udiv8.bench_udiv8, "zp", False),
            "MATH_ISQRT32": (selective_speed_isqrt32.bench_isqrt32, "scratch", True),
            "MATH_UMUL32": (selective_speed_umul32.bench_umul32, "scratch", True),
            "MATH_SMUL32": (selective_speed_smul32.bench_smul32, "scratch", True),
            "MATH_UMUL32_READY": (speed32extras.bench_umul32_ready, "scratch", True),
            "MATH_SMUL32_READY": (speed32extras.bench_smul32_ready, "scratch", True),
            "MATH_UMUL32_SHR16": (speed32extras.bench_umul32_shr16, "scratch", True),
            "MATH_SMUL32_SHR16": (speed32extras.bench_smul32_shr16, "scratch", True),
            "MATH_UDIV16_SHL8": (speed_shl8.bench_udiv16_shl8, "scratch", True),
            "MATH_SDIV16_SHL8": (speed_signedshl8.bench_sdiv16_shl8, "scratch", True),
            "MATH_SDIV16": (speed_sdiv16shared.bench_sdiv16, "scratch", False),
            "MATH_SMOD16": (speed_sdiv16shared.bench_sdiv16, "scratch", False),
            "MATH_URECIP16_Q16": (speed_recip16.bench_urecip16_q16, "scratch", False),
            "MATH_UDIV32_16": (speed_u3216.bench_udiv32_16, "scratch", True),
            "MATH_SDIV32_16": (speed_s3216.bench_sdiv32_16, "scratch", True),
            "MATH_SMOD32_16": (speed_s3216.bench_smod32_16, "scratch", True),
            "MATH_SDIV32_32": (speed_s3232.bench_sdiv32_32, "scratch", True),
            "MATH_SMOD32_32": (speed_s3232.bench_smod32_32, "scratch", True),
            "MATH_UMOD32_16": (speed_u3216.bench_umod32_16, "scratch", True),
            "MATH_UDIV32_32": (speed_u3232.bench_udiv32_32, "scratch", True),
            "MATH_UMOD32_32": (speed_u3232.bench_umod32_32, "scratch", True),
            "MATH_UDIV24": (speed_u24.bench_udiv24, "scratch", True),
            "MATH_SDIV24": (speed_s24.bench_sdiv24, "scratch", True),
            "MATH_SMOD24": (speed_s24.bench_smod24, "scratch", True),
            "MATH_UMOD24": (speed_u24.bench_umod24, "scratch", True),
            "MATH_UMOD16": (speed_umod16.bench_umod16, "scratch", True),
            "MATH_DIST8_ACCURATE": (speed_dist8_accurate.bench_dist8_accurate, "scratch", True),
            "MATH_ATAN2_8": (speed_atan2.bench_atan2, "scratch", True),
            "MATH_UDIV16": (speed_udiv16.bench_udiv16, "scratch", True),
            "MATH_ISQRT16": (speed_isqrt16.bench_isqrt16, "scratch", True),
        }
        unavailable = sorted(set(names) - set(measured))
        if unavailable:
            raise LinkError("No authenticated matched-input speed basis for " +
                            ", ".join(unavailable) +
                            "; available: UMUL8, UMUL16, UMUL24, UMUL16_SHR8, UMOD8, UDIV8, ISQRT32, UMUL32, SMUL32, UMUL32_READY, SMUL32_READY, UMUL32_SHR16, SMUL32_SHR16, UDIV32_16, UMOD32_16, SDIV32_16, SMOD32_16, UDIV32_32, UMOD32_32, UDIV24, UMOD24, SDIV24, SMOD24, UMOD16, DIST8_ACCURATE, ATAN2_8, UDIV16, ISQRT16")
        models = {}
        per_operation_cycles = {}
        for api in names:
            benchmark, placement, need_zp = measured[api]
            try:
                if need_zp:
                    result = benchmark(MODULES[api], code, io,
                                       sb if placement == "scratch" else zb, root, zp=zb)
                else:
                    result = benchmark(MODULES[api], code, io,
                                       sb if placement == "scratch" else zb, root)
            except (ValueError, OSError, RuntimeError) as exc:
                raise LinkError(api + " cycle-model measurement failed: " + str(exc)) from exc
            if set(result.get("mean_cycles", {})) != set(MODULES[api]):
                raise LinkError(api + ": incomplete same-corpus cycle measurement")
            if not result.get("cpu_model_only", False) or not result.get("corpus_sha256"):
                raise LinkError(api + ": unqualified cycle provenance")
            models[api] = result
            per_operation_cycles[api] = result["mean_cycles"]
        if len(names) == 1:
            cycle_model = models[names[0]]  # Preserve existing manifest schema.
        else:
            cycle_model = {
                "basis": "per-operation identical-input CPU-model means, weighted call frequencies",
                "cpu_model_only": True,
                "native_hardware_timing": False,
                "code_placement_note": "Benchmark candidate sources assembled individually at requested code base; link order may relocate them",
                "workload_calls": dict(sorted(workload_calls.items())),
                "operations": models,
            }
    modules = choose(names, pins, plan["objective"], zp_budget, ram_budget,
                     code_base=code, cycle_metrics=per_operation_cycles,
                     scratch_base=sb, workload_calls=workload_calls)
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
        if module.get("smul8_qs") and set(x["source_path"] for x in dep_provenance) != {
                "tools/selective_fast_umul8.py",
                "tools/selective_smul8_qs_readonly.py"}:
            raise LinkError(api + ": read-only signed8 quarter-square source provenance missing")
        if module.get("smuldiv16_qsv2") and set(x["source_path"] for x in dep_provenance) != {
                "tools/selective_fast_umul8.py", "tools/selective_fast_umul16.py",
                "tools/selective_smul16_quartersquare.py",
                "tools/selective_v2_fast_u3216.py",
                "tools/research_signed_v2_u3216.py",
                "tools/selective_smuldiv16_qs_v2.py"}:
            raise LinkError(api + ": signed muldiv16 source provenance missing")
        if module.get("umuldiv16_qsv2") and set(x["source_path"] for x in dep_provenance) != {
                "tools/selective_fast_umul8.py",
                "tools/selective_fast_umul16.py",
                "tools/selective_v2_fast_u3216.py",
                "tools/selective_umuldiv16_qs_v2.py",
                "v2_pareto_fast/resident/modules/pareto_udiv32_16.a"}:
            raise LinkError(api + ": UMULDIV16 canonical QS/V2 source provenance missing")
        if module.get("fast_umul8") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_fast_umul8.py"]:
            raise LinkError(api + ": quarter-square table generator provenance missing")
        if module.get("fast31_umul32") and set(x["source_path"] for x in dep_provenance) != {
                "tools/selective_fast31_umul32.py",
                "v2_pareto_fast/resident/modules/pareto_umul32.a"}:
            raise LinkError(api + ": historical FAST31 generator/canonical provenance missing")
        if module.get("v2_umul24") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_v2_fast_umul24.py"]:
            raise LinkError(api + ": original V2 UMUL24 quarter-square relocator provenance missing")
        if module.get("smul16_shr8_qs") and set(x["source_path"] for x in dep_provenance) != {
                "tools/selective_fast_umul8.py", "tools/selective_fast_umul16.py",
                "tools/selective_smul16_quartersquare.py",
                "tools/selective_smul16_shr8_quartersquare.py"}:
            raise LinkError(api + ": signed SHR8 QS16 source provenance missing")
        if module.get("smul16_qs") and set(x["source_path"] for x in dep_provenance) != {
                "tools/selective_fast_umul8.py", "tools/selective_fast_umul16.py",
                "tools/selective_smul16_quartersquare.py"}:
            raise LinkError(api + ": signed 16-bit QS source/adapter provenance missing")
        if module.get("fast_umul16") and set(x["source_path"] for x in dep_provenance) != {
                "tools/selective_fast_umul8.py", "tools/selective_fast_umul16.py"}:
            raise LinkError(api + ": 16-bit quarter-square emitter provenance missing")
        if module.get("hybrid_u3232") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_hybrid_u3232.py",
                "tools/selective_v2_fast_u3216.py",
                "routines/standalone_lab/portable/div_u32_zptail.asm"]:
            raise LinkError(api + ": V2 32/32 hybrid donor/relocator provenance missing")
        if module.get("signed_hybrid_u3232") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_signed_hybrid_u3232.py",
                "tools/selective_hybrid_u3232.py",
                "tools/selective_v2_fast_u3216.py",
                "routines/standalone_lab/portable/div_u32_zptail.asm"]:
            raise LinkError(api + ": signed V2 32/32 hybrid donor/relocator provenance missing")
        if module.get("recip16_table") and [x["source_path"] for x in dep_provenance] != [
                "v3_reu_512k/standalone/recip_u16_u24_q16.asm"]:
            raise LinkError(api + ": V3 threshold table source provenance missing")
        if module.get("recip16_threshold") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_recip16_threshold.py",
                "v3_reu_512k/standalone/recip_u16_u24_q16.asm"]:
            raise LinkError(api + ": historical threshold donor/relocator provenance missing")
        if module.get("signed16_v2_shared") and set(x["source_path"] for x in dep_provenance) != {
                "tools/selective_v2_signed16_shared.py",
                "relocatable_source/v2_pareto_fast/udiv16_direct_fast.inc"}:
            raise LinkError(api + ": signed V2 16/16 shared donor provenance missing")
        if module.get("v2_signed_shifted16") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_v2_signed_shifted16.py", "tools/selective_v2_fast_u3216.py"]:
            raise LinkError(api + ": historical signed shifted16 source provenance missing")
        if module.get("v2_shifted_u3216") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_v2_shifted_u3216.py", "tools/selective_v2_fast_u3216.py"]:
            raise LinkError(api + ": V2 shifted public-source provenance missing")
        if module.get("v2_sizefast_u3216") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_v2_fast_u3216.py"]:
            raise LinkError(api + ": canonical V2 32/16 source relocation provenance missing")
        if module.get("signed_v2_u3216") and [x["source_path"] for x in dep_provenance] != [
                "tools/research_signed_v2_u3216.py", "tools/selective_v2_fast_u3216.py"]:
            raise LinkError(api + ": V2 signed magnitude canonical generator provenance missing")
        if module.get("udiv24_v2") and [x["source_path"] for x in dep_provenance] != [
                "relocatable_source/v2_pareto_fast/udiv24_direct_repose.inc",
                "tools/selective_udiv24_v2.py"]:
            raise LinkError(api + ": canonical V2 U24 source / relocation provenance missing")
        if module.get("isqrt32_v2") and [x["source_path"] for x in dep_provenance] != [
                "relocatable_source/v2_pareto_fast/isqrt32_direct_highword_normal.inc",
                "relocatable_source/v2_pareto_fast/math_relocatable.asm"]:
            raise LinkError(api + ": canonical V2 root32 seed/refinement provenance missing")
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
            if "atan2" in module or module.get("umuldiv16_qsv2") or module.get("smuldiv16_qsv2") or module.get("fast_umul8") or module.get("smul8_qs") or module.get("fast_umul16") or module.get("smul16_qs") or module.get("smul16_shr8_qs") or module.get("isqrt16") or module.get("umul8_v1") or module.get("seek8") or module.get("seek16") or module.get("vec2_stock") or module.get("fast31_umul32") or module.get("v2_umul24") or module.get("v2_sizefast_u3216") or module.get("v2_shifted_u3216") or module.get("recip16_threshold") or module.get("recip16_table") or module.get("v2_signed_shifted16") or module.get("signed16_v2_shared") or module.get("signed_v2_u3216") or module.get("hybrid_u3232") or module.get("signed_hybrid_u3232"):
                if "atan2" in module:
                    machine, entry, ranges, end = atan2.assemble(
                        module["atan2"], pc, io, root)
                elif module.get("isqrt16"):
                    machine, entry, ranges, end = sqrt16.assemble(pc, io, root)
                elif module.get("fast31_umul32"):
                    if module.get("fast31_shared"):
                        # The physical owner can be signed; retain BOTH labels
                        # for independently source-hash-authorized virtual exports.
                        locations_fast31, _ = fast31.layout(pc)
                        _, labels, _ = Assembler().assemble(fast31.render(
                            locations_fast31, io, zb, root, module["source"]))
                        machine, _, ranges, end = fast31.assemble(
                            pc, io, zb, root, source_path=module["source"],
                            entry_label="FAST_UMUL32_FAST31")
                        entry = labels[module["entry"]]
                    else:
                        machine, entry, ranges, end = fast31.assemble(
                            pc, io, zb, root, source_path=module["source"],
                            entry_label=module["entry"])
                elif module.get("v2_umul24"):
                    machine, labels, ranges, end = v2umul24.assemble(pc,io,zb,root)
                    entry = labels[module["entry"]]
                elif module.get("hybrid_u3232"):
                    machine, labels, ranges, end = hybrid_u3232.assemble(pc,io,zb,root)
                    entry = labels[module["entry"]]
                elif module.get("signed_hybrid_u3232"):
                    machine, labels, ranges, end = signed_u3232.assemble(pc,io,zb,root)
                    entry = labels[module["entry"]]
                elif module.get("recip16_table"):
                    machine, labels, ranges, end = recip_table.assemble_image(pc,io,root)
                    entry = labels[module["entry"]]
                elif module.get("recip16_threshold"):
                    machine, labels, ranges, end = recip_threshold.assemble_image(pc,io,sb,root)
                    entry = labels[module["entry"]]
                elif module.get("signed16_v2_shared"):
                    machine, labels, ranges, end = v2signed16.assemble_image(pc,io,sb,root)
                    entry = labels[module["entry"]]
                elif module.get("v2_signed_shifted16"):
                    machine, labels, ranges, end = signedshift.assemble_image(pc,io,zb,root)
                    entry = labels[module["entry"]]
                elif module.get("v2_shifted_u3216"):
                    machine, labels, ranges, end = v2shifted.assemble_image(pc,io,zb,root)
                    entry = labels[module["entry"]]
                elif module.get("v2_sizefast_u3216"):
                    machine, labels, ranges, end = v2u3216.assemble_image(pc,io,zb,root)
                    entry = labels[module["entry"]]
                elif module.get("signed_v2_u3216"):
                    machine, labels, _ = signedv2u3216.assemble(pc,io,zb,root)
                    entry = labels[module["entry"]]
                    end = pc + signedv2u3216.IMAGE_BYTES
                    ranges = [{"name": "KERNEL_CODE", "start": "$%04X" % pc,
                               "bytes": signedv2u3216.IMAGE_BYTES}]
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
                elif module.get("vec2_stock"):
                    # Preserve the certified stock-native page organization.
                    # Image is page-aligned and combines 2560 exact lookup
                    # bytes, the four quadrant code islands and final JMP.
                    pc = (pc + 255) & ~255
                    locations["KERNEL_CODE"] = pc
                    machine, labels, _ = Assembler().assemble(
                        relocate_source(module, locations, root))
                    entry = labels[module["entry"]]
                    end = pc + 3587
                    if entry != pc + 0x0E00:
                        raise LinkError("VEC2 normalized export is not at expected relocation")
                    ranges = [
                        {"name": "VEC2_LOG_RATIO", "start": "$%04X" % pc, "bytes": 1280},
                        {"name": "VEC2_QUADRANT_CODE", "start": "$%04X" % (pc+0x500), "bytes": 1024},
                        {"name": "VEC2_COMPONENTS", "start": "$%04X" % (pc+0x900), "bytes": 1280},
                        {"name": "VEC2_EXPORT", "start": "$%04X" % (pc+0xE00), "bytes": 3},
                    ]
                elif module.get("smul16_shr8_qs"):
                    machine, labels, ranges, end = qs16shr.assemble_image(pc,io,sb,root)
                    entry = labels[module["entry"]]
                elif module.get("smul16_qs"):
                    machine, labels, ranges, end = qs16signed.assemble_image(pc,io,sb,root)
                    entry = labels[module["entry"]]
                elif module.get("smul8_qs"):
                    machine, labels, ranges, end = smul8qs.assemble_image(pc,io,sb,root)
                    entry = labels[module["entry"]]
                elif module.get("smuldiv16_qsv2"):
                    machine, labels, ranges, end = signed_muldiv16qs.assemble_image(pc,io,zb,sb,root)
                    entry = labels[module["entry"]]
                elif module.get("umuldiv16_qsv2"):
                    machine, labels, ranges, end = muldiv16qs.assemble_image(pc,io,zb,sb,root)
                    entry = labels[module["entry"]]
                elif module.get("fast_umul16"):
                    machine, entry, ranges, end = fast16.assemble(
                        pc, io, sb, root, source_path=module["source"],
                        code_bytes=module["segments"][0][1],
                        entry_label=module["entry"])
                else:
                    machine, entry, ranges, end = fast8.assemble(pc, io, sb, root)
                expected = set(machine) if module.get("vec2_stock") else set()
                for seg in ([] if module.get("vec2_stock") else ranges):
                    start = int(seg["start"][1:], 16)
                    expected.update(range(start, start + seg["bytes"]))
                if not module.get("seek8") and not module.get("seek16") and not module.get("vec2_stock") and not module.get("fast31_shared") and not module.get("v2_umul24") and not module.get("v2_sizefast_u3216") and not module.get("v2_shifted_u3216") and not module.get("recip16_threshold") and not module.get("recip16_table") and not module.get("v2_signed_shifted16") and not module.get("signed16_v2_shared") and not module.get("signed_v2_u3216") and not module.get("hybrid_u3232") and not module.get("signed_hybrid_u3232"):
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
        "; UDIV32_16 and UMOD32_16: N32/D16 => Q32/R16 both outputs, C=1 on D=0.",
        "; UDIV16_SHL8: unsigned (N16 << 8)/D16 => Q24/R16, C=1 on D=0.",
        "; SDIV16/SMOD16: shared signed N16/D16 => Q16 truncated toward zero, R16 N-signed; D=0 C=1.",
        "; SDIV16_SHL8: signed (N16 << 8)/D16 => signed Q24 and R16 (N sign), C=1 for D=0.",
        "; SDIV24/SMOD24: signed N24/D24 => signed Q24/R24, shared code, D=0 C=1.",
        "; SDIV32_16/SMOD32_16: signed N32/D16 => Q32/R16, shared code, D=0 C=1.",
        "; SDIV32_32/SMOD32_32: signed N32/D32 => Q32/R32, shared code, D=0 C=1.",
        "; URECIP16_Q16: D16 => Q24 = floor(65536/D), C=1 on D=0; Q3/R unchanged.",
        "; Portable 32/16 source is the correctness fallback, not the resident speed champion.",
        "; UMOD8: low byte N/D => low byte R ONLY; Q untouched, C=1 if D=0.",
        "; UMOD8 V1 fast/fallback uses two writable immediate operands in RAM.",
        "; SDIV8/SMOD8: signed low byte N/D => signed low Q/R, both outputs written.",
        "; carry set iff D=0. UMOD leaves quotient untouched.",
        "; UMUL8: unsigned 8-bit MATH_X/Y => unsigned 16-bit MATH_Z;",
        "; UMUL16: unsigned 16-bit MATH_X/Y => unsigned 32-bit MATH_Z;",
        "; SMUL16: signed X16*Y16 => signed full 32-bit Z[0..3], C=0.",
        "; SMUL16_SHR8: signed (X16*Y16)>>8 => signed Z[0..2], C=0.",
        "; UMUL24: unsigned X24*Y24 => exact low 48-bit Z[0..5], Z[6..7] untouched.",
        "; UMUL32: unsigned X32*Y32 => exact full 64-bit Z[0..7], C=0.",
        "; UMUL32_SHR16: unsigned X32*Y32>>16 => exact unsigned Z[0..5], high Z volatile, C=0.",
        "; SMUL32: signed X32*Y32 => exact signed64 two\'s-complement Z[0..7], C=0.",
        "; SMUL32_SHR16: signed (X32*Y32)>>16 => low 48 bits in Z[0..5], C=0.",
        "; SMUL32_READY and UMUL32_READY: safe state-independent full64 fallbacks, not resident READY speed.",
        "; UMULDIV16 / SMULDIV16: full 32-bit signed/unsigned product divided by D16; Q32 R16, zero-div C=1.",
        "; VEC2_NORMALIZE_Q8_8: signed Q8.8 X/Y => unit Q1.15 Z[0..3], zero input C=1; stock log-ratio precision.",
        "; SMUL24: signed X24*Y24 => exact signed48 Z[0..5], Z[6..7] preserved.",
        "; UMUL16_SHR8: unsigned X16*Y16 >> 8 => low 24 bits MATH_Z, C=0.",
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
                       "tools/selective_speed.py", "tools/selective_speed_umul16_shr8.py",
                       "tools/selective_isqrt16.py",
                       "tools/selective_fast_umul16.py", "tools/selective_fast31_umul32.py",
                       "tools/selective_speed_umul32.py", "tools/selective_speed_smul32.py",
                       "tools/selective_speed_mul32_ready_shr16.py",
                       "tools/selective_speed_u3216.py",
                       "tools/selective_speed_u3232.py",
                       "tools/selective_speed_u24.py",
                       "tools/selective_speed_umod16.py",
                       "tools/selective_speed_dist8_accurate.py",
                       "tools/selective_speed_atan2.py",
                       "tools/selective_speed_udiv16.py",
                       "tools/selective_speed_isqrt16.py",
                       "tools/generate_selective_udiv16_v2.py",
                       "tools/selective_hybrid_u3232.py",
                       "tools/selective_v2_fast_u3216.py",
                       "tools/selective_speed_umul16.py",
                       "tools/selective_speed_umod8.py", "tools/selective_speed_udiv8.py",
                       "tools/selective_speed_isqrt32.py",
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
        "selection_basis": (("workload-weighted same-corpus per-operation CPU-model cycles"
                             if len(names) > 1 else
                             "same-corpus measured CPU-model cycles for " + names[0])
                            if cycle_model else
                            "global code/RAM/ZP resource optimization; cycle-speed not certified"),
        "cycle_model_benchmark": cycle_model,
        **({"workload_calls": dict(sorted(workload_calls.items())),
            "estimated_weighted_cycles": sum(
                workload_calls[api] * per_operation_cycles[api][ident]
                for api, (ident, _) in modules.items())}
           if workload_calls else {}),
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
