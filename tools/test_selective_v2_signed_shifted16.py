#!/usr/bin/env python3
"""Full Q24/R16/C and automatic speed qualification for signed shifted V2."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU

import math_builder
import selective_linker as linker
import selective_speed_sdiv16_shl8 as speed

class SignedShiftedV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,pin=speed.FAST,ram=2656,zp=12,objective="size"):
        return math_builder.create_plan(
            self.index,["SDIV16_SHL8"],objective=objective,
            pins={"SDIV16_SHL8":pin} if pin else {},
            zp_budget=zp,ram_budget=ram,
            workload_calls={"SDIV16_SHL8":100} if objective=="speed" else None)

    def test_relocated_384_same_input_public_calls(self):
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(origin=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,
                    "zp_base":zp,"scratch_base":io+0x40})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],2624)
                self.assertEqual(use["main_ram_total_bytes"],2656)
                self.assertEqual(use["zero_page_bytes"],12)
                self.assertEqual(use["private_ram_scratch_bytes"],0)
                self.assertEqual(man["operations"][0]["variant"],speed.FAST)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(prg[:2],code.to_bytes(2,"little"))
                self.assertEqual(len(prg),2626)
                memory=bytearray(65536)
                memory[code:code+2624]=prg[2:]
                pristine=bytes(memory[code:code+2624])
                cpu=CPU(memory)
                entry=int(man["operations"][0]["entry"][1:],16)
                self.assertEqual(entry,code+2368)
                sp=cpu.sp
                for i,(n,d) in enumerate(speed.corpus()):
                    nb=n.to_bytes(2,"little")+bytes((0xa5,0x5a))
                    db=d.to_bytes(2,"little")+bytes((0x6b,0x7c))
                    memory[io+16:io+20]=nb
                    memory[io+20:io+24]=db
                    memory[io+24:io+28]=bytes((0x42,0x43,0x44,0x45))
                    memory[io+28:io+32]=bytes((0x51,0x52,0x53,0x54))
                    cpu.a=(n+i)&255
                    cpu.x=(d+i)&255
                    cpu.y=(n^d^i)&255
                    cpu.c=(n+d+i)&1
                    cpu.d=0
                    cpu.call(entry,65000)
                    got=(int.from_bytes(memory[io+24:io+27],"little"),
                         int.from_bytes(memory[io+28:io+30],"little"),cpu.c)
                    self.assertEqual(got,speed.oracle(n,d),(code,n,d))
                    self.assertEqual(memory[io+27],0x45)
                    self.assertEqual(bytes(memory[io+30:io+32]),bytes((0x53,0x54)))
                    self.assertEqual(bytes(memory[io+16:io+20]),nb)
                    self.assertEqual(bytes(memory[io+20:io+24]),db)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(memory[code:code+2624]),pristine)

    def test_speed_source_at_both_relocations_and_size_fallback(self):
        for code,io,scratch,zp in ((0x8000,0xc000,0xc020,0x50),
                                   (0x7123,0xc040,0xc080,0x70)):
            with self.subTest(code=code):
                m=speed.bench_sdiv16_shl8(
                    linker.MODULES["MATH_SDIV16_SHL8"],
                    code,io,scratch,math_builder.ROOT,zp=zp)
                print("SIGNED_V2_SHIFTED16_MATCHED",hex(code),
                      m["mean_cycles"],m["maximum_cycles"],
                      m["p95_cycles"],flush=True)
                self.assertEqual(m["cases"],384)
                self.assertLess(m["mean_cycles"][speed.FAST],
                                m["mean_cycles"][speed.SMALL])
        for ram,zp,winner in ((2656,12,speed.FAST),
                              (272,0,speed.SMALL),
                              (272,12,speed.SMALL)):
            with tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(None,ram,zp,"speed"),Path(td))
                self.assertEqual(man["operations"][0]["variant"],winner)
                self.assertEqual(man["cycle_model_benchmark"]["cases"],384)

    def test_pin_fails_without_exact_ram_or_zp(self):
        with tempfile.TemporaryDirectory() as td:
            for ram,zp in ((2655,12),(2656,11)):
                with self.subTest(ram=ram,zp=zp):
                    with self.assertRaises(linker.LinkError):
                        linker.build(self.plan(ram=ram,zp=zp),Path(td)/"short")

if __name__=="__main__":
    unittest.main()
