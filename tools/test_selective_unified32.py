#!/usr/bin/env python3
"""Six 32-bit multiply API entries from one shared 375-byte source image."""
from __future__ import annotations
import random
import tempfile
import unittest
from pathlib import Path
import math_builder
import selective_linker as linker
from mini6502 import CPU

OPS = ("UMUL32", "UMUL32_READY", "UMUL32_SHR16", "SMUL32", "SMUL32_READY", "SMUL32_SHR16")
EDGES = (0, 1, 2, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0xffffffff)

def signed(x):
    return x - (1 << 32) if x & 0x80000000 else x

def corpus():
    rng = random.Random(0x640375)
    return [(x, y) for x in EDGES for y in EDGES] + [
        (rng.getrandbits(32), rng.getrandbits(32)) for _ in range(128)]

class Unified32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, ops=OPS, budget=419, pins=None):
        return math_builder.create_plan(self.index, list(ops), objective="size",
                                        zp_budget=0, ram_budget=budget, pins=pins)

    def test_six_public_entries_and_interleavings(self):
        for code, io, sb in ((0x8000, 0xc000, 0xc020),
                             (0x7123, 0xc040, 0xc080)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as td:
                man = linker.build(self.plan(), Path(td), memory={
                    "code_base":code, "math_io":io, "scratch_base":sb})
                use = man["resource_use"]
                self.assertEqual((use["image_span_bytes"],
                                  use["main_ram_total_bytes"],
                                  use["zero_page_bytes"],
                                  use["private_ram_scratch_bytes"]), (375,419,0,12))
                self.assertEqual(len(man["link_order"]), 1)
                self.assertEqual({v["variant"] for v in man["operations"]},
                                 {"link:unified-375"})
                ep = {a["api"].removeprefix("MATH_"): int(a["entry"][1:],16)
                      for a in man["operations"]}
                self.assertEqual(ep["UMUL32"], ep["UMUL32_READY"])
                self.assertEqual(ep["SMUL32"], ep["SMUL32_READY"])
                self.assertEqual([ep[x]-code for x in
                                  ("UMUL32", "SMUL32", "SMUL32_SHR16", "UMUL32_SHR16")],
                                 [0, 204, 293, 334])
                image = (Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(image), 377)
                mem = bytearray(65536)
                mem[code:code+375] = image[2:]
                original = bytes(mem[code:code+375])
                cpu = CPU(mem)
                sp = cpu.sp
                for i,(x,y) in enumerate(corpus()):
                    xb,yb = x.to_bytes(4,"little"),y.to_bytes(4,"little")
                    for api in OPS:
                        mem[io:io+4] = xb
                        mem[io+4:io+8] = yb
                        mem[io+8:io+16] = b"\xa5"*8
                        cpu.d = 0
                        cpu.c = (x^y^i)&1
                        cpu.call(ep[api], 125000)
                        product = ((signed(x)*signed(y)) if api.startswith("SMUL")
                                   else x*y)&((1<<64)-1)
                        expected = (product >> 16) if api.endswith("SHR16") else product
                        width = 6 if api.endswith("SHR16") else 8
                        self.assertEqual(int.from_bytes(mem[io+8:io+8+width],"little"),expected,
                                         (api,x,y))
                        self.assertEqual(cpu.c, 0, api)
                        self.assertEqual(cpu.sp, sp, api)
                        self.assertEqual((bytes(mem[io:io+4]),bytes(mem[io+4:io+8])),
                                         (xb,yb),api)
                self.assertEqual(bytes(mem[code:code+375]),original)

    def test_standalone_and_pinned_backward_compatibility(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(budget=418),Path(td)/"too_small")
            single = linker.build(self.plan(("UMUL32",),budget=248),Path(td)/"single")
            self.assertEqual(single["operations"][0]["variant"],"link:compact-zerozp")
            self.assertEqual(single["resource_use"]["main_ram_total_bytes"],248)
            legacy = linker.build(self.plan(budget=1120,pins={x:"link:compact-zerozp"
                                             for x in OPS}),Path(td)/"legacy")
            self.assertEqual(legacy["resource_use"]["image_span_bytes"],1076)
            self.assertEqual(legacy["resource_use"]["main_ram_total_bytes"],1120)

if __name__ == "__main__":
    unittest.main()
