#!/usr/bin/env python3
"""Matched-input CPU-model cycle baselines for the six newly source-linked APIs.

This deliberately measures current *portable/link-ready* assembler outputs,
NOT historical fixed-profile resident timings. Its fixed input corpora are
future speed-transplant qualification inputs; compare donor and baseline
only on the same corpus, memory map and ABI/resource contract.
"""
from __future__ import annotations

import hashlib
import json
import random
import tempfile
from pathlib import Path

import math_builder
import selective_linker
from mini6502 import CPU
from normalize_model import normalized_reference

ROOT = Path(__file__).resolve().parents[1]
SEED = 0xC642026
COUNT = 256
OPS32 = ("UMUL32_READY", "SMUL32_READY", "SMUL32_SHR16")
OPSDIV = ("UMULDIV16", "SMULDIV16")
OPSVEC = ("VEC2_NORMALIZE_Q8_8",)
OPS = OPS32 + OPSDIV + OPSVEC
MAPS = ((0x8000, 0xC000, 0x50), (0x7123, 0xC040, 0x61))
MASK32 = (1 << 32) - 1
MASK64 = (1 << 64) - 1
DESIGN = json.loads(
    (ROOT / "validation/normalize/LOG_RATIO_TABLE_DESIGN.json").read_text()
)


def s16(n: int) -> int:
    return n - 65536 if n & 0x8000 else n


def s32(n: int) -> int:
    return n - (1 << 32) if n & 0x80000000 else n


def corpora():
    edge32 = (0, 1, 2, 255, 256, 65535, 0x80000000,
              0x7fffffff, 0xffffffff)
    edge16 = (0, 1, 2, 255, 256, 0x7fff, 0x8000, 0xffff)
    vector_edge = (-32768, -16384, -256, -1, 0, 1, 255, 16384, 32767)
    r = random.Random(SEED)
    xx = [(a, b) for a in edge32 for b in edge32]
    xx += [(r.getrandbits(32), r.getrandbits(32))
           for _ in range(COUNT - len(xx))]
    md = [(a, b, d) for a in edge16 for b in (0, 1, 0x7fff, 0x8000)
          for d in (0, 1, 0x8000, 0xffff)]
    md += [(r.getrandbits(16), r.getrandbits(16), r.getrandbits(16))
           for _ in range(COUNT - len(md))]
    vv = [(x, y) for x in vector_edge for y in vector_edge]
    vv += [(r.randrange(-32768, 32768), r.randrange(-32768, 32768))
           for _ in range(COUNT - len(vv))]
    assert len(xx) == len(md) == len(vv) == COUNT
    return {"mul32": xx, "muldiv16": md, "vec2": vv}


def checksum(pairs, nbytes):
    return hashlib.sha256(
        b"".join((n & ((1 << (8 * nbytes)) - 1)).to_bytes(nbytes, "little")
                 for pair in pairs for n in pair)
    ).hexdigest()


def reference(op, pair):
    if op in OPS32:
        x, y = pair
        result = ((s32(x) * s32(y)) if op.startswith("SMUL")
                  else x * y) & MASK64
        return (result >> 16) & ((1 << 48) - 1) if op.endswith("SHR16") else result
    if op in OPSDIV:
        x, y, d = pair
        if not d:
            return 0, 0, 1
        if op.startswith("S"):
            product = s16(x) * s16(y)
            divisor = s16(d)
            q = abs(product) // abs(divisor)
            if (product < 0) != (divisor < 0):
                q = -q
            return q & MASK32, (product - q * divisor) & 65535, 0
        return (x * y) // d, (x * y) % d, 0
    return normalized_reference(*pair, DESIGN)


def quantiles(cycles):
    s = sorted(cycles)
    return {
        "min": s[0],
        "p50": s[(len(s) - 1) // 2],
        "p90": s[(len(s) * 90 - 1) // 100],
        "max": s[-1],
        "mean": round(sum(s) / len(s), 6),
    }


def benchmark(op, cases, code, io, zp, index):
    with tempfile.TemporaryDirectory(prefix="bench_math_source_") as temporary:
        out = Path(temporary)
        plan = math_builder.create_plan(index, [op], objective="size",
                                        zp_budget=4, ram_budget=8192)
        man = selective_linker.build(
            plan, out, memory={"code_base": code, "math_io": io,
                               "zp_base": zp, "scratch_base": io + 32})
        entry = man["operations"][0]
        address = int(entry["entry"][1:], 16)
        image = (out / "math_selective.prg").read_bytes()
        assert image[:2] == code.to_bytes(2, "little")
        mem = bytearray(65536)
        mem[code:code+len(image)-2] = image[2:]
        cpu = CPU(mem)
        sp = cpu.sp
        times = []
        for i, pair in enumerate(cases):
            if op in OPS32:
                x, y = pair
                xb, yb = x.to_bytes(4, "little"), y.to_bytes(4, "little")
                mem[io:io+4] = xb
                mem[io+4:io+8] = yb
                mem[io+8:io+16] = bytes((0x77,)) * 8
            elif op in OPSDIV:
                x, y, d = pair
                xb, yb = x.to_bytes(2, "little"), y.to_bytes(2, "little")
                db = d.to_bytes(2, "little")
                mem[io:io+2] = xb
                mem[io+4:io+6] = yb
                mem[io+20:io+22] = db
                mem[io+24:io+30] = bytes((0x77,)) * 6
            else:
                x, y = pair
                xb = (x & 65535).to_bytes(2, "little")
                yb = (y & 65535).to_bytes(2, "little")
                mem[io:io+2] = xb
                mem[io+4:io+6] = yb
                mem[io+8:io+12] = bytes((0x77,)) * 4
            cpu.d = 0
            cpu.c = i & 1
            times.append(cpu.call(address, 125000))
            if op in OPS32:
                width = 6 if op.endswith("SHR16") else 8
                got = int.from_bytes(mem[io+8:io+8+width], "little")
                assert got == reference(op, pair) and cpu.c == 0, (op, pair, got)
                assert bytes(mem[io:io+4]) == xb
                assert bytes(mem[io+4:io+8]) == yb
            elif op in OPSDIV:
                got = (int.from_bytes(mem[io+24:io+28], "little"),
                       int.from_bytes(mem[io+28:io+30], "little"), cpu.c)
                assert got == reference(op, pair), (op, pair, got)
                assert bytes(mem[io:io+2]) == xb
                assert bytes(mem[io+4:io+6]) == yb
                assert bytes(mem[io+20:io+22]) == db
            else:
                got = (int.from_bytes(mem[io+8:io+10], "little", signed=True),
                       int.from_bytes(mem[io+10:io+12], "little", signed=True))
                assert got == reference(op, pair), (op, pair, got)
                assert cpu.c == int(not (x or y)), (op, pair, cpu.c)
                assert bytes(mem[io:io+2]) == xb
                assert bytes(mem[io+4:io+6]) == yb
            assert cpu.sp == sp, (op, pair, "stack imbalance")
        return {
            **quantiles(times),
            "source_path": entry["source"],
            "source_sha256": entry["sha256"],
            "variant": entry["variant"],
            "image_span_bytes": man["resource_use"]["image_span_bytes"],
            "ram_bytes": man["resource_use"]["main_ram_total_bytes"],
            "zp_bytes": man["resource_use"]["zero_page_bytes"],
            "cases": len(cases),
        }


def main():
    index = math_builder.operation_index()
    groups = corpora()
    corpora_hash = {
        "mul32": checksum(groups["mul32"], 4),
        "muldiv16": checksum(groups["muldiv16"], 2),
        "vec2": checksum(groups["vec2"], 2),
    }
    results = {}
    for name in OPS:
        corpus = "mul32" if name in OPS32 else "muldiv16" if name in OPSDIV else "vec2"
        results[name] = {
            "corpus_id": corpus,
            "corpus_sha256": corpora_hash[corpus],
            "maps": {
                "$%04X/$%04X/$%02X" % (code, io, zp):
                    benchmark(name, groups[corpus], code, io, zp, index)
                for code, io, zp in MAPS
            },
        }
    report = {
        "schema": "c64-selective-migration-cycle-baseline-v1",
        "model": "mini6502 CPU model, assembled public calls through RTS",
        "native_vice_timing": False,
        "matched_within_operation": True,
        "global_mixed_op_speed_ranking": False,
        "seed": SEED,
        "inputs_per_op_per_map": COUNT,
        "maps": [{"code": "$%04X"%c, "io": "$%04X"%i, "zp": "$%02X"%z}
                 for c,i,z in MAPS],
        "corpora_sha256": corpora_hash,
        "operations": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
