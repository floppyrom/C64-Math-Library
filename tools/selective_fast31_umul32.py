#!/usr/bin/env python3
"""Relocate public-ABI FAST31 UMUL32 from certified V2 native arithmetic source.

We intentionally reserve a 512-byte code island on the first port.  Tables
use four 512-byte page-aligned slots (511 data + one inert padding byte).
No caller initialization, resident profile, REU or stack-page dependency.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
from mini6502 import Assembler

SOURCE = "routines/multiply/umul32_fast31_public.asm"
CANONICAL = "v2_pareto_fast/resident/modules/pareto_umul32.a"
CODE_SLOT = 512
TABLE_SLOT = 512
TABLES = ("sqr_lo", "sqr_hi", "neg_sqr_lo", "neg_sqr_hi")
ZP_BYTES = 31

def layout(start):
    table_start = (start + CODE_SLOT + 255) & ~255
    positions = {"KERNEL_CODE": start}
    for j, name in enumerate(TABLES):
        positions[name] = table_start + j * TABLE_SLOT
    return positions, table_start + len(TABLES)*TABLE_SLOT

def tables():
    def q(i):
        return (i*i + 202*(i&1)) // 4
    lo = bytes(q(i)&255 for i in range(511))
    hi = bytes((q(i)>>8)&255 for i in range(511))
    neglo = bytes((255 - (q(255-i)&255))&255 for i in range(511))
    neghi = bytes((255 - ((q(255-i)>>8)&255))&255 for i in range(511))
    return (lo, hi, neglo, neghi)

def render(positions, io, zp, root, source_path=SOURCE):
    s = (root / source_path).read_text(encoding="utf-8")
    bindings = {"INPUT_X":io, "INPUT_Y":io+4, "OUTPUT_Z":io+8,
                "TEMP_ZP":zp, **positions}
    for key, value in bindings.items():
        pat = r"(?m)^"+re.escape(key)+r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        s, count = re.subn(pat, "%s = $%04X"%(key,value), s)
        if count != 1:
            raise ValueError("FAST31 missing/nonunique address: "+key)
    return s

def assemble(start, io, zp, root, *, source_path=SOURCE,
             entry_label="FAST_UMUL32_FAST31"):
    if not 2 <= zp <= 225 or zp+ZP_BYTES>256:
        raise ValueError("FAST31 requires 31 ordinary contiguous ZP bytes")
    positions, end = layout(start)
    if end > 65536:
        raise ValueError("FAST31 code+tables exceed 64KiB")
    code, labels, _ = Assembler().assemble(render(positions,io,zp,root,source_path))
    if not code or min(code)<start or max(code)>=start+CODE_SLOT:
        raise ValueError("FAST31 public/native code exceeds reserved code slot")
    if labels.get(entry_label)!=start:
        raise ValueError("FAST31 public entry moved")
    # Fill untouched code/padding to make a deterministic contiguous PRG image.
    image = {addr:0xea for addr in range(start,end)}
    image.update(code)
    for name, plane in zip(TABLES,tables()):
        base=positions[name]
        if len(plane)!=511 or base & 255:
            raise ValueError("FAST31 quarter-square page contract")
        for i,value in enumerate(plane):
            image[base+i]=value
        image[base+511]=0
    segments=[{"name":"KERNEL_CODE","start":"$%04X"%start,"bytes":CODE_SLOT},
              {"name":"ALIGN_PADDING","start":"$%04X"%(start+CODE_SLOT),
               "bytes":positions["sqr_lo"]-(start+CODE_SLOT)}]
    segments.extend({"name":name,"start":"$%04X"%positions[name],
                     "bytes":TABLE_SLOT} for name in TABLES)
    return image, labels[entry_label], segments, end

def source_sha256(root:Path, source_path=SOURCE):
    return hashlib.sha256((root/source_path).read_bytes()).hexdigest()
