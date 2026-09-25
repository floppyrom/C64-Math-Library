#!/usr/bin/env python3
"""Benchmark MATH_SEEK8_* / MATH_SEEK16_* in every shipped profile image.

Public-entry cycles (JMP slot through RTS; caller JSR and input stores
excluded), measured on each profile's resident PRG after MATH_INIT. Every
frame of every move is checked against the Bresenham reference model while
measuring. Writes validation/movement/SEEK_PROFILE_BENCHMARK.json.

Corpus: 408 random moves (plus edge cases) on a 256x200 screen for SEEK8 and a
320x200 screen for SEEK16.
  INIT       all moves x 6 major-axis speeds 0.5..4 px/frame, plus the same
             speeds with the Euclidean flag (reported separately too)
  STEP       every frame of those moves
  STEP_INT   every frame at integer major-axis speeds 1, 2, 3, 4
  STEP1      every frame at 1 px/frame
"""
from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'routines/movement'))
from mini6502 import CPU  # noqa: E402
from seek_model import expected_frames, EUCLID  # noqa: E402
from validate_source_build import seek_symbols  # noqa: E402

PROFILES = ['v1_balanced', 'v2_pareto_fast', 'v3_reu_512k', 'v4_reu_16m', 'v5_hybrid_lowzp']
REU = {'v3_reu_512k': ROOT / 'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu',
       'v4_reu_16m': ROOT / 'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'}
SPEEDS = (0x0080, 0x0100, 0x0180, 0x0200, 0x0300, 0x0400)
INT_SPEEDS = (0x0100, 0x0200, 0x0300, 0x0400)
MOVES = 400


def corpus(width):
    r = random.Random(0xC64)
    xm = width - 1
    edge = [(0, 0, xm, 199), (xm, 199, 0, 0), (0, 199, xm, 0), (width // 2, 100, width // 2, 100),
            (0, 0, xm, 0), (0, 0, 0, 199), (0, 0, 199, 199), (10, 10, 11, 12)]
    return edge + [(r.randrange(width), r.randrange(200), r.randrange(width), r.randrange(200))
                   for _ in range(MOVES)]


def api(profile):
    import re
    out = {}
    for line in (ROOT / profile / 'resident/math_api.inc').read_text().splitlines():
        m = re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)', line)
        if m:
            out[m.group(1)] = int(m.group(2), 16)
    return out


def load(profile):
    prg = next((ROOT / profile / 'resident').glob('math_*_game_math.prg'))
    b = prg.read_bytes()
    lo = b[0] | b[1] << 8
    mem = bytearray(65536)
    mem[lo:lo + len(b) - 2] = b[2:]
    reu = bytearray(REU[profile].read_bytes()) if profile in REU else None
    c = CPU(mem, reu=reu)
    c.d = 0
    A = api(profile)
    c.call(A['MATH_INIT'], 2_000_000)
    return c, A


def summary(xs):
    return {'mean_cycles': statistics.fmean(xs), 'min_cycles': min(xs), 'max_cycles': max(xs), 'cases': len(xs)}


def run(profile):
    c, A = load(profile)
    S = {k: v for k, v in A.items() if k.startswith('MATH_SEEK') and '_POS' in k}
    io = A['MATH_X']
    res = {}
    for width in (8, 16):
        pre = 'MATH_SEEK8_' if width == 8 else 'MATH_SEEK16_'
        moves = corpus(256 if width == 8 else 320)

        def setpos(slot, x, y):
            if width == 8:
                c.mem[S['MATH_SEEK8_POS_X'] + slot] = x
                c.mem[S['MATH_SEEK8_POS_Y'] + slot] = y
            else:
                c.mem[S['MATH_SEEK16_POS_XL'] + slot] = x & 255
                c.mem[S['MATH_SEEK16_POS_XH'] + slot] = x >> 8
                c.mem[S['MATH_SEEK16_POS_Y'] + slot] = y

        def pos(slot):
            if width == 8:
                return c.mem[S['MATH_SEEK8_POS_X'] + slot], c.mem[S['MATH_SEEK8_POS_Y'] + slot]
            return (c.mem[S['MATH_SEEK16_POS_XL'] + slot] | c.mem[S['MATH_SEEK16_POS_XH'] + slot] << 8,
                    c.mem[S['MATH_SEEK16_POS_Y'] + slot])

        def move(i, m, speed, stepper, inits, steps):
            x0, y0, x1, y1 = m
            slot = i & 7
            setpos(slot, x0, y0)
            c.mem[io:io + 2] = bytes((x1 & 255, x1 >> 8))
            c.mem[io + 4] = y1
            c.mem[io + 0x10:io + 0x12] = bytes((speed & 255, speed >> 8))
            c.x = slot
            inits.append(c.call(A[pre + 'INIT']))
            exp = expected_frames(x0, y0, x1, y1, speed, stepper)
            assert c.c == int(not exp), (profile, pre, m, hex(speed))
            name = pre + {'step': 'STEP', 'int': 'STEP_INT', 'one': 'STEP1'}[stepper]
            for want, arr in exp:
                c.x = slot
                steps.append(c.call(A[name]))
                assert pos(slot) == want and c.c == int(arr), (profile, name, m, hex(speed), pos(slot), want)

        init_major, init_euclid, step, step_int, step1, init_int, init_one = [], [], [], [], [], [], []
        for i, m in enumerate(moves):
            for sp in SPEEDS:
                move(i, m, sp, 'step', init_major, step)
                move(i, m, sp | EUCLID, 'step', init_euclid, step)
            for sp in INT_SPEEDS:
                move(i, m, sp, 'int', init_int, step_int)
            move(i, m, 0x0100, 'one', init_one, step1)
        res[pre + 'INIT'] = dict(summary(init_major + init_euclid),
                                 major_axis_speed=summary(init_major), euclidean_speed=summary(init_euclid),
                                 integer_speed=summary(init_int), one_pixel=summary(init_one))
        res[pre + 'STEP'] = summary(step)
        res[pre + 'STEP_INT'] = summary(step_int)
        res[pre + 'STEP1'] = summary(step1)
    return res


def main():
    out = {'status': 'PASS',
           'basis': 'public entry (JMP slot) through RTS after MATH_INIT; caller JSR/input stores excluded; '
                    'every frame checked against the Bresenham model',
           'corpus': {'moves': MOVES + 8, 'screen_seek8': '256x200', 'screen_seek16': '320x200',
                      'speeds_q8_8': [f'${s:04X}' for s in SPEEDS], 'euclidean_flag': 'same speeds with bit 15 set',
                      'integer_speeds': [f'${s:04X}' for s in INT_SPEEDS]},
           'profiles': {}}
    import hashlib
    out['prg_sha256'] = {p: hashlib.sha256(next((ROOT / p / 'resident').glob('math_*_game_math.prg')).read_bytes()).hexdigest()
                         for p in PROFILES}
    for p in PROFILES:
        out['profiles'][p] = run(p)
        r = out['profiles'][p]
        print(p, ' '.join(f"{k.split('_',1)[1]}={v['mean_cycles']:.2f}" for k, v in r.items()), flush=True)
    path = ROOT / 'validation/movement/SEEK_PROFILE_BENCHMARK.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
