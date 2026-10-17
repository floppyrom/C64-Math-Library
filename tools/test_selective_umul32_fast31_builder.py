#!/usr/bin/env python3
"""Independently linked FAST31 V2 public-call, budget and provenance checks."""
from __future__ import annotations
from pathlib import Path
import random
import tempfile
import unittest
import math_builder
import selective_linker as linker
import selective_fast31_umul32 as fast
from mini6502 import CPU

ROOT=Path(__file__).resolve().parents[1]
IDENT="link:fast31-v2-public"

class FAST31BuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self, *, ram=3000,zp=31):
        return math_builder.create_plan(
            self.index,["UMUL32"],objective="size",zp_budget=zp,
            ram_budget=ram,pins={"UMUL32":IDENT})

    def test_public_abi_two_layouts_and_exact_resources(self):
        rng=random.Random(0x6431531)
        edges=(0,1,2,255,256,65535,0x7fffffff,0x80000000,0xffffffff)
        pairs=[(x,y) for x in edges for y in edges]
        pairs += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(200)]
        for base,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(base=base),tempfile.TemporaryDirectory() as td:
                target=Path(td)
                man=linker.build(self.plan(),target,memory={
                    "code_base":base,"math_io":io,"zp_base":zp})
                pos,end=fast.layout(base)
                res=man["resource_use"]
                self.assertEqual(res["image_span_bytes"],end-base)
                self.assertEqual(res["zero_page_bytes"],31)
                self.assertEqual(res["private_ram_scratch_bytes"],0)
                self.assertEqual(res["main_ram_total_bytes"],end-base+32)
                self.assertEqual(man["operations"][0]["variant"],IDENT)
                deps={v["source_path"] for v in man["operations"][0]["dependencies"]}
                self.assertEqual(deps,{
                    "tools/selective_fast31_umul32.py",
                    "v2_pareto_fast/resident/modules/pareto_umul32.a"})
                prg=(target/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),end-base+2)
                self.assertEqual(prg[:2],bytes((base&255,base>>8)))
                memory,entry,_,_=fast.assemble(base,io,zp,ROOT)
                self.assertEqual(prg[2:],bytes(memory[x] for x in range(base,end)))
                asm=fast.render(pos,io,zp,ROOT)
                from mini6502 import Assembler
                _,labels,_=Assembler().assemble(asm)
                mutable={a+1 for name,a in labels.items() if name.startswith("SMC_")}
                self.assertEqual(len(mutable),10)
                mem=bytearray(65536)
                mem[base:end]=prg[2:]
                cpu=CPU(mem); old_sp=cpu.sp
                for i,(x,y) in enumerate(pairs):
                    xb=x.to_bytes(4,"little");yb=y.to_bytes(4,"little")
                    mem[io:io+4]=xb
                    mem[io+4:io+8]=yb
                    mem[io+8:io+16]=b"\xa5"*8
                    cpu.c=i&1;cpu.d=0
                    cpu.call(entry,10000)
                    self.assertEqual(int.from_bytes(mem[io+8:io+16],"little"),x*y)
                    self.assertEqual(mem[io:io+4],xb)
                    self.assertEqual(mem[io+4:io+8],yb)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,old_sp)
                self.assertTrue(all(mem[a]==memory[a] for a in memory if a not in mutable))

    def test_exact_budget_and_zero_page_guard(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=2591),Path(td)/"ram")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(zp=30),Path(td)/"zp")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(),Path(td)/"reserved",memory={
                    "zp_reserved":[{"start":"$60","end":"$60"}]})

if __name__=="__main__":
    unittest.main()
