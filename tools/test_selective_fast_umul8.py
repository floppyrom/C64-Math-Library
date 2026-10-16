#!/usr/bin/env python3
"""CPU and layout qualification for source-linked quarter-square UMUL8.

The 511-entry Q(n) planes are generated from arithmetic, not copied from
resident binaries. Full 8-bit domain plus RAM, ABI and source provenance checks.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_fast_umul8 as fast8
import selective_linker
from mini6502 import CPU

VARIANT = "link:quarter-square"


class FastUMUL8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, names=None, **kwargs):
        return math_builder.create_plan(
            self.index, names or ["UMUL8"],
            pins={"UMUL8": VARIANT},
            **kwargs)

    def test_quartersquare_math_exact_full_domain(self):
        low, high = fast8.tables()
        self.assertEqual(len(low), 511)
        self.assertEqual(len(high), 511)
        q = lambda n: low[n] | high[n] << 8
        for x in range(256):
            for y in range(256):
                self.assertEqual(q(x+y)-q(abs(x-y)), x*y, (x,y))

    def test_source_built_binary_full_domain_and_relocation(self):
        for base, io in ((0x8000, 0xC000), (0x7123, 0xC040)):
            with self.subTest(base=base), tempfile.TemporaryDirectory() as d:
                plan = self.plan(zp_budget=0, ram_budget=1129)
                manifest = selective_linker.build(
                    plan, Path(d), memory={"code_base": base, "math_io": io})
                res = manifest["resource_use"]
                self.assertEqual(res["code_and_tables_bytes"], 1095)
                self.assertEqual(res["image_span_bytes"], 1095)
                self.assertEqual(res["alignment_padding_bytes"], 0)
                self.assertEqual(res["private_ram_scratch_bytes"], 2)
                self.assertEqual(res["zero_page_bytes"], 0)
                self.assertEqual(res["main_ram_total_bytes"], 1129)
                self.assertEqual(manifest["operations"][0]["variant"], VARIANT)
                dep = manifest["operations"][0]["dependencies"]
                self.assertEqual([p["source_path"] for p in dep],
                                 ["tools/selective_fast_umul8.py"])
                img = (Path(d) / "math_selective.prg").read_bytes()
                self.assertEqual(len(img), 1097)
                self.assertEqual(img[:2], base.to_bytes(2,"little"))
                self.assertEqual(hashlib.sha256(img).hexdigest(),
                                 manifest["prg_sha256"])
                mem = bytearray(65536)
                mem[base:base+1095] = img[2:]
                cpu = CPU(mem)
                before = bytes(mem[base:base+1095])
                sp = cpu.sp
                entry = int(manifest["operations"][0]["entry"][1:], 16)
                for x in range(256):
                    for y in range(256):
                        mem[io] = x
                        mem[io+4] = y
                        mem[io+8:io+10] = b"\x55\x55"
                        cpu.d = 0
                        cpu.c = (x^y)&1
                        cpu.call(entry, 30000)
                        actual = mem[io+8] | (mem[io+9]<<8)
                        self.assertEqual(actual, x*y,(base,x,y))
                        self.assertEqual(cpu.c, 0,(base,x,y,"C"))
                        self.assertEqual(mem[io], x)
                        self.assertEqual(mem[io+4], y)
                        self.assertEqual(cpu.sp, sp)
                self.assertEqual(bytes(mem[base:base+1095]), before)

    def test_fixed_same_corpus_cycles_faster_than_compact(self):
        rng = random.Random(0xC64F8)
        inputs = [(x,y) for x in (0,1,2,15,127,128,255)
                  for y in (0,1,2,15,127,128,255)]
        inputs += [(rng.randrange(256),rng.randrange(256)) for _ in range(1024)]
        means = {}
        for variant in ("link:compact-zerozp", VARIANT):
            with tempfile.TemporaryDirectory() as d:
                plan = math_builder.create_plan(
                    self.index,["UMUL8"], pins={"UMUL8": variant},
                    zp_budget=0, ram_budget=1300)
                man = selective_linker.build(plan,Path(d))
                prg = (Path(d)/"math_selective.prg").read_bytes()
                cpu = CPU(bytearray(65536))
                cpu.mem[0x8000:0x8000+len(prg)-2]=prg[2:]
                entry=int(man["operations"][0]["entry"][1:],16)
                total=0
                for x,y in inputs:
                    cpu.mem[0xc000]=x
                    cpu.mem[0xc004]=y
                    cpu.c = (x+y)&1
                    cpu.d=0
                    total += cpu.call(entry,30000)
                    self.assertEqual(cpu.mem[0xc008] | cpu.mem[0xc009]<<8,x*y)
                means[variant] = total/len(inputs)
        self.assertLess(means[VARIANT], means["link:compact-zerozp"])

    def test_small_budget_rejects_fast_and_auto_stays_compact(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)
            rejected=self.plan(zp_budget=0,ram_budget=1128)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(rejected,path)
            self.assertFalse(list(path.glob("*.prg")))
            selected=math_builder.create_plan(self.index,["UMUL8"],
                                               objective="size",ram_budget=1200,
                                               zp_budget=0)
            result=selective_linker.build(selected,path)
            self.assertEqual(result["operations"][0]["variant"],
                             "link:compact-zerozp")
            self.assertEqual(result["resource_use"]["main_ram_total_bytes"],95)

    def test_table_emitter_source_hash_locked(self):
        plan=self.plan()
        variant=next(v for v in plan["operations"][0]["available_source_variants"]
                     if v["id"]==VARIANT)
        self.assertIn("tools/selective_fast_umul8.py",
                      variant["dependency_sha256"])
        math_builder.validate_sha(ROOT,variant)
        variant["dependency_sha256"]["tools/selective_fast_umul8.py"]="0"*64
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(selective_linker.LinkError,
                                        "source dependency changed"):
                selective_linker.build(plan,Path(d))
            self.assertFalse(list(Path(d).glob("*.prg")))


if __name__=="__main__":
    unittest.main()
