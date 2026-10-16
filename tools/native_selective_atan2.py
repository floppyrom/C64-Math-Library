#!/usr/bin/env python3
"""Native x64sc correctness of selective ATAN2 compact/fast full-table PRGs.

This does not claim wall-clock or native cycle timings. It checks 96 signed
pairs per variant per placement, phase/A/carry/inputs, using a RAM-backed
monitor harness and the exact linker output.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import random
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "routines" / "atan2"))
from tables import exact_phase, phase_error, signed8
import math_builder
import selective_linker

H = 0x2000
INPUT = 0x3000
OUTPUT = 0x3800
STRIDE = 0x80
N = 96
SAVE_A = 0xC030
SAVE_P = 0xC031


def corpus():
    edges = [0, 1, 2, 3, 63, 64, 127, 128, 129, 192, 254, 255]
    pairs = [(x, y) for x in edges for y in edges]
    rng = random.Random(0xA7A2C64)
    rng.shuffle(pairs)
    return pairs[:48] + [(rng.randrange(256), rng.randrange(256))
                         for _ in range(48)]


def harness(entry, io):
    b = bytearray()
    def emit(*values):
        b.extend(values)
    def absop(opcode, address):
        emit(opcode, address & 255, address >> 8)
    # Keep KERNAL/BASIC shadowed by RAM, disable interrupts and clear D.
    emit(0x78, 0xD8, 0xA9, 0x34, 0x85, 0x01, 0xA2, 0)
    loop = H + len(b)
    absop(0xBD, INPUT)
    absop(0x8D, io)
    absop(0xBD, INPUT + STRIDE)
    absop(0x8D, io + 4)
    emit(0x8A, 0x48)
    absop(0x20, entry)
    absop(0x8D, SAVE_A)
    emit(0x08, 0x68)
    absop(0x8D, SAVE_P)
    emit(0x68, 0xAA)
    for source, target in (
        (io + 8, OUTPUT),
        (SAVE_A, OUTPUT + STRIDE),
        (SAVE_P, OUTPUT + 2 * STRIDE),
        (io, OUTPUT + 3 * STRIDE),
        (io + 4, OUTPUT + 4 * STRIDE),
    ):
        absop(0xAD, source)
        absop(0x9D, target)
    emit(0xE8, 0xE0, N, 0xF0, 0x03)
    absop(0x4C, loop)
    stop = H + len(b)
    absop(0x4C, stop)
    assert len(b) < 0x300
    return bytes(b), stop


def run_native(path, variant, code, io, port, folder):
    data = path.read_bytes()
    load = data[0] | data[1] << 8
    assert load == code
    mem = bytearray(65536)
    mem[load:load+len(data)-2] = data[2:]
    program, stop = harness(code, io)
    # The exported label is the kernel origin for ATAN2 only.
    mem[H:H+len(program)] = program
    cases = corpus()
    for index, (x, y) in enumerate(cases):
        mem[INPUT + index] = x
        mem[INPUT + STRIDE + index] = y
    tag = "atan2_" + variant + ("_%04x" % code)
    prg = folder / (tag + ".prg")
    dump = folder / (tag + ".bin")
    prg.write_bytes(bytes((H & 255, H >> 8)) + mem[H:0xC100])
    vice = os.environ["VICE_WRAPPER"]
    argv = [vice, "-console", "-silent", "-sounddev", "dummy", "-warp",
            "-remotemonitor", "-remotemonitoraddress", "127.0.0.1:" + str(port),
            "-initbreak", "reset"]
    with (folder / (tag + ".log")).open("w") as log:
        proc = subprocess.Popen(argv, cwd=folder, stdout=log, stderr=log)
        try:
            for _ in range(150):
                try:
                    sock = socket.create_connection(("127.0.0.1", port), timeout=.1)
                    break
                except (ConnectionRefusedError, TimeoutError):
                    time.sleep(.04)
            else:
                raise RuntimeError("x64sc monitor did not start")
            sock.settimeout(.25)
            def cmd(line, marker):
                sock.sendall((line + "\n").encode())
                result = b""
                for _ in range(180):
                    try:
                        chunk = sock.recv(16384)
                        if not chunk:
                            break
                        result += chunk
                        if marker.encode() in result and result.endswith(b") "):
                            break
                    except socket.timeout:
                        continue
                if marker.encode() not in result:
                    raise RuntimeError("Monitor command %r: %r" %
                                       (line, result[-500:]))
            cmd('load "' + str(prg) + '" 0', "Loading")
            cmd("break " + format(stop, "04x"), "BREAK:")
            cmd("g " + format(H, "04x"), "Stop on  exec")
            end = OUTPUT + 5 * STRIDE - 1
            cmd('bsave "' + str(dump) + '" 0 ' +
                format(OUTPUT, "04x") + " " + format(end, "04x"), "Saving")
            sock.sendall(b"quit\n")
            sock.close()
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    read = dump.read_bytes()
    assert len(read) == 5 * STRIDE
    for i, (x, y) in enumerate(cases):
        phase = read[i]
        acc = read[STRIDE + i]
        p = read[2 * STRIDE + i]
        actual_x = read[3 * STRIDE + i]
        actual_y = read[4 * STRIDE + i]
        if (phase_error(phase, exact_phase(signed8(x), signed8(y))) > 1 or
                acc != phase or p & 1 or actual_x != x or actual_y != y):
            raise AssertionError((tag, i, x, y, phase, acc, p, actual_x, actual_y))
    return {"case_count": N, "input_sha256": hashlib.sha256(
        json.dumps(cases, separators=(",", ":")).encode()).hexdigest(),
        "dump_sha256": hashlib.sha256(read).hexdigest()}


def main():
    if not os.path.isfile(os.environ.get("VICE_WRAPPER", "")):
        raise RuntimeError("VICE_WRAPPER must be a working headless x64sc")
    index = math_builder.operation_index()
    total = 0
    with tempfile.TemporaryDirectory(prefix="selective_atan2_vice_") as tmp:
        folder = Path(tmp)
        for i, (origin, io) in enumerate(((0x8000, 0xC000), (0x7123, 0xC040))):
            for kind in ("compact", "sum-fast"):
                plan = math_builder.create_plan(
                    index, ["ATAN2_8"], zp_budget=0, ram_budget=1500,
                    pins={"ATAN2_8": "link:" + kind})
                manifest = selective_linker.build(
                    plan, folder, memory={"code_base": origin, "math_io": io})
                entry = int(manifest["operations"][0]["entry"][1:], 16)
                if entry != origin:
                    raise AssertionError("ATAN2 public entry is not code origin")
                proof = run_native(folder / "math_selective.prg", kind,
                                   origin, io, 7470 + 2*i +
                                   (0 if kind == "compact" else 1), folder)
                total += proof["case_count"]
                print("native linked ATAN2", kind, "%04x" % origin,
                      "PASS", proof, flush=True)
    assert total == 384
    print("NATIVE SELECTIVE ATAN2 PASS", total)

if __name__ == "__main__":
    main()
