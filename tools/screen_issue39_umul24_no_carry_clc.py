#!/usr/bin/env python3
"""Issue #39: research-only V2/V3/V4 UMUL24 fallthrough carry-clear removal.

The no-carry path is entered only when BCS is NOT taken. STA and STX do not
change C. Replace trailing CLC/RTS with RTS/NOP in a temporary source checkout,
preserving *every* subsequent code address and production files.

This script never promotes or writes released PRGs. Both source relocations,
public ABI/product/carry/stack, signed mixed calls and exact cycle vectors are
compared against the unmodified source-built residents.
"""
import collections
import hashlib
import json
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import assemble_sources as asm
import validate_source_build as buildcheck
from validate_umul24_directout import corpus

PROFILES = ("v2_pareto_fast", "v3_reu_512k", "v4_reu_16m")
MAPS = ("reference", "alternate")
SOURCE = ROOT / "relocatable_source/multiply/umul24_directout.asm"
ORIGINAL = ("        sta MATH_IO+$0C\n"
            "        stx MATH_IO+$0D\n"
            "        clc\n"
            "        rts\n"
            "R24_final:")
CANDIDATE = ("        sta MATH_IO+$0C\n"
             "        stx MATH_IO+$0D\n"
             "        rts\n"
             "        nop\n"
             "R24_final:")
LIMIT = (1 << 48) - 1


def digest(b):
    return hashlib.sha256(b).hexdigest()


def copy_input(cpu, io, x, y):
    for offset, num in ((0, x), (4, y)):
        for i in range(3):
            cpu.mem[io + offset + i] = (num >> (i * 8)) & 255
    cpu.mem[io + 3] = 0x92
    cpu.mem[io + 7] = 0x73
    cpu.mem[io + 14] = 0x56
    cpu.mem[io + 15] = 0xA4
    for i in range(6):
        cpu.mem[io + 8 + i] = 0xCC


def call(cpu, api, io, x, y, signed=False):
    copy_input(cpu, io, x, y)
    before = bytes(cpu.mem[io:io + 8])
    sp = cpu.sp
    cpu.d = 0
    name = "MATH_SMUL24" if signed else "MATH_UMUL24"
    cycles = cpu.call(api[name], 20000)
    product = sum(cpu.mem[io + 8 + i] << (8 * i) for i in range(6))
    a = x - (1 << 24) if signed and x & (1 << 23) else x
    b = y - (1 << 24) if signed and y & (1 << 23) else y
    assert product == ((a * b) & LIMIT), (name, hex(x), hex(y), product)
    assert cpu.c == 0 and cpu.sp == sp, (name, "carry/stack", cpu.c, cpu.sp, sp)
    assert bytes(cpu.mem[io:io + 8]) == before, (name, "input modified")
    assert cpu.mem[io + 14:io + 16] == bytes([0x56, 0xA4]), (name, "high sentinel")
    return cycles, product


def build_one(profile, mode, base):
    cfg = ROOT / "relocatable_source" / profile / ("math_config_" + mode + ".inc")
    man = asm.build(profile, cfg, base / profile)
    raw = (base / profile / man["output_prg"]).read_bytes()
    return man, raw


def run():
    original = SOURCE.read_text()
    assert original.count(ORIGINAL) == 1, "missing or duplicate UMUL24 no-carry tail"
    modified = original.replace(ORIGINAL, CANDIDATE)
    assert len(modified) == len(original), "trial text is length-neutral"
    pairs = corpus()
    assert len(pairs) == 10324
    rng = random.Random(0xC6392402)
    alternate = pairs[:256] + [pairs[i] for i in rng.sample(range(len(pairs)), 512)]
    report = {
        "status": "PASS_RESEARCH_ONLY_IF_COMPLETED",
        "source_changed_permanently": False,
        "production_prgs_changed": False,
        "native_vice_calls": 0,
        "candidate": "no-carry BCS fallthrough: STA/STX/RTS/NOP replacing STA/STX/CLC/RTS",
        "scope": "V2/V3/V4 UMUL24, reference and alternate relocation maps",
        "profiles": {},
        "unsigned_paired_cases": 0,
        "signed_mixed_paired_cases": 0,
    }
    with tempfile.TemporaryDirectory(prefix="issue39_u24_no_clc_") as tmp:
        root = Path(tmp)
        # Build all old maps before modifying the shared source.
        baseline = {}
        for p in PROFILES:
            for mode in MAPS:
                _, raw = build_one(p, mode, root / "old" / mode)
                baseline[p, mode] = raw
        try:
            SOURCE.write_text(modified)
            candidate = {}
            for p in PROFILES:
                for mode in MAPS:
                    _, raw = build_one(p, mode, root / "new" / mode)
                    candidate[p, mode] = raw
        finally:
            SOURCE.write_text(original)
        assert SOURCE.read_text() == original, "source not restored"

        release = json.loads((ROOT / "RELEASE_STATUS.json").read_text())
        for p in PROFILES:
            report["profiles"][p] = {}
            for mode in MAPS:
                before, after = baseline[p, mode], candidate[p, mode]
                assert len(before) == len(after), (p, mode, "resident grew")
                loadaddr = int.from_bytes(before[:2], "little")
                assert loadaddr == int.from_bytes(after[:2], "little")
                if mode == "reference":
                    assert digest(before) == release["reference_prg_sha256"][p], (p, "main pin")
                diffs = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
                assert len(diffs) == 2 and diffs[1] == diffs[0] + 1, (p, mode, diffs)
                i = diffs[0]
                assert before[i:i+2] == bytes((0x18, 0x60)) and after[i:i+2] == bytes((0x60, 0xea)), (p, mode, "unexpected instruction edit")
                old_cpu, old_api, old_io, _, _ = buildcheck.load(p, root / "old" / mode)
                new_cpu, new_api, new_io, _, _ = buildcheck.load(p, root / "new" / mode)
                assert old_api == new_api and old_io == new_io
                inputs = pairs if mode == "reference" else alternate
                dist = collections.Counter()
                signed_cases = 0
                for j, (x, y) in enumerate(inputs):
                    co, ro = call(old_cpu, old_api, old_io, x, y)
                    cn, rn = call(new_cpu, new_api, new_io, x, y)
                    assert ro == rn
                    delta = cn - co
                    assert delta in (-2, 0), (p, mode, x, y, delta)
                    dist[delta] += 1
                    if j % 23 == 0:
                        so, sr = call(old_cpu, old_api, old_io, x, y, signed=True)
                        sn, ss = call(new_cpu, new_api, new_io, x, y, signed=True)
                        assert sr == ss and sn == so, (p, mode, "signed changed")
                        signed_cases += 1
                assert dist[-2] > 0, (p, mode, "no saving")
                report["unsigned_paired_cases"] += len(inputs)
                report["signed_mixed_paired_cases"] += signed_cases
                report["profiles"][p][mode] = {
                    "cases": len(inputs),
                    "signed_mixed_cases": signed_cases,
                    "old_prg_sha256": digest(before),
                    "candidate_prg_sha256": digest(after),
                    "modified_addresses": [hex(loadaddr+i-2), hex(loadaddr+i-1)],
                    "cycle_delta_histogram": dict(sorted(dist.items())),
                    "mean_saving_cycles": -sum(k*v for k, v in dist.items()) / len(inputs),
                }
                print("UMUL24 NO-CLC RESEARCH PASS", p, mode, len(inputs),
                      dict(dist), "mean_saved", report["profiles"][p][mode]["mean_saving_cycles"], flush=True)
    out = ROOT / "validation/review/ISSUE39_UMUL24_NO_CARRY_CLC_SCREEN.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("ISSUE39 UMUL24 NO-CLC PRIVATE CANDIDATE SCREEN PASS", report["unsigned_paired_cases"])


if __name__ == "__main__":
    run()
