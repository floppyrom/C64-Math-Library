#!/usr/bin/env python3
"""Research: source-linked signed 32/16 Q/R using the historical V2 fast U3216 core.

This is a qualified *candidate producer* only, not yet a selectable builder variant.
The original V2 source, immutable resident binaries and released ABIs are untouched.
The signed public adapter mirrors the V3 sign/magnitude strategy but delegates all
actual 32/16 division to the canonical independently relocatable V2 producer.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from mini6502 import Assembler
import selective_v2_fast_u3216 as unsigned

ROOT = Path(__file__).resolve().parents[1]
SIGNED_OFFSET = unsigned.IMAGE_BYTES       # after historical unsigned public adapter
SIGNED_SLOT = 0x200                       # explicit bounded independent signed code
IMAGE_BYTES = SIGNED_OFFSET + SIGNED_SLOT
ENTRY = "FAST_SDIV32_16_V2MAG"

SIGNED_BODY = """
FAST_SDIV32_16_V2MAG:
FAST_SMOD32_16_V2MAG:
    ; Public input N32, D16 unchanged. R high two bytes are not outputs.
    lda INPUT_DIV
    ora INPUT_DIV+1
    bne SF32_NONZERO
    lda #$00
    sta OUTPUT_QUOT
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    sta OUTPUT_QUOT+3
    sta OUTPUT_REM
    sta OUTPUT_REM+1
    sec
    rts

SF32_NONZERO:
    ; Signed absolute N -> V2 unsigned magnitude state, low to high.
    lda INPUT_NUM+3
    bmi SF32_N_NEG
SF32_N_POS:
    lda INPUT_NUM
    sta ln0
    lda INPUT_NUM+1
    sta ln1
    lda INPUT_NUM+2
    sta n0
    lda INPUT_NUM+3
    sta n1
    jmp SF32_N_DONE
SF32_N_NEG:
    lda #$00
    sec
    sbc INPUT_NUM
    sta ln0
    lda #$00
    sbc INPUT_NUM+1
    sta ln1
    lda #$00
    sbc INPUT_NUM+2
    sta n0
    lda #$00
    sbc INPUT_NUM+3
    sta n1
SF32_N_DONE:
    ; Signed absolute D -> the same private unsigned divisor.
    lda INPUT_DIV+1
    bmi SF32_D_NEG
SF32_D_POS:
    lda INPUT_DIV
    sta d0
    lda INPUT_DIV+1
    sta d1
    jmp SF32_D_DONE
SF32_D_NEG:
    lda #$00
    sec
    sbc INPUT_DIV
    sta d0
    lda #$00
    sbc INPUT_DIV+1
    sta d1
SF32_D_DONE:
    jsr div_u32_16

    ; Full signed quotient wraps in 32 bits (-2^31 / -1 included).
    lda INPUT_NUM+3
    eor INPUT_DIV+1
    bpl SF32_Q_POS
SF32_Q_NEG:
    lda #$00
    sec
    sbc lq0
    sta OUTPUT_QUOT
    lda #$00
    sbc lq1
    sta OUTPUT_QUOT+1
    lda #$00
    sbc q0
    sta OUTPUT_QUOT+2
    lda #$00
    sbc q1
    sta OUTPUT_QUOT+3
    jmp SF32_Q_DONE
SF32_Q_POS:
    lda lq0
    sta OUTPUT_QUOT
    lda lq1
    sta OUTPUT_QUOT+1
    lda q0
    sta OUTPUT_QUOT+2
    lda q1
    sta OUTPUT_QUOT+3
SF32_Q_DONE:
    ; Remainder always has the numerator's sign (truncate toward zero).
    lda INPUT_NUM+3
    bmi SF32_R_NEG
SF32_R_POS:
    lda r0
    sta OUTPUT_REM
    lda r1
    sta OUTPUT_REM+1
    clc
    rts
SF32_R_NEG:
    lda #$00
    sec
    sbc r0
    sta OUTPUT_REM
    lda #$00
    sbc r1
    sta OUTPUT_REM+1
    clc
    rts
"""


def source(code: int, io: int, zp: int, root: Path = ROOT) -> str:
    if code < 0x1000 or code + IMAGE_BYTES > 0x10000:
        raise ValueError("Historical magnitude image exceeds user RAM")
    return (unsigned.render(code, io, zp, root) +
            "\n* = $%04X\n" % (code + SIGNED_OFFSET) + SIGNED_BODY)


def assemble(code: int, io: int, zp: int, root: Path = ROOT):
    """Pack the authentic unsigned donor once; sign adaptation has own entry."""
    if not 0x02 <= zp <= 0xF4:
        raise ValueError("V2 shared magnitude needs twelve reserved ZP bytes")
    image, labels, _ = Assembler().assemble(source(code, io, zp, root))
    original, ulab, _ = unsigned.assemble(code, io, zp, root)
    if any(image[addr] != value for addr, value in original.items()):
        raise ValueError("Canonical V2 unsigned magnitude has been modified")
    if labels["FAST_UDIV32_16_V2"] != code + unsigned.WRAPPER_OFFSET:
        raise ValueError("Unsigned public ABI moved")
    if labels[ENTRY] != code + SIGNED_OFFSET or labels["FAST_SMOD32_16_V2MAG"] != labels[ENTRY]:
        raise ValueError("Signed public aliases no longer share one entry")
    signed_addresses = [a for a in image if a >= code + SIGNED_OFFSET]
    if (not signed_addresses or min(signed_addresses) != code + SIGNED_OFFSET
            or max(signed_addresses) >= code + IMAGE_BYTES):
        raise ValueError("Signed adapter no longer fits reserved executable slot")
    if min(image) != min(original):
        raise ValueError("Canonical donor origin moved")
    packed = {addr: 0xEA for addr in range(code, code + IMAGE_BYTES)}
    packed.update(image)
    return packed, labels, {
        "historical_unsigned_source_sha256": unsigned.source_sha256(root),
        "historical_magnitude_executable_bytes": len(original),
        "signed_adapter_bytes": len(signed_addresses),
        "image_span_bytes": IMAGE_BYTES,
        "scratch_zp_bytes": 12,
        "ordinary_ram_scratch_bytes": 0,
        "public_entries": [labels[ENTRY], labels["FAST_SMOD32_16_V2MAG"]],
        "source_sha256": hashlib.sha256(source(code, io, zp, root).encode()).hexdigest(),
    }


if __name__ == "__main__":
    for code, io, zp in ((0x8000, 0xC000, 0x50), (0x7123, 0xC040, 0x70)):
        image, labels, metadata = assemble(code, io, zp)
        print("SIGNED V2 3216 MAGNITUDE", hex(code), hex(labels[ENTRY]),
              metadata, flush=True)
