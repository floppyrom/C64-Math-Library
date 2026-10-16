#!/usr/bin/env python3
"""Authenticated same-corpus source-assembled UMOD8 cycle basis for speed selection.

Only source-assembled NMOS 6502 CPU-model estimates, never native VICE timings.
The fixed, deliberately small-divisor-weighted corpus is exactly the one used
by the qualifying V1/V2/V5 benchmark in tools/test_selective_umod8_speed.py.
Every measured call validates the public ABI, stack and zero-divisor carry.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import random
import re

from mini6502 import Assembler, CPU, load_sparse

BASIS = "cpu-model-umod8-same-input-small-divisor-v1"
SEED = 0xC6450D8
EDGES = (0, 1, 2, 3, 7, 15, 16, 31, 32, 63, 64, 127, 128, 255)
COUNT = 1000
EXPECTED_VARIANTS = frozenset((
    "link:v1-fast-fallback", "link:v2-unrolled-fallback",
    "link:v5-unrolled-hybrid",
))
EXPECTED_CORPUS_SHA256 = "9842b98d29eb3e842c8bb1632e9b627d645ad057a866804fbbda42eec0572fc9"


def corpus():
    rng = random.Random(SEED)
    cases = [(n, d) for d in EDGES for n in EDGES]
    cases.extend((rng.randrange(256), rng.choice(range(3, 32)))
                 for _ in range(500))
    cases.extend((rng.randrange(256), rng.randrange(256))
                 for _ in range(COUNT - len(cases)))
    assert len(cases) == COUNT
    return cases


def bench_umod8(modules, origin, io, zp, root: Path):
    """Measure all available implementations, even when RAM budget excludes some.

    The linker applies per-variant constraints *after* collecting comparable
    cycle estimates, so a smaller eligible producer remains an option.
    """
    if set(modules) != EXPECTED_VARIANTS:
        raise ValueError("UMOD8 variant set changed; matched benchmark must be requalified")
    pairs = corpus()
    checksum = hashlib.sha256(bytes(v for n, d in pairs for v in (n, d))).hexdigest()
    if checksum != EXPECTED_CORPUS_SHA256:
        raise ValueError("UMOD8 matching benchmark operand corpus changed")

    averages, sizes, source_hashes = {}, {}, {}
    for ident, mod in sorted(modules.items()):
        if not mod.get("requires_writable_code") or mod["zp"] != 2:
            raise ValueError("UMOD8 writable-code/ZP source contract changed: " + ident)
        path = root / mod["source"]
        src = path.read_text(encoding="utf-8")
        values = {
            "KERNEL_CODE": origin, "INPUT_NUM": io + 16,
            "INPUT_DIV": io + 20, "OUTPUT_REM": io + 28, "TEMP_ZP": zp,
        }
        for symbol, address in values.items():
            pattern = r"(?m)^" + re.escape(symbol) + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
            src, n = re.subn(pattern, symbol + " = $%04X" % address, src)
            if n != 1:
                raise ValueError("UMOD8 benchmark symbol binding is not unique: " + symbol)
        image, symbols, _ = Assembler().assemble(src)
        length = sum(n for _, n in mod["segments"])
        entry = symbols[mod["entry"]]
        if set(image) != set(range(origin, origin + length)) or entry != origin:
            raise ValueError("UMOD8 source geometry changed: " + ident)
        cpu = CPU(load_sparse(image))
        sp, total = cpu.sp, 0
        for numerator, divisor in pairs:
            cpu.mem[io+16:io+20] = bytes((numerator, 0xa1, 0xb2, 0xc3))
            cpu.mem[io+20:io+24] = bytes((divisor, 0xd4, 0xe5, 0xf6))
            cpu.mem[io+24:io+28] = b"\x55" * 4
            cpu.mem[io+28:io+32] = b"\x66" * 4
            cpu.d = 0
            cpu.c = (numerator ^ divisor) & 1
            total += cpu.call(entry, 30000)
            expected = numerator % divisor if divisor else 0
            if cpu.mem[io+28] != expected or cpu.c != int(divisor == 0):
                raise ValueError("UMOD8 arithmetic/carry failure " +
                                 repr((ident, numerator, divisor)))
            if (cpu.mem[io+16:io+20] != bytes((numerator, 0xa1, 0xb2, 0xc3))
                or cpu.mem[io+20:io+24] != bytes((divisor, 0xd4, 0xe5, 0xf6))
                or cpu.mem[io+24:io+28] != b"\x55" * 4
                or cpu.mem[io+29:io+32] != b"\x66" * 3
                or cpu.sp != sp):
                raise ValueError("UMOD8 public I/O or stack ABI violated: " + ident)
        averages[ident] = total / len(pairs)
        sizes[ident] = length
        source_hashes[ident] = hashlib.sha256(path.read_bytes()).hexdigest()

    return {
        "basis": BASIS,
        "cases": len(pairs),
        "corpus_sha256": checksum,
        "cpu_model_only": True,
        "note": "Same source-assembled 6502 input corpus, not VICE hardware timing; "
                "does not certify mixed-operation speed ranking",
        "code_origin": "$%04X" % origin,
        "io_origin": "$%04X" % io,
        "zp_origin": "$%02X" % zp,
        "mean_cycles": averages,
        "code_bytes": sizes,
        "source_sha256": source_hashes,
    }
