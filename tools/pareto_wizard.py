#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, json, shutil, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_pareto as bp


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f' [{default}]' if default is not None else ''
    v = input(f'{prompt}{suffix}: ').strip()
    return v if v else (default or '')


def parse_hot(text: str) -> dict[str, float]:
    out: dict[str, float] = {}
    if not text.strip():
        return out
    for raw in text.split(','):
        raw = raw.strip()
        if not raw:
            continue
        if '=' in raw:
            name, val = raw.split('=', 1)
            weight = float(val)
        else:
            name, weight = raw, 10.0
        name = name.strip().upper()
        if not name.startswith('MATH_'):
            name = 'MATH_' + name
        out[name] = weight
    return out


def selection_summary(sel: dict, ram_budget: int | None, init_policy: str, weights: dict[str, float]) -> dict:
    return {
        'mode': sel['mode'],
        'selected_packs': ['v2_full'] if sel['mode'] == 'v2_full' else sel['packs'],
        'zp_bytes_reserved': sel['zp_bytes'],
        'extra_private_ram_bytes': sel['extra_ram'],
        'ram_budget': ram_budget,
        'math_init_required': sel['init_required'],
        'init_policy': init_policy,
        'routine_weights': weights,
    }


def main():
    ap = argparse.ArgumentParser(description='Interactive stock-C64 Pareto profile builder.')
    ap.add_argument('--zp-budget', type=int)
    ap.add_argument('--ram-budget', type=int, help='exact extra private/resident bytes relative to V1; omit for unlimited')
    ap.add_argument('--init-policy', choices=['auto', 'optional'])
    ap.add_argument('--hot', default=None, help='comma-separated routine weights, e.g. UMUL16=20,SMUL16=5')
    ap.add_argument('--config-kind', choices=['reference', 'alternate'])
    ap.add_argument('--config', type=Path)
    ap.add_argument('--out', type=Path, default=ROOT / 'build_pareto')
    ap.add_argument('--name')
    ap.add_argument('--yes', action='store_true', help='build immediately after showing the selection')
    ap.add_argument('--preview-only', action='store_true')
    args = ap.parse_args()

    print('C64 Math Library — Custom Pareto Builder')
    print('The builder chooses certified V1/V2 implementation packs at build time; there is no runtime dispatcher.\n')

    zp = args.zp_budget
    if zp is None:
        zp = int(ask('How many total zero-page bytes can the math library use?', '31'))

    ram = args.ram_budget
    if ram is None and '--ram-budget' not in sys.argv:
        r = ask('Maximum extra private RAM bytes relative to V1? blank = unlimited', '')
        ram = int(r) if r else None

    init_policy = args.init_policy
    if init_policy is None:
        a = ask('May the generated profile require one MATH_INIT call at startup? Y/n', 'Y').lower()
        init_policy = 'optional' if a in ('n', 'no') else 'auto'

    hot_text = args.hot
    if hot_text is None:
        hot_text = ask('Hot routines (optional, e.g. UMUL16=20,SMUL16=10; blank = equal weights)', '')
    weights = parse_hot(hot_text)

    kind = args.config_kind
    if kind is None and args.config is None:
        k = ask('Memory map: reference or alternate?', 'reference').lower()
        kind = 'alternate' if k.startswith('a') else 'reference'
    kind = kind or 'reference'

    sel = bp.select_packs(zp, ram, init_policy, weights)
    sel['zp_budget_requested'] = zp
    print('\nSelected configuration:')
    print(json.dumps(selection_summary(sel, ram, init_policy, weights), indent=2))

    if args.preview_only:
        return
    do_build = args.yes
    if not do_build:
        do_build = ask('Build this profile now? Y/n', 'Y').lower() not in ('n', 'no')
    if not do_build:
        print('Preview only; no files written.')
        return

    cfg = args.config or ROOT / 'relocatable_source' / bp.PROFILE / f'math_config_{kind}.inc'
    name = args.name or f'wizard_zp{zp}_{kind}'
    out = args.out / name
    if out.exists():
        shutil.rmtree(out)
    man = bp.build_full_v2(cfg, out, sel) if sel['mode'] == 'v2_full' else bp.build_hybrid_custom(cfg, out, sel)
    print('\nBuild complete:')
    print(json.dumps({
        'directory': str(out),
        'prg': man['output_prg'],
        'math_api_inc': str(out / 'math_api.inc'),
        'manifest': str(out / 'selection_manifest.json'),
        'sha256': man['output_sha256'],
    }, indent=2))


if __name__ == '__main__':
    main()
