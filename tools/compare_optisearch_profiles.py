#!/usr/bin/env python3
"""Compare rebuilt baseline profiles with current OptiSearch adaptations.

Build both maps and V5 in an isolated baseline checkout first. This optional
review proof keeps baseline artifacts outside the distributable package.
"""
from pathlib import Path
import argparse, collections, hashlib, json
import validate_smul24_directout as v
from generate_consolidated_routine_table import trace


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline-source', type=Path, required=True)
    ap.add_argument('--baseline-hybrid', type=Path, required=True)
    ap.add_argument('--baseline-commit', required=True)
    args = ap.parse_args()
    current = (v.BUILD, v.HYBRID)
    baseline = (args.baseline_source, args.baseline_hybrid)
    results = {}
    cases = v.corpus()
    for profile in v.PROFILES:
        results[profile] = {}
        for kind in v.KINDS:
            rows = []
            memories = []
            ownership = []
            for roots in (baseline, current):
                v.BUILD, v.HYBRID = roots
                cpu, api = v.load(profile, kind)
                memories.append(bytes(cpu.mem))
                code, zp, stack = trace(cpu.mem, api['MATH_SMUL24'])
                atan, _, _ = trace(cpu.mem, api['MATH_ATAN2_8'])
                ownership.append(code | atan)
                row = v.run(profile, kind, cases)
                row.update(code_bytes=len(code), zp_bytes=len(zp),
                           persistent_stack_bytes=len(stack))
                rows.append(row)
            before, after = rows
            saved = [b-a for b, a in zip(before['cycles'], after['cycles'])]
            assert min(saved) >= 4 and max(saved) <= 5, (profile, kind, 'cycles')
            assert after['code_bytes'] == before['code_bytes']-6
            assert after['zp_bytes'] == before['zp_bytes'] == 24
            assert after['persistent_stack_bytes'] == before['persistent_stack_bytes'] == 0
            changed = {i for i, (b, a) in enumerate(zip(*memories)) if b != a}
            unexpected = changed - ownership[0] - ownership[1]
            assert not unexpected, (profile, kind, 'unrelated bytes', sorted(unexpected))
            for row in rows:
                del row['cycles']
            results[profile][kind] = {
                'before': before, 'after': after,
                'saved_cycles_distribution': dict(sorted(collections.Counter(saved).items())),
                'changed_initialized_image_bytes': len(changed),
                'changes_outside_SMUL24_ATAN2_code': 0,
                'initialized_image_sha256': [hashlib.sha256(m).hexdigest() for m in memories],
            }
            print(profile, kind, f"{before['mean_cycles']:.6f} -> {after['mean_cycles']:.6f}", flush=True)
    v.BUILD, v.HYBRID = current
    out = v.ROOT/'validation/records/OPTISEARCH_PROFILE_COMPARISON.json'
    out.write_text(json.dumps({
        'status': 'PASS', 'date': '2026-10-07',
        'baseline_commit': args.baseline_commit,
        'basis': 'identical deterministic SMUL24 corpus; public entry through RTS; rebuilt baseline and current profiles',
        'machine_calls': len(cases)*len(v.PROFILES)*len(v.KINDS)*2,
        'seed': hex(v.SEED), 'results': results,
    }, indent=2)+'\n')


if __name__ == '__main__':
    main()
