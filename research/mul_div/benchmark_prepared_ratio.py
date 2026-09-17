#!/usr/bin/env python3
"""Benchmark prepared ratio against Quake64's near-clip arithmetic.

The prepared candidates run on the shipped V2 resident image and use the native
record UMUL16 `same_x` path after MATH_INIT. The comparison side is a literal
standalone transcription of Quake64's `umul8j`, `scale_nd`, `lerp16`,
`div24u8`, and `.nlrun` arithmetic from commit
7c84654946a60314568b709e7e7b97467fed69df.

This is a research/stress benchmark, not release certification and not a claim
about Quake64's runtime event-frequency distribution.
"""
from __future__ import annotations

import argparse
import hashlib
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
from generate_prepared_ratio import generate_compact, generate_unrolled  # noqa: E402

V2_PRG = ROOT / 'v2_pareto_fast' / 'resident' / 'math_v2_pareto_fast_game_math.prg'
MATH_INIT = 0x3280
N0, D0, Y0, Z0 = 0xC010, 0xC014, 0xC004, 0xC008
ZCLIP = 0x0100
QUAKE_COMMIT = '7c84654946a60314568b709e7e7b97467fed69df'

# Standalone Quake scratch map used only in the comparison CPU.
QN = 0x48
QD = 0x4A
QY = 0x4C
QROT = 0x45

QUAKE_SOURCE = r'''
mul_a=$40
mul_b=$41
mul_sign=$42
prod_l=$43
prod_h=$44
rot0=$45
rot1=$46
rot2=$47
nlo=$48
nhi=$49
dlo=$4A
dhi=$4B
ylo=$4C
yhi=$4D
sqlo=$A000
sqhi=$A200

.org $D000
umul8j:
    sta mul_a
    sty mul_b
    clc
    adc mul_b
    bcc um_s0
    tax
    lda sqlo+$100,x
    sta prod_l
    lda sqhi+$100,x
    sta prod_h
    jmp um_dif
um_s0:
    tax
    lda sqlo,x
    sta prod_l
    lda sqhi,x
    sta prod_h
um_dif:
    lda mul_a
    sec
    sbc mul_b
    bcs um_dpos
    eor #$ff
    adc #1
um_dpos:
    tay
    sec
    lda prod_l
    sbc sqlo,y
    sta prod_l
    lda prod_h
    sbc sqhi,y
    sta prod_h
    rts

scale_nd:
    lda #8
    sta mul_a
snd_loop:
    jsr nd_fitn
    bcc snd_do
    jsr nd_fitd
    bcc snd_do
    rts
snd_do:
    lda nhi
    cmp #$80
    ror nhi
    ror nlo
    lda dhi
    cmp #$80
    ror dhi
    ror dlo
    dec mul_a
    bne snd_loop
    rts
nd_fitn:
    lda nhi
    ldy nlo
    jmp nd_fit
nd_fitd:
    lda dhi
    ldy dlo
nd_fit:
    tax
    beq nd_fz
    cmp #$ff
    bne nd_fn
    tya
    bmi nd_fy
nd_fn:
    clc
    rts
nd_fz:
    tya
    bmi nd_fn
nd_fy:
    sec
    rts

lerp16:
    lda #0
    sta mul_sign
    lda yhi
    bpl lp_yp
    lda #$80
    sta mul_sign
    sec
    lda #0
    sbc ylo
    sta ylo
    lda #0
    sbc yhi
    sta yhi
lp_yp:
    lda nlo
    bpl lp_np
    lda mul_sign
    eor #$80
    sta mul_sign
    lda nlo
    eor #$ff
    clc
    adc #1
    sta nlo
lp_np:
    lda dlo
    bpl lp_dp
    lda mul_sign
    eor #$80
    sta mul_sign
    lda dlo
    eor #$ff
    clc
    adc #1
    sta dlo
lp_dp:
    lda dlo
    bne lp_mul
    lda #0
    sta rot0
    sta rot1
    rts
lp_mul:
    lda ylo
    ldy nlo
    jsr umul8j
    lda prod_l
    sta rot0
    lda prod_h
    sta rot1
    lda yhi
    ldy nlo
    jsr umul8j
    clc
    lda rot1
    adc prod_l
    sta rot1
    lda prod_h
    adc #0
    sta rot2
    jsr div24u8
    bit mul_sign
    bpl lp_ok
    sec
    lda #0
    sbc rot0
    sta rot0
    lda #0
    sbc rot1
    sta rot1
lp_ok:
    lda rot0
    rts

div24u8:
    lda #0
    sta nlo
    ldx #24
    lda rot2
    bne d24
    lda rot1
    sta rot2
    lda rot0
    sta rot1
    lda #0
    sta rot0
    ldx #16
    lda rot2
    bne d24
    lda rot1
    sta rot2
    lda #0
    sta rot1
    ldx #8
d24:
    asl rot0
    rol rot1
    rol rot2
    rol nlo
    lda nlo
    bcs dsub
    cmp dlo
    bcc dnext
dsub:
    sbc dlo
    sta nlo
    inc rot0
dnext:
    dex
    bne d24
    lda rot2
    beq d16
    lda #$ff
    sta rot0
    sta rot1
d16:
    rts

nlrun:
    jsr scale_nd
    lda dlo
    ora dhi
    bne nl_nonzero
    lda #0
    sta rot0
    sta rot1
    rts
nl_nonzero:
    jmp lerp16
'''


def load_prg(path: Path) -> bytearray:
    raw = path.read_bytes()
    load = raw[0] | (raw[1] << 8)
    mem = bytearray(65536)
    mem[load:load + len(raw) - 2] = raw[2:]
    return mem


def patch(mem: bytearray, source: str) -> dict[str, int]:
    code, labels, _ = Assembler().assemble(source)
    for addr, value in code.items():
        mem[addr] = value
    return labels


def prepared_cpu(kind: str):
    mem = load_prg(V2_PRG)
    cpu = CPU(mem)
    cpu.d = 0
    cpu.call(MATH_INIT)  # outside timing
    source = generate_compact() if kind == 'compact' else generate_unrolled()
    labels = patch(cpu.mem, source)
    prep = labels['ratio_prep_compact' if kind == 'compact' else 'ratio_prep_unrolled']
    return cpu, prep, labels['ratio_apply']


def quake_cpu():
    mem = bytearray(65536)
    labels = patch(mem, QUAKE_SOURCE)
    # Quake tables contain floor(i*i/4), indexed over 0..510.
    for i in range(511):
        value = (i * i) // 4
        mem[0xA000 + i] = value & 0xFF
        mem[0xA200 + i] = (value >> 8) & 0xFF
    cpu = CPU(mem)
    cpu.d = 0
    return cpu, labels['nlrun']


def put16(mem: bytearray, addr: int, value: int) -> None:
    value &= 0xFFFF
    mem[addr] = value & 0xFF
    mem[addr + 1] = value >> 8


def gets16(mem: bytearray, addr: int) -> int:
    value = mem[addr] | (mem[addr + 1] << 8)
    return value if value < 0x8000 else value - 0x10000


def trunc_div(num: int, den: int) -> int:
    sign = -1 if (num < 0) ^ (den < 0) else 1
    return sign * (abs(num) // abs(den))


def prepared_reference(y: int, n: int, d: int) -> int:
    an, ad = abs(n), abs(d)
    sign = -1 if (n < 0) ^ (d < 0) else 1
    if an == 0:
        return 0
    if an == ad:
        return sign * y
    m = ((an << 16) + ad // 2) // ad
    return trunc_div(y * sign * m, 65536)


def summarize(values):
    return {
        'mean': statistics.fmean(values),
        'min': min(values),
        'max': max(values),
    }


def err_summary(errors):
    return {
        'outputs': len(errors),
        'nonzero_error_percent': 100.0 * sum(e != 0 for e in errors) / len(errors),
        'mean_absolute_error': statistics.fmean(abs(e) for e in errors),
        'max_absolute_error': max(abs(e) for e in errors),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=5000)
    ap.add_argument('--seed', type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    rng = random.Random(args.seed)
    pc, pc_prep, pc_apply = prepared_cpu('compact')
    pu, pu_prep, pu_apply = prepared_cpu('unrolled')
    qc, qrun = quake_cpu()

    compact_prep, compact_apply, compact_pair = [], [], []
    unrolled_prep, unrolled_apply, unrolled_pair = [], [], []
    quake_pair = []
    compact_contract_errors = 0
    unrolled_contract_errors = 0
    compact_exact_errors, unrolled_exact_errors, quake_exact_errors = [], [], []

    for _ in range(args.cases):
        z0 = rng.randint(-8192, ZCLIP - 1)
        z1 = rng.randint(ZCLIP, 8191)
        n = ZCLIP - z0
        d = z1 - z0
        ya = rng.randint(-8192, 8191)
        yb = rng.randint(-8192, 8191)
        exact_a = trunc_div(ya * n, d)
        exact_b = trunc_div(yb * n, d)

        # Compact prepared path.
        put16(pc.mem, N0, n); put16(pc.mem, D0, d)
        cp = pc.call(pc_prep)
        put16(pc.mem, Y0, ya); ca = pc.call(pc_apply); cga = gets16(pc.mem, Z0)
        put16(pc.mem, Y0, yb); cb = pc.call(pc_apply); cgb = gets16(pc.mem, Z0)
        compact_prep.append(cp); compact_apply.extend((ca, cb)); compact_pair.append(cp + ca + cb)
        compact_contract_errors += int(cga != prepared_reference(ya, n, d))
        compact_contract_errors += int(cgb != prepared_reference(yb, n, d))
        compact_exact_errors.extend((cga - exact_a, cgb - exact_b))

        # Unrolled prepared path.
        put16(pu.mem, N0, n); put16(pu.mem, D0, d)
        up = pu.call(pu_prep)
        put16(pu.mem, Y0, ya); ua = pu.call(pu_apply); uga = gets16(pu.mem, Z0)
        put16(pu.mem, Y0, yb); ub = pu.call(pu_apply); ugb = gets16(pu.mem, Z0)
        unrolled_prep.append(up); unrolled_apply.extend((ua, ub)); unrolled_pair.append(up + ua + ub)
        unrolled_contract_errors += int(uga != prepared_reference(ya, n, d))
        unrolled_contract_errors += int(ugb != prepared_reference(yb, n, d))
        unrolled_exact_errors.extend((uga - exact_a, ugb - exact_b))

        # Quake current path: original n/d is restored before the Y component,
        # so scale_nd runs again. Add the actual 4 PHA + 4 PLA = 28 cycles.
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, ya)
        qa = qc.call(qrun); qga = gets16(qc.mem, QROT)
        put16(qc.mem, QN, n); put16(qc.mem, QD, d); put16(qc.mem, QY, yb)
        qb = qc.call(qrun); qgb = gets16(qc.mem, QROT)
        quake_pair.append(qa + qb + 28)
        quake_exact_errors.extend((qga - exact_a, qgb - exact_b))

    qmean = statistics.fmean(quake_pair)
    cmean = statistics.fmean(compact_pair)
    umean = statistics.fmean(unrolled_pair)
    result = {
        'status': 'research_evidence_not_release_certification',
        'v2_prg_sha256': hashlib.sha256(V2_PRG.read_bytes()).hexdigest(),
        'quake64_source_commit': QUAKE_COMMIT,
        'cases': args.cases,
        'seed': args.seed,
        'corpus': {
            'zclip': ZCLIP,
            'z0_range': [-8192, ZCLIP - 1],
            'z1_range': [ZCLIP, 8191],
            'component_range': [-8192, 8191],
            'applications_per_ratio': 2,
        },
        'cycles_excluding_external_caller_jsr': {
            'compact': {
                'prep': summarize(compact_prep),
                'apply': summarize(compact_apply),
                'pair': summarize(compact_pair),
            },
            'unrolled': {
                'prep': summarize(unrolled_prep),
                'apply': summarize(unrolled_apply),
                'pair': summarize(unrolled_pair),
            },
            'quake64_current_pair': summarize(quake_pair),
        },
        'speedup_vs_quake64_current_pair_percent': {
            'compact': 100.0 * (qmean - cmean) / qmean,
            'unrolled': 100.0 * (qmean - umean) / qmean,
        },
        'accuracy_vs_exact': {
            'compact': err_summary(compact_exact_errors),
            'unrolled': err_summary(unrolled_exact_errors),
            'quake64_current': err_summary(quake_exact_errors),
        },
        'prepared_contract_errors': {
            'compact': compact_contract_errors,
            'unrolled': unrolled_contract_errors,
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"cases={args.cases} seed=${args.seed:X}")
        for kind in ('compact', 'unrolled'):
            row = result['cycles_excluding_external_caller_jsr'][kind]
            print(
                f"{kind:8s} prep={row['prep']['mean']:.3f} "
                f"apply={row['apply']['mean']:.3f} pair={row['pair']['mean']:.3f} "
                f"speedup={result['speedup_vs_quake64_current_pair_percent'][kind]:.2f}% "
                f"contract_errors={result['prepared_contract_errors'][kind]}"
            )
        qr = result['cycles_excluding_external_caller_jsr']['quake64_current_pair']
        print(f"quake64  pair={qr['mean']:.3f} range={qr['min']}-{qr['max']}")
        print('accuracy:', result['accuracy_vs_exact'])

    if compact_contract_errors or unrolled_contract_errors:
        raise SystemExit(1)
    if max(abs(e) for e in compact_exact_errors) > 1:
        raise SystemExit('compact exceeded <=1 error contract')
    if max(abs(e) for e in unrolled_exact_errors) > 1:
        raise SystemExit('unrolled exceeded <=1 error contract')


if __name__ == '__main__':
    main()
