#!/usr/bin/env python3
"""Validate seek_u16_u8_dda.asm and benchmark it against the normalize pipeline.

The DDA source runs in its own image. The baseline runs on the V1 reference
PRG (build it first with `make reference`), calling the shipped
MATH_VEC2_NORMALIZE_Q8_8, MATH_SMUL16_SHR8, MATH_SMUL16, MATH_ISQRT32 and
MATH_UDIV16_SHL8 entries. Cycle counts exclude the caller's JSR, as elsewhere
in this repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'tools'))
from mini6502 import Assembler  # noqa: E402
from seek_model import Seek, bresenham, expected_frames, NSLOT  # noqa: E402

SPEEDS = (0x0080, 0x0100, 0x0180, 0x0200, 0x0300, 0x0400)  # Q8.8 px/frame


def corpus(count: int, seed: int = 0xC64):
    r = random.Random(seed)
    edge = [(0, 0, 319, 199), (319, 199, 0, 0), (0, 199, 319, 0), (160, 100, 160, 100),
            (0, 0, 319, 0), (0, 0, 0, 199), (0, 0, 199, 199), (10, 10, 11, 12)]
    moves = edge + [(r.randrange(320), r.randrange(200), r.randrange(320), r.randrange(200))
                    for _ in range(count)]
    return [(m, s) for m in moves for s in SPEEDS]


def line_dev(x0, y0, x1, y1, px, py):
    """Perpendicular distance of (px,py) from the infinite start->target line."""
    dx, dy = x1 - x0, y1 - y0
    h = math.hypot(dx, dy)
    return 0.0 if h == 0 else abs(dy * (px - x0) - dx * (py - y0)) / h


def run_dda(cases, euclid=False, integer=False):
    s = Seek()
    inits, steps, totals, frames_list = [], [], [], []
    maxdev = 0.0
    errors = 0
    for i, ((x0, y0, x1, y1), sp) in enumerate(cases):
        slot = i % NSLOT
        cyc, c = s.init(slot, x0, y0, x1, y1, sp, euclid)
        inits.append(cyc)
        total = cyc
        exp = expected_frames(x0, y0, x1, y1, sp, euclid, integer)
        if not exp:
            errors += int(c != 1 or s.pos(slot) != (x1, y1))
            totals.append(total)
            frames_list.append(0)
            continue
        errors += int(c != 0)
        for pos, arrived in exp:
            cyc, c = s.step(slot, integer)
            steps.append(cyc)
            total += cyc
            errors += int(s.pos(slot) != pos or c != arrived)
            maxdev = max(maxdev, line_dev(x0, y0, x1, y1, *s.pos(slot)))
        totals.append(total)
        frames_list.append(len(exp))
        errors += int(s.pos(slot) != (x1, y1))
    return dict(code_bytes=s.code_bytes, state_bytes_per_slot=32,
                io_bytes=16, init=inits, step=steps, total=totals,
                frames=frames_list, max_line_dev_px=maxdev, errors=errors)


def run_interleaved(rounds: int = 60, seed: int = 0x5EE):
    """Eight slots moving at once, stepped round-robin every frame."""
    s = Seek()
    r = random.Random(seed)
    checked = 0
    for _ in range(rounds):
        euclid = r.random() < 0.5
        jobs = []
        for slot in range(NSLOT):
            m = (r.randrange(320), r.randrange(200), r.randrange(320), r.randrange(200))
            sp = r.randrange(0x40, 0x500)
            _, c = s.init(slot, *m, sp, euclid)
            exp = expected_frames(*m, sp, euclid)
            assert c == (not exp)
            jobs.append((slot, m, exp))
        for f in range(max(len(e) for _, _, e in jobs) + 2):
            for slot, m, exp in jobs:
                _, c = s.step(slot)
                want = exp[f] if f < len(exp) else ((m[2], m[3]), True)
                assert (s.pos(slot), bool(c)) == want, (slot, m, f)
                checked += 1
    return checked


def load_v1():
    import validate_source_build as vsb
    build = ROOT / 'build_source/reference'
    c, P, I, M, _ = vsb.load('v1_balanced', build)
    text = (HERE / 'baseline_normalize.asm').read_text(encoding='utf-8')
    code, labels, const = Assembler().assemble(text)
    for name, sym in (('NORM', 'MATH_VEC2_NORMALIZE_Q8_8'), ('SMUL16_SHR8', 'MATH_SMUL16_SHR8'),
                      ('SMUL16', 'MATH_SMUL16'), ('ISQRT32', 'MATH_ISQRT32'),
                      ('UDIV16_SHL8', 'MATH_UDIV16_SHL8')):
        assert const[name] == P[sym], (name, hex(const[name]), hex(P[sym]))
    assert I == 0xC000
    for a, b in code.items():
        assert a < 0x1000
        c.mem[a] = b
    return c, labels, const, len(code)


def run_baseline(cases):
    c, L, K, code_bytes = load_v1()
    io, st = K['IO'], K['ST']
    m = c.mem

    def rd(name, slot):
        return m[K[name] + slot]

    def call(entry, slot):
        c.x = slot
        return c.call(L[entry])

    bare_init, arr_init, steps, arr_steps, bare_totals, arr_totals = [], [], [], [], [], []
    miss, maxdev, frames_list = [], 0.0, []
    for i, ((x0, y0, x1, y1), sp) in enumerate(cases):
        slot = i % NSLOT
        m[io:io + 8] = bytes((x0 & 255, x0 >> 8, y0, x1 & 255, x1 >> 8, y1, sp & 255, sp >> 8))
        if (x0, y0) == (x1, y1):
            continue  # normalize reports C=1; a caller must special-case it
        bare_init.append(call('b_init', slot))
        m[io:io + 8] = bytes((x0 & 255, x0 >> 8, y0, x1 & 255, x1 >> 8, y1, sp & 255, sp >> 8))
        cyc = call('b_init_arrive', slot)
        arr_init.append(cyc)
        frames = rd('FRL', slot) | (rd('FRH', slot) << 8)
        frames_list.append(frames)
        total_arr = cyc
        total_bare = bare_init[-1]
        # Count down; measure how far the free-running position is from the
        # target on the frame the counter expires (before the snap).
        for f in range(frames):
            if f == frames - 1:
                save = bytes(m[st:st + 120])
                cyc_b = call('b_step', slot)
                px = rd('PXL', slot) | (rd('PXH', slot) << 8)
                py = rd('PY', slot)
                ex = ((px - x1 + 32768) & 0xFFFF) - 32768 + rd('PXF', slot) / 256 - 0.5
                ey = ((py - y1 + 128) & 0xFF) - 128 + rd('PYF', slot) / 256 - 0.5
                miss.append(math.hypot(ex, ey))
                m[st:st + 120] = save
            cyc = call('b_step_arrive', slot)
            arr_steps.append(cyc)
            total_arr += cyc
            px = rd('PXL', slot) | (rd('PXH', slot) << 8)
            py = rd('PY', slot)
            maxdev = max(maxdev, line_dev(x0, y0, x1, y1, px, py))
        assert c.c == 1 and (rd('PXL', slot) | rd('PXH', slot) << 8, rd('PY', slot)) == (x1, y1)
        # Bare stepper cost for the same number of frames.
        for _ in range(frames):
            steps.append(call('b_step', slot))
            total_bare += steps[-1]
        bare_totals.append(total_bare)
        arr_totals.append(total_arr)
    return dict(glue_code_bytes=code_bytes, bare_init=bare_init, arrive_init=arr_init,
                bare_step=steps, arrive_step=arr_steps, bare_total=bare_totals,
                arrive_total=arr_totals, frames=frames_list, miss_px=miss,
                max_line_dev_px=maxdev)


def summary(xs):
    return dict(mean=statistics.fmean(xs), min=min(xs), max=max(xs)) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--moves', type=int, default=400)
    ap.add_argument('--out', type=Path, default=ROOT / 'validation/movement/SEEK_DDA_BENCHMARK.json')
    args = ap.parse_args()
    cases = corpus(args.moves)
    dda = {}
    int_cases = [c for c in cases if c[1] & 0xFF == 0]
    for name, euclid, integer, cs in (('major_axis_speed', False, False, cases),
                                      ('major_axis_speed_integer_step', False, True, int_cases),
                                      ('euclidean_speed', True, False, cases)):
        d = run_dda(cs, euclid, integer)
        assert d['errors'] == 0, (name, d['errors'])
        dda[name] = dict(entry=('seek_init_euclid' if euclid else 'seek_init') + ' + ' +
                         ('seek_step_int' if integer else 'seek_step'), cases=len(cs),
                         init=summary(d['init']), step=summary(d['step']),
                         total_per_move=summary(d['total']),
                         frames_per_move=summary(d['frames']),
                         max_line_dev_px=d['max_line_dev_px'], exact_arrival=True,
                         frame_position_mismatches=d['errors'])
    interleaved = run_interleaved()
    b = run_baseline(cases)
    res = {
        'corpus': dict(moves=args.moves + 8, speeds_q8_8=[f'${s:04X}' for s in SPEEDS],
                       cases=len(cases), screen='x 0..319, y 0..199'),
        'source': 'routines/movement/seek_u16_u8_dda.asm',
        'source_sha256': hashlib.sha256((HERE / 'seek_u16_u8_dda.asm').read_bytes()).hexdigest(),
        'dda': dict(code_bytes=d['code_bytes'], table_bytes=32,
                    state_bytes_per_slot=d['state_bytes_per_slot'], io_bytes=d['io_bytes'],
                    interleaved_slot_frames_checked=interleaved, **dda),
        'baseline_v1_normalize': dict(glue_code_bytes=b['glue_code_bytes'],
                                      init_bare=summary(b['bare_init']),
                                      init_with_arrival=summary(b['arrive_init']),
                                      step_bare=summary(b['bare_step']),
                                      step_with_arrival=summary(b['arrive_step']),
                                      total_per_move_bare=summary(b['bare_total']),
                                      total_per_move_with_arrival=summary(b['arrive_total']),
                                      frames_per_move=summary(b['frames']),
                                      miss_before_snap_px=summary(b['miss_px']),
                                      max_line_dev_px=b['max_line_dev_px']),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(res, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
