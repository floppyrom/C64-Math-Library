#!/usr/bin/env python3
"""Reference model and emulator loaders for the seek DDA kernels."""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from mini6502 import Assembler, CPU  # noqa: E402

NSLOT = 8
EUCLID = 0x8000  # speed flag: SPH bit 7


def bresenham(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """Pixel list from start to target, err starting at dmaj//2, err -= dmin."""
    dx, dy = x1 - x0, y1 - y0
    sx, sy = (1 if dx >= 0 else -1), (1 if dy >= 0 else -1)
    ax, ay = abs(dx), abs(dy)
    xmajor = ax >= ay
    dmaj, dmin = (ax, ay) if xmajor else (ay, ax)
    err = dmaj // 2
    x, y = x0, y0
    out = [(x, y)]
    for _ in range(dmaj):
        err -= dmin
        if err < 0:
            err += dmaj
            if xmajor:
                y += sy
            else:
                x += sx
        if xmajor:
            x += sx
        else:
            y += sy
        out.append((x, y))
    return out


COS_D = [round(256 * (1 - math.cos(math.atan((q + 0.5) / 32)))) for q in range(32)]


def major_speed(x0, y0, x1, y1, speed):
    """Major-axis Q8.8 speed the init derives (bit-exact), speed incl. flag."""
    s = speed & 0x7FFF
    if not speed & EUCLID or (x0, y0) == (x1, y1):
        return s
    ax, ay = abs(x1 - x0), abs(y1 - y0)
    dmaj, dmin = max(ax, ay), min(ax, ay)
    while dmaj > 255:
        dmaj >>= 1
        dmin >>= 1
    q = min(31, (dmin * 32) // dmaj)
    return s - (s * COS_D[q] >> 8)


def expected_frames(x0, y0, x1, y1, speed, stepper='step'):
    """Expected (position, arrived) after each stepper call until arrival.

    stepper: 'step' (Q8.8), 'int' (integer part only) or 'one' (1 px/frame).
    """
    s = major_speed(x0, y0, x1, y1, speed)
    line = bresenham(x0, y0, x1, y1)
    dmaj = len(line) - 1
    if dmaj == 0:
        return []
    bud, done, out = 0, 0, []
    while True:
        if stepper == 'one':
            k = 1
        elif stepper == 'int':
            k = s >> 8
        else:
            bud += s & 0xFF
            k = (s >> 8) + (bud >> 8)
            bud &= 0xFF
        done = min(dmaj, done + k)
        out.append((line[done], done == dmaj))
        if done == dmaj:
            return out


class Seek:
    """Standalone kernel loader. width = 8 (seek_u8_u8_dda) or 16."""

    def __init__(self, width=8, org=0x8000, io=0x00E0, st=0x9000):
        self.width = width
        src = HERE / ('seek_u8_u8_dda.asm' if width == 8 else 'seek_u16_u8_dda.asm')
        text = src.read_text(encoding='utf-8')
        text = text.replace('ORG = $8000', f'ORG = ${org:04X}')
        text = text.replace('IO  = $E0', f'IO  = ${io:02X}' if io < 256 else f'IO  = ${io:04X}')
        text = text.replace('ST  = $9000', f'ST  = ${st:04X}')
        code, self.labels, self.const = Assembler().assemble(text)
        self.code = code
        self.code_bytes = len(code)
        mem = bytearray(65536)
        for a, b in code.items():
            mem[a] = b
        self.cpu = CPU(mem)
        self.cpu.d = 0
        self.io = io
        self.p = 'seek8' if width == 8 else 'seek16'
        self.s = 'S8_' if width == 8 else 'S16_'

    def c(self, name):
        return self.const[name] if name in self.const else self.labels[name]

    def set_pos(self, slot, x, y):
        m = self.cpu.mem
        if self.width == 8:
            m[self.c('S8_POS_X') + slot] = x
        else:
            m[self.c('S16_POS_XL') + slot] = x & 255
            m[self.c('S16_POS_XH') + slot] = x >> 8
        m[self.c(self.s + 'POS_Y') + slot] = y

    def pos(self, slot):
        m = self.cpu.mem
        if self.width == 8:
            x = m[self.c('S8_POS_X') + slot]
        else:
            x = m[self.c('S16_POS_XL') + slot] | (m[self.c('S16_POS_XH') + slot] << 8)
        return x, m[self.c(self.s + 'POS_Y') + slot]

    def init(self, slot, x0, y0, x1, y1, speed):
        self.set_pos(slot, x0, y0)
        io = self.io
        inputs = bytes((x1 & 255, x1 >> 8, y1, speed & 255, speed >> 8))
        self.cpu.mem[io:io + 5] = inputs
        self.cpu.x = slot
        cyc = self.cpu.call(self.labels[self.p + '_init'])
        assert self.cpu.x == slot
        assert bytes(self.cpu.mem[io:io + 5]) == inputs, 'inputs not preserved'
        return cyc, self.cpu.c

    def step(self, slot, stepper='step'):
        self.cpu.x = slot
        name = {'step': '_step', 'int': '_step_int', 'one': '_step1'}[stepper]
        cyc = self.cpu.call(self.labels[self.p + name])
        assert self.cpu.x == slot
        return cyc, self.cpu.c
