#!/usr/bin/env python3
"""Native-source equivalent CPU-model proof for shifted quarter-square multiply."""
from __future__ import annotations
import hashlib
import random
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU

EDGES = (0, 1, 2, 3, 7, 15, 16, 127, 128, 255, 256, 257,
         511, 1023, 32767, 32768, 32769, 65534, 65535)

class QuarterSquareShift16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def test_full_width_relocations_and_source_provenance(self):
        rng = random.Random(0x16F8C64)
        cases = [(x,y) for x in EDGES for y in EDGES]
        cases += [(rng.getrandbits(16), rng.getrandbits(16))
                  for _ in range(1600)]
        for code, io, scratch in ((0x8000, 0xc000, 0xc020),
                                  (0x7123, 0xc040, 0xc080),
                                  (0x830f, 0xc100, 0xc140)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as tmp:
                plan = math_builder.create_plan(
                    self.index, ["UMUL16_SHR8"], objective="size",
                    zp_budget=0, ram_budget=1314,
                    pins={"UMUL16_SHR8":"link:quarter-square"})
                manifest = selective_linker.build(
                    plan, Path(tmp), memory={
                        "code_base":code, "math_io":io,"scratch_base":scratch})
                use = manifest["resource_use"]
                self.assertEqual(use["image_span_bytes"], 1278)
                self.assertEqual(use["zero_page_bytes"], 0)
                self.assertEqual(use["private_ram_scratch_bytes"], 4)
                self.assertEqual(use["main_ram_total_bytes"], 1314)
                deps = {x["source_path"]:x["sha256"] for x in
                        manifest["operations"][0]["dependencies"]}
                self.assertEqual(set(deps),
                                 {"tools/selective_fast_umul8.py",
                                  "tools/selective_fast_umul16.py"})
                for name, expected in deps.items():
                    self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),
                                     expected)
                prg = (Path(tmp)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg), 1280)
                self.assertEqual(prg[:2], code.to_bytes(2,"little"))
                mem = bytearray(65536)
                mem[code:code+1278] = prg[2:]
                cpu = CPU(mem)
                start = bytes(mem[code:code+1278])
                entry = int(manifest["operations"][0]["entry"][1:], 16)
                self.assertEqual(entry,code+233)
                sp = cpu.sp
                for x,y in cases:
                    mem[io:io+2] = x.to_bytes(2,"little")
                    mem[io+4:io+6] = y.to_bytes(2,"little")
                    mem[io+8:io+12] = bytes([0xA5])*4
                    cpu.d = 0
                    cpu.c = (x^y)&1
                    cpu.call(entry, 50000)
                    self.assertEqual(int.from_bytes(mem[io+8:io+11],"little"),
                                     (x*y)>>8,(code,x,y))
                    self.assertEqual(bytes(mem[io:io+2]),x.to_bytes(2,"little"))
                    self.assertEqual(bytes(mem[io+4:io+6]),y.to_bytes(2,"little"))
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+1278]),start)

    def test_budget_fails_closed_and_compact_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            def plan(limit, pin=None):
                return math_builder.create_plan(
                    self.index,["UMUL16_SHR8"],objective="size",
                    zp_budget=0,ram_budget=limit,
                    pins={"UMUL16_SHR8":pin} if pin else None)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(
                    plan(1313, "link:quarter-square"),Path(tmp)/"reject")
            compact = selective_linker.build(plan(164),Path(tmp)/"compact")
            self.assertEqual(compact["operations"][0]["variant"],
                             "link:compact-zerozp")
            self.assertEqual(compact["resource_use"]["main_ram_total_bytes"],164)

if __name__ == "__main__":
    unittest.main()
