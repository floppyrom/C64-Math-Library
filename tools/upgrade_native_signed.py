#!/usr/bin/env python3
"""Promote signed multiply/divide paths to private native executable kernels.

This tool performs the resident-image transformation used by the 2026-09-14
native-signed refresh.  It deliberately uses only already-reserved holes in each
profile, changes no public ABI address, consumes no additional ZP, and leaves the
resident PRG load/end range unchanged.

Native-signed definition enforced here:
  * a public signed entry owns its executable arithmetic engine;
  * it may share immutable lookup tables with unsigned entries;
  * it must not execute the corresponding public/full-width unsigned engine;
  * sign handling remains part of the signed entry before it returns.

For wider multiply this keeps the proven quarter-square/Comba arithmetic but
relocates a private copy for the signed path.  For signed 32/32 division the
private magnitude engine is likewise split from UDIV32/32.  Existing SDIV8,
SDIV16, SDIV24, SDIV32/16 and SDIV16_SHL8 were already executable-independent.
"""
from __future__ import annotations
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mini6502 import CPU, REV, SIZE

PROFILES = ["v1_balanced", "v2_pareto_fast", "v3_reu_512k", "v4_reu_16m"]
REU = {
    "v3_reu_512k": ROOT / "v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
    "v4_reu_16m": ROOT / "v4_reu_16m/reu/c64_math_v4_16m_game_math.reu",
}

# source_lo, source_hi_exclusive, private destination, signed API, unsigned API
# V2/V3/V4 UMUL24 has one self-modified scratch byte at source_hi, hence 0x571F.
SPLITS = {
    "v1_balanced": [
        (0x4700, 0x471C, 0x2600, "MATH_SMUL8", "MATH_UMUL8"),
        # SMUL16 calls the same 8x8 primitive four times; its wrapper is patched
        # separately below to the same private primitive.
        (0x4A00, 0x4ACC, 0x2700, "MATH_SMUL24", "MATH_UMUL24"),
        (0x4C00, 0x4D15, 0x2800, "MATH_SMUL32", "MATH_UMUL32"),
        (0xC222, 0xC51E, 0x2A00, "MATH_SDIV32_32", "MATH_UDIV32_32"),
    ],
    "v2_pareto_fast": [
        (0x5300, 0x5323, 0x2600, "MATH_SMUL8", "MATH_UMUL8"),
        (0x5600, 0x571F, 0x3600, "MATH_SMUL24", "MATH_UMUL24"),
        (0x5800, 0x5915, 0x3800, "MATH_SMUL32", "MATH_UMUL32"),
        (0xC1FE, 0xC4B5, 0x5AA8, "MATH_SDIV32_32", "MATH_UDIV32_32"),
    ],
    "v3_reu_512k": [
        (0x5600, 0x571F, 0x1400, "MATH_SMUL24", "MATH_UMUL24"),
        (0x5800, 0x5915, 0x1600, "MATH_SMUL32", "MATH_UMUL32"),
        (0xC1FE, 0xC4B5, 0x1828, "MATH_SDIV32_32", "MATH_UDIV32_32"),
    ],
    "v4_reu_16m": [
        (0x5600, 0x571F, 0x1400, "MATH_SMUL24", "MATH_UMUL24"),
        (0x5800, 0x5915, 0x1600, "MATH_SMUL32", "MATH_UMUL32"),
        (0xC1FE, 0xC4B5, 0x1828, "MATH_SDIV32_32", "MATH_UDIV32_32"),
    ],
}

# Reachable JMP-to-the-next-instruction handoffs at the unsigned-producer ->
# signed-finalizer boundary.  Relocating the finalizer three bytes earlier makes
# the transition fall through and saves three cycles without changing ABI.
TAIL_COMPACTIONS = {
    "v1_balanced": [
        (0x2019, 0x201C, 0x203C),
        (0x2185, 0x2188, 0x21BA),
        (0x223D, 0x2240, 0x2284),
        (0x2359, 0x235C, 0x23B2),
    ],
    "v2_pareto_fast": [
        (0x2011, 0x2014, 0x2034),
        (0x2244, 0x2247, 0x228B),
        (0x2349, 0x234C, 0x23A2),
    ],
    "v3_reu_512k": [
        (0x202C, 0x202F, 0x204F),
        (0x2344, 0x2347, 0x238B),
        (0x2449, 0x244C, 0x24A2),
    ],
    "v4_reu_16m": [
        (0x202C, 0x202F, 0x204F),
        (0x2244, 0x2247, 0x228B),
        (0x2349, 0x234C, 0x23A2),
    ],
}


def parse_api(profile: str) -> dict[str, int]:
    out = {}
    path = ROOT / profile / "resident/math_api.inc"
    for line in path.read_text().splitlines():
        m = re.match(r"\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)", line)
        if m:
            out[m.group(1)] = int(m.group(2), 16)
    return out


def load_raw(profile: str):
    path = ROOT / profile / "resident" / f"math_{profile}_game_math.prg"
    b = path.read_bytes()
    load = b[0] | b[1] << 8
    mem = bytearray(65536)
    mem[load:load + len(b) - 2] = b[2:]
    return path, load, load + len(b) - 2, mem


def initialized(profile: str, raw: bytearray) -> bytearray:
    reu = bytearray(REU[profile].read_bytes()) if profile in REU else None
    c = CPU(bytearray(raw), reu=reu)
    c.d = 0
    c.call(0x3280, 2_000_000)
    return c.mem


def trace(mem: bytearray, start: int) -> set[int]:
    todo = [start]
    seen: set[int] = set()
    while todo:
        pc = todo.pop() & 0xFFFF
        if pc in seen:
            continue
        oc = mem[pc]
        if oc not in REV:
            raise RuntimeError(f"untraceable opcode ${oc:02X} at ${pc:04X}")
        seen.add(pc)
        op, mode = REV[oc]
        nxt = (pc + SIZE[mode]) & 0xFFFF
        if op in ("rts", "rti", "brk"):
            continue
        if mode == "rel":
            d = mem[pc + 1]
            if d >= 128:
                d -= 256
            todo.extend((nxt, (nxt + d) & 0xFFFF))
        elif op == "jmp":
            if mode != "abs":
                raise RuntimeError(f"indirect JMP in trace at ${pc:04X}")
            todo.append(mem[pc + 1] | mem[pc + 2] << 8)
        elif op == "jsr":
            todo.extend((mem[pc + 1] | mem[pc + 2] << 8, nxt))
        else:
            todo.append(nxt)
    return seen


def patch_word(mem: bytearray, pc: int, value: int):
    mem[pc + 1] = value & 0xFF
    mem[pc + 2] = value >> 8


def relocate_blob(mem: bytearray, src_lo: int, src_hi: int, dst_lo: int,
                  code_pcs: set[int]):
    """Copy [src_lo,src_hi) and relocate internal absolute operands."""
    n = src_hi - src_lo
    if any(mem[dst_lo:dst_lo + n]):
        bad = [(dst_lo + i, x) for i, x in enumerate(mem[dst_lo:dst_lo+n]) if x][:8]
        raise AssertionError(f"destination not empty ${dst_lo:04X}-${dst_lo+n:04X}: {bad}")
    snap = bytes(mem[src_lo:src_hi])
    mem[dst_lo:dst_lo + n] = snap
    delta = dst_lo - src_lo
    for pc in sorted(code_pcs):
        if not (src_lo <= pc < src_hi):
            continue
        op, mode = REV[mem[pc]]
        if mode in ("abs", "absx", "absy", "ind"):
            target = snap[pc - src_lo + 1] | snap[pc - src_lo + 2] << 8
            if src_lo <= target < src_hi:
                npc = pc + delta
                nt = target + delta
                patch_word(mem, npc, nt)
    return delta


def redirect_wrapper_refs(mem: bytearray, signed_trace: set[int], src_lo: int,
                          src_hi: int, delta: int):
    patched = []
    for pc in sorted(signed_trace):
        if src_lo <= pc < src_hi:
            continue
        oc = mem[pc]
        if oc not in REV:
            continue
        op, mode = REV[oc]
        if mode in ("abs", "absx", "absy", "ind"):
            target = mem[pc + 1] | mem[pc + 2] << 8
            if src_lo <= target < src_hi:
                patch_word(mem, pc, target + delta)
                patched.append((pc, target, target + delta, op))
    if not patched:
        raise AssertionError(f"no signed wrapper references into ${src_lo:04X}-${src_hi:04X}")
    return patched


def compact_tail(mem: bytearray, jump_pc: int, tail_start: int, tail_end: int):
    if mem[jump_pc] != 0x4C or (mem[jump_pc+1] | mem[jump_pc+2] << 8) != tail_start:
        raise AssertionError(f"expected JMP ${tail_start:04X} at ${jump_pc:04X}")
    if tail_start != jump_pc + 3:
        raise AssertionError("tail compaction only supports JMP-to-next")
    code = trace(mem, tail_start)
    local = {pc for pc in code if tail_start <= pc < tail_end}
    # No control flow may escape to code after the compacted tail.
    for pc in local:
        op, mode = REV[mem[pc]]
        if mode == "rel":
            d = mem[pc+1] - (256 if mem[pc+1] >= 128 else 0)
            t = (pc + 2 + d) & 0xffff
            if not (tail_start <= t < tail_end):
                raise AssertionError(f"tail branch escape ${pc:04X}->${t:04X}")
        elif op in ("jmp", "jsr") and mode == "abs":
            t = mem[pc+1] | mem[pc+2] << 8
            if tail_start <= t < tail_end:
                pass
    # Overlap-safe relocation by snapshot, including absolute self references.
    snap = bytes(mem[tail_start:tail_end])
    dst = jump_pc
    mem[dst:dst+len(snap)] = snap
    delta = dst - tail_start
    for pc in sorted(local):
        op, mode = REV[snap[pc-tail_start]]
        if mode in ("abs", "absx", "absy", "ind"):
            off = pc - tail_start
            t = snap[off+1] | snap[off+2] << 8
            if tail_start <= t < tail_end:
                patch_word(mem, pc + delta, t + delta)
    mem[tail_end-3:tail_end] = b"\x00\x00\x00"


def write_raw(path: Path, load: int, end: int, mem: bytearray):
    path.write_bytes(bytes((load & 0xff, load >> 8)) + bytes(mem[load:end]))


def main():
    report = {"status": "PASS", "definition": "private signed executable kernel; immutable tables may be shared", "profiles": {}}
    for profile in PROFILES:
        path, load, end, raw = load_raw(profile)
        api = parse_api(profile)
        tm = initialized(profile, raw)
        rec = {"private_splits": [], "tail_compactions": []}

        for src_lo, src_hi, dst, sname, uname in SPLITS[profile]:
            st = trace(tm, api[sname])
            ut = trace(tm, api[uname])
            overlap = st & ut
            overlap_local = {pc for pc in overlap if src_lo <= pc < src_hi}
            if not overlap_local:
                raise AssertionError(f"{profile} {sname}: expected shared code in source range")
            delta = relocate_blob(raw, src_lo, src_hi, dst, overlap_local)
            patched = redirect_wrapper_refs(raw, st, src_lo, src_hi, delta)
            rec["private_splits"].append({
                "signed": sname, "unsigned": uname,
                "source": f"${src_lo:04X}-${src_hi-1:04X}",
                "private": f"${dst:04X}-${dst+(src_hi-src_lo)-1:04X}",
                "bytes": src_hi-src_lo,
                "redirects": [{"pc": f"${pc:04X}", "from": f"${old:04X}", "to": f"${new:04X}", "op": op}
                              for pc, old, new, op in patched],
            })

        # V1 SMUL16 shares the same UMUL8 primitive as V1 SMUL8.  Redirect all
        # its primitive calls to the already-created private $2600 copy.
        if profile == "v1_balanced":
            st = trace(tm, api["MATH_SMUL16"])
            redirects = redirect_wrapper_refs(raw, st, 0x4700, 0x471C, 0x2600 - 0x4700)
            rec["private_splits"].append({
                "signed": "MATH_SMUL16", "unsigned": "private 8x8 primitive, not MATH_UMUL16",
                "source": "$4700-$471B", "private": "$2600-$261B", "bytes": 0x1c,
                "redirects": [{"pc": f"${pc:04X}", "from": f"${old:04X}", "to": f"${new:04X}", "op": op}
                              for pc, old, new, op in redirects],
            })

        for jump_pc, tail_start, tail_end in TAIL_COMPACTIONS[profile]:
            compact_tail(raw, jump_pc, tail_start, tail_end)
            rec["tail_compactions"].append({"from": f"${tail_start:04X}", "to": f"${jump_pc:04X}", "saved_cycles": 3})

        write_raw(path, load, end, raw)
        report["profiles"][profile] = rec
        print(profile, "PATCHED", sum(x["bytes"] for x in rec["private_splits"]), "private bytes")

    out = ROOT / "validation/review/NATIVE_SIGNED_UPGRADE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("WROTE", out.relative_to(ROOT))

if __name__ == "__main__":
    main()
