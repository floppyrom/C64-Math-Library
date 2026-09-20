#!/usr/bin/env python3
"""Install and exhaustively certify the 2026-09-20 stock-C64 ATAN2 upgrade.

Readable kernel sources and deterministic table generation live in
``routines/atan2/``. This tool only installs those kernels into the shipped
profiles and certifies the installed public entry.

V1 uses the 512-byte / zero-ZP optimized compact implementation. V2/V3 use
the 1024-byte / zero-ZP sum-fast implementation. V4 keeps the exact REU path.
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
from tables import (
    LOG_OFFSET, LOG_SCALE, build_sum_tables, build_tables,
    exact_phase, phase_error, signed8,
)

PROFILES = ('v1_balanced', 'v2_pareto_fast', 'v3_reu_512k')
PRG = {p: next((ROOT / p / 'resident').glob('*game_math.prg')) for p in PROFILES}
PUBLIC_ATAN = 0x5E2A
PUBLIC_ISQRT16 = 0x5E2D
X0, Y0, Z0 = 0xC000, 0xC004, 0xC008

COMPACT_LOG_PAGE = 0x9600
COMPACT_ANGLE_PAGE = 0x9700
SUM_LOGX_PAGE = 0x9600
SUM_LOGY_PAGE = 0x9700
SUM_QPOS_PAGE = 0x6E00
SUM_QNEG_PAGE = 0x6F00
OLD_FAST_Q3_PAGE = 0x9100


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


def kernel_source(kind: str, org: int, symbols: dict[str, int] | None = None) -> str:
    path = ATAN_DIR / f'atan2_{kind}.asm'
    if not path.exists():
        raise RuntimeError(f'missing ATAN2 source: {path}')
    text = path.read_text(encoding='utf-8').replace('@ORG@', f'${org:04X}')
    for name, address in (symbols or {}).items():
        text = text.replace(f'@{name}@', f'${address:04X}')
    return text


def patch_profile(profile: str, compact_tables, sum_tables):
    log, base, _, _, _, _, _, _ = compact_tables
    logx, logy, qpos, qneg = sum_tables
    path = PRG[profile]
    mem, lo, hi = load_prg(path)
    atan = jmp_target(mem, PUBLIC_ATAN)
    isqrt = jmp_target(mem, PUBLIC_ISQRT16)
    if profile == 'v1_balanced':
        kind = 'compact_opt'
        symbols = None
    else:
        kind = 'sum_fast'
        symbols = {
            'LOGX': SUM_LOGX_PAGE,
            'LOGY': SUM_LOGY_PAGE,
            'QPOS': SUM_QPOS_PAGE,
            'QNEG': SUM_QNEG_PAGE,
        }
    code, _, _ = Assembler().assemble(kernel_source(kind, atan, symbols))
    if min(code) != atan or max(code) >= isqrt:
        raise RuntimeError(f'{profile}: ATAN2 body does not fit stable slot')
    for addr, value in code.items():
        mem[addr] = value
    for addr in range(max(code) + 1, isqrt):
        mem[addr] = 0
    if profile == 'v1_balanced':
        mem[COMPACT_LOG_PAGE:COMPACT_LOG_PAGE + 256] = log
        mem[COMPACT_ANGLE_PAGE:COMPACT_ANGLE_PAGE + 256] = base
    else:
        mem[SUM_LOGX_PAGE:SUM_LOGX_PAGE + 256] = logx
        mem[SUM_LOGY_PAGE:SUM_LOGY_PAGE + 256] = logy
        mem[SUM_QPOS_PAGE:SUM_QPOS_PAGE + 256] = qpos
        mem[SUM_QNEG_PAGE:SUM_QNEG_PAGE + 256] = qneg
        mem[OLD_FAST_Q3_PAGE:OLD_FAST_Q3_PAGE + 256] = bytes(256)
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
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    compact_tables = build_tables()
    sum_tables = build_sum_tables()
    result = {
        'status': 'PASS',
        'date': '2026-09-20',
        'algorithm': {
            'log_scale': LOG_SCALE,
            'log_offset': LOG_OFFSET,
            'finite_log_span': max(compact_tables[6][1:]) - min(compact_tables[6][1:]),
            'max_first_quadrant_class_span': compact_tables[7],
            'compact_tables_bytes': 512,
            'fast_tables_bytes': 1024,
            'zp_bytes': 0,
            'readable_sources': 'routines/atan2',
            'fast_pages_reference': ['$9600', '$9700', '$6E00', '$6F00'],
            'v5_remap_note': (
                'V5 maps all four donor pages to REG_TABLE+$0D00 through '
                'REG_TABLE+$1000. These pages are free in the current V1 base.'
            ),
        },
        'profiles': {},
    }
    for profile in PROFILES:
        install = patch_profile(profile, compact_tables, sum_tables)
        validation = validate_profile(profile)
        if validation['status'] != 'PASS':
            raise RuntimeError(f'{profile}: ATAN2 exhaustive validation failed')
        update_perf(profile, validation)
        result['profiles'][profile] = {
            **install,
            **validation,
            'tier': 'compact_opt_512B' if profile == 'v1_balanced' else 'sum_fast_1024B',
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
