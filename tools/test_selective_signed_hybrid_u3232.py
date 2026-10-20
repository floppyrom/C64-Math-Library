#!/usr/bin/env python3
"""Source-linked signed V2-hybrid 32/32 ABI, both aliases and placements."""
from __future__ import annotations
import random
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_signed_hybrid_u3232 as v2s
from test_selective_sdiv32_32 import corpus,reference
import selective_speed_s3232 as timing

FAST="link:v2-hybrid-signed"
COMPACT="link:portable-zerozp"
OPS=("SDIV32_32","SMOD32_32")

class Signed32HybridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,zp=12,ram=2912,pinned=True):
        return math_builder.create_plan(
            self.index,list(OPS),objective="size",
            zp_budget=zp,ram_budget=ram,
            pins={op:FAST for op in OPS} if pinned else None)

    def test_public_aliases_source_hash_resources_and_two_code_origins(self):
        pairs=corpus()[:192]
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                folder=Path(td)
                man=linker.build(self.plan(),folder,memory={
                    "code_base":code,"math_io":io,"zp_base":zp,
                    "scratch_base":io+0x40})
                entries={op["api"]:int(op["entry"][1:],16)
                         for op in man["operations"]}
                self.assertEqual(entries,{"MATH_SDIV32_32":code+2496,
                                          "MATH_SMOD32_32":code+2496})
                self.assertEqual(len(man["link_order"]),1)
                use=man["resource_use"]
                self.assertEqual(use["main_ram_total_bytes"],2912)
                self.assertEqual(use["zero_page_bytes"],12)
                self.assertEqual(use["private_ram_scratch_bytes"],0)
                data=(folder/"math_selective.prg").read_bytes()
                self.assertEqual(len(data),2882)
                self.assertEqual(data[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536)
                mem[code:code+2880]=data[2:]
                original=bytes(mem[code:code+2880])
                cpu=CPU(mem);sp=cpu.sp
                for index,(n,d) in enumerate(pairs):
                    api="MATH_SDIV32_32" if index%2==0 else "MATH_SMOD32_32"
                    nb=n.to_bytes(4,"little")
                    db=d.to_bytes(4,"little")
                    mem[io+16:io+20]=nb
                    mem[io+20:io+24]=db
                    mem[io+24:io+32]=bytes([0xdd])*8
                    cpu.a=(n^d)&255
                    cpu.x=(n>>8)&255
                    cpu.y=(d>>8)&255
                    cpu.c=index&1
                    cpu.d=0
                    cpu.call(entries[api],150000)
                    got=(int.from_bytes(mem[io+24:io+28],"little"),
                         int.from_bytes(mem[io+28:io+32],"little"),cpu.c)
                    self.assertEqual(got,reference(n,d),(code,index,n,d))
                    self.assertEqual(bytes(mem[io+16:io+20]),nb)
                    self.assertEqual(bytes(mem[io+20:io+24]),db)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+2880]),original)

    def test_same_corpus_signed32_public_speed_at_two_relocations(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            for api in ("MATH_SDIV32_32","MATH_SMOD32_32"):
                with self.subTest(code=code,api=api):
                    result=timing.benchmark(api,linker.MODULES[api],
                        code,io,io+0x40,linker.ROOT,zp)
                    self.assertEqual(result["cases"],384)
                    self.assertEqual(result["corpus_sha256"],timing.CORPUS_SHA256)
                    mean=result["mean_cycles"]
                    self.assertEqual(set(mean),{COMPACT,FAST,"link:d65536-hybrid"})
                    self.assertGreater(mean["link:d65536-hybrid"],0)
                    self.assertLess(mean[FAST],mean[COMPACT])
                    print("SIGNED3232_V2_PAIRED_SPEED",hex(code),api,
                          "portable",round(mean[COMPACT],3),
                          "V2",round(mean[FAST],3),
                          "max_portable",result["maximum_cycles"][COMPACT],
                          "max_v2",result["maximum_cycles"][FAST],flush=True)
            with tempfile.TemporaryDirectory() as td:
                plan=math_builder.create_plan(self.index,list(OPS),
                    objective="speed",zp_budget=12,ram_budget=2912,
                    workload_calls={op:100 for op in OPS})
                manifest=linker.build(plan,Path(td),memory={
                    "code_base":code,"math_io":io,"zp_base":zp,
                    "scratch_base":io+0x40})
                self.assertEqual({m["variant"] for m in manifest["operations"]},
                                 {FAST})
                self.assertEqual(len(manifest["link_order"]),1)
                self.assertEqual(manifest["resource_use"]["main_ram_total_bytes"],
                                 2912)

    def test_compact_remains_selected_when_zp_or_ram_is_tight(self):
        with tempfile.TemporaryDirectory() as td:
            m=linker.build(self.plan(zp=0,ram=453,pinned=False),Path(td))
            self.assertEqual({e["variant"] for e in m["operations"]},{COMPACT})
            self.assertEqual(m["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(m["resource_use"]["main_ram_total_bytes"],453)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(zp=0),Path(td)/"impossiblezp")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=2911),Path(td)/"impossibleram")

if __name__=="__main__":
    unittest.main()
