#!/usr/bin/env python3
"""Cycle-accurate resident-image benchmark for MUL_DIV16 research.

Research tooling only. It patches generated wrappers into RAM under KERNAL in
the mini6502 memory model, initializes the selected stock profile, and measures
all available candidates on identical deterministic inputs.
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
from generate_umuldiv16 import (  # noqa: E402
    generate_bounded,
    generate_composed,
    generate_direct_hybrid_v2,
    generate_direct_v2,
    generate_hybrid,
)

MATH_INIT = 0x3280
X0, X1 = 0xC000, 0xC001
Y0, Y1 = 0xC004, 0xC005
Z0, Z1, Z2, Z3 = 0xC008, 0xC009, 0xC00A, 0xC00B
D0, D1 = 0xC014, 0xC015

ORIGIN_CANDIDATE = 0xE000
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


def available_variants(profile: str):
    if profile == 'v2':
        return ('composed', 'fused', 'hybrid', 'direct', 'direct_hybrid')
    if profile == 'v1':
        return ('composed', 'fused', 'hybrid')
    return ('composed', 'fused')


def make_cpu(profile: str, kind: str):
    path = PROFILE_PRG[profile]
    if not path.exists():
        raise FileNotFoundError(path)
    cpu = CPU(load_prg(path))
    cpu.d = 0
    # V2 requires init; V1/V5 tolerate it. Initialization is outside timing.
    cpu.call(MATH_INIT)

    if kind == 'fused':
        labels = patch_source(cpu.mem, generate_bounded(ORIGIN_CANDIDATE))
        entry = labels['umuldiv16_bounded']
    elif kind == 'hybrid':
        labels = patch_source(cpu.mem, generate_hybrid(profile, ORIGIN_CANDIDATE))
        entry = labels['umuldiv16_hybrid']
    elif kind == 'direct':
        if profile != 'v2':
            raise ValueError('direct is currently V2-only')
        labels = patch_source(cpu.mem, generate_direct_v2(ORIGIN_CANDIDATE))
        entry = labels['umuldiv16_direct_v2']
    elif kind == 'direct_hybrid':
        if profile != 'v2':
            raise ValueError('direct_hybrid is currently V2-only')
        labels = patch_source(cpu.mem, generate_direct_hybrid_v2(ORIGIN_CANDIDATE))
        entry = labels['umuldiv16_direct_hybrid_v2']
    elif kind == 'composed':
        labels = patch_source(cpu.mem, generate_composed(ORIGIN_COMPOSED))
        entry = labels['umuldiv16_composed']
    else:
        raise ValueError(kind)
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
    return [(a, b, d) for a in vals for b in vals for d in vals]


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


def corpus_shape(cases):
    product16 = bounded = q0 = q1 = q255 = 0
    for a, b, d in cases:
        product = a * b
        product16 += int(product <= 0xFFFF)
        if d:
            q = product // d
            if q <= 0xFFFF:
                bounded += 1
                q0 += int(q == 0)
                q1 += int(q <= 1)
                q255 += int(q <= 0xFF)
    n = len(cases)
    return {
        'cases': n,
        'product_fits_16_percent': 100.0 * product16 / n if n else 0.0,
        'bounded_percent': 100.0 * bounded / n if n else 0.0,
        'q_eq_0_percent': 100.0 * q0 / n if n else 0.0,
        'q_le_1_percent': 100.0 * q1 / n if n else 0.0,
        'q_le_255_percent': 100.0 * q255 / n if n else 0.0,
    }


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
                print(
                    f'{profile}/{kind} mismatch a={a} b={b} d={d}: '
                    f'got={got} expected={exp}',
                    file=sys.stderr,
                )
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
    ap.add_argument(
        '--corpus',
        choices=('bounded_uniform', 'mixed_uniform', 'game8', 'game12_bounded', 'all'),
        default='all',
    )
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    names = (
        ('bounded_uniform', 'mixed_uniform', 'game8', 'game12_bounded')
        if args.corpus == 'all' else (args.corpus,)
    )
    variants = available_variants(args.profile)
    results = {
        'profile': args.profile,
        'seed': args.seed,
        'variants': variants,
        'edge_cases': {},
        'corpora': {},
    }

    edges = edge_cases()
    for kind in variants:
        results['edge_cases'][kind] = run_variant(args.profile, kind, edges)

    for i, name in enumerate(names):
        cases = corpus(name, args.cases, args.seed + i)
        row = {'shape': corpus_shape(cases)}
        for kind in variants:
            row[kind] = run_variant(args.profile, kind, cases)
        baseline = row['composed']['mean_cycles']
        row['speedup_vs_composed_percent'] = {
            kind: 100.0 * (baseline - row[kind]['mean_cycles']) / baseline
            for kind in variants if kind != 'composed'
        }
        results['corpora'][name] = row

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"profile={args.profile} seed=${args.seed:X} variants={','.join(variants)}")
        for kind, r in results['edge_cases'].items():
            print(
                f"edge {kind:13s}: mean={r['mean_cycles']:.3f} "
                f"range={r['min_cycles']}-{r['max_cycles']} errors={r['errors']}"
            )
        for name, row in results['corpora'].items():
            print(name)
            s = row['shape']
            print(
                f"  shape: product16={s['product_fits_16_percent']:.2f}% "
                f"bounded={s['bounded_percent']:.2f}% q0={s['q_eq_0_percent']:.2f}% "
                f"q<=1={s['q_le_1_percent']:.2f}% q<=255={s['q_le_255_percent']:.2f}%"
            )
            for kind in variants:
                r = row[kind]
                extra = ''
                if kind != 'composed':
                    extra = f" speedup={row['speedup_vs_composed_percent'][kind]:.2f}%"
                print(
                    f"  {kind:13s}: mean={r['mean_cycles']:.3f} "
                    f"range={r['min_cycles']}-{r['max_cycles']} "
                    f"errors={r['errors']}{extra}"
                )

    bad = any(v['errors'] for v in results['edge_cases'].values())
    for row in results['corpora'].values():
        bad |= any(row[k]['errors'] for k in variants)
    if bad:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
