#!/usr/bin/env python3
"""Same-corpus full-public UDIV16_SHL8 speed qualification for both variants.

Measures the builder-linked historical V2 adapter, never the historical
resident record. All Q32/R16, carry, input-preservation and sentinel checks
run for both sources at the same code and I/O origins.
"""
from __future__ import annotations
import hashlib
import random
from pathlib import Path

from mini6502 import Assembler, CPU, load_sparse
import selective_linker as linker
import selective_v2_shifted_u3216 as shifted

BASIS = "cpu-model-udiv16-shl8-public-v2-source-384-v1"
FAST = "link:v2-shifted-public"
SMALL = "link:accumulator-remainder"
EXPECTED = frozenset((FAST, SMALL))
RESOURCES = {FAST: (2368, 12, 0), SMALL: (129, 0, 1)}
CORPUS_SHA256 = "f78373d1422f84e75a96f89e944e44e925cfae4f3531c66696cc5272fab39f6c"
EDGE = (0, 1, 2, 3, 7, 15, 127, 255, 256, 257, 32767, 32768, 65534, 65535)
DIVS = (0, 1, 2, 3, 7, 127, 255, 256, 257, 32768, 65535)
COUNT = 384


def corpus():
    rng = random.Random(0x168C2026)
    pairs = [(n, d) for n in EDGE for d in DIVS]
    pairs.extend((rng.randrange(65536), rng.randrange(65536))
                 for _ in range(COUNT-len(pairs)))
    assert len(pairs) == COUNT
    return pairs


def bench_udiv16_shl8(modules, code, io, scratch, root: Path, zp=0x50):
    if set(modules) != EXPECTED:
        raise ValueError("UDIV16_SHL8 Pareto source set changed; requalify")
    cases = corpus()
    digest = hashlib.sha256(b"".join(
        n.to_bytes(2, "little")+d.to_bytes(2, "little")
        for n, d in cases)).hexdigest()
    if digest != CORPUS_SHA256:
        raise ValueError("UDIV16_SHL8 public corpus changed")
    means, maxima, p95s, source_hashes = {}, {}, {}, {}
    for variant, mod in sorted(modules.items()):
        resource = (sum(n for _, n in mod["segments"]),
                    mod["zp"], mod["scratch"])
        if (resource != RESOURCES[variant] or
                bool(mod.get("v2_shifted_u3216")) != (variant == FAST)):
            raise ValueError("UDIV16_SHL8 source/resource contract changed")
        if variant == FAST:
            machine, labels, _, _ = shifted.assemble_image(code, io, zp, root)
        else:
            loc = {"KERNEL_CODE": code, "INPUT_NUM": io+16,
                   "INPUT_DIV": io+20, "OUTPUT_QUOT": io+24,
                   "OUTPUT_REM": io+28, "TEMP_RAM": scratch}
            machine, labels, _ = Assembler().assemble(
                linker.relocate_source(mod, loc, root))
        entry = labels[mod["entry"]]
        cpu = CPU(load_sparse(machine))
        sp = cpu.sp
        timings = []
        for i, (n, d) in enumerate(cases):
            nb = n.to_bytes(2, "little")+b"\x5a\xa5"
            db = d.to_bytes(2, "little")+b"\x69\xab"
            cpu.mem[io+16:io+20] = nb
            cpu.mem[io+20:io+24] = db
            cpu.mem[io+24:io+32] = b"\xcc"*4+b"\xdd\xdd\x49\x59"
            cpu.a = (n + i) & 255
            cpu.x = (d + i) & 255
            cpu.y = (n ^ d ^ i) & 255
            cpu.c = i & 1
            cpu.d = 0
            ticks = cpu.call(entry, 50000)
            q = int.from_bytes(cpu.mem[io+24:io+28], "little")
            rem = int.from_bytes(cpu.mem[io+28:io+30], "little")
            expected = ((n<<8)//d if d else 0,
                        (n<<8)%d if d else 0, int(d==0))
            if ((q, rem, cpu.c) != expected or cpu.sp != sp or
                    bytes(cpu.mem[io+16:io+20]) != nb or
                    bytes(cpu.mem[io+20:io+24]) != db or
                    bytes(cpu.mem[io+30:io+32]) != b"\x49\x59"):
                raise ValueError("UDIV16_SHL8 public semantics changed: "+
                                 repr((variant, n, d, (q,rem,cpu.c), expected)))
            timings.append(ticks)
        means[variant] = sum(timings)/COUNT
        maxima[variant] = max(timings)
        p95s[variant] = sorted(timings)[int(COUNT*0.95)-1]
        source_hashes[variant] = hashlib.sha256(
            (root/mod["source"]).read_bytes()).hexdigest()
    return {"basis": BASIS, "cases": COUNT, "corpus_sha256": digest,
            "cpu_model_only": True, "mean_cycles": means,
            "maximum_cycles": maxima, "p95_cycles": p95s,
            "source_sha256": source_hashes,
            "code_origin": "$%04X"%code, "io_origin": "$%04X"%io,
            "note": "Source-assembled full public Q32/R16/C calls at same origins; CPU model only, not physical PAL timing"}
