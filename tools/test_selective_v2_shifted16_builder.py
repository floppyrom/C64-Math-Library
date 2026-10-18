#!/usr/bin/env python3
"""Canonical V2 shifted 16/16 public-source proof at two relocated origins.

No historical resident timing is used for comparisons: both candidates run
the same complete public ABI calls on the same input pairs.
"""
from __future__ import annotations

import random
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU

import math_builder
import selective_linker as linker
import selective_v2_shifted_u3216 as shifted

FAST = "link:v2-shifted-public"
SMALL = "link:accumulator-remainder"
EDGE = (0, 1, 2, 3, 7, 15, 127, 255, 256, 257,
        32767, 32768, 65534, 65535)
DIVS = (0, 1, 2, 3, 7, 127, 255, 256, 257, 32768, 65535)


def pairs():
    rng = random.Random(0x168C2026)
    result = [(n, d) for n in EDGE for d in DIVS]
    result.extend((rng.randrange(65536), rng.randrange(65536))
                  for _ in range(384 - len(result)))
    return result


class ShiftedV2Public(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, ident, zp, ram):
        return math_builder.create_plan(
            self.index, ["UDIV16_SHL8"], objective="size",
            pins={"UDIV16_SHL8": ident},
            zp_budget=zp, ram_budget=ram)

    def run_image(self, ident, code, io, zp):
        fast = ident == FAST
        with tempfile.TemporaryDirectory() as td:
            man = linker.build(self.plan(
                ident, 12 if fast else 0, 2400 if fast else 162),
                Path(td), memory={
                    "code_base": code, "math_io": io,
                    "zp_base": zp, "scratch_base": io + 0x40})
            expected_bytes = shifted.BYTES if fast else 129
            self.assertEqual(man["resource_use"]["image_span_bytes"], expected_bytes)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],
                             expected_bytes + 32 + (0 if fast else 1))
            self.assertEqual(man["resource_use"]["zero_page_bytes"], 12 if fast else 0)
            self.assertEqual(man["operations"][0]["variant"], ident)
            data = (Path(td) / "math_selective.prg").read_bytes()
            self.assertEqual(data[:2], code.to_bytes(2, "little"))
            self.assertEqual(len(data), 2 + expected_bytes)
            mem = bytearray(65536)
            mem[code:code + expected_bytes] = data[2:]
            pristine = bytes(mem[code:code + expected_bytes])
            cpu = CPU(mem)
            entry = int(man["operations"][0]["entry"][1:], 16)
            sp = cpu.sp
            times = []
            for i, (n, d) in enumerate(pairs()):
                numerator = n.to_bytes(2, "little") + b"\x5a\xa5"
                divisor = d.to_bytes(2, "little") + b"\x69\xab"
                mem[io+16:io+20] = numerator
                mem[io+20:io+24] = divisor
                mem[io+24:io+32] = b"\xcc"*4+b"\xdd\xdd\x49\x59"
                cpu.a = (n+i) & 255
                cpu.x = (d+i) & 255
                cpu.y = (n^d^i) & 255
                cpu.c = i & 1
                cpu.d = 0
                ticks = cpu.call(entry, 50000)
                q = int.from_bytes(mem[io+24:io+28], "little")
                rem = int.from_bytes(mem[io+28:io+30], "little")
                expected = ((n << 8)//d if d else 0,
                            (n << 8)%d if d else 0, int(d==0))
                self.assertEqual((q, rem, cpu.c), expected,
                                 (ident, hex(code), n, d))
                self.assertEqual(bytes(mem[io+16:io+20]), numerator)
                self.assertEqual(bytes(mem[io+20:io+24]), divisor)
                self.assertEqual(bytes(mem[io+30:io+32]), b"\x49\x59")
                self.assertEqual(cpu.sp, sp)
                times.append(ticks)
            self.assertEqual(bytes(mem[code:code + expected_bytes]), pristine)
            return times

    def test_full_public_abi_two_origins_and_same_corpus_cycles(self):
        for code, io, zp in ((0x8000, 0xc000, 0x50),
                             (0x7123, 0xc040, 0x70)):
            with self.subTest(code=code):
                portable = self.run_image(SMALL, code, io, zp)
                v2 = self.run_image(FAST, code, io, zp)
                self.assertEqual(len(v2), 384)
                self.assertLess(sum(v2), sum(portable))
                print("V2_SHL8_MATCHED_PUBLIC", hex(code),
                      "v2_mean", round(sum(v2)/384, 3),
                      "portable_mean", round(sum(portable)/384, 3),
                      "v2_max", max(v2),
                      "portable_max", max(portable),
                      flush=True)

    def test_automatic_speed_respects_the_zp_and_ram_frontier(self):
        with tempfile.TemporaryDirectory() as td:
            for budget_zp, budget_ram, expected in (
                    (12, 2400, FAST),
                    (0, 162, SMALL),
                    (12, 162, SMALL)):
                with self.subTest(budget_zp=budget_zp, budget_ram=budget_ram):
                    plan = math_builder.create_plan(
                        self.index, ["UDIV16_SHL8"], objective="speed",
                        workload_calls={"UDIV16_SHL8": 100},
                        zp_budget=budget_zp, ram_budget=budget_ram)
                    man = linker.build(plan, Path(td)/("speed_%d_%d" %
                                       (budget_zp, budget_ram)))
                    self.assertEqual(man["operations"][0]["variant"], expected)
                    self.assertEqual(man["cycle_model"]["cases"], 384)
                    self.assertEqual(man["cycle_model"]["corpus_sha256"],
                                     "f78373d1422f84e75a96f89e944e44e925cfae4f3531c66696cc5272fab39f6c")
                    self.assertLess(
                        man["cycle_model"]["mean_cycles"][FAST],
                        man["cycle_model"]["mean_cycles"][SMALL])

    def test_resource_constraints_and_fail_closed_pin(self):
        with tempfile.TemporaryDirectory() as td:
            for ram, zp in ((2399, 12), (2400, 11)):
                with self.subTest(ram=ram, zp=zp):
                    with self.assertRaises(linker.LinkError):
                        linker.build(self.plan(FAST, zp, ram), Path(td)/"no")
            compact = linker.build(self.plan(SMALL, 0, 162), Path(td)/"compact")
            self.assertEqual(compact["resource_use"]["zero_page_bytes"], 0)
            self.assertEqual(compact["operations"][0]["variant"], SMALL)


if __name__ == "__main__":
    unittest.main()
