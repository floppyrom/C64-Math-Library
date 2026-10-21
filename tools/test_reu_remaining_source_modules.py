#!/usr/bin/env python3
"""Regression proofs for newly separated Turbo32 / QS16 source modules."""
from __future__ import annotations

import hashlib
import random
import unittest

from mini6502 import CPU
from reu_remaining_source_modules import (
    REUSourceError, QS_BANKS, QS_BYTES, QS_RECORDS,
    qs16_fragments, qs16_table, turbo32_fragments,
)


def number(value):
    return int(value[1:], 16)


class IndependentREUSourceModules(unittest.TestCase):
    def test_turbo32_source_assembles_at_two_real_maps(self):
        for placement in (
            dict(zp=0x0a, io=0xc000, table=0x6000, low=0x4000, api=0x3000),
            dict(zp=0x40, io=0xc080, table=0x7000, low=0x5000, api=0x8000),
        ):
            with self.subTest(placement=placement):
                info, chunks, planes = turbo32_fragments(**placement)
                self.assertFalse(info["native_dma_and_hardware_qualified"])
                self.assertEqual(len(chunks["turbo32_executable_zp.bin"]), 135)
                self.assertEqual(len(planes), 4)
                self.assertEqual(sum(len(x) for x in planes.values()), 2048)
                self.assertEqual(set(chunks), {
                    "turbo32_executable_zp.bin", "turbo32_low_preparer.bin",
                    "turbo32_low_summation.bin", "turbo32_public_binder.bin"})
                mem = bytearray(65536)
                zp, io = placement["zp"], placement["io"]
                mem[zp:zp+135] = chunks["turbo32_executable_zp.bin"]
                mem[placement["low"]:placement["low"]+
                    len(chunks["turbo32_low_preparer.bin"])] = chunks[
                        "turbo32_low_preparer.bin"]
                start = placement["low"] + 0x100
                mem[start:start+len(chunks["turbo32_low_summation.bin"])] = chunks[
                    "turbo32_low_summation.bin"]
                start = placement["api"] + 0x900
                mem[start:start+len(chunks["turbo32_public_binder.bin"])] = chunks[
                    "turbo32_public_binder.bin"]
                for offset, name in zip((0x1000, 0x1200, 0x1400, 0x1600), planes):
                    mem[placement["table"]+offset:placement["table"]+offset+512] = planes[name]
                cpu = CPU(mem)
                saved_sp = cpu.sp
                inputs = [(0, 0), (1, 1), (0xffffffff, 0xffffffff),
                          (0x12345678, 0x9abcdef0), (0xffffffff, 0)]
                rng = random.Random(20261021)
                inputs += [(rng.getrandbits(32), rng.getrandbits(32))
                           for _ in range(64)]
                for a, b in inputs:
                    mem[io:io+4] = a.to_bytes(4, "little")
                    mem[io+4:io+8] = b.to_bytes(4, "little")
                    cpu.d = 0
                    cpu.call(number(info["public_entry"]), 20000)
                    got = int.from_bytes(mem[io+8:io+16], "little")
                    self.assertEqual(got, a * b, (placement, a, b))
                    self.assertEqual(cpu.c, 0)
                    self.assertEqual(cpu.sp, saved_sp)
                    self.assertEqual(int.from_bytes(mem[io:io+4], "little"), a)
                    self.assertEqual(int.from_bytes(mem[io+4:io+8], "little"), b)

    def test_qs16_exact_generated_lookup_table(self):
        data = qs16_table()
        self.assertEqual(len(data), QS_BYTES)
        self.assertEqual(QS_RECORDS, 131071)
        for value in (0, 1, 2, 3, 4, 65535, 65536, 131069, 131070):
            q = int.from_bytes(data[value*4:value*4+4], "little")
            self.assertEqual(q, (value*value)//4)
        self.assertEqual(int.from_bytes(data[-4:], "little"), 4294836225)
        rng = random.Random(1492)
        for _ in range(3000):
            x, y = rng.randrange(65536), rng.randrange(65536)
            summation, difference = x + y, abs(x - y)
            qa = int.from_bytes(data[summation*4:summation*4+4], "little")
            qb = int.from_bytes(data[difference*4:difference*4+4], "little")
            self.assertEqual(qa - qb, x*y)

    def test_qs16_source_executes_with_prewritten_reu_lookup(self):
        data = qs16_table()
        for map_ in (
            dict(io=0xc000, scratch=0xc020, zp=0x02, api=0x3000, reu_bank=0x10),
            dict(io=0xc080, scratch=0xc0a0, zp=0x40, api=0x4000, reu_bank=0x30),
        ):
            with self.subTest(map=map_):
                info, chunks, table = qs16_fragments(**map_)
                self.assertEqual(hashlib.sha256(table).hexdigest(),
                                 info["table_sha256"])
                self.assertEqual(info["exclusive_zp_bytes"], 16)
                self.assertEqual(info["reu_bank_count"], QS_BANKS)
                self.assertFalse(info["native_dma_and_hardware_qualified"])
                mem = bytearray(65536)
                for name, at in (
                    ("qs16_begin.bin", map_["api"]+0xa80),
                    ("qs16_call.bin", map_["api"]+0xa8b),
                    ("qs16_end.bin", map_["api"]+0xb5c),
                ):
                    mem[at:at+len(chunks[name])] = chunks[name]
                mem[0xdf02] = map_["scratch"] & 255
                mem[0xdf03] = map_["scratch"] >> 8
                mem[0xdf08] = 0
                mem[0xdf09] = 0
                reu = bytearray(16 * 1024 * 1024)
                at = map_["reu_bank"] * 65536
                reu[at:at+len(data)] = data
                cpu = CPU(mem, reu=reu)
                sp = cpu.sp
                cpu.call(number(info["entrypoints"]["MATH_REU_QS16_BEGIN"]))
                self.assertEqual(cpu.sp, sp)
                cases = [(0, 0), (1, 1), (65535, 65535),
                         (0x1234, 0xabcd), (0, 0xffff)]
                rng = random.Random(56)
                cases += [(rng.randrange(65536), rng.randrange(65536))
                          for _ in range(40)]
                for x, y in cases:
                    io = map_["io"]
                    mem[io:io+2] = x.to_bytes(2, "little")
                    mem[io+4:io+6] = y.to_bytes(2, "little")
                    cpu.d = 0
                    cpu.call(number(info["entrypoints"]["MATH_REU_QS16"]), 5000)
                    self.assertEqual(int.from_bytes(mem[io+8:io+12], "little"),
                                     x*y, (x, y, map_))
                    self.assertEqual(cpu.c, 0)
                    self.assertEqual(cpu.sp, sp)
                cpu.call(number(info["entrypoints"]["MATH_REU_QS16_END"]))
                self.assertEqual(cpu.sp, sp)

    def test_fail_closed_on_out_of_bounds_or_conflicts(self):
        for args in (
            {"zp": 0x7a}, {"zp": 0}, {"table": 0xc000},
            {"low": 0xd000}, {"io": 0x4000},
            {"api": 0x3700},
        ):
            with self.subTest(turbo32=args):
                with self.assertRaises(REUSourceError):
                    turbo32_fragments(**args)
        for args in (
            {"reu_bank": 17}, {"reu_bank": 249}, {"zp": 0xe3},
            {"scratch": 0xc000}, {"api": 0xd000},
        ):
            with self.subTest(qs16=args):
                with self.assertRaises(REUSourceError):
                    qs16_fragments(**args)


if __name__ == "__main__":
    unittest.main()
