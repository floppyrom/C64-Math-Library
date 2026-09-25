#!/usr/bin/env python3
"""Reference model and emulator loader for seek_u16_u8_dda.asm."""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from mini6502 import Assembler, CPU  # noqa: E402

SOURCE = HERE / 'seek_u16_u8_dda.asm'
NSLOT = 8


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


def euclid_major_speed(x0, y0, x1, y1, speed_q8):
    """Major-axis Q8.8 speed that seek_init_euclid derives (bit-exact)."""
    ax, ay = abs(x1 - x0), abs(y1 - y0)
    dmaj, dmin = max(ax, ay), min(ax, ay)
    while dmaj > 255:
        dmaj >>= 1
        dmin >>= 1
    q = min(31, (dmin * 32) // dmaj)
    return speed_q8 - (speed_q8 * COS_D[q] >> 8)


def expected_frames(x0, y0, x1, y1, speed_q8, euclid=False, integer=False):
    """Expected position after each seek_step call until and including arrival."""
    if euclid and (x0, y0) != (x1, y1):
        speed_q8 = euclid_major_speed(x0, y0, x1, y1, speed_q8)
    line = bresenham(x0, y0, x1, y1)
    dmaj = len(line) - 1
    if dmaj == 0:
        return []
    bud, done, out = 0, 0, []
    while True:
        bud += 0 if integer else speed_q8 & 0xFF
        k = (speed_q8 >> 8) + (bud >> 8)
        bud &= 0xFF
        done = min(dmaj, done + k)
        out.append((line[done], done == dmaj))
        if done == dmaj:
            return out


class Seek:
    def __init__(self, org=0x8000, io=0x00F0, st=0x9000):
        text = SOURCE.read_text(encoding='utf-8')
        text = text.replace('ORG = $8000', f'ORG = ${org:04X}')
        text = text.replace('IO  = $00F0', f'IO  = ${io:04X}')
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
        self.st = st

    def c(self, name):
        return self.const[name] if name in self.const else self.labels[name]

    def set_pos(self, slot, x, y):
        m = self.cpu.mem
        m[self.c('POS_XL') + slot] = x & 255
        m[self.c('POS_XH') + slot] = x >> 8
        m[self.c('POS_Y') + slot] = y

    def init(self, slot, x0, y0, x1, y1, speed_q8, euclid=False):
        self.set_pos(slot, x0, y0)
        m = self.cpu.mem
        io = self.io
        m[io:io + 5] = bytes((x1 & 255, x1 >> 8, y1, speed_q8 & 255, speed_q8 >> 8))
        self.cpu.x = slot
        cyc = self.cpu.call(self.labels['seek_init_euclid' if euclid else 'seek_init'])
        assert self.cpu.x == slot
        return cyc, self.cpu.c

    def step(self, slot, integer=False):
        self.cpu.x = slot
        cyc = self.cpu.call(self.labels['seek_step_int' if integer else 'seek_step'])
        assert self.cpu.x == slot
        return cyc, self.cpu.c

    def pos(self, slot):
        m = self.cpu.mem
        x = m[self.c('POS_XL') + slot] | (m[self.c('POS_XH') + slot] << 8)
        return x, m[self.c('POS_Y') + slot]
