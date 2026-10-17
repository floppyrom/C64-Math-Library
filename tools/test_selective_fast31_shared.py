#!/usr/bin/env python3
"""Full unsigned/signed FAST31 shared producer: one binary, two exports, RAM/ZP."""
from __future__ import annotations

import random
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU, Assembler
import math_builder
import selective_linker as linker
import selective_fast31_umul32 as fast31

SHARED="link:fast31-shared-full64"
MASK=(1<<64)-1

def signed(x):
    return x-(1<<32) if x&0x80000000 else x

class SharedFAST31Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ram,zp=31,pins=None,objective="size"):
        return math_builder.create_plan(
            self.index,["UMUL32","SMUL32"],objective=objective,
            zp_budget=zp,ram_budget=ram,
            pins=pins or {"UMUL32":SHARED,"SMUL32":SHARED},
            workload_calls={"UMUL32":10,"SMUL32":10} if objective=="speed" else None)

    def test_exact_single_image_both_entries_and_relocatable_mixed_calls(self):
        rng=random.Random(0x6431F531)
        edges=(0,1,2,255,256,65535,0x7fffffff,0x80000000,0xffffffff)
        pairs=[(x,y) for x in edges for y in edges]
        pairs.extend((rng.getrandbits(32),rng.getrandbits(32)) for _ in range(220))
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            positions,end=fast31.layout(code)
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                out=Path(td)
                man=linker.build(self.plan(end-code+32),out,memory={
                    "code_base":code,"math_io":io,"zp_base":zp})
                self.assertEqual(len(man["link_order"]),1)
                self.assertEqual(man["resource_use"]["image_span_bytes"],end-code)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],31)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],end-code+32)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
                self.assertEqual(set(op["variant"] for op in man["operations"]),{SHARED})
                self.assertEqual(len({op["sha256"] for op in man["operations"]}),1)
                self.assertEqual(sum("shared_kernel_of" in op for op in man["operations"]),1)
                entries={op["api"]:int(op["entry"][1:],16) for op in man["operations"]}
                self.assertEqual(entries["MATH_UMUL32"],code)
                self.assertNotEqual(entries["MATH_SMUL32"],code)
                self.assertLess(entries["MATH_SMUL32"],code+512)
                binary=(out/"math_selective.prg").read_bytes()
                self.assertEqual(len(binary),end-code+2)
                image,_,_,_=fast31.assemble(code,io,zp,
                    Path(__file__).resolve().parents[1],
                    source_path="routines/multiply/mul32_fast31_shared_public.asm")
                self.assertEqual(binary[2:],bytes(image[a] for a in range(code,end)))
                source=fast31.render(positions,io,zp,
                    Path(__file__).resolve().parents[1],
                    "routines/multiply/mul32_fast31_shared_public.asm")
                _,labels,_=Assembler().assemble(source)
                mutable={a+1 for k,a in labels.items() if k.startswith("SMC_")}
                self.assertEqual(len(mutable),10)
                mem=bytearray(65536)
                mem[code:end]=binary[2:]
                cpu=CPU(mem)
                sp=cpu.sp
                for i,(x,y) in enumerate(pairs):
                    for op in ("MATH_SMUL32","MATH_UMUL32"):
                        xb=x.to_bytes(4,"little");yb=y.to_bytes(4,"little")
                        mem[io:io+4]=xb;mem[io+4:io+8]=yb
                        mem[io+8:io+16]=b"\xa5"*8
                        cpu.d=0;cpu.c=(i^x^y)&1
                        cpu.call(entries[op],12000)
                        product=(signed(x)*signed(y))&MASK if op=="MATH_SMUL32" else x*y
                        self.assertEqual(int.from_bytes(mem[io+8:io+16],"little"),product,
                                         (hex(code),op,hex(x),hex(y)))
                        self.assertEqual(bytes(mem[io:io+4]),xb)
                        self.assertEqual(bytes(mem[io+4:io+8]),yb)
                        self.assertEqual(cpu.c,0)
                        self.assertEqual(cpu.sp,sp)
                self.assertTrue(all(mem[a]==b for a,b in image.items() if a not in mutable))

    def test_enforced_budget_and_two_independent_sources_remain_available(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            m=linker.build(self.plan(2592),root/"shared")
            self.assertEqual(m["resource_use"]["main_ram_total_bytes"],2592)
            self.assertEqual(m["resource_use"]["alignment_padding_bytes"],0)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(2591),root/"ram")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(2592,zp=30),root/"zp")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(2592),root/"reserved",
                    memory={"zp_reserved":[{"start":"$60","end":"$61"}]})
            legacy=self.plan(5152,pins={
                "UMUL32":"link:fast31-v2-public",
                "SMUL32":"link:fast31-v2-signed"})
            two=linker.build(legacy,root/"legacy")
            self.assertEqual(two["resource_use"]["main_ram_total_bytes"],5152)
            self.assertEqual(len(two["link_order"]),2)

    def test_global_speed_selects_shared_under_memory_limit(self):
        with tempfile.TemporaryDirectory() as td:
            man=linker.build(self.plan(2592,objective="speed"),Path(td))
            self.assertEqual(len(man["link_order"]),1)
            self.assertEqual(set(x["variant"] for x in man["operations"]),{SHARED})
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],2592)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],31)
            model=man["cycle_model_benchmark"]
            self.assertTrue(model["cpu_model_only"])
            self.assertEqual(set(model["operations"]),{"MATH_UMUL32","MATH_SMUL32"})
            for entry in model["operations"].values():
                self.assertEqual(entry["cases"],192)
                self.assertIn(SHARED,entry["mean_cycles"])

if __name__=="__main__":
    unittest.main()
