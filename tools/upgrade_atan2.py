#!/usr/bin/env python3
"""Install and exhaustively certify the 2026-09-17 stock-C64 ATAN2 upgrade.

Readable kernel sources and deterministic table generation live in
``routines/atan2/``. This tool only installs those kernels into the shipped
profiles and certifies the installed public entry.

V1 uses the 512-byte / zero-ZP compact implementation. V2/V3 use the
1280-byte / zero-ZP four-quadrant implementation. V4 keeps the exact REU path.
"""
from __future__ import annotations

from pathlib import Path
import collections
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
ATAN_DIR = ROOT / 'routines' / 'atan2'
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ATAN_DIR))

from mini6502 import Assembler, CPU
from tables import LOG_OFFSET, LOG_SCALE, build_tables, exact_phase, phase_error, signed8

PROFILES = ('v1_balanced', 'v2_pareto_fast', 'v3_reu_512k')
PRG = {p: next((ROOT / p / 'resident').glob('*game_math.prg')) for p in PROFILES}
PUBLIC_ATAN = 0x5E2A
PUBLIC_ISQRT16 = 0x5E2D
X0, Y0, Z0 = 0xC000, 0xC004, 0xC008

# Fast donor pages are chosen from page-aligned holes that remain free after the
# direct-signed SMUL8 upgrade. V5 later remaps donor $4700 to the V1-free
# REG_KERNEL+$1700 page ($5700 reference); $5500/$5F00 are shared.
LOG_PAGE = 0x9600
Q0_PAGE = 0x9700
Q1_PAGE = 0x5500
Q2_PAGE = 0x5F00
Q3_PAGE = 0x4700


def load_prg(path: Path):
    b = path.read_bytes()
    lo = b[0] | (b[1] << 8)
    hi = lo + len(b) - 3
    mem = bytearray(65536)
    mem[lo:hi + 1] = b[2:]
    return mem, lo, hi


def write_prg(mem: bytearray, lo: int, hi: int, path: Path):
    path.write_bytes(bytes((lo & 255, lo >> 8)) + bytes(mem[lo:hi + 1]))


def jmp_target(mem: bytearray, addr: int) -> int:
    if mem[addr] != 0x4C:
        raise RuntimeError(f'expected JMP at ${addr:04X}')
    return mem[addr + 1] | (mem[addr + 2] << 8)


def kernel_source(kind: str, org: int) -> str:
    path = ATAN_DIR / f'atan2_{kind}.asm'
    if not path.exists():
        raise RuntimeError(f'missing ATAN2 source: {path}')
    return path.read_text(encoding='utf-8').replace('@ORG@', f'${org:04X}')


def patch_profile(profile: str, tables):
    log, base, q0, q1, q2, q3, _, _ = tables
    path = PRG[profile]
    mem, lo, hi = load_prg(path)
    atan = jmp_target(mem, PUBLIC_ATAN)
    isqrt = jmp_target(mem, PUBLIC_ISQRT16)
    kind = 'compact' if profile == 'v1_balanced' else 'fast'
    code, _, _ = Assembler().assemble(kernel_source(kind, atan))
    if min(code) != atan or max(code) >= isqrt:
        raise RuntimeError(f'{profile}: ATAN2 body does not fit stable slot')
    for addr, value in code.items():
        mem[addr] = value
    for addr in range(max(code) + 1, isqrt):
        mem[addr] = 0
    mem[LOG_PAGE:LOG_PAGE + 256] = log
    if profile == 'v1_balanced':
        mem[Q0_PAGE:Q0_PAGE + 256] = base
    else:
        mem[Q0_PAGE:Q0_PAGE + 256] = q0
        mem[Q1_PAGE:Q1_PAGE + 256] = q1
        mem[Q2_PAGE:Q2_PAGE + 256] = q2
        mem[Q3_PAGE:Q3_PAGE + 256] = q3
    write_prg(mem, lo, hi, path)
    return {
        'atan_body': f'${atan:04X}-${max(code):04X}',
        'isqrt16_body': f'${isqrt:04X}',
        'code_bytes': len(code),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def validate_profile(profile: str):
    mem, _, _ = load_prg(PRG[profile])
    cpu = CPU(mem)
    cpu.d = 0
    total = 0
    mn = 10**9
    mx = 0
    failures = 0
    maxerr = 0
    errors = collections.Counter()
    cycles = collections.Counter()
    for rx in range(256):
        sx = signed8(rx)
        for ry in range(256):
            sy = signed8(ry)
            cpu.mem[X0] = rx
            cpu.mem[Y0] = ry
            cyc = cpu.call(PUBLIC_ATAN)
            got = cpu.mem[Z0]
            exp = exact_phase(sx, sy)
            err = phase_error(got, exp)
            total += cyc
            mn = min(mn, cyc)
            mx = max(mx, cyc)
            cycles[cyc] += 1
            errors[err] += 1
            maxerr = max(maxerr, err)
            if err > 1:
                failures += 1
    return {
        'cases': 65536,
        'mean_cycles': total / 65536,
        'min_cycles': mn,
        'max_cycles': mx,
        'cycle_distribution': {str(k): v for k, v in sorted(cycles.items())},
        'max_phase_error': maxerr,
        'error_distribution': {str(k): v for k, v in sorted(errors.items())},
        'failures_gt_1': failures,
        'status': 'PASS' if failures == 0 else 'FAIL',
    }


def update_perf(profile: str, result: dict):
    path = ROOT / profile / 'PUBLIC_PERFORMANCE_GAME_MATH.csv'
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0])
    found = False
    for row in rows:
        if row['routine'] == 'ATAN2_8':
            row['cases'] = str(result['cases'])
            row['mean_cycles'] = repr(result['mean_cycles'])
            row['min_cycles'] = str(result['min_cycles'])
            row['max_cycles'] = str(result['max_cycles'])
            found = True
    if not found:
        raise RuntimeError(f'{profile}: ATAN2 row missing')
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    tables = build_tables()
    result = {
        'status': 'PASS',
        'date': '2026-09-17',
        'algorithm': {
            'log_scale': LOG_SCALE,
            'log_offset': LOG_OFFSET,
            'finite_log_span': max(tables[6][1:]) - min(tables[6][1:]),
            'max_first_quadrant_class_span': tables[7],
            'compact_tables_bytes': 512,
            'fast_tables_bytes': 1280,
            'zp_bytes': 0,
            'readable_sources': 'routines/atan2',
            'fast_extra_pages_reference': ['$5500', '$5F00', '$4700'],
            'v5_q3_remap_note': (
                'V5 maps donor $4700 to REG_KERNEL+$1700 ($5700 reference); '
                'Q1/Q2 remain at $5500/$5F00. These pages are free in the '
                'current direct-SMUL8 V1 base.'
            ),
        },
        'profiles': {},
    }
    for profile in PROFILES:
        install = patch_profile(profile, tables)
        validation = validate_profile(profile)
        if validation['status'] != 'PASS':
            raise RuntimeError(f'{profile}: ATAN2 exhaustive validation failed')
        update_perf(profile, validation)
        result['profiles'][profile] = {
            **install,
            **validation,
            'tier': 'compact_512B' if profile == 'v1_balanced' else 'fast_1280B',
        }
        print(
            profile,
            result['profiles'][profile]['tier'],
            f"{validation['mean_cycles']:.6f}",
            validation['min_cycles'],
            validation['max_cycles'],
            install['code_bytes'],
            'B code',
        )
    out = ROOT / 'validation/ATAN2_UPGRADE_VALIDATION.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS ->', out)


if __name__ == '__main__':
    main()
