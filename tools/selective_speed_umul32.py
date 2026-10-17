#!/usr/bin/env python3
"""Matched-operand CPU-model speed basis for three source-linked UMUL32 kernels.

All candidates run the identical full64 public ABI. Historic profile-specific
means are intentionally excluded. Supports CPU speed selection, not a native
VICE cycle claim or a guarantee for special application operand distributions.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import random
import re
from mini6502 import Assembler, CPU, load_sparse
import selective_fast_umul16 as quarter

BASIS = "cpu-model-umul32-full64-source-linked-identical-inputs-v1"
SEED = 0xC6432A
EDGES = (0, 1, 2, 255, 256, 65535, 0x80000000, 0xffffffff)
COUNT = 192
CORPUS_SHA256 = "65625f8a89189164c4ac974a166ec5eb6cd677d0159489ddf4d9a4100f05f923"
EXPECTED = frozenset(("link:compact-zerozp", "link:unified-375",
                     "link:quarter-square-32"))
EXPECTED_RESOURCES = {
    "link:compact-zerozp": (204, 0, 12),
    "link:unified-375": (375, 0, 12),
    "link:quarter-square-32": (2050, 0, 4),
}


def corpus():
    rng = random.Random(SEED)
    pairs = [(x, y) for x in EDGES for y in EDGES]
    pairs += [(rng.getrandbits(32), rng.getrandbits(32))
              for _ in range(COUNT - len(pairs))]
    assert len(pairs) == COUNT
    return pairs


def source_assemble(ident, mod, origin, io, scratch, root):
    if ident == "link:quarter-square-32":
        memory, entry, segments, end = quarter.assemble(
            origin, io, scratch, root, source_path=mod["source"],
            code_bytes=mod["segments"][0][1], entry_label=mod["entry"])
        if end - origin != 2050:
            raise ValueError("UMUL32 quarter-square geometry changed")
        return memory, entry
    source = (root / mod["source"]).read_text(encoding="utf-8")
    for symbol, addr in {
        "KERNEL_CODE": origin,
        "INPUT_X": io, "INPUT_Y": io + 4, "OUTPUT_Z": io + 8,
        "TEMP_RAM": scratch,
    }.items():
        pattern = r"(?m)^" + re.escape(symbol) + r"\s*=\s*\$[0-9A-Fa-f]+\s*$"
        source, count = re.subn(pattern, symbol + " = $%04X" % addr, source)
        if count != 1:
            raise ValueError("UMUL32 source binding changed: " + symbol)
    memory, labels, _ = Assembler().assemble(source)
    expected = EXPECTED_RESOURCES[ident][0]
    if set(memory) != set(range(origin, origin + expected)):
        raise ValueError("UMUL32 candidate geometry changed: " + ident)
    if labels[mod["entry"]] != origin:
        raise ValueError("UMUL32 entry moved: " + ident)
    return memory, labels[mod["entry"]]


def bench_umul32(modules, origin, io, scratch, root: Path):
    if set(modules) != EXPECTED:
        raise ValueError("UMUL32 candidate set changed; requalify matched basis")
    pairs = corpus()
    digest = hashlib.sha256(b"".join(
        x.to_bytes(4, "little") + y.to_bytes(4, "little") for x, y in pairs
    )).hexdigest()
    if digest != CORPUS_SHA256:
        raise ValueError("UMUL32 deterministic corpus changed")
    cycles, hashes = {}, {}
    for ident, mod in sorted(modules.items()):
        resources = (sum(size for _, size in mod["segments"]),
                     mod["zp"], mod["scratch"])
        if resources != EXPECTED_RESOURCES[ident]:
            raise ValueError("UMUL32 candidate resources changed: " + ident)
        if mod.get("requires_reu") or mod.get("requires_writable_code"):
            raise ValueError("UMUL32 candidate hardware contract changed")
        memory, entry = source_assemble(ident, mod, origin, io, scratch, root)
        cpu = CPU(load_sparse(memory))
        image = {addr: byte for addr, byte in memory.items()}
        stack = cpu.sp
        total = 0
        for i, (x, y) in enumerate(pairs):
            xb, yb = x.to_bytes(4, "little"), y.to_bytes(4, "little")
            cpu.mem[io:io+4] = xb
            cpu.mem[io+4:io+8] = yb
            cpu.mem[io+8:io+16] = b"\xa5" * 8
            cpu.d = 0
            cpu.c = (i ^ x ^ y) & 1
            total += cpu.call(entry, 125000)
            actual = int.from_bytes(cpu.mem[io+8:io+16], "little")
            if (actual != x*y or cpu.c or cpu.sp != stack
                or cpu.mem[io:io+4] != xb or cpu.mem[io+4:io+8] != yb):
                raise ValueError("UMUL32 speed candidate failed public ABI: " +
                                 repr((ident, hex(x), hex(y), actual)))
        if any(cpu.mem[addr] != value for addr, value in image.items()):
            raise ValueError("UMUL32 executable/tables modified: " + ident)
        cycles[ident] = total / COUNT
        hashes[ident] = hashlib.sha256((root / mod["source"]).read_bytes()).hexdigest()
    return {
        "basis": BASIS,
        "cases": COUNT, "corpus_sha256": digest,
        "cpu_model_only": True,
        "note": "Matched full64 32x32 source-assembled calls through RTS; no native hardware cycle claim",
        "code_origin": "$%04X" % origin,
        "io_origin": "$%04X" % io,
        "scratch_origin": "$%04X" % scratch,
        "mean_cycles": cycles, "source_sha256": hashes,
    }
