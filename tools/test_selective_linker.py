#!/usr/bin/env python3
"""CPU-level and resource-contract tests for truly selective 16-bit builds."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder as selector
import selective_linker as linker
from mini6502 import CPU

EDGES = (0, 1, 2, 3, 7, 15, 16, 127, 255, 256, 257, 511,
         1023, 32767, 32768, 32769, 65534, 65535)


def pairs():
    rng = random.Random(0xC64B16)
    result = [(n, d) for n in EDGES for d in EDGES]
    result.extend((rng.randrange(65536), rng.randrange(65536)) for _ in range(500))
    result.extend((rng.randrange(65536), 0) for _ in range(25))
    return result


class SelectiveLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = selector.operation_index()

    def plan(self, ops, **kw):
        return selector.create_plan(self.index, ops, **kw)

    def run_cases(self, manifest, folder):
        prg = (folder / "math_selective.prg").read_bytes()
        start = prg[0] | (prg[1] << 8)
        image = prg[2:]
        size = manifest["resource_use"]["code_and_tables_bytes"]
        self.assertEqual(len(image), size)
        self.assertEqual(start, int(manifest["memory_map"]["code_start"][1:], 16))
        self.assertEqual(hashlib.sha256(prg).hexdigest(), manifest["prg_sha256"])
        exports = (folder / "math_api.inc").read_text()
        self.assertNotIn("MATH_UMUL16 =", exports)
        cpu = CPU(bytearray(65536))
        cpu.d = 0
        cpu.mem[start:start+len(image)] = image
        io = int(manifest["memory_map"]["math_io_start"][1:], 16)
        entries = [(entry["api"], int(entry["entry"][1:], 16))
                   for entry in manifest["operations"]]
        before = bytes(cpu.mem[start:start+len(image)])
        original_sp = cpu.sp
        for i, (n, d) in enumerate(pairs()):
            for api, entry in entries:
                cpu.mem[io+16:io+18] = n.to_bytes(2, "little")
                cpu.mem[io+20:io+22] = d.to_bytes(2, "little")
                cpu.mem[io+24:io+26] = b"\x55\x55"
                cpu.mem[io+28:io+30] = b"\x66\x66"
                cpu.c = i & 1
                cpu.call(entry, 2_000_000)
                q = int.from_bytes(cpu.mem[io+24:io+26], "little")
                r = int.from_bytes(cpu.mem[io+28:io+30], "little")
                self.assertEqual(cpu.c, int(d == 0), (api, n, d, "carry"))
                self.assertEqual(r, n % d if d else 0, (api, n, d, "R"))
                self.assertEqual(q, (n // d if d else 0)
                                 if api == "MATH_UDIV16" else 0x5555,
                                 (api, n, d, "Q"))
                self.assertEqual(int.from_bytes(cpu.mem[io+16:io+18], "little"), n)
                self.assertEqual(int.from_bytes(cpu.mem[io+20:io+22], "little"), d)
                self.assertEqual(cpu.sp, original_sp)
        self.assertEqual(bytes(cpu.mem[start:start+len(image)]), before)
        return len(entries) * len(pairs())

    def test_div16_and_mod16_mixed_relocatable(self):
        total = 0
        for base, io, zp in ((0x8000, 0xc000, 0x50),
                             (0x7123, 0xc040, 0x60),
                             (0x830f, 0xc080, 0x70)):
            with self.subTest(base=base), tempfile.TemporaryDirectory() as d:
                path = Path(d)
                plan = self.plan(["UDIV16", "UMOD16"], zp_budget=2,
                                 ram_budget=1000)
                manifest = linker.build(
                    plan, path, memory={
                        "code_base": base, "math_io": io, "zp_base": zp})
                self.assertEqual(manifest["resource_use"]["code_and_tables_bytes"], 585)
                self.assertEqual(manifest["resource_use"]["zero_page_bytes"], 2)
                self.assertEqual([x["api"] for x in manifest["operations"]],
                                 ["MATH_UDIV16", "MATH_UMOD16"])
                total += self.run_cases(manifest, path)
                second = linker.build(
                    plan, path, memory={
                        "code_base": base, "math_io": io, "zp_base": zp})
                self.assertEqual(second["prg_sha256"], manifest["prg_sha256"])
        self.assertGreaterEqual(total, 5000)

    def test_mod16_zero_zp_alternative(self):
        for base in (0x8000, 0x7123):
            with self.subTest(base=base), tempfile.TemporaryDirectory() as d:
                plan = self.plan(["UMOD16"], objective="zp", zp_budget=0,
                                 ram_budget=1100,
                                 pins={"UMOD16": "link:direct-zerozp"})
                man = linker.build(
                    plan, Path(d), memory={"code_base": base, "math_io": 0xc000})
                self.assertEqual(man["resource_use"]["zero_page_bytes"], 0)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"], 2)
                self.assertEqual(man["resource_use"]["code_and_tables_bytes"], 976)
                self.run_cases(man, Path(d))

    def test_32bit_divmod_compact_and_zerozp(self):
        edge = (0, 1, 2, 3, 7, 255, 256, 65535, 65536,
                0x7fffffff, 0x80000000, 0xffffffff)
        rng = random.Random(0x32C64)
        operands = [(n, d) for n in edge for d in edge]
        operands += [(rng.getrandbits(32), rng.getrandbits(32))
                     for _ in range(192)]
        operands += [(rng.getrandbits(32), 0) for _ in range(16)]
        for origin, io in ((0x8000, 0xc000), (0x7123, 0xc040)):
            for zp_budget, variant in ((4, "link:zptail"),
                                       (0, "link:aligned-zerozp")):
                with self.subTest(origin=origin, zp_budget=zp_budget):
                    with tempfile.TemporaryDirectory() as d:
                        plan = self.plan(
                            ["UDIV32_32", "UMOD32_32"],
                            zp_budget=zp_budget, ram_budget=1200,
                            pins={"UDIV32_32": variant})
                        man = linker.build(
                            plan, Path(d),
                            memory={"code_base": origin, "math_io": io})
                        exp_size = 1040 if zp_budget == 4 else 1072
                        self.assertEqual(man["resource_use"]["code_and_tables_bytes"],
                                         exp_size)
                        self.assertEqual(man["resource_use"]["zero_page_bytes"],
                                         zp_budget)
                        self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"], 4)
                        prg = (Path(d) / "math_selective.prg").read_bytes()
                        self.assertEqual(len(prg), exp_size + 2)
                        mem = bytearray(65536)
                        mem[origin:origin+exp_size] = prg[2:]
                        cpu = CPU(mem)
                        code_before = bytes(mem[origin:origin+exp_size])
                        initial_sp = cpu.sp
                        for n, dv in operands:
                            for op in man["operations"]:
                                mem[io+16:io+20] = n.to_bytes(4, "little")
                                mem[io+20:io+24] = dv.to_bytes(4, "little")
                                mem[io+24:io+28] = b"\x55" * 4
                                mem[io+28:io+32] = b"\x66" * 4
                                cpu.d = 0
                                cpu.call(int(op["entry"][1:], 16), 2_000_000)
                                q = int.from_bytes(mem[io+24:io+28], "little")
                                rem = int.from_bytes(mem[io+28:io+32], "little")
                                self.assertEqual(cpu.c, int(dv == 0))
                                self.assertEqual(rem, n % dv if dv else 0,
                                                 (origin, op["api"], n, dv))
                                expect_q = (n // dv if dv else 0) if op["api"] == "MATH_UDIV32_32" else 0x55555555
                                self.assertEqual(q, expect_q, (origin, op["api"], n, dv))
                                self.assertEqual(mem[io+16:io+20], n.to_bytes(4, "little"))
                                self.assertEqual(mem[io+20:io+24], dv.to_bytes(4, "little"))
                                self.assertEqual(cpu.sp, initial_sp)
                        self.assertEqual(bytes(mem[origin:origin+exp_size]), code_before)

    def test_global_variant_selection_beats_local_choices(self):
        # UDIV16 needs 2 ZP bytes. The smaller UDIV32 donor needs 4, but
        # switching only UDIV32 to its zero-ZP donor lets both coexist.
        with tempfile.TemporaryDirectory() as d:
            plan = self.plan(["UDIV16", "UDIV32_32"],
                             zp_budget=2, ram_budget=950,
                             objective="size")
            man = linker.build(plan, Path(d))
            variants = {m["api"]: m["variant"] for m in man["operations"]}
            self.assertEqual(variants["MATH_UDIV16"], "link:biased")
            self.assertEqual(variants["MATH_UDIV32_32"], "link:aligned-zerozp")
            self.assertEqual(man["resource_use"]["zero_page_bytes"], 2)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"], 935)
            # Pinning the smaller 4-ZP UDIV32 source must fail this budget.
            pinned = self.plan(["UDIV16", "UDIV32_32"], zp_budget=2,
                               pins={"UDIV32_32": "link:zptail"})
            with self.assertRaises(linker.LinkError):
                linker.build(pinned, Path(d) / "not_valid")

    def test_constraints_and_unavailable_operations(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            baseline = self.plan(["UDIV16"], zp_budget=1)
            with self.assertRaises(linker.LinkError):
                linker.build(baseline, path)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(["UMUL16"]), path)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(["UDIV16"], objective="speed"), path)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(["UDIV16"], ram_budget=300), path)
            good = self.plan(["UDIV16"])
            for bad_memory in (
                {"code_base": 0xd000},
                {"code_base": 0xa000},
                {"code_base": 0xbfff},
                {"code_base": 0x8000, "math_io": 0x8000},
                {"code_base": 0xff00},
                {"zp_base": 0xff},
                {"zp_base": 0x01},
                {"math_io": 0xd000},
            ):
                with self.subTest(memory=bad_memory), self.assertRaises(linker.LinkError):
                    linker.build(good, path, memory=bad_memory)
            self.assertFalse((path / "math_selective.prg").exists())

    def test_cli_build_compact_and_exports(self):
        with tempfile.TemporaryDirectory() as d:
            config = Path(d) / "config.json"
            config.write_text(json.dumps({
                "operations": ["UDIV16", "UMOD16"],
                "objective": "size",
                "constraints": {"max_zp_bytes": 2, "max_ram_bytes": 1000},
            }))
            call = [sys.executable, str(ROOT / "tools" / "math_builder.py"),
                    "--config", str(config), "--build",
                    "--out", str(Path(d) / "plan.json")]
            proc = subprocess.run(call, cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("Built minimal PRG", proc.stdout)
            manifest = json.loads((Path(d) / "selective_manifest.json").read_text())
            self.assertEqual(manifest["resource_use"]["main_ram_total_bytes"], 617)
            self.assertEqual(len((Path(d) / "math_selective.prg").read_bytes()), 587)
            self.assertIn("MATH_UDIV16 =", (Path(d) / "math_api.inc").read_text())
            self.assertIn("MATH_UMOD16 =", (Path(d) / "math_api.inc").read_text())


if __name__ == "__main__":
    unittest.main()
