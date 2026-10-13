#!/usr/bin/env python3
"""Actual native VICE x64sc old/new V1 UDIV32/16 and UMOD32/16 ABI proof.

Ephemeral bytes patched from EXACT published V1 full resident, no production
resident source mutation. 48 deterministic operands × 2 images × 2 aliases.
No native cycle-timing claim; paired instruction counts are a separate proof.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import random
import socket
import subprocess
import tempfile
import time
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from screen_issue39_v1_3216_outofline_zero import proposal
from native_issue39_u24_txa_resident import command

H = 0x0B00
INPUT, OUTPUT = 0x0400, 0x0600
STRIDE, COUNT = 64, 48
IO = 0xC000
API = {"MATH_UDIV32_16": 0x31B0, "MATH_UMOD32_16": 0x3226}
FIELDS = ([IO + 0x18 + i for i in range(4)] +
          [IO + 0x1C + i for i in range(4)] +
          [IO + 0x10 + i for i in range(4)] +
          [IO + 0x14 + i for i in range(2)] +
          [0xC030, 0xC024, 0xC032])
assert OUTPUT + (len(FIELDS) - 1) * STRIDE + COUNT <= H

def hash_bytes(x):
    return hashlib.sha256(x).hexdigest()

def operands():
    fixed = [
        (0, 0), (0, 1), (1, 0), (1, 1), (2, 1), (3, 2),
        (0xFFFF, 0), (0x10000, 0), (0x10000, 1), (0x10001, 0x100),
        (0xFFFFFFFF, 0), (0xFFFFFFFF, 1), (0xFFFFFFFF, 2),
        (0xFFFFFFFF, 0xFFFF), (0xFFFFFFFF, 0x100),
        (0x80000000, 0x8000), (0x7FFFFFFF, 0x7FFF),
        (0x80000001, 0xFFFF), (0xFFFF0000, 0xFF),
        (0x12345678, 0x1234), (0x87654321, 0xFEDC),
        (0x10000000, 0x0001), (0x10000000, 0xFFFF),
        (0xABCDEF01, 0x7FFF), (0xFFFF, 0xFFFF),
        (0x1234, 0x5678), (0x5678, 0x1234), (0x12345678, 0)
    ]
    rng = random.Random(0xC6393216)
    while len(fixed) < COUNT:
        n, d = rng.getrandbits(32), rng.getrandbits(16)
        fixed.append((n, d))
    assert len(fixed) == COUNT
    return fixed

def harness(entry):
    b = bytearray()
    def emit(*xs): b.extend(xs)
    def op(code, addr): emit(code, addr & 255, addr >> 8)
    emit(0x78, 0xD8, 0xA9, 0x34, 0x85, 0x01)  # SEI CLD + RAM under BASIC/KERNAL
    op(0x20, 0x3280)
    emit(0xA2, 0x00)  # LDX #0
    loop = H + len(b)
    for j in range(4):
        op(0xBD, INPUT + j * STRIDE)
        op(0x8D, IO + 0x10 + j)
    for j in range(2):
        op(0xBD, INPUT + (4 + j) * STRIDE)
        op(0x8D, IO + 0x14 + j)
    emit(0xA9, 0x91)
    for j in range(4): op(0x8D, IO + 0x18 + j)
    emit(0xA9, 0x82)
    for j in range(4): op(0x8D, IO + 0x1C + j)
    emit(0xA9, 0xA6)
    op(0x8D, 0xC024)
    emit(0x8A, 0x48, 0x38)  # save caller index, set incoming carry
    op(0x20, entry)
    emit(0x08, 0x68)  # PHP PLA
    op(0x8D, 0xC030)  # preserve CPU status
    emit(0xBA)  # TSX (before saved index PLA)
    op(0x8E, 0xC032)
    emit(0x68, 0xAA)  # PLA TAX restore loop index
    for i, address in enumerate(FIELDS):
        op(0xAD, address)
        op(0x9D, OUTPUT + i * STRIDE)
    emit(0xE8, 0xE0, COUNT, 0xF0, 0x03)
    op(0x4C, loop)
    stop = H + len(b)
    op(0x4C, stop)
    assert len(b) < 0x300, len(b)
    return bytes(b), stop

def run_native(prg, op, label, port, folder, vice):
    load = int.from_bytes(prg[:2], "little")
    assert load == 0x1000
    mem = bytearray(65536)
    mem[load:load + len(prg) - 2] = prg[2:]
    code, stop = harness(API[op])
    mem[H:H + len(code)] = code
    pairs = operands()
    for i, (n, d) in enumerate(pairs):
        for j in range(4):
            mem[INPUT + j * STRIDE + i] = (n >> (8 * j)) & 255
        for j in range(2):
            mem[INPUT + (j + 4) * STRIDE + i] = (d >> (8 * j)) & 255
    image = folder / (label + ".prg")
    dump = folder / (label + ".dump")
    log = folder / (label + ".log")
    image.write_bytes(bytes((INPUT & 255, INPUT >> 8)) + mem[INPUT:0xD000])
    cmd = [str(vice), "-console", "-silent", "-sounddev", "dummy", "-warp",
           "-remotemonitor", "-remotemonitoraddress",
           f"127.0.0.1:{port}", "-initbreak", "reset"]
    with log.open("w") as out:
        proc = subprocess.Popen(cmd, cwd=folder, stdout=out, stderr=out)
        try:
            sock = None
            for _ in range(180):
                try:
                    sock = socket.create_connection(("127.0.0.1", port), timeout=0.15)
                    break
                except (ConnectionRefusedError, TimeoutError):
                    time.sleep(0.07)
            if sock is None:
                raise RuntimeError(("VICE monitor timeout", label, log.read_text()[-1500:]))
            sock.settimeout(0.3)
            try:
                command(sock, 'load "' + str(image) + '" 0', "Loading")
                command(sock, "break " + format(stop, "04x"), "BREAK:")
                command(sock, "g " + format(H, "04x"), "Stop on  exec")
                command(sock,
                        'bsave "' + str(dump) + '" 0 ' +
                        format(OUTPUT, "04x") + " " +
                        format(OUTPUT + len(FIELDS) * STRIDE - 1, "04x"), "Saving")
                sock.sendall(b"quit\n")
            finally:
                sock.close()
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    if not dump.exists():
        raise RuntimeError(("missing dump", label, log.read_text()[-1800:]))
    data = dump.read_bytes()
    assert len(data) == len(FIELDS) * STRIDE, (label, len(data))
    result = []
    for i, (n, d) in enumerate(pairs):
        v = [data[k * STRIDE + i] for k in range(len(FIELDS))]
        q = sum(v[j] << (8 * j) for j in range(4))
        r = sum(v[4 + j] << (8 * j) for j in range(4))
        out_n = sum(v[8 + j] << (8 * j) for j in range(4))
        out_d = v[12] | v[13] << 8
        carry = v[14] & 1
        want_q, want_r = ((0, 0) if not d else divmod(n, d))
        assert (q, r & 0xFFFF, r >> 16, carry, out_n, out_d, v[15]) == (
            want_q, want_r, 0x8282, int(d == 0), n, d, 0xA6), (
                label, i, hex(n), hex(d), v)
        result.append((q, r, carry, out_n, out_d, v[15], v[16]))
    return {"tag": label, "calls": COUNT, "image_sha256": hash_bytes(prg),
            "dump_sha256": hash_bytes(data), "records": result}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    original = (ROOT / "v1_balanced" / "resident" /
                "math_v1_balanced_game_math.prg").read_bytes()
    state = json.loads((ROOT / "RELEASE_STATUS.json").read_text())
    assert hash_bytes(original) == state["reference_prg_sha256"]["v1_balanced"]
    start = int.from_bytes(original[:2], "little")
    mem = bytearray(65536)
    mem[start:start + len(original) - 2] = original[2:]
    changed, evidence = proposal(mem)
    candidate = original[:2] + bytes(changed[start:start + len(original) - 2])
    assert len(original) == len(candidate)
    assert hash_bytes(original) != hash_bytes(candidate)
    vice = os.getenv("VICE_WRAPPER", "x64sc")
    result = {
        "status": "PASS_NATIVE_CANDIDATE_ONLY",
        "native_cycles_measured": False, "resident_published": False,
        "profile": "v1_balanced", "source_pinned_sha256": hash_bytes(original),
        "candidate": evidence, "ops": {}, "paired_inputs": 0,
        "full_resident_native_calls": 0
    }
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        for k, op in enumerate(API):
            baseline = run_native(original, op, f"v1_{k}_old", 6560 + k * 2, folder, vice)
            changed = run_native(candidate, op, f"v1_{k}_new", 6561 + k * 2, folder, vice)
            assert baseline["records"] == changed["records"], (op, "native old/new differ")
            result["ops"][op] = {
                "operand_count": COUNT,
                "same_outputs": True,
                "old_dump_sha256": baseline["dump_sha256"],
                "new_dump_sha256": changed["dump_sha256"]
            }
            result["paired_inputs"] += COUNT
            result["full_resident_native_calls"] += 2 * COUNT
            print("NATIVE VICE V1 32/16", op, "PASS", 2 * COUNT, "full calls", flush=True)
    assert result["paired_inputs"] == 96
    assert result["full_resident_native_calls"] == 192
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("NATIVE VICE V1 32/16 OOL ZERO SCREEN PASS", result["full_resident_native_calls"])

if __name__ == "__main__":
    main()
