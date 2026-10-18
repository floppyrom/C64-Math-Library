#!/usr/bin/env python3
"""One historical V2 signed32/16 producer, two public APIs, resources and speed."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as L
import selective_speed_s3216 as timing

APIS = ("SDIV32_16", "SMOD32_16")
FAST = "link:v2-signed-magnitude"
COMPACT = "link:portable-zerozp"
FAST_RAM = 2880 + 32


class SignedV2BuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, objective="speed", zp=12, ram=FAST_RAM, pins=None):
        return math_builder.create_plan(
            self.index, list(APIS), objective=objective,
            zp_budget=zp, ram_budget=ram, pins=pins,
            workload_calls={api: 100 for api in APIS} if objective == "speed" else None)

    def test_same_384_case_full_public_speed_comparison_at_two_placements(self):
        for code, io, zp in ((0x8000, 0xc000, 0x50),
                             (0x7123, 0xc040, 0x70)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as td:
                res = timing.bench_sdiv32_16(
                    L.MODULES["MATH_SDIV32_16"], code, io, io+0x40,
                    L.ROOT, zp=zp)
                self.assertEqual(res["cases"], 384)
                self.assertEqual(res["corpus_sha256"], timing.CORPUS_SHA256)
                self.assertLess(res["mean_cycles"][FAST],
                                res["mean_cycles"][COMPACT])
                man = L.build(self.plan(), Path(td), memory={
                    "code_base": code, "math_io": io, "zp_base": zp})
                chosen = {op["api"]: op["variant"] for op in man["operations"]}
                self.assertEqual(chosen, {"MATH_SDIV32_16": FAST,
                                          "MATH_SMOD32_16": FAST})
                self.assertEqual(len(man["link_order"]), 1)
                resources = man["resource_use"]
                self.assertEqual(resources["main_ram_total_bytes"], FAST_RAM)
                self.assertEqual(resources["zero_page_bytes"], 12)
                self.assertEqual(resources["private_ram_scratch_bytes"], 0)
                entries = {op["api"]: int(op["entry"][1:], 16)
                           for op in man["operations"]}
                self.assertEqual(len(set(entries.values())), 1)
                prg = (Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(prg[:2], code.to_bytes(2, "little"))
                self.assertEqual(len(prg), 2 + 2880)
                mem = bytearray(65536)
                mem[code:code+2880] = prg[2:]
                before = bytes(mem[code:code+2880])
                cpu = CPU(mem)
                sp = cpu.sp
                for i,(n,d) in enumerate(timing.corpus()):
                    mem[io+16:io+20] = n.to_bytes(4, "little")
                    mem[io+20:io+24] = d.to_bytes(2, "little")+b"\x7c\x6b"
                    mem[io+24:io+28] = b"\xcc"*4
                    mem[io+28:io+32] = b"\xdd\xdd\x49\x59"
                    cpu.d=0
                    cpu.c=i&1
                    cpu.call(entries["MATH_SDIV32_16" if i & 1 else "MATH_SMOD32_16"], 150000)
                    got = (int.from_bytes(mem[io+24:io+28],"little"),
                           int.from_bytes(mem[io+28:io+30],"little"),cpu.c)
                    self.assertEqual(got,timing.reference(n,d),(code,n,d))
                    self.assertEqual(bytes(mem[io+16:io+20]),n.to_bytes(4,"little"))
                    self.assertEqual(bytes(mem[io+20:io+24]),d.to_bytes(2,"little")+b"\x7c\x6b")
                    self.assertEqual(bytes(mem[io+30:io+32]),b"\x49\x59")
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+2880]),before)

    def test_zero_zp_compact_fallback_and_impossible_pins(self):
        with tempfile.TemporaryDirectory() as td:
            out = L.build(self.plan(zp=0, ram=295), Path(td))
            self.assertEqual({op["variant"] for op in out["operations"]}, {COMPACT})
            self.assertEqual(out["resource_use"]["main_ram_total_bytes"], 295)
            self.assertEqual(out["resource_use"]["zero_page_bytes"], 0)
            with self.assertRaises(L.LinkError):
                L.build(self.plan(zp=0, pins={api: FAST for api in APIS}),
                        Path(td) / "nozp")
            with self.assertRaises(L.LinkError):
                L.build(self.plan(ram=2911,pins={api:FAST for api in APIS}),
                        Path(td) / "noram")


if __name__ == "__main__":
    unittest.main()
