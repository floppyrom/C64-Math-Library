#!/usr/bin/env python3
"""Source-linked V2 32/16 donor with an exact shifted-16 public adapter.

This is a research candidate until matched public-call and native VICE
qualification; never compare its native-only historical timings to the portable
public adapter.  Both N16 source bytes and N[2:4] sentinels stay unchanged.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from mini6502 import Assembler
import selective_v2_fast_u3216 as donor

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "FAST_UDIV16_SHL8_V2"
BYTES = donor.IMAGE_BYTES
CUT = "\n* = KERNEL_WRAPPER\nFAST_UDIV32_16_V2:\nFAST_UMOD32_16_V2:\n"

# The 32-bit dividend is 00:N_hi:N_lo:00.  In native donor state,
# n1:n0 is the high word and ln1:ln0 the low word.
# Staging two zero bytes once avoids the generic widening/restore adapter.
ADAPTER = """* = KERNEL_WRAPPER
FAST_UDIV16_SHL8_V2:
    lda #0
    sta ln0
    sta n1
    lda INPUT_NUM
    sta ln1
    lda INPUT_NUM+1
    sta n0
    lda INPUT_DIV
    sta d0
    lda INPUT_DIV+1
    sta d1
    jsr div_u32_16
    lda lq0
    sta OUTPUT_QUOT
    lda lq1
    sta OUTPUT_QUOT+1
    lda q0
    sta OUTPUT_QUOT+2
    lda q1
    sta OUTPUT_QUOT+3
    lda r0
    sta OUTPUT_REM
    lda r1
    sta OUTPUT_REM+1
    rts
"""


def render(code: int, io: int, zp: int, root: Path = ROOT) -> str:
    full = donor.render(code, io, zp, root)
    if full.count(CUT) != 1:
        raise ValueError("Canonical V2 32/16 wrapper boundary changed")
    header, previous = full.split(CUT, 1)
    if not previous.strip().endswith("rts"):
        raise ValueError("Canonical V2 wrapper unexpectedly changed")
    return header + "\n" + ADAPTER


def assemble_image(code: int, io: int, zp: int, root: Path = ROOT):
    cg, mx, wrapper = donor.layout(code)
    sparse, labels, _ = Assembler().assemble(render(code, io, zp, root))
    if labels.get(ENTRY) != wrapper:
        raise ValueError("Shifted V2 public entry was not relocated")
    if not (sparse and min(sparse) == cg
            and max(sparse) < wrapper + donor.PUBLIC_CODE_BYTES):
        raise ValueError("Historical V2 code islands or wrapper overflowed")
    for lo, hi in ((cg, mx), (mx, wrapper), (wrapper, wrapper + 64)):
        addresses = sorted(a for a in sparse if lo <= a < hi)
        if not addresses or addresses != list(range(lo, lo + len(addresses))):
            raise ValueError("Historical V2 source island not contiguous")
    end = code + BYTES
    if not all(code <= a < end for a in sparse):
        raise ValueError("Shifted V2 image left reserved RAM")
    image = {a: 0xea for a in range(code, end)}
    image.update(sparse)
    ranges = [{"name": "KERNEL_CODE", "start": "$%04X" % code,
               "bytes": BYTES}]
    return image, labels, ranges, end


def provenance(root: Path = ROOT):
    return {
        "historical_v2_sha256": donor.source_sha256(root),
        "shifted_relocator_sha256": hashlib.sha256(
            (root / "tools/selective_v2_shifted_u3216.py").read_bytes()
        ).hexdigest(),
    }


if __name__ == "__main__":
    for code, io, zp in ((0x8000, 0xc000, 0x50),
                         (0x7123, 0xc040, 0x70)):
        image, labels, _, end = assemble_image(code, io, zp)
        print("V2 SHL8 historical source", hex(code), len(image),
              "entry", hex(labels[ENTRY]), "end", hex(end))
