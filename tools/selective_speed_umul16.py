#!/usr/bin/env python3
"""Same-corpus CPU-model benchmark for source-linked UMUL16 alternatives.

Calls are measured on assembled source bytes at the requested memory map.
Results are CPU-model estimates, not independently timed native VICE cycles.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import random
import re

from mini6502 import Assembler, CPU, load_sparse
import selective_fast_umul16 as fast16

BASIS = "cpu-model-umul16-seeded-edge-uniform-v1"
SEED = 0xC64162026
EDGE = (0, 1, 2, 3, 7, 15, 16, 127, 128, 255, 256,
        257, 32767, 32768, 65534, 65535)
COUNT = 1000


def corpus():
    pairs = [(a, b) for a in EDGE for b in EDGE]
    rng = random.Random(SEED)
    pairs.extend((rng.randrange(65536), rng.randrange(65536))
                 for _ in range(COUNT - len(pairs)))
    assert len(pairs) == COUNT
    return pairs


def assemble_variant(ident, source, origin, io, scratch, root):
    if ident == "link:quarter-square":
        mem, entry, _, _ = fast16.assemble(origin, io, scratch, root)
        return mem, entry
    if ident != "link:compact-zerozp":
        raise ValueError("No comparable UMUL16 cycle basis for " + ident)
    program = (root / source).read_text(encoding="utf-8")
    values = {"KERNEL_CODE": origin, "INPUT_X": io,
              "INPUT_Y": io + 4, "OUTPUT_Z": io + 8, "TEMP_RAM": scratch}
    for label, value in values.items():
        regex = r"(?m)^" + re.escape(label) + r"\s*=\s*\$[0-9A-Fa-f]+\s*$"
        program, n = re.subn(regex, label + " = $%04X" % value, program)
        if n != 1:
            raise ValueError("Nonunique compact UMUL16 binding " + label)
    mem, labels, _ = Assembler().assemble(program)
    if set(mem) != set(range(origin, origin + 108)):
        raise ValueError("Compact UMUL16 benchmark source geometry changed")
    return mem, labels["FAST_UMUL16_COMPACT"]


def bench_umul16(modules, origin, io, scratch, root: Path):
    if set(modules) != {"link:compact-zerozp", "link:quarter-square"}:
        raise ValueError("UMUL16 source-set changed; requalify cycle comparison")
    pairs = corpus()
    checksum = hashlib.sha256(
        bytes(byte for x, y in pairs
              for byte in (*x.to_bytes(2, "little"), *y.to_bytes(2, "little")))
    ).hexdigest()
    means = {}
    sources = {}
    for ident, mod in sorted(modules.items()):
        mem, entry = assemble_variant(ident, mod["source"], origin, io,
                                      scratch, root)
        cpu = CPU(load_sparse(mem))
        sp = cpu.sp
        total = 0
        for x, y in pairs:
            cpu.mem[io:io+2] = x.to_bytes(2, "little")
            cpu.mem[io+4:io+6] = y.to_bytes(2, "little")
            cpu.mem[io+8:io+12] = b"\xaa" * 4
            cpu.c = (x ^ y) & 1
            cpu.d = 0
            total += cpu.call(entry, 2500)
            got = int.from_bytes(cpu.mem[io+8:io+12], "little")
            if got != x * y or cpu.c or cpu.sp != sp:
                raise ValueError("Invalid UMUL16 bench " +
                                 repr((ident, x, y, got, cpu.c, cpu.sp)))
            if cpu.mem[io:io+2] != x.to_bytes(2, "little") or (
                    cpu.mem[io+4:io+6] != y.to_bytes(2, "little")):
                raise ValueError("UMUL16 candidate clobbered caller input")
        means[ident] = total / len(pairs)
        sources[ident] = hashlib.sha256(
            (root / mod["source"]).read_bytes()).hexdigest()
    return {
        "basis": BASIS,
        "cases": len(pairs),
        "corpus_sha256": checksum,
        "cpu_model_only": True,
        "note": "Measured assembled-source call-through-RTS cycles; not native VICE timing",
        "code_origin": "$%04X" % origin,
        "io_origin": "$%04X" % io,
        "mean_cycles": means,
        "source_sha256": sources,
    }
