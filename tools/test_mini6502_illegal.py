#!/usr/bin/env python3
"""Checks for the stable NMOS unintended opcodes in mini6502.

Expected values come from the definitions and worked examples in
"No More Secrets - NMOS 6510 Unintended Opcodes" (2025-12-24 edition).
"""
from mini6502 import Assembler, CPU


def run(src, setup=None):
    code, labels, _ = Assembler().assemble('* = $2000\n' + src + '\n rts\n')
    mem = bytearray(65536)
    for a, b in code.items():
        mem[a] = b
    cpu = CPU(mem)
    if setup:
        setup(cpu)
    cyc = cpu.call(0x2000) - 6  # minus the RTS
    return cpu, cyc


def check(name, cond):
    if not cond:
        raise AssertionError(name)


def main():
    # DCP: 16-bit decrement idiom (doc: "decrementing 16bit counter")
    c, _ = run('lda #$ff\n dcp $10\n bne done\n dec $11\ndone:',
               lambda c: c.mem.__setitem__(slice(0x10, 0x12), b'\x00\x12'))
    check('dcp 16-bit', c.mem[0x10] == 0xFF and c.mem[0x11] == 0x11 and c.c == 1)
    c, cyc = run('ldx #1\n lda #5\n dcp $3000,x', lambda c: c.mem.__setitem__(0x3001, 6))
    check('dcp abs,x value/flags', c.mem[0x3001] == 5 and c.z == 1 and c.c == 1)
    check('dcp abs,x 7 cycles', cyc == 2 + 2 + 7)
    c, cyc = run('ldy #1\n dcp $3000,y', lambda c: c.mem.__setitem__(0x3001, 0))
    check('dcp abs,y', c.mem[0x3001] == 0xFF and cyc == 2 + 7)
    # ISC: inc then SBC
    c, _ = run('sec\n lda #$10\n isc $10', lambda c: c.mem.__setitem__(0x10, 4))
    check('isc', c.mem[0x10] == 5 and c.a == 0x0B and c.c == 1)
    # SLO / RLA / SRE / RRA
    c, _ = run('lda #$02\n slo $10', lambda c: c.mem.__setitem__(0x10, 0x81))
    check('slo', c.mem[0x10] == 0x02 and c.c == 1 and c.a == 0x02)
    c, _ = run('sec\n lda #$0f\n rla $10', lambda c: c.mem.__setitem__(0x10, 0x81))
    check('rla', c.mem[0x10] == 0x03 and c.c == 1 and c.a == 0x03)
    c, _ = run('lda #$ff\n sre $10', lambda c: c.mem.__setitem__(0x10, 0x03))
    check('sre', c.mem[0x10] == 0x01 and c.c == 1 and c.a == 0xFE)
    c, _ = run('sec\n lda #$10\n rra $10', lambda c: c.mem.__setitem__(0x10, 0x02))
    check('rra', c.mem[0x10] == 0x81 and c.a == 0x91 and c.c == 0)
    # SAX / LAX
    c, _ = run('lda #$f0\n ldx #$3c\n sax $10')
    check('sax', c.mem[0x10] == 0x30)
    c, cyc = run('ldy #$ff\n lax ($10),y', lambda c: (c.mem.__setitem__(slice(0x10, 0x12), b'\x01\x30'),
                                                      c.mem.__setitem__(0x3100, 0x80)))
    check('lax (zp),y page cross', c.a == c.x == 0x80 and c.n == 1 and cyc == 2 + 6)
    # Immediate combinations
    c, _ = run('lda #$f0\n ldx #$3c\n sbx #$10')
    check('sbx', c.x == 0x20 and c.c == 1 and c.a == 0xF0)
    c, _ = run('lda #$01\n ldx #$ff\n sbx #$02')
    check('sbx borrow', c.x == 0xFF and c.c == 0)
    c, _ = run('lda #$03\n alr #$ff')
    check('alr', c.a == 0x01 and c.c == 1)
    c, _ = run('lda #$81\n anc #$ff')
    check('anc', c.a == 0x81 and c.c == 1 and c.n == 1)
    c, _ = run('sec\n lda #$ff\n arr #$ff')
    check('arr', c.a == 0xFF and c.c == 1 and c.v == 0)
    c, _ = run('clc\n lda #$00\n arr #$ff')
    check('arr zero', c.a == 0 and c.z == 1 and c.c == 0 and c.v == 0)
    print('MINI6502 ILLEGAL OPCODES PASS')


if __name__ == '__main__':
    main()
