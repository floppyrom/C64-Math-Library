#!/usr/bin/env python3
"""Cycle-accurate resident-image benchmark for the first UMULDIV16 candidate.

This is research tooling, not release validation. It patches wrappers into RAM
under KERNAL in the mini6502 memory model, initializes the selected stock profile,
and measures the composed and fused paths on identical deterministic inputs.
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
from generate_umuldiv16 import generate_bounded, generate_composed  # noqa: E402

MATH_INIT = 0x3280
X0, X1 = 0xC000, 0xC001
Y0, Y1 = 0xC004, 0xC005
Z0, Z1, Z2, Z3 = 0xC008, 0xC009, 0xC00A, 0xC00B
D0, D1 = 0xC014, 0xC015

ORIGIN_FUSED = 0xE000
ORIGIN_COMPOSED = 0xE800

PROFILE_PRG = {
    'v1': ROOT / 'v1_balanced' / 'resident' / 'math_v1_balanced_game_math.prg',
    'v2': ROOT / 'v2_pareto_fast' / 'resident' / 'math_v2_pareto_fast_game_math.prg',
    'v5': ROOT / 'v5_hybrid_lowzp' / 'resident' / 'math_v5_hybrid_lowzp_game_math.prg',
}


def load_prg(path: Path) -> bytearray:
    raw = path.read_bytes()
    load = raw[0] | (raw[1] << 8)
    mem = bytearray(65536)
    mem[load:load + len(raw) - 2] = raw[2:]
    return mem


def patch_source(mem: bytearray, text: str) -> dict[str, int]:
    code, labels, _ = Assembler().assemble(text)
    for addr, value in code.items():
        mem[addr] = value
    return labels


def make_cpu(profile: str, kind: str):
    path = PROFILE_PRG[profile]
    if not path.exists():
        raise FileNotFoundError(path)
    cpu = CPU(load_prg(path))
    cpu.d = 0
    # V1/V5 tolerate this; V2 requires it. Initialization is outside timing.
    cpu.call(MATH_INIT)
    if kind == 'fused':
        labels = patch_source(cpu.mem, generate_bounded(ORIGIN_FUSED))
        entry = labels['umuldiv16_bounded']
    else:
        labels = patch_source(cpu.mem, generate_composed(ORIGIN_COMPOSED))
        entry = labels['umuldiv16_composed']
    return cpu, entry


def expected(a: int, b: int, d: int):
    if d == 0:
        return 1, 0, 0
    q, r = divmod(a * b, d)
    if q > 0xFFFF:
        return 1, 0, 0
    return 0, q, r


def set_inputs(cpu: CPU, a: int, b: int, d: int) -> None:
    cpu.mem[X0] = a & 0xFF
    cpu.mem[X1] = (a >> 8) & 0xFF
    cpu.mem[Y0] = b & 0xFF
    cpu.mem[Y1] = (b >> 8) & 0xFF
    cpu.mem[D0] = d & 0xFF
    cpu.mem[D1] = (d >> 8) & 0xFF


def get_outputs(cpu: CPU):
    q = cpu.mem[Z0] | (cpu.mem[Z1] << 8)
    r = cpu.mem[Z2] | (cpu.mem[Z3] << 8)
    return cpu.c, q, r


def edge_cases():
    vals = [0, 1, 2, 3, 0x7F, 0x80, 0xFF, 0x100, 0x101,
            0x7FFF, 0x8000, 0xFFFE, 0xFFFF]
    cases = []
    for a in vals:
        for b in vals:
            for d in vals:
                cases.append((a, b, d))
    return cases


def corpus(name: str, n: int, seed: int):
    rng = random.Random(seed)
    out = []
    if name == 'bounded_uniform':
        while len(out) < n:
            a = rng.randrange(0x10000)
            b = rng.randrange(0x10000)
            d = rng.randrange(1, 0x10000)
            if (a * b) // d <= 0xFFFF:
                out.append((a, b, d))
    elif name == 'mixed_uniform':
        for _ in range(n):
            out.append((rng.randrange(0x10000), rng.randrange(0x10000), rng.randrange(0x10000)))
    elif name == 'game8':
        for _ in range(n):
            out.append((rng.randrange(0x100), rng.randrange(0x100), rng.randrange(1, 0x10000)))
    elif name == 'game12_bounded':
        while len(out) < n:
            a = rng.randrange(0x1000)
            b = rng.randrange(0x1000)
            d = rng.randrange(1, 0x10000)
            if (a * b) // d <= 0xFFFF:
                out.append((a, b, d))
    else:
        raise ValueError(name)
    return out


def run_variant(profile: str, kind: str, cases):
    cpu, entry = make_cpu(profile, kind)
    cycles = []
    errors = 0
    for a, b, d in cases:
        exp = expected(a, b, d)
        set_inputs(cpu, a, b, d)
        cyc = cpu.call(entry)
        got = get_outputs(cpu)
        if got != exp:
            errors += 1
            if errors <= 5:
                print(f'{profile}/{kind} mismatch a={a} b={b} d={d}: got={got} expected={exp}', file=sys.stderr)
        cycles.append(cyc)
    return {
        'cases': len(cases),
        'errors': errors,
        'mean_cycles': statistics.fmean(cycles),
        'min_cycles': min(cycles),
        'max_cycles': max(cycles),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--profile', choices=('v1', 'v2', 'v5'), default='v2')
    ap.add_argument('--cases', type=int, default=5000, help='random cases per corpus')
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--corpus', choices=('bounded_uniform', 'mixed_uniform', 'game8', 'game12_bounded', 'all'), default='all')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    names = ('bounded_uniform', 'mixed_uniform', 'game8', 'game12_bounded') if args.corpus == 'all' else (args.corpus,)
    results = {
        'profile': args.profile,
        'seed': args.seed,
        'edge_cases': {},
        'corpora': {},
    }

    edges = edge_cases()
    for kind in ('composed', 'fused'):
        results['edge_cases'][kind] = run_variant(args.profile, kind, edges)

    for i, name in enumerate(names):
        cases = corpus(name, args.cases, args.seed + i)
        row = {}
        for kind in ('composed', 'fused'):
            row[kind] = run_variant(args.profile, kind, cases)
        c = row['composed']['mean_cycles']
        f = row['fused']['mean_cycles']
        row['speedup_percent'] = 100.0 * (c - f) / c
        results['corpora'][name] = row

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"profile={args.profile} seed=${args.seed:X}")
        print('edge:', results['edge_cases'])
        for name, row in results['corpora'].items():
            c = row['composed']
            f = row['fused']
            print(
                f"{name:20s} composed={c['mean_cycles']:.3f} "
                f"fused={f['mean_cycles']:.3f} "
                f"speedup={row['speedup_percent']:.2f}% "
                f"errors={c['errors']}/{f['errors']}"
            )

    bad = any(v['errors'] for v in results['edge_cases'].values())
    for row in results['corpora'].values():
        bad |= bool(row['composed']['errors'] or row['fused']['errors'])
    if bad:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
