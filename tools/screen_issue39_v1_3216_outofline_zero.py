#!/usr/bin/env python3
"""Issue39 research screen: V1 32/16 zero-handler out-of-line, normal path fallthrough.

This changes ONLY ephemeral emulator memory. It is not an installed library
change or a native VICE certification. A source-owned production relocation
is separately required if it proves advantageous.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "tools"))
from mini6502 import CPU, REV, SIZE
from validate_unsigned_division import load
from screen_issue39_u3216_n16_delegate import OPS, inputs, sample

PROFILE = "v1_balanced"
CORE_BEGIN = 0x4500
BODY_BEGIN = 0x450C
CORE_END = 0x457B
NEW_BODY = 0x4505
COLD_ENTRY = 0x44F0
UNROLL_BEGIN, UNROLL_END = 0x1900, 0x1CF8
DELTA = NEW_BODY - BODY_BEGIN
assert DELTA == -7

def proposal(before: bytearray):
    """Relocate only decoded instructions and all verified island backlinks."""
    after = bytearray(before)
    assert before[CORE_BEGIN:CORE_BEGIN + 5] == bytes.fromhex("2000449007"), "entry changed"
    assert before[CORE_BEGIN + 5:BODY_BEGIN] == bytes.fromhex("a900851a851b60"), "zero stub changed"
    assert before[COLD_ENTRY:COLD_ENTRY + 7] == bytes(7), "cold site occupied"
    assert before[0x4570:0x4573] == bytes.fromhex("4c0019"), "unroll entry changed"
    assert before[0x446A:0x446D] == bytes.fromhex("4c6d1b"), "high unroll entry changed"
    moved = bytearray(before[BODY_BEGIN:CORE_END])
    pc = BODY_BEGIN
    branches = 0
    internal_abs = 0
    while pc < CORE_END:
        opcode = before[pc]
        assert opcode in REV, (hex(pc), hex(opcode))
        op, mode = REV[opcode]
        size = SIZE[mode]
        assert pc + size <= CORE_END, ("instruction straddles core", hex(pc))
        off = pc - BODY_BEGIN
        if mode == "rel":
            disp = before[pc + 1]
            disp = disp - 256 if disp >= 128 else disp
            target = pc + 2 + disp
            assert BODY_BEGIN <= target < CORE_END, (
                "branch target must be moved with body", hex(pc), hex(target))
            branches += 1
        if opcode in (0x4C, 0x20):
            target = before[pc + 1] | before[pc + 2] << 8
            if BODY_BEGIN <= target < CORE_END:
                target += DELTA
                moved[off + 1] = target & 255
                moved[off + 2] = target >> 8
                internal_abs += 1
        pc += size
    assert pc == CORE_END
    # Move the divide-by-zero block to a documented-empty nearby kernel slot.
    after[COLD_ENTRY:COLD_ENTRY + 7] = before[CORE_BEGIN + 5:BODY_BEGIN]
    # BCS from $4503 to $44F0 (rare zero only). Good calls fall through.
    disp = COLD_ENTRY - (CORE_BEGIN + 5)
    assert -128 <= disp <= 127
    after[CORE_BEGIN + 3:CORE_BEGIN + 5] = bytes((0xB0, disp & 255))
    after[NEW_BODY:NEW_BODY + len(moved)] = moved
    after[NEW_BODY + len(moved):CORE_END] = bytes(-DELTA)

    # Existing 15-round unroll calls back into the three-byte exit epilogue.
    # Shift only its identified absolute JMP targets into the moved code.
    patch_list = []
    for address in range(UNROLL_BEGIN, UNROLL_END - 2):
        if before[address] != 0x4C:
            continue
        target = before[address + 1] | before[address + 2] << 8
        if BODY_BEGIN <= target < CORE_END:
            fixed = target + DELTA
            after[address + 1] = fixed & 255
            after[address + 2] = fixed >> 8
            patch_list.append((address, target, fixed))
    assert patch_list, "no island-to-body backlinks found: inspect unroll source"
    # Keep the relocated body and all cold slots completely separate.
    assert CORE_END <= 0x4600 and NEW_BODY + len(moved) == CORE_END + DELTA
    return after, {"relocated_bytes": len(moved),
                   "internal_relative_branches": branches,
                   "internal_absolute_targets": internal_abs,
                   "unroll_backlinks": patch_list,
                   "cold_handler_addr": COLD_ENTRY,
                   "cold_handler_bytes": 7,
                   "normal_zp_growth": 0,
                   "stable_public_entry_changed": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    state = json.loads((R / "RELEASE_STATUS.json").read_text())
    data = (R / PROFILE / "resident" /
            ("math_" + PROFILE + "_game_math.prg")).read_bytes()
    h = hashlib.sha256(data).hexdigest()
    assert h == state["reference_prg_sha256"][PROFILE], "resident SHA drift"
    original, entry = load(PROFILE)
    candidate, entry2 = load(PROFILE)
    assert entry == entry2
    assert all(entry[k] in (0x31B0, 0x3226) for k in OPS)
    candidate.mem, details = proposal(original.mem)
    report = {"status": "PASS_RESEARCH_ONLY",
              "resident_changed": False,
              "source": "tools/screen_issue39_v1_3216_outofline_zero.py",
              "resident_sha256": h,
              "native_vice_calls": 0,
              "profile": PROFILE,
              "candidate": details,
              "operations": {},
              "paired_inputs": 0,
              "machine_calls": 0,
              "mismatches": 0}
    for op in OPS:
        report["operations"][op] = {}
        for group, vec in inputs(op).items():
            diff = []
            prior_sum = new_sum = 0
            dig = hashlib.sha256()
            for n, d in vec:
                old_cycles, old_state = sample(original, entry[op], n, d)
                new_cycles, new_state = sample(candidate, entry[op], n, d)
                assert old_state == new_state, (
                    "public ABI mismatch", op, group, hex(n), hex(d),
                    old_state, new_state)
                dig.update(n.to_bytes(4, "little") + d.to_bytes(2, "little"))
                prior_sum += old_cycles
                new_sum += new_cycles
                diff.append(new_cycles - old_cycles)
            assert diff
            record = {
                "cases": len(vec),
                "input_sha256": dig.hexdigest(),
                "mean_before": prior_sum / len(vec),
                "mean_after": new_sum / len(vec),
                "mean_delta": (new_sum - prior_sum) / len(vec),
                "faster": sum(x < 0 for x in diff),
                "equal": sum(x == 0 for x in diff),
                "slower": sum(x > 0 for x in diff),
                "max_regression": max(diff),
                "max_speedup": -min(diff)}
            report["operations"][op][group] = record
            report["paired_inputs"] += len(vec)
            report["machine_calls"] += 2 * len(vec)
            print(PROFILE, op, group, "mean_delta",
                  round(record["mean_delta"], 6), "slower", record["slower"],
                  flush=True)
    assert report["paired_inputs"] > 10000
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("V1 32/16 RARE-ZERO OOL SCREEN PASS",
          report["paired_inputs"], "paired inputs",
          report["machine_calls"], "full CPU-model calls")

if __name__ == "__main__":
    main()
