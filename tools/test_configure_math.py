#!/usr/bin/env python3
"""User-facing C64 one-command setup must match the production optimizer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import configure_math as setup
import math_builder as mb
import selective_linker as linker

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools"/"configure_math.py"


class UserSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=mb.operation_index()

    def args(self, tmp, **overrides):
        data={
            "operation":["UMUL8"],
            "objective":"size",
            "zp_budget":0,
            "ram_budget":4096,
            "calls":[],
            "pin":[],
            "memory_config":None,
            "config_out":tmp/"user.json",
            "build_dir":tmp/"build",
        }
        data.update(overrides)
        return argparse.Namespace(**data)

    def test_one_command_config_and_binary_match_existing_builder(self):
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)
            args=self.args(folder, operation=["UMUL8","UDIV16"])
            result=setup.run(args,self.index,interactive=False)
            config=json.loads(args.config_out.read_text(encoding="utf-8"))
            self.assertEqual(config["target"],"c64")
            self.assertEqual(set(config["operations"]),{"UMUL8","UDIV16"})
            self.assertEqual(config["objective"],"size")
            self.assertEqual(config["constraints"]["max_zp_bytes"],0)
            self.assertEqual(result["selection_objective"],"size")
            generated=json.loads((args.build_dir/"selective_manifest.json").read_text())
            self.assertEqual(result["prg_sha256"],generated["prg_sha256"])
            with tempfile.TemporaryDirectory() as tmp:
                plan=mb.create_plan(
                    self.index,config["operations"],objective="size",
                    zp_budget=0,ram_budget=4096)
                old=linker.build(plan,Path(tmp))
                self.assertEqual(old["prg_sha256"],result["prg_sha256"])
                self.assertEqual((Path(tmp)/"math_selective.prg").read_bytes(),
                                 (args.build_dir/"math_selective.prg").read_bytes())
            self.assertTrue((args.build_dir/"math_api.inc").is_file())

    def test_speed_requires_exposed_weights_and_no_guessing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            args=self.args(root,objective="speed",zp_budget=8,operation=["UMUL8","UDIV8"],
                           calls=["UMUL8=100"])
            with self.assertRaisesRegex(mb.SelectionError,"requires --calls"):
                setup.run(args,self.index,interactive=False)
            self.assertFalse(root.joinpath("user.json").exists())
            self.assertFalse(root.joinpath("build").exists())
            args.calls+=["UDIV8=2"]
            result=setup.run(args,self.index,interactive=False)
            cfg=json.loads(args.config_out.read_text())
            self.assertEqual(cfg["workload_calls"],{"UDIV8":2,"UMUL8":100})
            self.assertEqual(result["selection_objective"],"speed")
            self.assertEqual(result["workload_calls"],
                             {"MATH_UDIV8":2,"MATH_UMUL8":100})

    def test_rejects_existing_outputs_without_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            args=self.args(root)
            first=setup.run(args,self.index,interactive=False)
            expected=args.config_out.read_bytes()
            image=(args.build_dir/"math_selective.prg").read_bytes()
            with self.assertRaisesRegex(mb.SelectionError,"already exists"):
                setup.run(args,self.index,interactive=False)
            self.assertEqual(expected,args.config_out.read_bytes())
            self.assertEqual(image,(args.build_dir/"math_selective.prg").read_bytes())
            self.assertEqual(first["status"],"selective_binary_emitted")

    def test_bad_resource_limits_do_not_write_files(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            args=self.args(folder,ram_budget=10)
            with self.assertRaisesRegex(linker.LinkError,"fits RAM/ZP"):
                setup.run(args,self.index,interactive=False)
            self.assertFalse(args.config_out.exists())
            self.assertFalse(args.build_dir.exists())

    def test_memory_map_and_reserved_collisions_do_not_write(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            memory=folder/"memory.json"
            memory.write_text(json.dumps({
                "code_base":"$8000",
                "math_io":"$C000",
                "zp_base":"$60",
                "reserved":[{"name":"my_game","start":"$8000","end":"$8FFF"}]
            }))
            args=self.args(folder,memory_config=memory)
            with self.assertRaisesRegex(linker.LinkError,"overlaps"):
                setup.run(args,self.index,interactive=False)
            self.assertFalse(args.config_out.exists())
            self.assertFalse(args.build_dir.exists())
            memory.write_text(json.dumps({
                "code_base":"$7123","math_io":"$C040",
                "zp_base":"$60", "scratch_base":"$C060",
                "reserved":[{"name":"user_program","start":"$8000","end":"$8FFF"}]
            }))
            actual=setup.run(args,self.index,interactive=False)
            self.assertEqual(json.loads(args.config_out.read_text())["memory"]
                            ["code_base"],"$7123")
            self.assertEqual(actual["memory_map"]["code_start"],"$7123")

    def test_interactive_prompts_budget_speed_and_operations(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            args=self.args(folder,operation=[],objective=None,zp_budget=None,
                           ram_budget=None)
            # Keep the real planner; substitute the *selection prompt* only,
            # not the linker, resource accounting or source verification.
            with patch.object(mb,"interactive_pick",return_value=["UMUL8"]),\
                 patch("builtins.input",side_effect=["speed","0","4096","12","none"]):
                result=setup.run(args,self.index,interactive=True)
            self.assertEqual(result["selection_objective"],"speed")
            cfg=json.loads(args.config_out.read_text())
            self.assertEqual(cfg["workload_calls"],{"UMUL8":12})

    def test_guided_setup_offers_all_reu_options(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            args=self.args(folder,operation=[],objective="size",zp_budget=210,
                           ram_budget=30000)
            with patch.object(mb,"interactive_pick",return_value=["UMUL32"]),\
                 patch("builtins.input",side_effect=["turbo32","512"]):
                result=setup.run(args,self.index,interactive=True)
            cfg=json.loads(args.config_out.read_text())
            self.assertEqual(cfg["hardware"]["reu"]["turbo32"]["capacity_kib"],512)
            self.assertIn("MATH_UMUL32",[o["api"] for o in result["operations"]])
            self.assertTrue((args.build_dir/"turbo32_reu.prg").exists())
            self.assertTrue((args.build_dir/"math_project_manifest.json").exists())

    def test_unknown_pin_duplicate_calls_and_invalid_config(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            for kwargs,message in (
                ({"pin":["UMUL8=garbage"]},"Unknown variant"),
                ({"calls":["UMUL8=2"]},"only valid"),
                ({"objective":"speed","calls":["UMUL8=2","UMUL8=3"]},
                 "Repeated"),
                ({"objective":"speed","calls":["UMUL8=0"]},
                 "from 1"),
                ({"operation":[]},"requires --operation"),
            ):
                with self.subTest(kwargs=kwargs):
                    args=self.args(folder,**kwargs)
                    with self.assertRaisesRegex((mb.SelectionError,linker.LinkError),
                                                message):
                        setup.run(args,self.index,interactive=False)

    def test_cli_noninteractive_can_be_consumed_by_existing_main_cli(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            cmd=[sys.executable,str(SCRIPT),"--operation","UMUL8",
                 "--objective","size","--zp-budget","0",
                 "--ram-budget","4096",
                 "--config-out",str(folder/"config.json"),
                 "--build-dir",str(folder/"product")]
            outcome=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(outcome.returncode,0,outcome.stderr)
            self.assertIn("Built source-qualified selective PRG",outcome.stdout)
            other=subprocess.run(
                [sys.executable,str(ROOT/"tools"/"math_builder.py"),
                 "--config",str(folder/"config.json"),"--measure"],
                cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(other.returncode,0,other.stderr)
            self.assertEqual(json.loads(other.stdout)["selected_variants"],
                             {x["api"]:x["variant"] for x in
                              json.loads((folder/"product"/
                                          "selective_manifest.json").read_text())["operations"]})


if __name__=="__main__":
    unittest.main()
