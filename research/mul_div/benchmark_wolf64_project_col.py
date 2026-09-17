#!/usr/bin/env python3
"""Benchmark the ~198-cycle small-width exact MUL_DIV against a real Wolf64 fake.

Wolf64 source snapshot:
    Kweepa/Wolf64 @ d606a14bbfb9fb17059c24824e0d921f23fd6860

Call site:
    e_col_cx = 20 +/- min(30, |side|*20/perp_mid)

The real caller has already culled |side| > perp_mid, so accepted projection
inputs satisfy q=floor(|side|*20/perp_mid) <= 20. This is exactly the kind of
semantic information the implementation-plan laws require us to benchmark
against instead of pretending the game must use a general MUL_DIV.

Compared paths:
  wolf64_current
      literal project_col_from_side + mul_8x8 + div_q40 shape

  v2_width_hybrid
      sign/abs wrapper + research pareto_width_hybrid with Y=20 + final +/-

This is research evidence, not a Wolf64 build certification.
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
from benchmark import MATH_INIT, PROFILE_PRG, load_prg, patch_source  # noqa: E402
from generate_umuldiv16_pareto_width import generate as generate_width  # noqa: E402

WOLF_COMMIT = 'd606a14bbfb9fb17059c24824e0d921f23fd6860'

# Shared standalone-call I/O for both CPUs.
SIDE0, SIDE1 = 0xB000, 0xB001
PERP0, PERP1 = 0xB002, 0xB003
COL = 0xB004

# Library vectors.
X0, X1 = 0xC000, 0xC001
Y0, Y1 = 0xC004, 0xC005
Z0 = 0xC008
D0, D1 = 0xC014, 0xC015
WIDTH_ENTRY = 0xE000
WRAPPER = 0xF000

WOLF_SOURCE = r'''
side0=$B000
side1=$B001
perp0=$B002
perp1=$B003
colout=$B004

aux_l=$40
aux_h=$41
tmp0=$42
tmp1=$43
tmp2=$44
tmp3=$45
tmp4=$46
tmp5=$47
sq1_l=$48
sq1_h=$49
sq2_l=$4A
sq2_h=$4B
sq3_l=$4C
sq3_h=$4D
sq4_l=$4E
sq4_h=$4F

SQTAB1=$D000
SQTAB2=$D200
SQTAB3=$D400
SQTAB4=$D600

.org $9000
neg_aux:
    sec
    lda #0
    sbc aux_l
    sta aux_l
    lda #0
    sbc aux_h
    sta aux_h
    rts

; Wolf64 src/mul.asm: Y=factor1, A=factor2 -> X=lo A=hi
mul_8x8:
    sta sq1_l
    sta sq2_l
    eor #$ff
    sta sq3_l
    sta sq4_l
    sec
    lda (sq1_l),y
    sbc (sq3_l),y
    tax
    lda (sq2_l),y
    sbc (sq4_l),y
    rts

; Wolf64 src/items_draw.asm: tmp0:1 / tmp2:3 -> tmp4=min(q,40)
div_q40:
    lda tmp2
    ora tmp3
    bne dq_nonzero
    lda #40
    sta tmp4
    rts
dq_nonzero:
    lda tmp3
    bne dq_d16
    lda tmp1
    bne dq_d168
    lda #0
    sta tmp4
    lda tmp0
    beq dq_out
dq_d88:
    cmp tmp2
    bcc dq_out
    sbc tmp2
    inc tmp4
    ldx tmp4
    cpx #40
    bcc dq_d88
dq_out:
    rts
dq_d168:
    ldx #16
    lda #0
dq_d168l:
    asl tmp0
    rol tmp1
    rol a
    bcs dq_d168s
    cmp tmp2
    bcc dq_d168n
dq_d168s:
    sbc tmp2
    inc tmp0
dq_d168n:
    dex
    bne dq_d168l
    lda tmp1
    bne dq_sat
    lda tmp0
    cmp #41
    bcc dq_d168o
dq_sat:
    lda #40
dq_d168o:
    sta tmp4
    rts
dq_d16:
    lda #0
    sta tmp4
dq_d16l:
    lda tmp1
    cmp tmp3
    bcc dq_out
    bne dq_d16s
    lda tmp0
    cmp tmp2
    bcc dq_out
dq_d16s:
    sec
    lda tmp0
    sbc tmp2
    sta tmp0
    lda tmp1
    sbc tmp3
    sta tmp1
    inc tmp4
    lda tmp4
    cmp #40
    bcc dq_d16l
    rts

project_col_from_side:
    lda #0
    sta tmp5
    lda side0
    sta aux_l
    lda side1
    sta aux_h
    bpl pc_mul
    inc tmp5
    jsr neg_aux
pc_mul:
    ldy aux_l
    lda #20
    jsr mul_8x8
    stx tmp0
    sta tmp1
    lda aux_h
    beq pc_div
    tay
    lda #20
    jsr mul_8x8
    txa
    clc
    adc tmp1
    sta tmp1
pc_div:
    lda perp0
    sta tmp2
    lda perp1
    sta tmp3
    jsr div_q40
    lda tmp4
    cmp #30
    bcc pc_clamped
    lda #30
    sta tmp4
pc_clamped:
    lda tmp5
    bne pc_add
    sec
    lda #20
    sbc tmp4
    sta colout
    rts
pc_add:
    clc
    lda #20
    adc tmp4
    sta colout
    rts
'''

LIB_WRAPPER = r'''
side0=$B000
side1=$B001
perp0=$B002
perp1=$B003
colout=$B004
X0=$C000
X1=$C001
Y0=$C004
Y1=$C005
Z0=$C008
D0=$C014
D1=$C015
MULDIV=$E000
sign=$4F
.org $F000
project_col_width_hybrid:
    lda #0
    sta sign
    lda side0
    sta X0
    lda side1
    sta X1
    bpl lib_mag
    inc sign
    sec
    lda #0
    sbc X0
    sta X0
    lda #0
    sbc X1
    sta X1
lib_mag:
    lda #20
    sta Y0
    lda #0
    sta Y1
    lda perp0
    sta D0
    lda perp1
    sta D1
    jsr MULDIV
    ; Accepted Wolf64 inputs have |side|<=perp, therefore q<=20.
    lda sign
    bne lib_add
    sec
    lda #20
    sbc Z0
    sta colout
    rts
lib_add:
    clc
    lda #20
    adc Z0
    sta colout
    rts
'''


def patch(mem: bytearray, source: str):
    code, labels, _ = Assembler().assemble(source)
    for a, v in code.items():
        mem[a] = v
    return labels


def build_wolf_sqtab() -> bytes:
    """Exact tools/gen_sqtab.py construction from the audited Wolf64 commit."""
    mem = bytearray(0x800)
    s1 = lambda i: i
    s2 = lambda i: 0x200 + i
    s3 = lambda i: 0x400 + i
    s4 = lambda i: 0x600 + i
    mem[s3(0xFE)] = 0
    mem[s4(0xFE)] = 0
    y = 0xFF
    x = 0
    while True:
        a = x >> 1
        s = a + mem[s3(0xFE + x)]
        a, c = s & 0xFF, int(s > 0xFF)
        mem[s1(x)] = a
        mem[s3(0xFF + x)] = a
        mem[s3(y)] = a
        s = mem[s4(0xFE + x)] + c
        a = s & 0xFF
        mem[s2(x)] = a
        mem[s4(0xFF + x)] = a
        mem[s4(y)] = a
        y = (y - 1) & 0xFF
        x = (x + 1) & 0xFF
        if x == 0:
            break
    while True:
        a = 0x80 | (x >> 1)
        s = a + mem[s1(0xFF + x)]
        a, c = s & 0xFF, int(s > 0xFF)
        mem[s1(0x100 + x)] = a
        mem[s2(0x100 + x)] = (mem[s2(0xFF + x)] + c) & 0xFF
        x = (x + 1) & 0xFF
        if x == 0:
            break
    return bytes(mem)


def wolf_cpu():
    mem = bytearray(65536)
    labels = patch(mem, WOLF_SOURCE)
    mem[0xD000:0xD800] = build_wolf_sqtab()
    mem[0x49] = 0xD0
    mem[0x4B] = 0xD2
    mem[0x4D] = 0xD4
    mem[0x4F] = 0xD6
    cpu = CPU(mem)
    cpu.d = 0
    return cpu, labels['project_col_from_side']


def lib_cpu():
    path = PROFILE_PRG['v2']
    cpu = CPU(load_prg(path))
    cpu.d = 0
    cpu.call(MATH_INIT)
    labels = patch_source(cpu.mem, generate_width(WIDTH_ENTRY))
    assert labels['umuldiv16_pareto_width_hybrid'] == WIDTH_ENTRY
    labels2 = patch(cpu.mem, LIB_WRAPPER)
    return cpu, labels2['project_col_width_hybrid']


def put16(mem: bytearray, addr: int, value: int):
    value &= 0xFFFF
    mem[addr] = value & 0xFF
    mem[addr + 1] = value >> 8


def expected(side: int, perp: int) -> int:
    q = (abs(side) * 20) // perp
    q = min(q, 30)
    return (20 + q if side < 0 else 20 - q) & 0xFF


def corpus(kind: str, n: int, seed: int):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        if kind == 'perp8':
            perp = rng.randint(1, 255)
        elif kind == 'perp16':
            perp = rng.randint(256, 0x3FFF)
        elif kind == 'mixed':
            perp = rng.randint(1, 0x3FFF)
        else:
            raise ValueError(kind)
        mag = rng.randint(0, perp)  # exactly the caller's accepted FOV domain
        side = -mag if rng.getrandbits(1) and mag else mag
        out.append((side, perp))
    return out


def run(cpu: CPU, entry: int, cases):
    cycles, errors = [], 0
    first = []
    for side, perp in cases:
        put16(cpu.mem, SIDE0, side)
        put16(cpu.mem, PERP0, perp)
        cyc = cpu.call(entry)
        got = cpu.mem[COL]
        exp = expected(side, perp)
        if got != exp:
            errors += 1
            if len(first) < 8:
                first.append({'side': side, 'perp': perp, 'got': got, 'expected': exp})
        cycles.append(cyc)
    return {
        'cases': len(cases),
        'errors': errors,
        'first_errors': first,
        'mean_cycles': statistics.fmean(cycles),
        'min_cycles': min(cycles),
        'max_cycles': max(cycles),
    }


def shape(cases):
    qs = [(abs(s) * 20) // d for s, d in cases]
    return {
        'q0_percent': 100.0 * sum(q == 0 for q in qs) / len(qs),
        'q_le_1_percent': 100.0 * sum(q <= 1 for q in qs) / len(qs),
        'q_le_20_percent': 100.0 * sum(q <= 20 for q in qs) / len(qs),
        'side_fits_8_percent': 100.0 * sum(abs(s) <= 255 for s, _ in cases) / len(cases),
        'perp_fits_8_percent': 100.0 * sum(d <= 255 for _, d in cases) / len(cases),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=10000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    result = {
        'status': 'research_evidence_not_wolf64_build_certification',
        'wolf64_source_commit': WOLF_COMMIT,
        'contract': 'accepted sprite projection inputs: |side|<=perp_mid; col=20 +/- floor(|side|*20/perp_mid)',
        'corpora': {},
    }
    total_errors = 0
    for i, name in enumerate(('perp8', 'perp16', 'mixed')):
        cases = corpus(name, args.cases, args.seed + i)
        wc, we = wolf_cpu()
        lc, le = lib_cpu()
        wr = run(wc, we, cases)
        lr = run(lc, le, cases)
        total_errors += wr['errors'] + lr['errors']
        result['corpora'][name] = {
            'shape': shape(cases),
            'wolf64_current': wr,
            'v2_width_hybrid': lr,
            'library_gain_percent': 100.0 * (wr['mean_cycles'] - lr['mean_cycles']) / wr['mean_cycles'],
        }
    result['total_errors'] = total_errors

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for name, row in result['corpora'].items():
            w, l = row['wolf64_current'], row['v2_width_hybrid']
            print(name, row['shape'])
            print(f"  Wolf64       {w['mean_cycles']:.3f} ({w['min_cycles']}-{w['max_cycles']}) errors={w['errors']}")
            print(f"  width hybrid {l['mean_cycles']:.3f} ({l['min_cycles']}-{l['max_cycles']}) errors={l['errors']} gain={row['library_gain_percent']:.2f}%")

    if total_errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
