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

    def test_public_operations_survive_removal_of_v1_profile_metadata(self):
        # Profile migration must not make V1 an implicit schema dependency.
        from unittest.mock import patch
        original = mb.read_csv

        def without_historical_v1(path):
            records = original(path)
            if path.name == "SOURCE_CATALOG.csv":
                return [r for r in records
                        if not (r["scope"] == "shipped-profile" and
                                r["profile"] == "v1_balanced")]
            return records

        with patch.object(mb, "read_csv", side_effect=without_historical_v1):
            reduced = mb.operation_index()
        self.assertEqual(set(reduced), set(self.index))
        for api in reduced:
            self.assertEqual(reduced[api]["canonical_name"],
                             self.index[api]["canonical_name"])
            self.assertEqual(reduced[api]["category"],
                             self.index[api]["category"])
            self.assertTrue(all(v.get("historical_provenance") != "v1_balanced"
                                for v in reduced[api]["variants"]))
        self.assertIn("MATH_UMUL8", reduced)
        self.assertIn("MATH_ATAN2_8", reduced)

    def test_public_operation_catalog_is_unique(self):
        rows = mb.read_csv(ROOT / "routines" / "PUBLIC_OPERATIONS.csv")
        self.assertEqual(len(rows), 56)
        self.assertEqual(len({r["api"] for r in rows}), 56)
        self.assertEqual(len({r["canonical_name"] for r in rows}), 56)
        self.assertEqual(set(r["api"] for r in rows), set(self.index))

    def test_full_stable_api_indexed(self):
        self.assertEqual(len(self.index), 56)
        for api, op in self.index.items():
            self.assertTrue(api.startswith("MATH_"))
            self.assertGreaterEqual(
                sum(v["kind"] == "resident-source-mirror" for v in op["variants"]), 5
            )
            linkable = [v for v in op["variants"] if v["selective_link_ready"]]
            self.assertEqual(bool(linkable), api in {"MATH_UDIV16", "MATH_UMOD16", "MATH_UDIV32_32", "MATH_UMOD32_32", "MATH_ATAN2_8", "MATH_UMUL16", "MATH_UMUL8"})

    def test_typed_and_short_names_resolve(self):
        self.assertEqual(mb.resolve("umul16", self.index), "MATH_UMUL16")
        self.assertEqual(mb.resolve("math_umul16", self.index), "MATH_UMUL16")
        self.assertEqual(
            mb.resolve("mul_u16_u16_u32", self.index), "MATH_UMUL16"
        )
        with self.assertRaises(mb.SelectionError):
            mb.resolve("not_a_real_operation", self.index)

    def test_umul8_compact_source_is_linkable(self):
        variants = self.index["MATH_UMUL8"]["variants"]
        linkable = [v for v in variants if v["selective_link_ready"]]
        self.assertEqual([v["id"] for v in linkable], ["link:compact-zerozp"])
        self.assertEqual(linkable[0]["resources_reported"]["code_and_table_bytes"], 60)
        self.assertEqual(linkable[0]["resources_reported"]["scratch_bytes"], 3)

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

    def test_future_6502_targets_plan_only(self):
        for hardware in ("1541", "1571", "1581"):
            with self.subTest(hardware=hardware):
                plan = mb.create_plan(self.index, ["UMUL8", "ATAN2_8"],
                                      target=hardware, zp_budget=0,
                                      ram_budget=512)
                self.assertEqual(plan["target"], hardware)
                self.assertEqual(plan["target_backend_status"],
                                 "planning_only_no_target_backend")
                self.assertEqual(plan["linker_status"],
                                 "target_backend_unavailable")
                self.assertEqual(plan["public_operation_count"], 2)
                import selective_linker
                with tempfile.TemporaryDirectory() as workdir:
                    with self.assertRaises(selective_linker.LinkError):
                        selective_linker.build(plan, Path(workdir))
                    self.assertFalse(list(Path(workdir).iterdir()))
        available = mb.create_plan(self.index, ["UMUL8"], target="c64")
        self.assertEqual(available["linker_status"],
                         "experimental_subset_available")

    def test_plan_schema_is_hardware_neutral_and_enforced(self):
        import selective_linker
        for target in mb.TARGETS:
            plan = mb.create_plan(self.index, ["UMUL8"], target=target)
            self.assertEqual(plan["schema"], "math-selection-plan-v2")
        plan = mb.create_plan(self.index, ["UMUL8"])
        plan["schema"] = "c64-math-selection-plan-v1"
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(selective_linker.LinkError,
                                        "Unsupported selection plan schema"):
                selective_linker.build(plan, Path(d))
            self.assertFalse(list(Path(d).iterdir()))

    def test_target_specific_variant_reporting(self):
        for target, expected in (("c64", True), ("1541", False),
                                 ("1571", False), ("1581", False)):
            with self.subTest(target=target):
                inspect = subprocess.run(
                    [sys.executable, str(SCRIPT), "--variants", "UMUL8",
                     "--target", target], capture_output=True, text=True, cwd=ROOT)
                self.assertEqual(inspect.returncode, 0, inspect.stderr)
                operation = json.loads(inspect.stdout)
                self.assertEqual(operation["requested_target"], target)
                linkable = [v for v in operation["variants"]
                            if v["id"] == "link:compact-zerozp"]
                self.assertEqual(len(linkable), 1)
                self.assertEqual(linkable[0]["target_link_ready"], expected)
                listing = subprocess.run(
                    [sys.executable, str(SCRIPT), "--list-linkable",
                     "--target", target], capture_output=True, text=True, cwd=ROOT)
                self.assertEqual(listing.returncode, 0, listing.stderr)
                if expected:
                    self.assertIn("MATH_UMUL8", listing.stdout)
                else:
                    self.assertNotIn("MATH_UMUL8", listing.stdout)
                    self.assertIn("planning only", listing.stderr)

    def test_cli_future_target_refuses_binary(self):
        for target in ("1541", "1571", "1581"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as d:
                config = [sys.executable, str(SCRIPT), "--operation", "UMUL8",
                          "--target", target, "--out", str(Path(d) / "plan.json")]
                preview = subprocess.run(config + ["--preview"],
                                         text=True, capture_output=True, cwd=ROOT)
                self.assertEqual(preview.returncode, 0, preview.stderr)
                self.assertEqual(json.loads(preview.stdout)["target"], target)
                refuse = subprocess.run(config + ["--build"],
                                        text=True, capture_output=True, cwd=ROOT)
                self.assertNotEqual(refuse.returncode, 0)
                self.assertIn("No qualified selective modules", refuse.stderr)
                self.assertFalse(list(Path(d).iterdir()))

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

    def test_selection_plan_is_independent_source_snapshot(self):
        api = "MATH_UDIV16"
        plan_a = mb.create_plan(self.index, ["UDIV16"])
        plan_b = mb.create_plan(self.index, ["UDIV16"])
        chosen_a = next(v for v in plan_a["operations"][0]["available_source_variants"]
                        if v["id"] == "link:biased")
        chosen_b = next(v for v in plan_b["operations"][0]["available_source_variants"]
                        if v["id"] == "link:biased")
        pristine = next(v for v in self.index[api]["variants"]
                        if v["id"] == "link:biased")["source_sha256"]
        chosen_a["source_sha256"] = "0" * 64
        self.assertEqual(chosen_b["source_sha256"], pristine)
        self.assertEqual(
            next(v for v in self.index[api]["variants"] if v["id"] == "link:biased")
            ["source_sha256"], pristine)
        with tempfile.TemporaryDirectory() as d:
            import selective_linker
            with self.assertRaisesRegex(selective_linker.LinkError, "source changed"):
                selective_linker.build(plan_a, Path(d))
            # Later independent plans remain valid after the intentional tamper.
            valid = selective_linker.build(plan_b, Path(d))
            self.assertIn(api, valid["link_exports"])

    def test_source_hash_verification(self):
        # Every selected operation has a V1 source mirror with a published SHA.
        v = self.index["MATH_UMUL16"]["variants"][0]
        mb.validate_sha(ROOT, v)
        corrupted = dict(v, source_sha256="0" * 64)
        with self.assertRaises(mb.SelectionError):
            mb.validate_sha(ROOT, corrupted)

    def test_config_selection_is_plan_only_until_build_requested(self):
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
            self.assertEqual(plan["linker_status"], "experimental_subset_available")
            self.assertFalse(list(Path(d).rglob("*.prg")))
            # These operations became legitimately linkable after phase 1.
            # An explicit --build must produce only the selected modules.
            build = subprocess.run(call + ["--build"], text=True,
                                   capture_output=True, cwd=ROOT)
            self.assertEqual(build.returncode, 0, build.stderr)
            manifest = json.loads((Path(d) / "selective_manifest.json").read_text())
            self.assertEqual(set(manifest["link_exports"]),
                             {"MATH_ATAN2_8", "MATH_UMUL16"})
            self.assertEqual(manifest["resource_use"]["zero_page_bytes"], 0)
            self.assertEqual(len(list(Path(d).rglob("*.prg"))), 1)

    def test_build_rejects_nonlinkable_operation(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            invocation = [sys.executable, str(SCRIPT),
                          "--operation", "ISQRT16",
                          "--build", "--out", str(out / "plan.json")]
            result = subprocess.run(invocation, text=True,
                                    capture_output=True, cwd=ROOT)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no qualified selective source", result.stderr)
            self.assertFalse(list(out.rglob("*.prg")))

    def test_deterministic_selection_plan(self):
        a = mb.create_plan(self.index, ["isqrt16", "umul16"])
        b = mb.create_plan(self.index, ["umul16", "isqrt16"])
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
