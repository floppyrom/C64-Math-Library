#!/usr/bin/env python3
"""Standalone exhaustive benchmark/certifier for the readable ATAN2 sources."""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from mini6502 import Assembler, CPU  # noqa: E402
from tables import (build_tables, build_sum_tables, build_sum_small_tables,
                    exact_phase, phase_error, signed8)  # noqa: E402

KINDS = ('compact', 'fast', 'compact_opt', 'sum_small', 'sum_fast')
TABLE_BYTES = {'compact': 512, 'fast': 1280, 'compact_opt': 512,
               'sum_small': 768, 'sum_fast': 1024}

ORG = 0x8000
PUBLIC = 0x7F00  # 3-cycle JMP wrapper so timings match MATH_ATAN2_8 publication.
X0, Y0, Z0 = 0xC000, 0xC004, 0xC008
LOG_PAGE = 0x9600
Q0_PAGE = 0x9700
Q1_PAGE = 0x5500
Q2_PAGE = 0x5F00
Q3_PAGE = 0x4700


def source(kind: str, org: int = ORG) -> str:
    path = HERE / f'atan2_{kind}.asm'
    text = path.read_text(encoding='utf-8').replace('@ORG@', f'${org:04X}')
    for symbol, address in {
        'LOGX': 0x9400, 'LOGY': 0x9500, 'QPOS': 0x9600, 'QNEG': 0x9700,
    }.items():
        text = text.replace(f'@{symbol}@', f'${address:04X}')
    return text


def image(kind: str, org: int = ORG) -> bytearray:
    log, base, q0, q1, q2, q3, _, _ = build_tables()
    code, _, _ = Assembler().assemble(source(kind, org))
    mem = bytearray(65536)
    for addr, value in code.items():
        mem[addr] = value
    mem[PUBLIC:PUBLIC + 3] = bytes((0x4C, org & 0xFF, org >> 8))
    if kind in ('sum_small', 'sum_fast'):
        tables = build_sum_small_tables() if kind == 'sum_small' else build_sum_tables()
        for addr, data in zip((0x9400, 0x9500, 0x9600, 0x9700), tables):
            mem[addr:addr + 256] = data
        return mem
    mem[LOG_PAGE:LOG_PAGE + 256] = log
    if kind in ('compact', 'compact_opt'):
        mem[Q0_PAGE:Q0_PAGE + 256] = base
    else:
        mem[Q0_PAGE:Q0_PAGE + 256] = q0
        mem[Q1_PAGE:Q1_PAGE + 256] = q1
        mem[Q2_PAGE:Q2_PAGE + 256] = q2
        mem[Q3_PAGE:Q3_PAGE + 256] = q3
    return mem


def benchmark(kind: str, initial_carry: int = 0, org: int = ORG) -> dict:
    cpu = CPU(image(kind, org))
    cpu.d = 0
    total = 0
    mn = 10**9
    mx = 0
    maxerr = 0
    failures = 0
    abi_failures = 0
    cycles = collections.Counter()
    errors = collections.Counter()
    for rx in range(256):
        sx = signed8(rx)
        for ry in range(256):
            sy = signed8(ry)
            cpu.mem[X0] = rx
            cpu.mem[Y0] = ry
            cpu.c = initial_carry
            cyc = cpu.call(PUBLIC)
            got = cpu.mem[Z0]
            err = phase_error(got, exact_phase(sx, sy))
            total += cyc
            mn = min(mn, cyc)
            mx = max(mx, cyc)
            maxerr = max(maxerr, err)
            cycles[cyc] += 1
            errors[err] += 1
            if err > 1:
                failures += 1
            if (cpu.c != 0 or cpu.mem[X0] != rx or cpu.mem[Y0] != ry
                    or cpu.a != got or cpu.sp != 0xFD or cpu.d != 0):
                abi_failures += 1
    code, _, _ = Assembler().assemble(source(kind, org))
    return {
        'kernel': kind,
        'cases': 65536,
        'initial_carry': initial_carry,
        'origin': f'${org:04X}',
        'code_bytes': len(code),
        'table_bytes': TABLE_BYTES[kind],
        'occupied_bytes_excluding_public_jmp': len(code) + TABLE_BYTES[kind],
        'zp_bytes': 0,
        'cycles_include': 'public JMP (3), kernel, RTS (6); exclude caller JSR (6)',
        'mean_cycles': total / 65536,
        'min_cycles': mn,
        'max_cycles': mx,
        'max_phase_error': maxerr,
        'failures_gt_1': failures,
        'abi_failures': abi_failures,
        'cycle_distribution': {str(k): v for k, v in sorted(cycles.items())},
        'error_distribution': {str(k): v for k, v in sorted(errors.items())},
        'status': 'PASS' if failures == 0 and abi_failures == 0 else 'FAIL',
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kernel', choices=(*KINDS, 'all'), default='all')
    ap.add_argument('--json', action='store_true', help='emit machine-readable JSON')
    args = ap.parse_args()
    kinds = KINDS if args.kernel == 'all' else (args.kernel,)
    results = [benchmark(k) for k in kinds]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(
                f"{r['kernel']:7s}  {r['mean_cycles']:.6f} cycles  "
                f"range {r['min_cycles']}-{r['max_cycles']}  "
                f"max error {r['max_phase_error']}  {r['status']}"
            )
    if any(r['status'] != 'PASS' for r in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
