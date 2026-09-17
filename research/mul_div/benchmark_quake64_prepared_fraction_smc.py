#!/usr/bin/env python3
"""Benchmark a Quake64-native SMC prepared fraction against current paths.

The new candidate reuses Quake64's already resident quarter-square tables at
$F000-$F7FF and patches absolute,Y operands for the prepared multiplier bytes.
It measures the value of the prepared-ratio idea when integrated with the
*game's own* table/memory architecture rather than importing V2's UMUL8 path.

Compared on identical strict near-clip inputs:

  quake_current                 scale_nd + lerp16 twice
  v2_inline_nearest/floor       corrected V2 profile-native PREP/APPLY
  quake_smc_nearest/floor       new Quake-native SMC fixed-multiplier path

Research evidence only; this does not patch/build Quake64 itself.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(HERE))

from mini6502 import Assembler, CPU  # noqa: E402
from generate_quake64_prepared_fraction_smc import generate  # noqa: E402
from benchmark_prepared_fraction_pareto import (  # noqa: E402
    candidate_cpu as v2_candidate_cpu,
    prepared_reference,
    run_candidate as run_v2_candidate,
)
from benchmark_prepared_ratio import (  # noqa: E402
    QD,
    QN,
    QROT,
    QY,
    ZCLIP,
    err_summary,
    gets16,
    put16,
    quake_cpu,
    summarize,
    trunc_div,
)

# Actual Quake64 scratch ABI used by the new generator.
QNATIVE_N = 0x5E
QNATIVE_D = 0x60
QNATIVE_Y = 0x62
QNATIVE_Z = 0x40


def fill_quake_sq_tables(mem: bytearray) -> None:
    sq = [(i * i) // 4 for i in range(512)]
    neg = [((i - 255) * (i - 255)) // 4 for i in range(512)]
    for i, value in enumerate(sq):
        mem[0xF000 + i] = value & 0xFF
        mem[0xF200 + i] = (value >> 8) & 0xFF
    for i, value in enumerate(neg):
        mem[0xF400 + i] = value & 0xFF
        mem[0xF600 + i] = (value >> 8) & 0xFF


def quake_smc_cpu(rounding: str):
    mem = bytearray(65536)
    fill_quake_sq_tables(mem)
    cpu = CPU(mem)
    cpu.d = 0
    code, labels, _ = Assembler().assemble(generate(rounding=rounding))
    for addr, value in code.items():
        cpu.mem[addr] = value
    return cpu, labels['qfrac_prep'], labels['qfrac_apply_s16'], len(code)


def run_quake_smc(cpu: CPU, prep: int, apply: int,
                  n: int, d: int, xa: int, ya: int):
    put16(cpu.mem, QNATIVE_N, n)
    put16(cpu.mem, QNATIVE_D, d)
    cp = cpu.call(prep)
    put16(cpu.mem, QNATIVE_Y, xa)
    cx = cpu.call(apply)
    gx = gets16(cpu.mem, QNATIVE_Z)
    put16(cpu.mem, QNATIVE_Y, ya)
    cy = cpu.call(apply)
    gy = gets16(cpu.mem, QNATIVE_Z)
    return cp, cx, cy, gx, gy


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    qn_cpu, qn_prep, qn_apply, qn_code = quake_smc_cpu('nearest')
    qf_cpu, qf_prep, qf_apply, qf_code = quake_smc_cpu('floor')
    vn_cpu, vn_prep, vn_apply = v2_candidate_cpu('pareto_inline_nearest')
    vf_cpu, vf_prep, vf_apply = v2_candidate_cpu('pareto_inline_floor')
    qc, qrun = quake_cpu()

    rows = {
        'quake_smc_nearest': {'prep': [], 'apply': [], 'pair': [], 'errors': 0, 'exact': [], 'code_bytes': qn_code},
        'quake_smc_floor': {'prep': [], 'apply': [], 'pair': [], 'errors': 0, 'exact': [], 'code_bytes': qf_code},
        'v2_inline_nearest': {'prep': [], 'apply': [], 'pair': [], 'errors': 0, 'exact': []},
        'v2_inline_floor': {'prep': [], 'apply': [], 'pair': [], 'errors': 0, 'exact': []},
        'quake_current': {'pair': [], 'exact': []},
    }

    rng = random.Random(args.seed)
    for _ in range(args.cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP + 1, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        assert 0 < n < d <= 0xFFFF
        xa = rng.randint(-8192, 8191)
        ya = rng.randint(-8192, 8191)
        exact_x = trunc_div(xa * n, d)
        exact_y = trunc_div(ya * n, d)

        for name, cpu, prep, apply, rounding, runner in (
            ('quake_smc_nearest', qn_cpu, qn_prep, qn_apply, 'nearest', run_quake_smc),
            ('quake_smc_floor', qf_cpu, qf_prep, qf_apply, 'floor', run_quake_smc),
            ('v2_inline_nearest', vn_cpu, vn_prep, vn_apply, 'nearest', run_v2_candidate),
            ('v2_inline_floor', vf_cpu, vf_prep, vf_apply, 'floor', run_v2_candidate),
        ):
            cp, cx, cy, gx, gy = runner(cpu, prep, apply, n, d, xa, ya)
            refx = prepared_reference(xa, n, d, rounding)
            refy = prepared_reference(ya, n, d, rounding)
            row = rows[name]
            row['prep'].append(cp)
            row['apply'].extend((cx, cy))
            row['pair'].append(cp + cx + cy)
            row['errors'] += int(gx != refx) + int(gy != refy)
            row['exact'].extend((gx - exact_x, gy - exact_y))

        # Literal Quake current arithmetic pair with ratio save/restore.
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, xa)
        qx_c = qc.call(qrun); qx = gets16(qc.mem, QROT)
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, ya)
        qy_c = qc.call(qrun); qy = gets16(qc.mem, QROT)
        rows['quake_current']['pair'].append(qx_c + qy_c + 28)
        rows['quake_current']['exact'].extend((qx - exact_x, qy - exact_y))

    qmean = statistics.fmean(rows['quake_current']['pair'])
    result = {
        'status': 'standalone_quake_native_research_not_game_build_certification',
        'cases': args.cases,
        'seed': args.seed,
        'corpus': {
            'zclip': ZCLIP,
            'z0_range': [-8192, ZCLIP - 1],
            'z1_range': [ZCLIP + 1, 8191],
            'component_range': [-8192, 8191],
            'invariant': '0<n<d',
            'applications_per_preparation': 2,
        },
        'variants': {},
        'quake_current': {
            'pair_cycles': summarize(rows['quake_current']['pair']),
            'accuracy_vs_exact': err_summary(rows['quake_current']['exact']),
        },
    }

    for name in ('quake_smc_nearest', 'quake_smc_floor', 'v2_inline_nearest', 'v2_inline_floor'):
        row = rows[name]
        pair = summarize(row['pair'])
        entry = {
            'prep_cycles': summarize(row['prep']),
            'apply_cycles': summarize(row['apply']),
            'pair_cycles': pair,
            'prepared_contract_errors': row['errors'],
            'accuracy_vs_exact': err_summary(row['exact']),
            'speedup_vs_quake_current_percent': 100.0 * (qmean - pair['mean']) / qmean,
        }
        if 'code_bytes' in row:
            entry['assembled_code_bytes'] = row['code_bytes']
        result['variants'][name] = entry

    for rounding in ('nearest', 'floor'):
        qname = f'quake_smc_{rounding}'
        vname = f'v2_inline_{rounding}'
        qm = result['variants'][qname]['pair_cycles']['mean']
        vm = result['variants'][vname]['pair_cycles']['mean']
        result['variants'][qname]['speedup_vs_v2_inline_percent'] = 100.0 * (vm - qm) / vm

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for name, row in result['variants'].items():
            print(
                f"{name:20s} prep={row['prep_cycles']['mean']:.3f} "
                f"apply={row['apply_cycles']['mean']:.3f} "
                f"pair={row['pair_cycles']['mean']:.3f} "
                f"errors={row['prepared_contract_errors']}"
            )
        print(f"quake_current pair={qmean:.3f}")

    bad = sum(rows[name]['errors'] for name in rows if 'errors' in rows[name])
    if bad:
        raise SystemExit(1)
    for name in ('quake_smc_nearest', 'quake_smc_floor'):
        if max(abs(e) for e in rows[name]['exact']) > 1:
            raise SystemExit(f'{name} exceeded <=1 error bound')


if __name__ == '__main__':
    main()
