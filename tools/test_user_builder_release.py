#!/usr/bin/env python3
"""Release acceptance of user-defined C64 Math Library configurations.

All conditions use the actual CLI to generate an editable project config and
real source-linked PRG. Every result is independently rebuilt via the normal
operation-first builder; not a fixture pretending to be an assembled binary.
No historical profile or SID/graphics/REU benchmark is involved.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WIZARD = ROOT / "tools" / "configure_math.py"
BUILDER = ROOT / "tools" / "math_builder.py"

CASES = (
    ("balanced", ("UMUL16", "UDIV16", "ISQRT16"), 8, 4096, ()),
    ("size", ("UMUL8", "UDIV16"), 0, 4096, ()),
    ("zp", ("UMUL16", "ISQRT16"), 0, 4096, ()),
    ("speed", ("UMUL8", "UMUL16"), 4, 1400,
     ("UMUL8=1000", "UMUL16=1")),
)


def execute(args):
    """A failing CLI exits with an error; never accept a partial artifact."""
    return subprocess.run([sys.executable, *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True, check=False)


def verify_output(folder, configuration, objective, requested, max_zp, max_ram):
    inc = (folder / "math_api.inc").read_text(encoding="utf-8")
    prg = (folder / "math_selective.prg").read_bytes()
    manifest = json.loads((folder / "selective_manifest.json").read_text())
    actual = {op["api"] for op in manifest["operations"]}
    expected = {"MATH_" + op for op in requested}
    if len(prg) <= 2:
        raise AssertionError("Empty generated executable image")
    if actual != expected:
        raise AssertionError(("Wrong exported operations", actual, expected))
    if manifest["target"] != "c64" or manifest["status"] != "selective_binary_emitted":
        raise AssertionError("User setup did not emit a qualified stock C64 binary")
    if manifest["selection_objective"] != objective:
        raise AssertionError("Builder changed the requested optimization goal")
    if hashlib.sha256(prg).hexdigest() != manifest["prg_sha256"]:
        raise AssertionError("Generated binary differs from manifest SHA")
    resource = manifest["resource_use"]
    if resource["zero_page_bytes"] > max_zp:
        raise AssertionError("Over budget: zero page")
    if resource["main_ram_total_bytes"] > max_ram:
        raise AssertionError("Over budget: total physical main RAM")
    if resource["main_ram_total_bytes"] < resource["code_and_tables_bytes"] + 32:
        raise AssertionError("Reported RAM forgot the public I/O")
    if not configuration["operations"] or set(configuration["operations"]) != set(requested):
        raise AssertionError("User-editable config lost an operation")
    for api in actual:
        if not re.search(r"(?m)^" + re.escape(api) + r" = \$[0-9A-F]{4}$", inc):
            raise AssertionError("Missing real assembler export: " + api)
    if objective == "speed":
        expected_calls = {"MATH_" + n: configuration["workload_calls"][n]
                          for n in requested}
        if manifest["workload_calls"] != expected_calls:
            raise AssertionError("Speed weights not preserved in physical manifest")
        if manifest["estimated_weighted_cycles"] <= 0:
            raise AssertionError("Weighted speed choice lacks measured cost")
        basis = manifest["selection_basis"].casefold()
        if "cycle" not in basis:
            raise AssertionError("Speed choice lacks cycle provenance")
    else:
        if "workload_calls" in configuration:
            raise AssertionError("Non-speed goal unexpectedly acquired speed workload")
    return manifest, prg


class ReleaseUserConfigurationAcceptance(unittest.TestCase):
    def test_all_four_objectives_produce_rebuildable_verified_binaries(self):
        for objective, ops, zp, ram, calls in CASES:
            with self.subTest(objective=objective), tempfile.TemporaryDirectory(
                prefix="c64_user_acceptance_") as temp:
                base = Path(temp)
                config_path = base / "project.json"
                generated = base / "user_image"
                args = ([WIZARD] +
                        [part for name in ops for part in ("--operation", name)] +
                        ["--objective", objective, "--zp-budget", str(zp),
                         "--ram-budget", str(ram),
                         "--config-out", str(config_path),
                         "--build-dir", str(generated)] +
                        [part for call in calls for part in ("--calls", call)])
                outcome = execute(args)
                self.assertEqual(outcome.returncode, 0, outcome.stderr)
                self.assertTrue(config_path.is_file())
                config = json.loads(config_path.read_text())
                self.assertEqual(config["objective"], objective)
                self.assertEqual(config["constraints"]["max_zp_bytes"], zp)
                self.assertEqual(config["constraints"]["max_ram_bytes"], ram)
                first, binary = verify_output(
                    generated, config, objective, ops, zp, ram)
                # The config file is a real portable input to the ORIGINAL
                # installer: rebuilding must produce byte-for-byte same PRG.
                rebuild_dir = base / "repeat"
                again = execute([BUILDER, "--config", config_path, "--build",
                                 "--out", rebuild_dir / "selection_manifest.json"])
                self.assertEqual(again.returncode, 0, again.stderr)
                self.assertEqual(
                    (rebuild_dir / "math_selective.prg").read_bytes(), binary)
                second = json.loads(
                    (rebuild_dir / "selective_manifest.json").read_text())
                self.assertEqual(
                    {o["api"]:o["variant"] for o in first["operations"]},
                    {o["api"]:o["variant"] for o in second["operations"]})
                self.assertEqual(first["resource_use"], second["resource_use"])
                self.assertEqual(first["prg_sha256"], second["prg_sha256"])
                self.assertEqual(first["memory_map"], second["memory_map"])

    def test_memory_reservations_and_pin_rebuild_identically(self):
        with tempfile.TemporaryDirectory(prefix="c64_reserved_acceptance_") as d:
            base = Path(d)
            config_path = base / "game_config.json"
            product = base / "game_math"
            reservations = {
                "code_base": "$7123", "math_io": "$C040",
                "zp_base": "$60", "scratch_base": "$C060",
                "reserved": [
                    {"name": "my_game", "start": "$8000", "end": "$9FFF"}
                ],
                "zp_reserved": [
                    {"name": "interrupt_zp", "start": "$02", "end": "$4F"}
                ]
            }
            memory_path = base / "locations.json"
            memory_path.write_text(json.dumps(reservations))
            outcome = execute([
                WIZARD,"--operation","UMUL8","--operation","UDIV16",
                "--objective","size","--zp-budget","0","--ram-budget","4096",
                "--pin","UMUL8=link:compact-zerozp",
                "--memory-config",memory_path,
                "--config-out",config_path,"--build-dir",product
            ])
            self.assertEqual(outcome.returncode,0,outcome.stderr)
            cfg=json.loads(config_path.read_text())
            self.assertEqual(cfg["pins"]["UMUL8"],"link:compact-zerozp")
            self.assertEqual(cfg["memory"],reservations)
            manifest, binary=verify_output(
                product,cfg,"size",("UMUL8","UDIV16"),0,4096)
            self.assertEqual(manifest["memory_map"]["code_start"],"$7123")
            self.assertEqual(manifest["operations"][
                next(i for i, x in enumerate(manifest["operations"])
                     if x["api"]=="MATH_UMUL8")]["variant"],
                             "link:compact-zerozp")
            self.assertEqual(binary[:2],bytes((0x23,0x71)))
            again_dir=base/"rebuild"
            again=execute([
                BUILDER, "--config",config_path,"--build","--out",
                again_dir/"selection_manifest.json"
            ])
            self.assertEqual(again.returncode,0,again.stderr)
            self.assertEqual((again_dir/"math_selective.prg").read_bytes(),binary)

    def test_conflicting_project_memory_fails_closed_without_any_file(self):
        with tempfile.TemporaryDirectory(prefix="c64_conflict_acceptance_") as d:
            base=Path(d)
            reserved=base/"conflict.json"
            reserved.write_text(json.dumps({
                "code_base":"$8000",
                "reserved":[{"name":"user_code","start":"$8000","end":"$8FFF"}],
            }))
            config_path=base/"should_not_exist.json"
            build_dir=base/"should_not_exist"
            result=execute([
                WIZARD,"--operation","UMUL8","--objective","size",
                "--zp-budget","0","--ram-budget","4096",
                "--memory-config",reserved,
                "--config-out",config_path,"--build-dir",build_dir,
            ])
            self.assertNotEqual(result.returncode,0)
            self.assertIn("overlaps",result.stderr)
            self.assertFalse(config_path.exists())
            self.assertFalse(build_dir.exists())


if __name__ == "__main__":
    unittest.main()
