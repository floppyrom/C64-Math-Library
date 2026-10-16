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

    def test_four_operations_interleaved_share_scratch_safely(self):
        api = ["UDIV16", "UMOD16", "UDIV32_32", "UMOD32_32"]
        with tempfile.TemporaryDirectory() as d:
            plan = self.plan(api, objective="balanced",
                             zp_budget=4, ram_budget=1800)
            man = linker.build(plan, Path(d))
            self.assertEqual(man["resource_use"]["code_and_tables_bytes"], 1625)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"], 1661)
            self.assertEqual(man["resource_use"]["zero_page_bytes"], 4)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"], 4)
            prg = (Path(d) / "math_selective.prg").read_bytes()
            mem = bytearray(65536)
            mem[0x8000:0x8000+len(prg)-2] = prg[2:]
            cpu = CPU(mem)
            stack_start = cpu.sp
            image_before = bytes(mem[0x8000:0x8000+len(prg)-2])
            entry = {x["api"]: int(x["entry"][1:], 16)
                     for x in man["operations"]}
            rng = random.Random(0x16C6432)
            chosen = list(entry)
            for i in range(256):
                rng.shuffle(chosen)
                n_full = rng.getrandbits(32)
                d_full = rng.choice((0, 1, 2, 7, 255, 256,
                                     0xffff, rng.getrandbits(32)))
                for op in chosen:
                    width = 2 if op.endswith("16") and not op.endswith("_32") else 4
                    mask = (1 << (width * 8)) - 1
                    n, dv = n_full & mask, d_full & mask
                    mem[0xc010:0xc014] = (n_full & 0xffffffff).to_bytes(4, "little")
                    mem[0xc014:0xc018] = (d_full & 0xffffffff).to_bytes(4, "little")
                    input_n, input_d = bytes(mem[0xc010:0xc014]), bytes(mem[0xc014:0xc018])
                    mem[0xc018:0xc01c] = b"\x55" * 4
                    mem[0xc01c:0xc020] = b"\x66" * 4
                    cpu.d = 0
                    cpu.call(entry[op], 2_000_000)
                    q = int.from_bytes(mem[0xc018:0xc018+width], "little")
                    rem = int.from_bytes(mem[0xc01c:0xc01c+width], "little")
                    expect_q = 0x5555 if width == 2 else 0x55555555
                    if "UDIV" in op:
                        expect_q = n // dv if dv else 0
                    self.assertEqual(q, expect_q, (i, op, n, dv))
                    self.assertEqual(rem, n % dv if dv else 0, (i, op, n, dv))
                    self.assertEqual(cpu.c, int(dv == 0))
                    self.assertEqual(bytes(mem[0xc010:0xc014]), input_n)
                    self.assertEqual(bytes(mem[0xc014:0xc018]), input_d)
                    self.assertEqual(cpu.sp, stack_start)
            self.assertEqual(bytes(mem[0x8000:0x8000+len(prg)-2]), image_before)

    def test_resource_pareto_prunes_only_automatic_variants(self):
        # Compact and sum-fast ATAN2 have different table-page geometry:
        # neither may be pruned until equivalence is proved. Global
        # resource scoring still picks compact under the size objective.
        variants = linker.MODULES["MATH_ATAN2_8"]
        frontier = linker.pareto_resource_variants(variants)
        self.assertEqual(set(frontier), {"link:compact", "link:sum-fast"})
        for code in (0x8000, 0x7123):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as d:
                auto = self.plan(["ATAN2_8"], objective="size",
                                 zp_budget=0, ram_budget=1600)
                result = linker.build(
                    auto, Path(d), memory={"code_base": code})
                self.assertEqual(result["operations"][0]["variant"], "link:compact")
                pinned = self.plan(
                    ["ATAN2_8"], zp_budget=0, ram_budget=1600,
                    pins={"ATAN2_8": "link:sum-fast"})
                fast = linker.build(
                    pinned, Path(d), memory={"code_base": code})
                self.assertEqual(fast["operations"][0]["variant"], "link:sum-fast")
        def record(size, scratch, zp):
            return {"segments": (("KERNEL_CODE", size),),
                    "scratch": scratch, "zp": zp}
        records = {"a": record(100, 3, 0),
                   "b": record(110, 4, 0),
                   "c": record(80, 6, 2),
                   "d": record(140, 0, 0),
                   "e": record(100, 3, 0)}
        # b is dominated by a; e is equal but tie-broken by stable ID.
        self.assertEqual(set(linker.pareto_resource_variants(records)),
                         {"a", "c", "d"})
        # A lower raw-footprint candidate with a different alignment
        # constraint must not suppress a larger but potentially better
        # placed alternative.
        synthetic = {
            "plain": {"segments": (("KERNEL_CODE", 300),),
                      "scratch": 0, "zp": 0},
            "paged": {"segments": (("KERNEL_CODE", 90), ("T1", 256)),
                      "scratch": 0, "zp": 0, "atan2": "compact"},
        }
        self.assertEqual(set(linker.pareto_resource_variants(synthetic)),
                         {"plain", "paged"})

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
                linker.build(self.plan(["SMUL24"]), path)
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

    def test_user_reservations_are_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            plan = self.plan(["UDIV16", "UMOD16"], zp_budget=2)
            out = Path(temp)
            good = linker.build(plan, out, memory={
                "reserved": [{"name": "loader", "start": "$2000", "end": "$2fff"}],
                "zp_reserved": [{"name": "irq", "start": "$02", "end": "$4f"}],
            })
            self.assertEqual(good["memory_map"]["user_reserved"][0]["name"], "loader")
            self.assertEqual(good["memory_map"]["user_zp_reserved"][0]["name"], "irq")
            for overrides in (
                {"reserved": [{"start": "$8000", "end": "$80ff"}]},
                {"reserved": [{"start": "$c000", "end": "$c010"}]},
                {"zp_reserved": [{"start": "$50", "end": "$60"}]},
                {"reserved": [{"start": "$ffff", "end": "$fff0"}]},
                {"reserved": "8000-8100"},
                {"zp_reserved": [{"start": "$00", "end": "$0100"}]},
                {"math_oi": "$c000"},
            ):
                with self.subTest(overrides=overrides):
                    with self.assertRaises(linker.LinkError):
                        linker.build(plan, out / "invalid", memory=overrides)
            self.assertFalse((out / "invalid" / "math_selective.prg").exists())

    def test_source_hash_lock_rejects_stale_plan(self):
        with tempfile.TemporaryDirectory() as d:
            plan = self.plan(["UDIV16"])
            chosen = next(v for v in plan["operations"][0]["available_source_variants"]
                          if v["id"] == "link:biased")
            chosen["source_sha256"] = "0" * 64
            with self.assertRaisesRegex(linker.LinkError, "source changed"):
                linker.build(plan, Path(d))
            self.assertFalse((Path(d) / "math_selective.prg").exists())

    def test_staged_build_failure_does_not_publish_partial_outputs(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            plan = self.plan(["UMUL8"], zp_budget=0, ram_budget=95)
            linker.build(plan, out)
            names = ("math_selective.prg", "math_api.inc",
                     "selective_manifest.json")
            before = {name: (out / name).read_bytes() for name in names}
            original_write_text = Path.write_text

            def fail_on_staged_include(path, *args, **kwargs):
                if path.name == "math_api.inc" and ".math_stage_" in str(path):
                    raise OSError("simulated staged include write failure")
                return original_write_text(path, *args, **kwargs)

            with patch.object(Path, "write_text", fail_on_staged_include):
                with self.assertRaisesRegex(OSError, "simulated staged"):
                    linker.build(plan, out, memory={"code_base": 0x7123})
            self.assertEqual(
                {name: (out / name).read_bytes() for name in names}, before)
            self.assertFalse(list(out.glob(".math_stage_*")))

    def test_build_manifest_seals_complete_toolchain(self):
        with tempfile.TemporaryDirectory() as d:
            plan = self.plan(["UMUL8", "UDIV16"], zp_budget=2,
                             ram_budget=600)
            man = linker.build(plan, Path(d))
            files = ("tools/math_builder.py", "tools/selective_linker.py",
                     "tools/selective_atan2.py", "tools/selective_fast_umul8.py",
                     "tools/selective_speed.py", "tools/selective_isqrt16.py",
                     "tools/selective_trig8.py",
                     "tools/mini6502.py")
            self.assertEqual(set(man["toolchain_sha256"]), set(files))
            for name in files:
                expected = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                self.assertEqual(man["toolchain_sha256"][name], expected)
            saved = json.loads((Path(d) / "selective_manifest.json").read_text())
            self.assertEqual(saved["toolchain_sha256"], man["toolchain_sha256"])

    def test_exact_measure_preview_leaves_no_files(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "math_builder.py"),
                 "--operation", "UDIV16", "--operation", "UMOD16",
                 "--zp-budget", "2", "--ram-budget", "1000",
                 "--measure", "--out", str(target / "not_written.json")],
                cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["resource_use"]["code_and_tables_bytes"], 585)
            self.assertEqual(data["resource_use"]["main_ram_total_bytes"], 617)
            self.assertFalse(list(target.iterdir()))

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
            self.assertIn("div_u16_u16_u16_16 = MATH_UDIV16", (Path(d) / "math_api.inc").read_text())
            self.assertIn("mod_u16_u16_u16 = MATH_UMOD16", (Path(d) / "math_api.inc").read_text())


if __name__ == "__main__":
    unittest.main()
