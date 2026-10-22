#!/usr/bin/env python3
"""Operation-first Turbo32/QS16 project configuration and resource proofs."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import configure_math
import math_builder
import reu_unified_setup

ROOT=Path(__file__).resolve().parents[1]


class UnifiedOperationFirstREU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    @staticmethod
    def config(service,capacity=None,bank=None):
        default={"turbo32":(512,4,"UMUL32"),"qs16":(16384,200,"UMUL16")}
        kib,origin,op=default[service]
        return {
            "target":"c64","operations":[op],
            "objective":"size",
            "constraints":{"max_zp_bytes":210,"max_ram_bytes":30000},
            "hardware":{"reu":{service:{
                "capacity_kib":kib if capacity is None else capacity,
                "bank":origin if bank is None else bank,
                "reserved_banks":[],
            }}},
        }

    def test_new_reu_services_generate_stock_and_source_built_prgs(self):
        for service in ("turbo32","qs16"):
            with self.subTest(service=service),tempfile.TemporaryDirectory() as td:
                folder=Path(td)
                cfg=self.config(service)
                stock=configure_math.build_checked(cfg,self.index,folder)
                project=json.loads((folder/"math_project_manifest.json").read_text())
                reu=json.loads((folder/(service+"_reu_manifest.json")).read_text())
                self.assertEqual(project["service"],service)
                self.assertTrue(project["stock_remains_default"])
                self.assertTrue(project["one_reu_service_at_a_time"])
                self.assertTrue(project["source_built_service"])
                self.assertFalse(project["full_historical_resident_dependency"])
                self.assertFalse(project["native_mixed_irq_vic_qualified"])
                self.assertFalse(project["service"]=="turbo16")
                self.assertEqual(stock["memory_map"]["math_io_start"],"$C040")
                self.assertEqual(len(stock["memory_map"]["user_reserved"]),
                                 3 if service=="qs16" else 2)
                self.assertEqual(len(stock["memory_map"]["user_zp_reserved"]),1)
                self.assertIn("MATH_"+cfg["operations"][0],
                              [x["api"] for x in stock["operations"]])
                self.assertEqual(project["reu_entrypoints"],reu["public_exports"])
                self.assertEqual(project["stock_prg_sha256"],
                                 hashlib.sha256((folder/"math_selective.prg").read_bytes()).hexdigest())
                self.assertEqual(project["reu_prg_sha256"],
                                 hashlib.sha256((folder/(service+"_reu.prg")).read_bytes()).hexdigest())
                self.assertIn("MATH_"+("Q16_REU_INSTALL" if service=="qs16" else "T32_REU_INSTALL"),
                              (folder/("math_reu_"+service+".inc")).read_text())
                use=project["combined_resource_use"]
                required=reu_unified_setup.requirements(cfg)
                self.assertEqual(use["zero_page_bytes"],
                                 stock["resource_use"]["zero_page_bytes"]+required["zero_page_bytes"])
                self.assertEqual(use["main_ram_total_bytes"],
                                 stock["resource_use"]["main_ram_total_bytes"]+required["main_ram_total_bytes"])
                self.assertLessEqual(use["main_ram_total_bytes"],30000)
                self.assertLessEqual(use["zero_page_bytes"],210)

    def test_rebuild_preserves_service_and_source_hashes(self):
        for service in ("turbo32","qs16"):
            with self.subTest(service=service),tempfile.TemporaryDirectory() as td:
                root=Path(td)
                config=root/"configured.json"
                initial=root/"first"
                args=[sys.executable,str(ROOT/"tools/configure_math.py"),
                      "--operation","UMUL32" if service=="turbo32" else "UMUL16",
                      "--objective","size","--zp-budget","210",
                      "--ram-budget","30000","--reu-"+service,
                      "--config-out",str(config),"--build-dir",str(initial)]
                first=subprocess.run(args,capture_output=True,text=True,cwd=ROOT)
                self.assertEqual(first.returncode,0,first.stderr[-1500:])
                output=root/"second"
                saved=subprocess.run([
                    sys.executable,str(ROOT/"tools/math_builder.py"),
                    "--config",str(config),"--build",
                    "--out",str(output/"selection_manifest.json")
                ],capture_output=True,text=True,cwd=ROOT)
                self.assertEqual(saved.returncode,0,saved.stderr[-1500:])
                for name in ("math_selective.prg","math_api.inc",
                             service+"_reu.prg",service+"_reu_manifest.json",
                             "math_project_manifest.json","math_reu_"+service+".inc"):
                    self.assertEqual((initial/name).read_bytes(),(output/name).read_bytes(),name)
                selected=json.loads(config.read_text())
                self.assertIn(service,selected["hardware"]["reu"])
                again=subprocess.run(args,capture_output=True,text=True,cwd=ROOT)
                self.assertNotEqual(again.returncode,0)
                self.assertIn("already exists",again.stderr)

    def test_reservation_collisions_and_invalid_tiers_fail_closed(self):
        for service in ("turbo32","qs16"):
            candidate=self.config(service)
            variants=[
                {**candidate,"constraints":{"max_zp_bytes":10,"max_ram_bytes":30000}},
                {**candidate,"constraints":{"max_zp_bytes":210,"max_ram_bytes":12000}},
                {**candidate,"memory":{"math_io":"$C000"}},
                {**candidate,"memory":{"code_base":"$4000"}},
                {**candidate,"memory":{"reserved":[{"name":"game","start":"$7100","end":"$7200"}]}},
                {**candidate,"memory":{"zp_reserved":[{"name":"music","start":"$50","end":"$5F"}]}},
                {**candidate,"operations":["UDIV16"]},
                {**candidate,"hardware":{"reu":{"turbo16":candidate["hardware"]["reu"][service],
                                                 service:candidate["hardware"]["reu"][service]}}},
            ]
            if service=="qs16":
                variants.extend([
                    self.config(service,capacity=512),
                    self.config(service,bank=201),
                    {**candidate,"hardware":{"reu":{service:{
                        "capacity_kib":16384,"bank":200,"reserved_banks":[72]}}}},
                ])
            else:
                variants.extend([
                    self.config(service,capacity=16384,bank=256),
                    {**candidate,"hardware":{"reu":{service:{
                        "capacity_kib":512,"bank":4,"reserved_banks":[4]}}}},
                ])
            for idx,cfg in enumerate(variants):
                with self.subTest(service=service,idx=idx),tempfile.TemporaryDirectory() as td:
                    with self.assertRaises((ValueError,math_builder.SelectionError)):
                        configure_math.build_checked(cfg,self.index,Path(td)/"out")

    def test_existing_turbo16_and_stock_setup_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            old=self.config("qs16")
            old["hardware"]={"reu":{"turbo16":{
                "capacity_kib":512,"bank":4,"reserved_banks":[]}}}
            a=configure_math.build_checked(old,self.index,Path(td))
            self.assertTrue((Path(td)/"turbo16_reu.prg").is_file())
            self.assertTrue(a["operations"])
        with tempfile.TemporaryDirectory() as td:
            ordinary={"target":"c64","operations":["UMUL16"],"objective":"size",
                      "constraints":{"max_zp_bytes":0,"max_ram_bytes":3000}}
            configure_math.build_checked(ordinary,self.index,Path(td))
            self.assertFalse((Path(td)/"math_project_manifest.json").exists())


if __name__=="__main__":
    unittest.main()
