#!/usr/bin/env python3
"""Independent source-assembled ATAN2 selective linking and mixed ABI regression.

Every signed 8x8 vector is checked at the reference map for both table
variants. Additional unaligned relocations and mixed arithmetic call sequences
verify the source/table linker rather than trusting historical resident images.
"""
from __future__ import annotations

import math
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "routines" / "atan2"))
import math_builder
import selective_linker
from mini6502 import CPU
from tables import exact_phase, phase_error, signed8


class ATAN2SelectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def make(self, variant, code_base, io, directory):
        plan = math_builder.create_plan(
            self.index, ["ATAN2_8"], objective="size",
            zp_budget=0, ram_budget=1600,
            pins={"ATAN2_8": "link:" + variant})
        result = selective_linker.build(
            plan, directory, memory={"code_base": code_base, "math_io": io})
        payload = (directory / "math_selective.prg").read_bytes()
        self.assertEqual(payload[:2], code_base.to_bytes(2, "little"))
        self.assertEqual(result["resource_use"]["zero_page_bytes"], 0)
        self.assertEqual(result["resource_use"]["private_ram_scratch_bytes"], 0)
        semantic = 606 if variant == "compact" else 1109
        self.assertEqual(result["resource_use"]["code_and_tables_bytes"], semantic)
        self.assertEqual(
            result["resource_use"]["image_span_bytes"],
            len(payload) - 2)
        self.assertEqual(
            result["resource_use"]["alignment_padding_bytes"],
            len(payload) - 2 - semantic)
        self.assertEqual(
            result["resource_use"]["main_ram_total_bytes"],
            len(payload) - 2 + 32)
        if code_base == 0x8000:
            self.assertEqual(len(payload) - 2,
                             768 if variant == "compact" else 1280)
        cpu = CPU(bytearray(65536))
        cpu.mem[code_base:code_base+len(payload)-2] = payload[2:]
        return cpu, int(result["operations"][0]["entry"][1:], 16), result

    def run_inputs(self, cpu, entry, io, cases):
        before_sp = cpu.sp
        for idx, (x, y) in enumerate(cases):
            cpu.mem[io] = x
            cpu.mem[io+4] = y
            cpu.mem[io+8] = 0xee
            cpu.c = idx & 1
            cpu.d = 0
            cpu.call(entry, 20000)
            actual = cpu.mem[io+8]
            self.assertLessEqual(
                phase_error(actual, exact_phase(signed8(x), signed8(y))),
                1, ("phase", x, y, actual))
            self.assertEqual(cpu.a, actual, (x, y, "A"))
            self.assertEqual(cpu.c, 0, (x, y, "C"))
            self.assertEqual(cpu.mem[io], x)
            self.assertEqual(cpu.mem[io+4], y)
            self.assertEqual(cpu.sp, before_sp)

    def test_both_variants_complete_signed_domain(self):
        outputs = []
        for kind in ("compact", "sum-fast"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as d:
                cpu, entry, manifest = self.make(kind, 0x8000, 0xc000, Path(d))
                image = bytes(cpu.mem[0x8000:0x8000+manifest["resource_use"]["image_span_bytes"]])
                digest = bytearray()
                for x in range(256):
                    for y in range(256):
                        cpu.mem[0xc000], cpu.mem[0xc004] = x, y
                        cpu.c = (x ^ y) & 1
                        cpu.d = 0
                        cpu.call(entry, 20000)
                        got = cpu.mem[0xc008]
                        self.assertLessEqual(
                            phase_error(got, exact_phase(signed8(x), signed8(y))),
                            1, (kind, x, y, got))
                        self.assertEqual(cpu.a, got, (kind, x, y, "A"))
                        self.assertEqual(cpu.c, 0, (kind, x, y, "C"))
                        self.assertEqual(cpu.mem[0xc000], x)
                        self.assertEqual(cpu.mem[0xc004], y)
                        self.assertEqual(cpu.sp, 0xfd)
                        digest.append(got)
                outputs.append(bytes(digest))
                self.assertEqual(
                    bytes(cpu.mem[0x8000:0x8000+len(image)]), image)
        # Published compact_opt and sum_fast kernels have identical outputs
        # on the full 65,536-vector domain.
        self.assertEqual(outputs[0], outputs[1])

    def test_unaligned_relocation_and_mixed_div16(self):
        cases = [(x,y) for x in (0,1,127,128,255)
                       for y in (0,1,127,128,255)]
        rng = random.Random(0xA7A22026)
        cases += [(rng.randrange(256), rng.randrange(256)) for _ in range(2000)]
        for kind in ("compact", "sum-fast"):
            for base, io in ((0x7123, 0xc040), (0x830f, 0xc080)):
                with self.subTest(kind=kind, base=base):
                    with tempfile.TemporaryDirectory() as d:
                        cpu, entry, man = self.make(kind, base, io, Path(d))
                        self.run_inputs(cpu, entry, io, cases)
                        plan = math_builder.create_plan(
                            self.index, ["ATAN2_8", "UDIV16"],
                            zp_budget=2, ram_budget=1900,
                            pins={"ATAN2_8": "link:" + kind})
                        man = selective_linker.build(
                            plan, Path(d),
                            memory={"code_base": base, "math_io": io})
                        prg = (Path(d) / "math_selective.prg").read_bytes()
                        cpu = CPU(bytearray(65536))
                        cpu.mem[base:base+len(prg)-2] = prg[2:]
                        addresses = {
                            item["api"]: int(item["entry"][1:], 16)
                            for item in man["operations"]
                        }
                        for i, (x,y) in enumerate(cases[:256]):
                            cpu.mem[io] = x
                            cpu.mem[io+4] = y
                            cpu.c = i & 1
                            cpu.call(addresses["MATH_ATAN2_8"], 20000)
                            got = cpu.mem[io+8]
                            self.assertLessEqual(
                                phase_error(got, exact_phase(signed8(x), signed8(y))), 1)
                            n = (x << 8) | y
                            dval = (y << 8) | x
                            cpu.mem[io+16:io+18] = n.to_bytes(2, "little")
                            cpu.mem[io+20:io+22] = dval.to_bytes(2, "little")
                            cpu.call(addresses["MATH_UDIV16"], 2000000)
                            q = int.from_bytes(cpu.mem[io+24:io+26], "little")
                            rem = int.from_bytes(cpu.mem[io+28:io+30], "little")
                            self.assertEqual((q, rem),
                                             (n//dval, n%dval) if dval else (0,0))
                            self.assertEqual(cpu.c, int(dval == 0))
                            self.assertEqual(cpu.sp, 0xfd)

    def test_table_generator_source_is_hash_locked(self):
        plan = math_builder.create_plan(
            self.index, ["ATAN2_8"], pins={"ATAN2_8": "link:compact"})
        op = plan["operations"][0]
        variant = next(v for v in op["available_source_variants"]
                       if v["id"] == "link:compact")
        self.assertIn("routines/atan2/tables.py", variant["dependency_sha256"])
        math_builder.validate_sha(ROOT, variant)
        with tempfile.TemporaryDirectory() as d:
            variant["dependency_sha256"]["routines/atan2/tables.py"] = "0" * 64
            with self.assertRaises(math_builder.SelectionError):
                math_builder.validate_sha(ROOT, variant)
            with self.assertRaisesRegex(
                    selective_linker.LinkError, "source dependency changed"):
                selective_linker.build(plan, Path(d))
            self.assertFalse((Path(d) / "math_selective.prg").exists())

    def test_pins_and_budget_alignment_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            plan = math_builder.create_plan(self.index, ["ATAN2_8"], zp_budget=0,
                                             ram_budget=650,
                                             pins={"ATAN2_8": "link:compact"})
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(plan, Path(d))
            plan2 = math_builder.create_plan(self.index, ["ATAN2_8"], zp_budget=0,
                                              ram_budget=800, objective="size")
            man = selective_linker.build(plan2, Path(d))
            self.assertEqual(man["operations"][0]["variant"], "link:compact")
            self.assertEqual(man["resource_use"]["image_span_bytes"], 768)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"], 800)
            self.assertEqual(man["resource_use"]["alignment_padding_bytes"], 162)


if __name__ == "__main__":
    unittest.main()
