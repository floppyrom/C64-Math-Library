#!/usr/bin/env python3
"""Same-corpus CPU-model cycle sampling for selective UMUL8 variants.

Only a *single UMUL8* speed objective is qualified here. Numbers are
recomputed from the requested relocations and actual source bytes; they
are not copied from different historical profiles or from hardware VICE.
"""
from __future__ import annotations

import hashlib
import random
import re
from pathlib import Path

from mini6502 import Assembler, CPU, load_sparse
import selective_fast_umul8 as fast8
import selective_umul8_v1 as v1umul8

BASIS = "cpu-model-umul8-seeded-edge-and-uniform-v1-with-original-v1"
SEED = 0xC64B2026
EDGE = (0, 1, 2, 3, 15, 16, 127, 128, 254, 255)
COUNT = 1000


def corpus():
    pairs = [(x, y) for x in EDGE for y in EDGE]
    rng = random.Random(SEED)
    pairs.extend((rng.randrange(256), rng.randrange(256))
                 for _ in range(COUNT - len(pairs)))
    assert len(pairs) == COUNT
    return pairs


def assemble_variant(variant: str, source: str, origin: int,
                     io: int, scratch: int, root: Path, zp: int):
    if variant == "link:v1-resident-fast":
        mem, entry, _, _ = v1umul8.assemble(origin, io, zp, root)
        return mem, entry
    if variant == "link:quarter-square":
        mem, entry, _, _ = fast8.assemble(origin, io, scratch, root)
        return mem, entry
    if variant != "link:compact-zerozp":
        raise ValueError("No certified UMUL8 cycle basis for " + variant)
    code = (root / source).read_text(encoding="utf-8")
    symbols = {
        "KERNEL_CODE": origin,
        "INPUT_X": io,
        "INPUT_Y": io + 4,
        "OUTPUT_Z": io + 8,
        "TEMP_RAM": scratch,
    }
    for key, value in symbols.items():
        pattern = r"(?m)^" + re.escape(key) + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        code, n = re.subn(pattern, key + " = $%04X" % value, code)
        if n != 1:
            raise ValueError("Non-unique compact UMUL8 binding " + key)
    memory, labels, _ = Assembler().assemble(code)
    if set(memory) != set(range(origin, origin + 60)):
        raise ValueError("Compact UMUL8 binary geometry not preserved")
    return memory, labels["FAST_UMUL8_COMPACT"]


def bench_umul8(modules: dict, origin: int, io: int, scratch: int,
                root: Path, zp: int = 0x50):
    """Measure every known candidate on identical seeded 1000-pair corpus."""
    if set(modules) != {"link:compact-zerozp", "link:quarter-square",
                        "link:v1-resident-fast"}:
        raise ValueError("UMUL8 measured speed source set has changed")
    cases = corpus()
    checksum = hashlib.sha256(bytes(byte for x, y in cases
                                    for byte in (x, y))).hexdigest()
    costs = {}
    source_provenance = {}
    for ident, mod in sorted(modules.items()):
        source_path = root / mod["source"]
        mem, entry = assemble_variant(
            ident, mod["source"], origin, io, scratch, root, zp)
        cpu = CPU(load_sparse(mem))
        stack = cpu.sp
        cycles = 0
        for x, y in cases:
            cpu.mem[io] = x
            cpu.mem[io+4] = y
            cpu.mem[io+8] = 0x55
            cpu.mem[io+9] = 0x55
            cpu.d = 0
            cpu.c = (x ^ y) & 1
            cycles += cpu.call(entry, 1200)
            result = cpu.mem[io+8] | (cpu.mem[io+9] << 8)
            if result != x*y or cpu.c or cpu.sp != stack or (
                    cpu.mem[io], cpu.mem[io+4]) != (x, y):
                raise ValueError("Invalid UMUL8 benchmark result for " +
                                 ident + ": " + repr((x, y, result)))
        costs[ident] = cycles / len(cases)
        source_provenance[ident] = hashlib.sha256(
            source_path.read_bytes()).hexdigest()
    return {
        "basis": BASIS,
        "cases": len(cases),
        "corpus_sha256": checksum,
        "cpu_model_only": True,
        "note": "Measured source-assembled call-through-RTS CPU cycles, not native hardware cycles",
        "code_origin": "$%04X" % origin,
        "io_origin": "$%04X" % io,
        "mean_cycles": costs,
        "source_sha256": source_provenance,
    }
