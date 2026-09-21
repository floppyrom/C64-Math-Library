#!/usr/bin/env python3
"""Compare the size refresh against its git baseline, one public call at a time.

Requires the baseline commit in a git checkout. Normal source builds and the
other validators remain usable in the copy-over ZIP without git history.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import subprocess

from benchmark_normalize_profile_parity import CASES
from mini6502 import CPU, Assembler
from assemble_sources import preprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '7a74e750556c1da09db8759f9ed479cd92bd6d17'
PROFILES = ('v1_balanced', 'v2_pareto_fast', 'v3_reu_512k',
            'v4_reu_16m', 'v5_hybrid_lowzp')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(profile, baseline=None, reu_baseline=BASELINE):
    path = Path(profile) / 'resident' / f'math_{profile}_game_math.prg'
    raw = (subprocess.check_output(['git', 'show', f'{baseline}:{path}'], cwd=ROOT)
           if baseline else (ROOT / path).read_bytes())
    start = int.from_bytes(raw[:2], 'little')
    mem = bytearray(65536)
    mem[start:start + len(raw) - 2] = raw[2:]
    reu_files = list((ROOT / profile / 'reu').glob('*.reu'))
    reu = None
    if reu_files:
        path = reu_files[0].relative_to(ROOT)
        before = subprocess.check_output(['git', 'show', f'{reu_baseline}:{path}'], cwd=ROOT)
        assert before == reu_files[0].read_bytes(), 'REU image changed'
        reu = bytearray(before)
    cpu = CPU(mem, reu=reu)
    cpu.call(0x3280)
    return cpu, raw


def compare(profile, baseline, atan=False):
    old, oldraw = load(profile, baseline, baseline)
    new, newraw = load(profile, reu_baseline=baseline)
    cases = [(x, y) for x in range(256) for y in range(256)] if atan else CASES
    entry, count = (0x5e2a, 1) if atan else (0x5e39, 4)
    oldcycles, newcycles, oldoutputs, newoutputs = [], [], bytearray(), bytearray()
    different = 0
    for x, y in cases:
        for cpu in (old, new):
            cpu.mem[0xc000], cpu.mem[0xc001] = x & 255, (x >> 8) & 255
            cpu.mem[0xc004], cpu.mem[0xc005] = y & 255, (y >> 8) & 255
            cpu.c = (x ^ y) & 1
        before = bytes(new.mem[0xc000:0xc008])
        a, b = old.call(entry), new.call(entry)
        assert b <= a, (profile, atan, x, y, a, b)
        assert bytes(new.mem[0xc000:0xc008]) == before
        assert new.c == (0 if atan else int(x == 0 and y == 0))
        oa = bytes(old.mem[0xc008:0xc008 + count])
        ob = bytes(new.mem[0xc008:0xc008 + count])
        if atan:
            assert new.a == ob[0] and oa == ob
            assert b == a
        elif profile in PROFILES[2:4]:
            assert oa == ob
        different += oa != ob
        oldcycles.append(a); newcycles.append(b)
        oldoutputs.extend(oa); newoutputs.extend(ob)
    result = {
        'profile': profile, 'cases': len(cases),
        'baseline_prg_sha256': sha(oldraw), 'current_prg_sha256': sha(newraw),
        'baseline_prg_bytes': len(oldraw), 'current_prg_bytes': len(newraw),
        'baseline_mean_cycles': sum(oldcycles) / len(cases),
        'mean_cycles': sum(newcycles) / len(cases),
        'min_cycles': min(newcycles), 'max_cycles': max(newcycles),
        'slower_calls': 0, 'faster_calls': sum(b < a for a, b in zip(oldcycles, newcycles)),
        'changed_outputs': different,
        'baseline_output_sha256': sha(oldoutputs), 'output_sha256': sha(newoutputs),
        'baseline_cycle_sha256': sha(b''.join(struct.pack('<H', n) for n in oldcycles)),
        'cycle_sha256': sha(b''.join(struct.pack('<H', n) for n in newcycles)),
    }
    print(profile, 'atan2' if atan else 'normalize', result['mean_cycles'],
          'no slower calls', flush=True)
    return result


def binary_delta(baseline=BASELINE):
    """Confine all PRG changes to the two optimized families and donor data."""
    from publish_standalone_sources import initialized, trace
    checks = []
    for profile in PROFILES:
        relative = Path(profile) / 'resident/vector/native/vec2_normalize_q8_8.asm'
        cfg = ROOT / 'relocatable_source' / profile / 'math_config_reference.inc'
        before = subprocess.check_output(['git', 'show', f'{baseline}:{relative}'], cwd=ROOT, text=True)
        tables = subprocess.check_output(['git', 'show', f'{baseline}:{relative.with_name("vec2_normalize_tables.asm")}'], cwd=ROOT, text=True)
        before = before.replace('!source "vec2_normalize_tables.asm"', tables)
        before = '\n'.join(line for line in before.splitlines() if not line.strip().startswith('!cpu'))
        old_native, _, _ = Assembler().assemble(cfg.read_text() + '\n*=$5e39\n' + before)
        new_native, _, _ = Assembler().assemble('*=$5e39\n' + preprocess(ROOT / relative, cfg))
        old, oldraw = load(profile, baseline, baseline)
        new, newraw = load(profile, reu_baseline=baseline)
        def uninitialized(raw):
            mem = bytearray(65536); start = int.from_bytes(raw[:2], 'little')
            mem[start:start + len(raw) - 2] = raw[2:]
            return mem
        a, b = uninitialized(oldraw), uninitialized(newraw)
        allowed = set(old_native) | set(new_native)
        if profile in (PROFILES[1], PROFILES[2], PROFILES[4]):
            start = a[0x5e2b] | a[0x5e2c] << 8
            end = a[0x5e2e] | a[0x5e2f] << 8
            allowed.update(range(start, end))
        donor = []
        if profile == PROFILES[4]:
            donor = [(0xa500, 0xa5ff), (0xab00, 0xabff)]
            mem, api, _ = initialized(profile)
            reachable = set()
            for name, address in api.items():
                if name.startswith('MATH_') and name not in ('MATH_X','MATH_Y','MATH_Z','MATH_N','MATH_D','MATH_Q','MATH_R'):
                    reachable.update(trace(mem, address))
            for lo, hi in donor:
                addresses = set(range(lo, hi + 1))
                assert not (addresses & reachable)
                allowed.update(addresses)
        changed = {i for i in range(65536) if a[i] != b[i]}
        assert changed <= allowed, (profile, sorted(changed - allowed)[:16])
        checks.append({'profile': profile, 'changed_bytes': len(changed),
                       'outside_normalize_atan2_and_donor_ranges': 0,
                       'non_executable_donor_table_ranges': [[hex(lo), hex(hi)] for lo, hi in donor],
                       'baseline_prg_sha256': sha(oldraw), 'current_prg_sha256': sha(newraw)})
    result = {'status': 'PASS', 'baseline_commit': baseline, 'profiles': checks}
    (ROOT / 'validation/normalize/BINARY_DELTA_VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print('BINARY DELTA PASS', len(checks), 'profiles', flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline', default=BASELINE)
    args = ap.parse_args()
    native = json.loads((ROOT / 'validation/normalize/NATIVE_SOURCE_VALIDATION.json').read_text())
    result = {'status': 'PASS', 'baseline_commit': args.baseline,
              'normalize': [], 'atan2': [],
              'scope': 'Public JMP and RTS included; caller JSR and VIC/IRQ contention excluded.'}
    for profile in PROFILES:
        row = compare(profile, args.baseline)
        reu = profile in PROFILES[2:4]
        sizes = native['profiles'][profile]['maps']['reference']
        row.update(baseline_code_bytes=867 if reu else 915,
                   baseline_table_bytes=1024 if reu else 2816,
                   code_bytes=sizes['code_bytes'], table_bytes=sizes['table_bytes'])
        row['ram_bytes_saved'] = (row['baseline_code_bytes'] + row['baseline_table_bytes']
                                  - row['code_bytes'] - row['table_bytes'])
        result['normalize'].append(row)
        if profile in (PROFILES[1], PROFILES[2], PROFILES[4]):
            row = compare(profile, args.baseline, atan=True)
            row.update(baseline_body_bytes=89, body_bytes=85, table_bytes=1024,
                       public_jmp_bytes=3, ram_bytes_saved=4)
            result['atan2'].append(row)
    path = ROOT / 'validation/SIZE_OPTIMIZATION_VALIDATION.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    binary_delta(args.baseline)


if __name__ == '__main__':
    main()
