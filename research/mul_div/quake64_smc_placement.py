#!/usr/bin/env python3
"""Check whether the Quake-native prepared-ratio kernel fits Quake64's GAME/heap map.

Quake64 commit 7c846549... documents:

    GAME next-free / old end_game = $9546
    heap ceiling                 = $C000
    tightest current level need = 7958 bytes (E1M2)
    current heap slack           = 2980 bytes

The prepared SMC candidate already reuses Quake's $F000-$F7FF quarter-square
bank and existing zero-page math scratch. Its only material integration cost is
ordinary GAME code RAM. This script assembles PREP/APPLY once to determine their
actual section lengths, relocates them contiguously at the old end of GAME, and
reports the remaining heap slack.

This is a memory-layout feasibility check, not a Quake64 build certification.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(HERE))

from mini6502 import Assembler  # noqa: E402
from generate_quake64_prepared_fraction_smc import generate  # noqa: E402

QUAKE_COMMIT = '7c84654946a60314568b709e7e7b97467fed69df'
OLD_END_GAME_NEXT = 0x9546
HEAP_CEILING = 0xC000
E1M2_TIGHTEST_NEED = 7958
PROBE_PREP = 0x9000
PROBE_APPLY = 0x9800


def section_lengths(rounding: str):
    code, labels, _ = Assembler().assemble(
        generate(PROBE_PREP, PROBE_APPLY, rounding)
    )
    prep_addrs = [a for a in code if PROBE_PREP <= a < PROBE_APPLY]
    apply_addrs = [a for a in code if a >= PROBE_APPLY]
    if not prep_addrs or not apply_addrs:
        raise AssertionError('expected two populated sections')
    prep_span = max(prep_addrs) + 1 - PROBE_PREP
    apply_span = max(apply_addrs) + 1 - PROBE_APPLY
    return prep_span, apply_span, len(code), labels


def check(rounding: str):
    prep_span, apply_span, code_bytes, _ = section_lengths(rounding)
    prep_origin = OLD_END_GAME_NEXT
    apply_origin = prep_origin + prep_span
    source = generate(prep_origin, apply_origin, rounding)
    code, labels, _ = Assembler().assemble(source)
    lo = min(code)
    hi_exclusive = max(code) + 1
    span = hi_exclusive - lo
    holes = span - len(code)

    new_heap_available = HEAP_CEILING - hi_exclusive
    new_tightest_slack = new_heap_available - E1M2_TIGHTEST_NEED
    current_available = HEAP_CEILING - OLD_END_GAME_NEXT
    current_slack = current_available - E1M2_TIGHTEST_NEED

    return {
        'rounding': rounding,
        'prep_origin': prep_origin,
        'prep_span_bytes': prep_span,
        'apply_origin': apply_origin,
        'apply_span_bytes': apply_span,
        'assembled_code_bytes': len(code),
        'occupied_game_span_bytes': span,
        'internal_hole_bytes': holes,
        'new_end_game_next': hi_exclusive,
        'current_heap_available_bytes': current_available,
        'new_heap_available_bytes': new_heap_available,
        'tightest_level_need_bytes': E1M2_TIGHTEST_NEED,
        'current_tightest_slack_bytes': current_slack,
        'new_tightest_slack_bytes': new_tightest_slack,
        'fits_current_tightest_heap_gate': new_tightest_slack >= 0,
        'labels': {
            'prep': labels['qfrac_prep'],
            'apply': labels['qfrac_apply_s16'],
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    rows = {r: check(r) for r in ('nearest', 'floor')}
    result = {
        'status': 'layout_feasibility_not_game_build_certification',
        'quake64_source_commit': QUAKE_COMMIT,
        'source_memory_facts': {
            'old_end_game_next': OLD_END_GAME_NEXT,
            'heap_ceiling': HEAP_CEILING,
            'tightest_level': 'E1M2',
            'tightest_level_need_bytes': E1M2_TIGHTEST_NEED,
        },
        'variants': rows,
        'shared_resources_reused': [
            '$F000-$F7FF Quake quarter-square tables',
            'existing Quake math zero-page scratch',
        ],
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for name, row in rows.items():
            print(
                f"{name:7s} code={row['assembled_code_bytes']} span={row['occupied_game_span_bytes']} "
                f"new_end=${row['new_end_game_next']:04X} "
                f"E1M2_slack={row['new_tightest_slack_bytes']} fit={row['fits_current_tightest_heap_gate']}"
            )

    if not all(r['fits_current_tightest_heap_gate'] for r in rows.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
