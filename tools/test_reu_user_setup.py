#!/usr/bin/env python3
"""True operation-first setup + opt-in native REU project round-trip tests."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import configure_math as setup
import math_builder as builder
import reu_user_setup as reu

ROOT=Path(__file__).resolve().parents[1]


class OperationFirstREUOptIn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=builder.operation_index()

    @staticmethod
    def config(zp=200,ram=25000,capacity=512,bank=4):
        return {
            "target":"c64","operations":["UMUL16"],"objective":"size",
            "constraints":{"max_zp_bytes":zp,"max_ram_bytes":ram},
            "hardware":{"reu":{"turbo16":{
                "capacity_kib":capacity,"bank":bank,"reserved_banks":[2]}}},
        }

    def test_source_linked_two_prg_separate_public_io_and_global_resources(self):
        for capacity,bank in ((512,4),(16384,200)):
            with self.subTest(capacity=capacity):
                with tempfile.TemporaryDirectory() as td:
                    folder=Path(td)
                    data=self.config(capacity=capacity,bank=bank)
                    stock=setup.build_checked(data,self.index,folder)
                    self.assertTrue({"MATH_UMUL16"}.issubset(
                        {op["api"] for op in stock["operations"]}))
                    project=json.loads((folder/"math_project_manifest.json").read_text())
                    reuman=json.loads((folder/"turbo16_reu_manifest.json").read_text())
                    self.assertTrue(project["stock_remains_default"])
                    self.assertTrue(project["physical_memory_bound_by_stock_linker"])
                    self.assertFalse(project["mixed_stock_reu_vic_irq_qualified"])
                    self.assertFalse(reuman["reu_mode_selectable_in_operation_first_builder"])
                    self.assertEqual(project["stock_prg_sha256"],
                                     hashlib.sha256((folder/"math_selective.prg").read_bytes()).hexdigest())
                    self.assertEqual(project["reu_prg_sha256"],
                                     hashlib.sha256((folder/"turbo16_reu.prg").read_bytes()).hexdigest())
                    usage=project["combined_resource_use"]
                    self.assertEqual(usage["zero_page_bytes"],stock["resource_use"]["zero_page_bytes"]+122)
                    self.assertEqual(usage["main_ram_total_bytes"],stock["resource_use"]["main_ram_total_bytes"]+18464)
                    self.assertLessEqual(usage["zero_page_bytes"],200)
                    self.assertLessEqual(usage["main_ram_total_bytes"],25000)
                    claims=stock["memory_map"]
                    self.assertEqual(claims["math_io_start"],"$C040")
                    self.assertEqual(len(claims["user_reserved"]),2)
                    self.assertEqual(len(claims["user_zp_reserved"]),1)
                    self.assertEqual(project["reu_entrypoints"],reuman["public_exports"])

    def test_budget_and_memory_overlaps_fail_without_publishing(self):
        for config in (
            self.config(zp=121),
            self.config(ram=18463),
            {**self.config(),"memory":{"math_io":"$C000"}},
            {**self.config(),"memory":{"code_base":"$6000"}},
            {**self.config(),"memory":{"reserved":[
                {"name":"irq_code","start":"$3A00","end":"$3AFF"}]}},
            {**self.config(),"memory":{"zp_reserved":[
                {"name":"music_zp","start":"$40","end":"$5F"}]}},
            {**self.config(capacity=16384,bank=200),
             "hardware":{"reu":{"turbo16":{
                "capacity_kib":16384,"bank":200,"reserved_banks":[72]}}}},
            {**self.config(),"operations":["UDIV16"]},
        ):
            with self.subTest(config=config),tempfile.TemporaryDirectory() as td:
                with self.assertRaises((ValueError,builder.SelectionError)):
                    setup.build_checked(config,self.index,Path(td)/"result")

    def test_cli_reproducible_and_no_silent_drop_on_rebuild(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            cfg=folder/"user.json"
            first=folder/"first"
            base=[sys.executable,str(ROOT/"tools/configure_math.py"),
                  "--operation","UMUL16","--objective","size",
                  "--zp-budget","200","--ram-budget","25000",
                  "--reu-turbo16","--reu-kib","512","--reu-bank","0x4",
                  "--config-out",str(cfg),"--build-dir",str(first)]
            result=subprocess.run(base,capture_output=True,text=True,cwd=ROOT)
            self.assertEqual(result.returncode,0,result.stderr[-3000:])
            repeat=subprocess.run(base,capture_output=True,text=True,cwd=ROOT)
            self.assertNotEqual(repeat.returncode,0)
            self.assertIn("already exists",repeat.stderr)
            second=folder/"rebuild"
            builder_cmd=[sys.executable,str(ROOT/"tools/math_builder.py"),
                         "--config",str(cfg),"--build",
                         "--out",str(second/"selection_manifest.json")]
            rebuilt=subprocess.run(builder_cmd,capture_output=True,text=True,cwd=ROOT)
            self.assertEqual(rebuilt.returncode,0,rebuilt.stderr[-3000:])
            for name in ("math_selective.prg","turbo16_reu.prg","math_project_manifest.json",
                         "math_reu_turbo16.inc","math_api.inc"):
                self.assertEqual((first/name).read_bytes(),(second/name).read_bytes(),name)
            measured=subprocess.run([sys.executable,str(ROOT/"tools/math_builder.py"),
                                    "--config",str(cfg),"--measure"],
                                   capture_output=True,text=True,cwd=ROOT)
            self.assertEqual(measured.returncode,0,measured.stderr[-3000:])
            report=json.loads(measured.stdout)
            self.assertEqual(report["combined_resource_use"],
                             json.loads((first/"math_project_manifest.json").read_text())["combined_resource_use"])
            dropped=subprocess.run([sys.executable,str(ROOT/"tools/math_builder.py"),
                                    "--config",str(cfg),"--preview"],capture_output=True,text=True,cwd=ROOT)
            self.assertNotEqual(dropped.returncode,0)
            self.assertIn("Hardware REU",dropped.stderr)

    def test_default_setup_not_affected(self):
        with tempfile.TemporaryDirectory() as td:
            cfg={"target":"c64","operations":["UMUL16"],"objective":"size",
                 "constraints":{"max_zp_bytes":0,"max_ram_bytes":3000}}
            folder=Path(td)
            output=setup.build_checked(cfg,self.index,folder)
            self.assertIn("MATH_UMUL16",{o["api"] for o in output["operations"]})
            self.assertFalse((folder/"turbo16_reu.prg").exists())
            self.assertEqual(output["memory_map"]["math_io_start"],"$C000")

if __name__=="__main__": unittest.main()
