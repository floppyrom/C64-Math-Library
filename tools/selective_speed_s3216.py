#!/usr/bin/env python3
"""Same-corpus full public-call signed 32/16 speed model, Q32/R16/C.

A historical native-only resident mean must never enter the selector.
Both candidates are source-assembled at the requested placement and
measured across exactly the original 384 matched signed research cases.
"""
from __future__ import annotations

import hashlib
import random
import re
from pathlib import Path

from mini6502 import Assembler, CPU, load_sparse
import research_signed_v2_u3216 as donor

BASIS = "cpu-model-signed3216-paired-public-v2-mag-v1"
CASES = 384
SEED = 0x5D321603
N_EDGE = (0, 1, 2, 3, 127, 255, 65535, 65536, 65537,
          0x7fffffff, 0x80000000, 0x80000001, 0xfffffffe, 0xffffffff)
D_EDGE = (0, 1, 2, 3, 127, 128, 255, 256, 32767, 32768, 32769, 65534, 65535)
CORPUS_SHA256 = "6b35c319b133bc6c32e45ce5d9a9f0ff59e05dd24fbc739192db80916dc46d1e"
VARIANTS = frozenset(("link:portable-zerozp", "link:v2-signed-magnitude"))
APIS = frozenset(("MATH_SDIV32_16", "MATH_SMOD32_16"))
RESOURCE = {"link:portable-zerozp": (260, 0, 3),
            "link:v2-signed-magnitude": (2880, 12, 0)}


def corpus():
    rng = random.Random(SEED)
    cases = [(n, d) for n in N_EDGE for d in D_EDGE]
    cases.extend((rng.getrandbits(32), rng.getrandbits(16))
                 for _ in range(CASES - len(cases)))
    assert len(cases) == CASES
    return cases


def reference(n, d):
    num = n - (1 << 32) if n & 0x80000000 else n
    den = d - (1 << 16) if d & 0x8000 else d
    if den == 0:
        return 0, 0, 1
    quotient = abs(num) // abs(den)
    if (num < 0) != (den < 0):
        quotient = -quotient
    remainder = num - quotient * den
    return quotient & 0xffffffff, remainder & 0xffff, 0


def assemble(ident, mod, code, io, scratch, zp, root):
    if ident == "link:v2-signed-magnitude":
        image, labels, metadata = donor.assemble(code, io, zp, root)
        if metadata["image_span_bytes"] != RESOURCE[ident][0]:
            raise ValueError("Historical signed32/16 donor span changed")
        return image, labels[mod["entry"]]
    source = (root / mod["source"]).read_text(encoding="utf-8")
    bindings = {"KERNEL_CODE": code, "INPUT_NUM": io + 16,
                "INPUT_DIV": io + 20, "OUTPUT_QUOT": io + 24,
                "OUTPUT_REM": io + 28, "TEMP_RAM": scratch}
    for name, address in bindings.items():
        pat = r"(?m)^" + name + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        source, n = re.subn(pat, name + " = $%04X" % address, source)
        if n != 1:
            raise ValueError("Portable signed32/16 relocation failed: " + name)
    image, labels, _ = Assembler().assemble(source)
    if set(image) != set(range(code, code + 260)):
        raise ValueError("Portable signed32/16 source span changed")
    return image, labels[mod["entry"]]


def benchmark(api, modules, code, io, scratch, root: Path, zp=0x50):
    if api not in APIS or set(modules) != VARIANTS:
        raise ValueError("Signed 32/16 comparable source-set changed")
    pairs = corpus()
    digest = hashlib.sha256(b"".join(
        n.to_bytes(4, "little") + d.to_bytes(2, "little")
        for n, d in pairs)).hexdigest()
    if digest != CORPUS_SHA256:
        raise ValueError("Signed 32/16 benchmark corpus changed")
    means, maximums, hashes = {}, {}, {}
    for ident, mod in sorted(modules.items()):
        size = sum(n for _, n in mod["segments"])
        if ((size, mod["zp"], mod["scratch"]) != RESOURCE[ident] or
                not mod.get("multi_entry") or
                (ident == "link:v2-signed-magnitude") != bool(mod.get("signed_v2_u3216"))):
            raise ValueError("Signed 32/16 variant contract changed: " + ident)
        image, entry = assemble(ident, mod, code, io, scratch, zp, root)
        cpu = CPU(load_sparse(image))
        sp = cpu.sp
        original = {address: cpu.mem[address] for address in image}
        times = []
        for i, (n, d) in enumerate(pairs):
            nbytes = n.to_bytes(4, "little")
            dbytes = d.to_bytes(2, "little") + b"\x7c\x6b"
            cpu.mem[io+16:io+20] = nbytes
            cpu.mem[io+20:io+24] = dbytes
            cpu.mem[io+24:io+28] = b"\xcc"*4
            cpu.mem[io+28:io+32] = b"\xdd\xdd\x49\x59"
            cpu.a, cpu.x, cpu.y = (n ^ d) & 255, (n >> 8) & 255, (d >> 8) & 255
            cpu.d, cpu.c = 0, i & 1
            cycles = cpu.call(entry, 150000)
            got = (int.from_bytes(cpu.mem[io+24:io+28], "little"),
                   int.from_bytes(cpu.mem[io+28:io+30], "little"), cpu.c)
            if (got != reference(n, d) or cpu.sp != sp or
                    bytes(cpu.mem[io+16:io+20]) != nbytes or
                    bytes(cpu.mem[io+20:io+24]) != dbytes or
                    bytes(cpu.mem[io+30:io+32]) != b"\x49\x59"):
                raise ValueError("Signed32/16 full-call ABI/carry mismatch: " +
                                 repr((ident, hex(n), hex(d), got)))
            times.append(cycles)
        if any(cpu.mem[address] != value for address, value in original.items()):
            raise ValueError("Signed32/16 unexpected SMC: " + ident)
        means[ident] = sum(times) / CASES
        maximums[ident] = max(times)
        hashes[ident] = hashlib.sha256((root / mod["source"]).read_bytes()).hexdigest()
    return {
        "basis": BASIS + "-" + api.lower(),
        "cases": CASES, "corpus_sha256": digest,
        "cpu_model_only": True,
        "note": "Complete public Q32/R16/C through RTS; not native VICE timing",
        "code_origin": "$%04X" % code, "io_origin": "$%04X" % io,
        "mean_cycles": means, "maximum_cycles": maximums,
        "source_sha256": hashes,
    }


def bench_sdiv32_16(modules, code, io, scratch, root: Path, zp=0x50):
    return benchmark("MATH_SDIV32_16", modules, code, io, scratch, root, zp)


def bench_smod32_16(modules, code, io, scratch, root: Path, zp=0x50):
    return benchmark("MATH_SMOD32_16", modules, code, io, scratch, root, zp)
