#!/usr/bin/env python3
"""Regression checks for the operation-first, non-linking builder phase."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "math_builder.py"
spec = importlib.util.spec_from_file_location("math_builder", SCRIPT)
assert spec and spec.loader
mb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mb)


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = mb.operation_index()

    def test_full_stable_api_indexed(self):
        self.assertEqual(len(self.index), 56)
        for api, op in self.index.items():
            self.assertTrue(api.startswith("MATH_"))
            self.assertGreaterEqual(
                sum(v["kind"] == "resident-source-mirror" for v in op["variants"]), 5
            )
            linkable = [v for v in op["variants"] if v["selective_link_ready"]]
            self.assertEqual(bool(linkable), api in {"MATH_UDIV16", "MATH_UMOD16", "MATH_UDIV32_32", "MATH_UMOD32_32", "MATH_ATAN2_8", "MATH_UMUL16"})

    def test_typed_and_short_names_resolve(self):
        self.assertEqual(mb.resolve("umul16", self.index), "MATH_UMUL16")
        self.assertEqual(mb.resolve("math_umul16", self.index), "MATH_UMUL16")
        self.assertEqual(
            mb.resolve("mul_u16_u16_u32", self.index), "MATH_UMUL16"
        )
        with self.assertRaises(mb.SelectionError):
            mb.resolve("not_a_real_operation", self.index)

    def test_compact_multiply_variant_publication(self):
        variants = self.index["MATH_UMUL16"]["variants"]
        eligible = {v["id"] for v in variants if v["selective_link_ready"]}
        self.assertEqual(eligible, {"link:compact-zerozp"})
        self.assertEqual(next(v for v in variants
                              if v["id"] == "link:compact-zerozp")
                         ["resources_reported"]["scratch_bytes"], 6)

    def test_atan2_variant_publication(self):
        variants = self.index["MATH_ATAN2_8"]["variants"]
        eligible = {v["id"] for v in variants if v["selective_link_ready"]}
        self.assertEqual(eligible, {"link:compact", "link:sum-fast"})

    def test_numbered_manual_selector(self):
        numbered = ["MATH_UDIV16", "MATH_UMOD16", "MATH_ISQRT16", "MATH_UDIV32_32"]
        picked = mb.parse_interactive_choices("1,2-3, UDIV32_32", numbered)
        self.assertEqual(
            mb.parse_operations(picked, self.index),
            sorted(numbered))
        self.assertIn("Unsigned divide", mb.operation_description("MATH_UDIV16"))
        self.assertIn("square root", mb.operation_description("MATH_ISQRT16"))
        for bad in ("0", "5", "3-2", "1-5", "0-2"):
            with self.subTest(bad=bad), self.assertRaises(mb.SelectionError):
                mb.parse_interactive_choices(bad, numbered)

    def test_selection_deduplicates_and_pins(self):
        op = "MATH_UMUL16"
        valid_id = self.index[op]["variants"][0]["id"]
        plan = mb.create_plan(
            self.index, ["umul16", "MATH_UMUL16", "isqrt16"],
            objective="speed", zp_budget=31, ram_budget=4096,
            pins={"umul16": valid_id},
        )
        self.assertEqual(plan["public_operation_count"], 2)
        self.assertEqual(plan["status"], "planning_only_not_a_loadable_binary")
        self.assertTrue(plan["unresolved_dependencies"])
        self.assertIsNone(plan["operations"][0]["chosen_linkable_variant"])
        self.assertEqual(
            next(v for v in plan["operations"] if v["api"] == op)["pinned_variant"],
            valid_id,
        )

    def test_pins_and_constraints_fail_closed(self):
        op = "MATH_UMUL16"
        for kwargs in (
            {"pins": {op: "does-not-exist"}},
            {"pins": {"MATH_ISQRT16": self.index["MATH_ISQRT16"]["variants"][0]["id"]}},
            {"zp_budget": -1},
            {"zp_budget": 255},
            {"ram_budget": -1},
            {"objective": "impossible"},
            {"target": "unknown"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(mb.SelectionError):
                mb.create_plan(self.index, [op], **kwargs)
        with self.assertRaises(mb.SelectionError):
            mb.create_plan(self.index, [])

    def test_source_hash_verification(self):
        # Every selected operation has a V1 source mirror with a published SHA.
        v = self.index["MATH_UMUL16"]["variants"][0]
        mb.validate_sha(ROOT, v)
        corrupted = dict(v, source_sha256="0" * 64)
        with self.assertRaises(mb.SelectionError):
            mb.validate_sha(ROOT, corrupted)

    def test_config_file_and_no_binary(self):
        with tempfile.TemporaryDirectory() as d:
            config = Path(d) / "pick.json"
            output = Path(d) / "plan.json"
            config.write_text(json.dumps({
                "target": "c64",
                "operations": ["MATH_ATAN2_8", "MATH_UMUL16"],
                "objective": "zp",
                "constraints": {"max_zp_bytes": 31, "max_ram_bytes": 1024},
            }))
            call = [
                sys.executable, str(SCRIPT), "--config", str(config),
                "--out", str(output),
            ]
            result = subprocess.run(call, text=True, capture_output=True, cwd=ROOT)
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(output.read_text())
            self.assertEqual(plan["public_operation_count"], 2)
            self.assertEqual(plan["objective"], "zp")
            self.assertEqual(plan["constraints"]["max_ram_bytes"], 1024)
            self.assertFalse(list(Path(d).rglob("*.prg")))
            reject = subprocess.run(call + ["--build"], text=True,
                                    capture_output=True, cwd=ROOT)
            self.assertNotEqual(reject.returncode, 0)
            self.assertIn("no qualified selective source", reject.stderr)
            self.assertFalse(list(Path(d).rglob("*.prg")))

    def test_deterministic_selection_plan(self):
        a = mb.create_plan(self.index, ["isqrt16", "umul16"])
        b = mb.create_plan(self.index, ["umul16", "isqrt16"])
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
