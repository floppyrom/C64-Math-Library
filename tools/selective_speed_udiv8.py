#!/usr/bin/env python3
"""Comparable, source-assembled CPU-model timing for historical C64 UDIV8.

Both V1 and V2/V5 are timed on exactly the same 1,000 numerator/divisor pairs
under the requested code / I/O / zero-page layout. No V1-V5 published
profile means are mixed into this model, and no native VICE speed claim is made.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import random
import re

from mini6502 import Assembler, CPU, load_sparse

BASIS = "cpu-model-udiv8-matched-small-divisor-v1"
SEED = 0xC648D80
EDGES = (0, 1, 2, 3, 7, 15, 16, 31, 32, 63, 64, 127, 128, 129, 254, 255)
COUNT = 1000
EXPECTED_VARIANTS = frozenset(("link:v1-resident-fast", "link:v2-v5-fast"))
EXPECTED_CORPUS_SHA256 = "86639c1545d78e6bbd95aab5db39d9a0b7d02cf9100e5ea41c863142cb975def"


def corpus():
    cases = [(n, d) for d in EDGES for n in EDGES]
    rng = random.Random(SEED)
    cases.extend((rng.randrange(256), rng.choice(range(1, 33)))
                 for _ in range(500))
    cases.extend((rng.randrange(256), rng.randrange(256))
                 for _ in range(COUNT - len(cases)))
    assert len(cases) == COUNT
    return cases


def bench_udiv8(modules, origin, io, zp, root: Path):
    if set(modules) != EXPECTED_VARIANTS:
        raise ValueError("UDIV8 variant set changed; requalify the matched corpus")
    cases = corpus()
    data = bytes(v for numerator, divisor in cases for v in (numerator, divisor))
    corpus_sha = hashlib.sha256(data).hexdigest()
    if corpus_sha != EXPECTED_CORPUS_SHA256:
        raise ValueError("UDIV8 matched-input corpus has changed")

    means, code_sizes, sources = {}, {}, {}
    for ident, mod in sorted(modules.items()):
        if mod["zp"] != 1 or mod["scratch"] or mod.get("requires_reu"):
            raise ValueError("UDIV8 C64 hardware/scratch contract changed: " + ident)
        path = root / mod["source"]
        program = path.read_text(encoding="utf-8")
        constants = {
            "KERNEL_CODE": origin,
            "INPUT_NUM": io + 16, "INPUT_DIV": io + 20,
            "OUTPUT_QUOT": io + 24, "OUTPUT_REM": io + 28,
            "TEMP_ZP": zp,
        }
        for symbol, value in constants.items():
            pattern = r"(?m)^" + re.escape(symbol) + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
            program, count = re.subn(
                pattern, symbol + " = $%04X" % value, program)
            if count != 1:
                raise ValueError("UDIV8 source binding is not unique: " + symbol)

        image, symbols, _ = Assembler().assemble(program)
        size = sum(length for _, length in mod["segments"])
        entry = symbols[mod["entry"]]
        if set(image) != set(range(origin, origin + size)) or entry != origin + 8:
            raise ValueError("UDIV8 linked source/entry geometry changed: " + ident)

        cpu = CPU(load_sparse(image))
        initial_sp = cpu.sp
        cycles = 0
        for numerator, divisor in cases:
            original_n = bytes((numerator, 0xa1, 0xb2, 0xc3))
            original_d = bytes((divisor, 0xd4, 0xe5, 0xf6))
            cpu.mem[io+16:io+20] = original_n
            cpu.mem[io+20:io+24] = original_d
            cpu.mem[io+24:io+28] = b"\x55" * 4
            cpu.mem[io+28:io+32] = b"\x66" * 4
            cpu.d = 0
            cpu.c = (numerator ^ divisor) & 1
            cycles += cpu.call(entry, 30000)
            want_q = numerator // divisor if divisor else 0
            want_r = numerator % divisor if divisor else 0
            if (cpu.mem[io+24], cpu.mem[io+28], cpu.c) != (
                    want_q, want_r, int(divisor == 0)):
                raise ValueError("UDIV8 quotient/remainder/carry failure: " +
                                 repr((ident, numerator, divisor)))
            if (cpu.mem[io+16:io+20] != original_n
                or cpu.mem[io+20:io+24] != original_d
                or cpu.mem[io+25:io+28] != b"\x55" * 3
                or cpu.mem[io+29:io+32] != b"\x66" * 3
                or cpu.sp != initial_sp):
                raise ValueError("UDIV8 public I/O or stack ABI violation: " + ident)
        means[ident] = cycles / len(cases)
        code_sizes[ident] = size
        sources[ident] = hashlib.sha256(path.read_bytes()).hexdigest()

    return {
        "basis": BASIS, "cases": len(cases),
        "corpus_sha256": corpus_sha, "cpu_model_only": True,
        "note": "Measured identical assembled-source 6502 calls; NOT native VICE "
                "cycle timing or a certified mixed-operation speed model",
        "code_origin": "$%04X" % origin,
        "io_origin": "$%04X" % io,
        "zp_origin": "$%02X" % zp,
        "mean_cycles": means,
        "code_bytes": code_sizes,
        "source_sha256": sources,
    }
