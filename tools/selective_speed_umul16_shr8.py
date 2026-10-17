#!/usr/bin/env python3
"""Same-input CPU-model benchmark for independently linked UMUL16_SHR8.

Time both complete public calls at the caller's actual link and I/O addresses.
Do not compare historical resident-profile cycle means to these measurements.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import random
import re
from mini6502 import Assembler, CPU, load_sparse
import selective_fast_umul16 as qs16

BASIS = "cpu-model-umul16-shr8-matched-edge-uniform-v1"
SEED = 0xC6416F08
EDGES = (0, 1, 2, 3, 7, 15, 16, 127, 128, 255,
         256, 257, 511, 32767, 32768, 65534, 65535)
COUNT = 1000

def corpus():
    rng = random.Random(SEED)
    pairs = [(a, b) for a in EDGES for b in EDGES]
    pairs += [(rng.randrange(65536), rng.randrange(65536))
              for _ in range(COUNT-len(pairs))]
    assert len(pairs) == COUNT
    return pairs

def assemble_variant(ident, mod, origin, io, scratch, root):
    if ident == "link:quarter-square":
        mem, entry, _, _ = qs16.assemble(
            origin, io, scratch, root, source_path=mod["source"],
            code_bytes=256, entry_label="FAST_UMUL16_SHR8_QUARTERSQUARE")
        return mem, entry
    if ident != "link:compact-zerozp":
        raise ValueError("Unqualified shifted-product cycle source: " + ident)
    program = (root / mod["source"]).read_text(encoding="utf-8")
    for label, value in {"KERNEL_CODE": origin, "INPUT_X": io,
                         "INPUT_Y": io+4, "OUTPUT_Z": io+8,
                         "TEMP_RAM": scratch}.items():
        expr = r"(?m)^" + re.escape(label) + r"\s*=\s*\$[0-9A-Fa-f]+\s*$"
        program, n = re.subn(expr, label + " = $%04X" % value, program)
        if n != 1:
            raise ValueError("Unqualified compact source constant: " + label)
    mem, labels, _ = Assembler().assemble(program)
    if set(mem) != set(range(origin, origin+126)):
        raise ValueError("Shifted-product compact source span changed")
    return mem, labels["FAST_UMUL16_SHR8_COMPACT"]

def bench_umul16_shr8(modules, origin, io, scratch, root: Path):
    if set(modules) != {"link:compact-zerozp", "link:quarter-square"}:
        raise ValueError("UMUL16_SHR8 source set changed; requalify measurements")
    pairs = corpus()
    checksum = hashlib.sha256(bytes(
        byte for x, y in pairs for byte in
        (*x.to_bytes(2, "little"), *y.to_bytes(2, "little")))).hexdigest()
    means, sources = {}, {}
    for ident, mod in sorted(modules.items()):
        mem, entry = assemble_variant(ident, mod, origin, io, scratch, root)
        cpu = CPU(load_sparse(mem))
        original = {addr: cpu.mem[addr] for addr in mem}
        stack = cpu.sp
        total = 0
        for x, y in pairs:
            cpu.mem[io:io+2] = x.to_bytes(2, "little")
            cpu.mem[io+4:io+6] = y.to_bytes(2, "little")
            cpu.mem[io+8:io+12] = bytes([0xA5]) * 4
            cpu.d = 0
            cpu.c = (x ^ y) & 1
            total += cpu.call(entry, 50000)
            got = int.from_bytes(cpu.mem[io+8:io+11], "little")
            expected = (x*y) >> 8
            if got != expected or cpu.c or cpu.sp != stack:
                raise ValueError("Invalid shifted result " +
                                 repr((ident, x, y, got, expected, cpu.c)))
            if (cpu.mem[io:io+2] != x.to_bytes(2, "little") or
                cpu.mem[io+4:io+6] != y.to_bytes(2, "little")):
                raise ValueError("UMUL16_SHR8 overwrote caller operands")
        if any(cpu.mem[addr] != value for addr, value in original.items()):
            raise ValueError("UMUL16_SHR8 changed executable source/tables")
        means[ident] = total / len(pairs)
        sources[ident] = hashlib.sha256(
            (root/mod["source"]).read_bytes()).hexdigest()
    return {
        "basis": BASIS, "cases": len(pairs),
        "corpus_sha256": checksum, "cpu_model_only": True,
        "note": "Matched-input source-assembled 6502 call-through-RTS cycles; native VICE verifies correctness, not timing",
        "code_origin": "$%04X" % origin,
        "io_origin": "$%04X" % io,
        "mean_cycles": means, "source_sha256": sources,
    }
