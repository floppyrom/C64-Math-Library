#!/usr/bin/env python3
"""Original four-entry SEEK8 speed qualification, deduplicated source and state."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import math_builder
import selective_linker as linker
import selective_speed_seek8 as model

OPS=tuple(model.API_NAMES)

class SharedSeek8Speed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=OPS,ram=867):
        return math_builder.create_plan(
            self.index,list(ops),objective="speed",
            workload_calls={n:100 for n in ops},
            zp_budget=0,ram_budget=ram)

    def test_all_four_public_models_relocation_provenance(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc100,0xc121)):
            with self.subTest(code=code):
                for name in OPS:
                    with self.subTest(api=name):
                        values=model.measured(name,linker.MODULES[name],
                                              code,io,scratch,math_builder.ROOT)
                        self.assertEqual(values["cases"],256)
                        self.assertTrue(values["corpus_sha256"])
                        self.assertEqual(set(values["mean_cycles"]),{model.VARIANT})
                        self.assertGreater(values["mean_cycles"][model.VARIANT],0)
                        print("SEEK8_HISTORICAL_PUBLIC_SPEED",name,hex(code),
                              values["mean_cycles"],values["maximum_cycles"],
                              values["p95_cycles"],flush=True)

    def test_speed_installer_keeps_four_entries_one_executable_and_state(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(),Path(td))
            self.assertEqual(len(man["operations"]),4)
            self.assertEqual({d["variant"] for d in man["operations"]},
                             {model.VARIANT})
            self.assertEqual(len(man["link_order"]),1)
            self.assertEqual(man["resource_use"]["code_and_tables_bytes"],651)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],19)
            self.assertEqual(man["resource_use"]["persistent_state_bytes"],160)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],867)
            self.assertEqual(len(set(d["entry"] for d in man["operations"])),4)
            cpu=man["cycle_model_benchmark"]
            self.assertEqual(set(cpu["operations"]),set(OPS))
            self.assertTrue(cpu["cpu_model_only"])
            self.assertEqual(len(set(cpu["operations"][x]["source_sha256"][model.VARIANT]
                                     for x in OPS)),1)

    def test_one_entry_speed_build_and_exact_ram_fail_closed(self):
        for name in OPS:
            with self.subTest(api=name),tempfile.TemporaryDirectory() as td:
                one=linker.build(self.plan((name,)),Path(td))
                self.assertEqual(one["operations"][0]["api"],name)
                self.assertEqual(one["operations"][0]["variant"],model.VARIANT)
                self.assertEqual(one["cycle_model_benchmark"]["cases"],256)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=866),Path(td)/"too_small")

if __name__=="__main__":
    unittest.main()
