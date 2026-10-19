#!/usr/bin/env python3
"""Builder speed provenance for both virtual APIs of one historical V1 divider."""
from __future__ import annotations
import hashlib
import tempfile
import unittest
from pathlib import Path
import math_builder
import selective_linker as linker
import selective_speed_sdiv8_shared as model

OPERATIONS=("SDIV8","SMOD8")
ID="link:v1-shared-producer"


class SharedSigned8SpeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops,ram=562,zp=1):
        return math_builder.create_plan(
            self.index,list(ops),objective="speed",
            workload_calls={k:100 for k in ops},
            zp_budget=zp,ram_budget=ram)

    def test_original_512_full_public_calls_at_two_origins(self):
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            for op,fn in (("SDIV8",model.bench_sdiv8),
                          ("SMOD8",model.bench_smod8)):
                with self.subTest(code=code,op=op):
                    result=fn(linker.MODULES["MATH_"+op],code,io,zp,
                              math_builder.ROOT)
                    self.assertEqual(result["cases"],512)
                    self.assertTrue(result["cpu_model_only"])
                    self.assertEqual(result["operation"],"MATH_"+op)
                    self.assertEqual(set(result["mean_cycles"]),{ID})
                    self.assertEqual(result["corpus_sha256"],hashlib.sha256(
                        bytes(v for n,d in model.corpus() for v in (n,d))
                    ).hexdigest())
                    self.assertGreater(result["mean_cycles"][ID],0)
                    self.assertGreaterEqual(result["maximum_cycles"][ID],
                                            result["p95_cycles"][ID])
                    print("SIGNED8_SHARED_FULL_PUBLIC",op,hex(code),
                          result["mean_cycles"],result["maximum_cycles"],
                          result["p95_cycles"],flush=True)

    def test_mixed_signed_divmod_speed_exports_share_one_producer(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            for ops in (OPERATIONS,OPERATIONS[::-1]):
                with self.subTest(code=code,ops=ops),tempfile.TemporaryDirectory() as td:
                    man=linker.build(self.plan(ops),Path(td),memory={
                        "code_base":code,"math_io":io,"zp_base":zp})
                    self.assertEqual(set(man["link_exports"]),
                                     {"MATH_SDIV8","MATH_SMOD8"})
                    self.assertEqual(len(man["link_order"]),1)
                    self.assertEqual(len(man["operations"]),2)
                    self.assertEqual(man["resource_use"]["image_span_bytes"],530)
                    self.assertEqual(man["resource_use"]["main_ram_total_bytes"],562)
                    self.assertEqual(man["resource_use"]["zero_page_bytes"],1)
                    self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
                    self.assertEqual(len({op["entry"] for op in man["operations"]}),1)
                    m=man["cycle_model_benchmark"]
                    self.assertEqual(set(m["operations"]),{
                        "MATH_SDIV8","MATH_SMOD8"})
                    for one in m["operations"].values():
                        self.assertEqual(one["cases"],512)
                        self.assertEqual(set(one["mean_cycles"]),{ID})
                        self.assertEqual(one["basis"],model.BASIS)
                    prg=(Path(td)/"math_selective.prg").read_bytes()
                    self.assertEqual(hashlib.sha256(prg).hexdigest(),
                                     man["prg_sha256"])

    def test_single_api_speed_and_fail_closed_ram_zp(self):
        for op in OPERATIONS:
            with self.subTest(op=op),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan([op]),Path(td))
                self.assertEqual(man["link_exports"],["MATH_"+op])
                self.assertEqual(man["cycle_model_benchmark"]["cases"],512)
                with self.assertRaises(linker.LinkError):
                    linker.build(self.plan([op],ram=561),Path(td)/"short")
                with self.assertRaises(linker.LinkError):
                    linker.build(self.plan([op],zp=0),Path(td)/"nozp")

if __name__=="__main__":
    unittest.main()
