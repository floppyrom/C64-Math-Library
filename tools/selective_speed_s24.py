#!/usr/bin/env python3
"""Matched, complete-public-call signed 24/24 division/modulo speed basis.

All three source-qualified variants execute exactly the same 512 signed
operand pairs at the requested memory map. We retain every resource Pareto
choice; old resident profile timings are never compared across corpora.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import random

from mini6502 import Assembler, CPU, load_sparse
import selective_linker as linker

CASES = 512
SEED = 0x5D24249
EDGES = (0, 1, 2, 3, 255, 65535, 65536,
         0x7fffff, 0x800000, 0x800001, 0xfffffe, 0xffffff)
EXPECTED_CORPUS_SHA256 = "429e92374a1b337cd0634f37be32afec5b3e79540a73dddf01d43a1b51f9a1fd"
BASIS = "cpu-model-signed24-public-Q24-R24-matched-512-v1"
APIS = frozenset(("MATH_SDIV24", "MATH_SMOD24"))
V3 = "link:v3-signed-magnitude"
PORTABLE = "link:portable-zerozp"
QZERO = "link:abs-qzero-guard"
VARIANTS = frozenset((V3, PORTABLE, QZERO))
RESOURCES = {V3: (1897, 9, 0), PORTABLE: (325, 0, 7),
             QZERO: (387, 0, 7)}


def corpus():
    rng = random.Random(SEED)
    pairs = [(n, d) for n in EDGES for d in EDGES]
    while len(pairs) < CASES:
        i = len(pairs)
        if i % 4 == 0:
            d = rng.randint(2, 0x7fffff)
            n = rng.randrange(d)
            if rng.randrange(2):
                n = (-n) & 0xffffff
            if rng.randrange(2):
                d = (-d) & 0xffffff
        elif i % 4 == 1:
            d = rng.randint(1, 256)
            n = rng.randrange(1 << 24)
            if rng.randrange(2):
                d = (-d) & 0xffffff
        else:
            n, d = rng.getrandbits(24), rng.getrandbits(24)
        pairs.append((n, d))
    return pairs


def signed(v):
    return v - (1 << 24) if v & 0x800000 else v


def reference(n, d):
    num, den = signed(n), signed(d)
    if den == 0:
        return 0, 0, 1
    q = abs(num) // abs(den)
    if (num < 0) != (den < 0):
        q = -q
    rem = num - q * den
    return q & 0xffffff, rem & 0xffffff, 0


def benchmark(api, modules, code, io, scratch, root: Path, zp=0x50):
    if api not in APIS or set(modules) != VARIANTS:
        raise ValueError("Signed24 speed candidate set changed; requalify")
    pairs = corpus()
    digest = hashlib.sha256(b"".join(
        n.to_bytes(3, "little") + d.to_bytes(3, "little")
        for n, d in pairs)).hexdigest()
    if len(pairs) != CASES or digest != EXPECTED_CORPUS_SHA256:
        raise ValueError("Signed24 deterministic corpus drifted")

    means, maxima, sources = {}, {}, {}
    for variant, mod in sorted(modules.items()):
        actual = (sum(v for _, v in mod["segments"]),
                  mod["zp"], mod["scratch"])
        if actual != RESOURCES[variant] or not mod.get("multi_entry"):
            raise ValueError("Signed24 source/resource contract drift: " + variant)
        if (variant == V3) != bool(mod.get("sdiv24_v3_relocated")):
            raise ValueError("Signed24 historical provenance drift")
        if variant == V3 and not mod.get("requires_writable_code"):
            raise ValueError("V3 signed24 SMC must remain declared")
        if variant != V3 and mod.get("requires_writable_code"):
            raise ValueError("Portable signed24 source unexpectedly needs SMC")
        locations = {
            "KERNEL_CODE": code, "INPUT_NUM": io + 16,
            "INPUT_DIV": io + 20, "OUTPUT_QUOT": io + 24,
            "OUTPUT_REM": io + 28,
        }
        locations["TEMP_ZP" if variant == V3 else "TEMP_RAM"] = (
            zp if variant == V3 else scratch)
        machine, labels, _ = Assembler().assemble(
            linker.relocate_source(mod, locations, root))
        if set(machine) != set(range(code, code + actual[0])):
            raise ValueError("Signed24 source geometry drift: " + variant)
        entry = labels[mod["entry"]]
        allowed_smc = ({labels["L8801_ADC_IMMEDIATE"] + 1}
                       if variant == V3 else set())
        cpu = CPU(load_sparse(machine))
        sp = cpu.sp
        cycles = []
        for i, (n, d) in enumerate(pairs):
            nb = n.to_bytes(3, "little") + b"\\x5a"
            db = d.to_bytes(3, "little") + b"\\xa5"
            cpu.mem[io+16:io+20] = nb
            cpu.mem[io+20:io+24] = db
            cpu.mem[io+24:io+28] = b"\\xcc\\xcc\\xcc\\x39"
            cpu.mem[io+28:io+32] = b"\\xdd\\xdd\\xdd\\x59"
            cpu.d, cpu.c = 0, (i ^ n ^ d) & 1
            cpu.a, cpu.x, cpu.y = (n ^ d) & 255, (n >> 8) & 255, (d >> 8) & 255
            taken = cpu.call(entry, 100000)
            got = (int.from_bytes(cpu.mem[io+24:io+27], "little"),
                   int.from_bytes(cpu.mem[io+28:io+31], "little"), cpu.c)
            if (got != reference(n, d) or cpu.sp != sp
                    or bytes(cpu.mem[io+16:io+20]) != nb
                    or bytes(cpu.mem[io+20:io+24]) != db
                    or cpu.mem[io+27] != 0x39 or cpu.mem[io+31] != 0x59):
                raise ValueError("Signed24 public ABI mismatch: " +
                                 repr((variant, hex(n), hex(d), got)))
            cycles.append(taken)
        altered = {address for address, orig in machine.items()
                   if cpu.mem[address] != orig}
        if not altered <= allowed_smc:
            raise ValueError("Unexpected signed24 source modification: " +
                             repr(sorted(altered - allowed_smc)))
        means[variant] = sum(cycles) / len(cycles)
        maxima[variant] = max(cycles)
        sources[variant] = hashlib.sha256(
            (root / mod["source"]).read_bytes()).hexdigest()
    return {
        "basis": BASIS + "-" + api.lower(),
        "cases": CASES, "corpus_sha256": digest,
        "cpu_model_only": True,
        "mean_cycles": means, "maximum_cycles": maxima,
        "source_sha256": sources,
        "code_origin": "$%04X" % code,
        "io_origin": "$%04X" % io,
        "note": "Complete public Q24/R24/C, signed domain, high-sentinel and input preserved; CPU model only, no physical VICE cycle claim",
    }


def bench_sdiv24(modules, code, io, scratch, root: Path, zp=0x50):
    return benchmark("MATH_SDIV24", modules, code, io, scratch, root, zp)


def bench_smod24(modules, code, io, scratch, root: Path, zp=0x50):
    return benchmark("MATH_SMOD24", modules, code, io, scratch, root, zp)
