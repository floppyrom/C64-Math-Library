#!/usr/bin/env python3
"""Source-linked UMUL16 quarter-square qualification on real compiled bytecode."""
from __future__ import annotations

import hashlib
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
import selective_fast_umul16 as fast16
import selective_fast_umul8 as fast8
from mini6502 import CPU

EDGE = (0, 1, 2, 3, 7, 15, 16, 127, 128, 255, 256,
        257, 511, 1023, 32767, 32768, 32769, 65534, 65535)


class QuarterSquareUMUL16(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, operations, *, zp=0, ram=1800, variant="link:quarter-square"):
        pins = {"UMUL16": variant} if "UMUL16" in operations else {}
        return math_builder.create_plan(
            self.index, operations, objective="size",
            zp_budget=zp, ram_budget=ram, pins=pins)

    def test_table_algebra_and_geometry(self):
        low, high = fast8.tables()
        self.assertEqual((len(low), len(high)), (511, 511))
        square = [low[n] | (high[n] << 8) for n in range(511)]
        self.assertEqual(square, [n*n//4 for n in range(511)])
        rng = random.Random(0xC641624)
        for _ in range(10000):
            a, b = rng.randrange(256), rng.randrange(256)
            self.assertEqual(square[a+b]-square[abs(a-b)], a*b)
        for origin in (0x8000, 0x7123):
            layout, end = fast16.layout(origin)
            self.assertEqual(end-origin, 1255)
            self.assertEqual(layout["Q_HI"]-layout["Q_LO"], 511)

    def test_mixed_edges_random_relocations_and_abi(self):
        rng = random.Random(0xC6416C64)
        inputs = [(a,b) for a in EDGE for b in EDGE]
        inputs += [(rng.getrandbits(16), rng.getrandbits(16))
                   for _ in range(5000)]
        inputs += [(0xffff, rng.getrandbits(16)) for _ in range(200)]
        for origin, io, scratch in ((0x8000, 0xc000, 0xc020),
                                    (0x7123, 0xc040, 0xc080),
                                    (0x830f, 0xc100, 0xc140)):
            with self.subTest(origin=origin), tempfile.TemporaryDirectory() as d:
                plan = self.plan(["UMUL16"], ram=1291)
                man = selective_linker.build(
                    plan, Path(d),
                    memory={"code_base": origin,
                            "math_io": io, "scratch_base": scratch})
                self.assertEqual(man["operations"][0]["variant"], "link:quarter-square")
                expected = {
                    "code_and_tables_bytes": 1255,
                    "image_span_bytes": 1255,
                    "shared_table_bytes": 0,
                    "alignment_padding_bytes": 0,
                    "public_io_bytes": 32,
                    "private_ram_scratch_bytes": 4,
                    "main_ram_total_bytes": 1291,
                    "zero_page_bytes": 0,
                    "persistent_stack_page_bytes": 0,
                }
                self.assertEqual(man["resource_use"], expected)
                deps = {x["source_path"]:x["sha256"]
                        for x in man["operations"][0]["dependencies"]}
                self.assertEqual(set(deps), {"tools/selective_fast_umul8.py",
                                             "tools/selective_fast_umul16.py"})
                for path, sha in deps.items():
                    self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), sha)
                payload = (Path(d)/"math_selective.prg").read_bytes()
                self.assertEqual(len(payload), 1257)
                self.assertEqual(payload[:2], origin.to_bytes(2,"little"))
                cpu = CPU(bytearray(65536))
                cpu.mem[origin:origin+1255] = payload[2:]
                baseline = bytes(cpu.mem[origin:origin+1255])
                stack = cpu.sp
                entry = int(man["operations"][0]["entry"][1:], 16)
                for x,y in inputs:
                    cpu.mem[io:io+2] = x.to_bytes(2,"little")
                    cpu.mem[io+4:io+6] = y.to_bytes(2,"little")
                    cpu.mem[io+8:io+12] = b"\xaa"*4
                    cpu.d = 0
                    cpu.c = (x+y)&1
                    cpu.call(entry, 2000)
                    z = int.from_bytes(cpu.mem[io+8:io+12],"little")
                    self.assertEqual(z,x*y,(origin,x,y))
                    self.assertEqual(cpu.c,0,(origin,x,y,"carry"))
                    self.assertEqual(cpu.sp,stack,(origin,x,y,"stack"))
                    self.assertEqual(int.from_bytes(cpu.mem[io:io+2],"little"),x)
                    self.assertEqual(int.from_bytes(cpu.mem[io+4:io+6],"little"),y)
                self.assertEqual(bytes(cpu.mem[origin:origin+1255]),baseline)

    def test_automatic_resource_tradeoff_and_expert_pin(self):
        with tempfile.TemporaryDirectory() as d:
            compact = self.plan(["UMUL16"], ram=146, variant="link:compact-zerozp")
            result = selective_linker.build(compact, Path(d))
            self.assertEqual(result["resource_use"]["main_ram_total_bytes"],146)
            forced = self.plan(["UMUL16"], ram=1291)
            result = selective_linker.build(forced, Path(d))
            self.assertEqual(result["resource_use"]["main_ram_total_bytes"],1291)
            auto = math_builder.create_plan(
                self.index, ["UMUL16"], objective="size", zp_budget=0,
                ram_budget=1300)
            result = selective_linker.build(auto, Path(d))
            self.assertEqual(result["operations"][0]["variant"], "link:compact-zerozp")
            rejected = self.plan(["UMUL16"], ram=1290)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(rejected, Path(d)/"rejected")
            self.assertFalse((Path(d)/"rejected").exists())

    def test_pair_with_umul8_qualified_images(self):
        # Both algorithms use the same numeric X/Y/Z ABI but require exclusive
        # scratch. Sequential mixed calls must not corrupt the first inputs.
        with tempfile.TemporaryDirectory() as d:
            plan = self.plan(["UMUL16","UMUL8"],ram=1450)
            man = selective_linker.build(plan,Path(d))
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],4)
            self.assertEqual(man["resource_use"]["image_span_bytes"],1315)
            payload=(Path(d)/"math_selective.prg").read_bytes()
            cpu=CPU(bytearray(65536))
            cpu.mem[0x8000:0x8000+len(payload)-2]=payload[2:]
            entries={x["api"]:int(x["entry"][1:],16) for x in man["operations"]}
            rng=random.Random(0x16E10)
            for _ in range(1000):
                x,y=rng.randrange(65536),rng.randrange(65536)
                cpu.mem[0xc000:0xc002]=x.to_bytes(2,"little")
                cpu.mem[0xc004:0xc006]=y.to_bytes(2,"little")
                cpu.d=0
                cpu.call(entries["MATH_UMUL8"],2000)
                self.assertEqual(int.from_bytes(cpu.mem[0xc008:0xc00a],"little"),
                                 (x&255)*(y&255))
                cpu.call(entries["MATH_UMUL16"],2000)
                self.assertEqual(int.from_bytes(cpu.mem[0xc008:0xc00c],"little"),x*y)
                self.assertEqual(cpu.c,0)
                self.assertEqual(cpu.sp,0xfd)


if __name__=="__main__":
    unittest.main()
