#!/usr/bin/env python3
"""Independent Issue #144 unsigned 32/16 low-tail screen; research, NOT public API."""
import hashlib
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mini6502 import Assembler, CPU

ORIGIN = 0x2070
STOP = 0x07FF

def source(which):
    assert which in ("baseline", "shared")
    out = ["* = $2070", "clc", "lda $35"]
    for i in range(16):
        q = "$34" if i < 8 else "$33"
        out += [f"STEP_{i}:", f"rol {q}", "rol $32", "rol a"]
        if which == "baseline":
            out += [
                f"bcs FORCE_{i}", "cmp $31", f"bcc NEXT_{i}",
                f"bne TAKE_{i}", "ldx $32", "cpx $30", f"bcc NEXT_{i}",
                f"TAKE_{i}:", "tax", "lda $32", "sbc $30", "sta $32",
                "txa", "sbc $31", f"bcs NEXT_{i}",
                f"FORCE_{i}:", "tax", "lda $32", "sbc $30", "sta $32",
                "txa", "sbc $31", "sec", f"NEXT_{i}:",
            ]
        else:
            # Both overflow-forced and ordinary-accepted subtraction arrive C=1.
            out += [
                f"bcs TAKE_{i}", "cmp $31", f"bcc NEXT_{i}",
                f"bne TAKE_{i}", "ldx $32", "cpx $30", f"bcc NEXT_{i}",
                f"TAKE_{i}:", "tax", "lda $32", "sbc $30", "sta $32",
                "txa", "sbc $31", "sec", f"NEXT_{i}:",
            ]
        if i == 7:
            out.append("rol $34")
    out += ["rol $33", "sta $35", "jmp $07FF"]
    return "\n".join(out) + "\n"

def assemble(which):
    code, _, _ = Assembler().assemble(source(which))
    assert min(code) == ORIGIN
    return code

def inputs():
    r = random.Random(0x1443216)
    pairs = [(r.getrandbits(32), r.randrange(1, 65536)) for _ in range(1200)]
    for d in (1, 2, 3, 15, 127, 128, 255, 256, 257, 1024,
              32767, 32768, 32769, 65535):
        for n in (0, 1, d-1, d, d+1, 0xffff, 0x10000, 0x10001,
                  0x7fffffff, 0x80000000, 0xffffffff):
            pairs.append((n, d))
    pairs += [(r.getrandbits(32), r.randrange(1, 256)) for _ in range(200)]
    r = random.Random(0x9F1443216)
    pairs += [(r.getrandbits(32), r.randrange(1, 65536)) for _ in range(6000)]
    assert len(pairs) == 7554
    return pairs

def execute(code, n, d):
    assert 1 <= d <= 65535
    seed = (n >> 16) % d
    mem = bytearray(65536)
    for addr, val in code.items():
        mem[addr] = val
    for addr, val in (
        (0x30, d & 255), (0x31, d >> 8),
        (0x32, seed & 255), (0x35, seed >> 8),
        (0x33, n & 255), (0x34, (n >> 8) & 255),
    ):
        mem[addr] = val
    cpu = CPU(mem, pc=ORIGIN, sp=0xFF, d=0)
    for _ in range(1500):
        if cpu.pc == STOP:
            break
        cpu.step()
    else:
        raise AssertionError(f"nonterminating inner loop n={n:#x} d={d:#x}")
    assert (cpu.sp, cpu.d, mem[0x30], mem[0x31]) == (
        0xFF, 0, d & 255, d >> 8
    )
    q = mem[0x33] | (mem[0x34] << 8)
    rem = mem[0x32] | (mem[0x35] << 8)
    return q, rem, cpu.cycles

def main():
    baseline, candidate = assemble("baseline"), assemble("shared")
    assert (len(baseline), len(candidate)) == (684, 492)
    pairs = inputs()
    old_cycles, new_cycles, savings = [], [], []
    for n, d in pairs:
        old = execute(baseline, n, d)
        new = execute(candidate, n, d)
        truth = ((n // d) & 65535, n % d)
        assert old[:2] == new[:2] == truth, (hex(n), hex(d), old, new, truth)
        old_cycles.append(old[2])
        new_cycles.append(new[2])
        savings.append(old[2] - new[2])
    corpus = b"".join(n.to_bytes(4, "little") + d.to_bytes(2, "little")
                      for n, d in pairs)
    result = {
        "status": "PASS_TAIL_ONLY",
        "cases": len(pairs),
        "corpus_sha256": hashlib.sha256(corpus).hexdigest(),
        "origin": hex(ORIGIN),
        "baseline_bytes": len(baseline),
        "candidate_bytes": len(candidate),
        "baseline_mean_cycles": statistics.mean(old_cycles),
        "candidate_mean_cycles": statistics.mean(new_cycles),
        "saved_mean_cycles": statistics.mean(savings),
        "saved_worst_cycles": min(savings),
        "saved_best_cycles": max(savings),
        "slower_cases": sum(x < 0 for x in savings),
        "equal_cases": savings.count(0),
        "paired_savings_sha256": hashlib.sha256(b"".join(
            int(x).to_bytes(4, "little", signed=True) for x in savings
        )).hexdigest(),
        "limits": "low16 tail, oracle-seeded highword, D!=0, NOT public ABI/native VICE",
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
