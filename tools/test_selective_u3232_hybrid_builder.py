#!/usr/bin/env python3
"""Builder-linked unrestricted Q32/R32 hybrid: two APIs, RAM/ZP guards, speed."""
from __future__ import annotations
import random
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_hybrid_u3232 as hybrid
import selective_speed_u3232 as speed

ID="link:v2-lowdivisor-hybrid"
APIS=("UDIV32_32","UMOD32_32")
RAM=hybrid.IMAGE_BYTES+32

class V2HybridBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=APIS,objective="size",ram=RAM,zp=12,pins=None):
        return math_builder.create_plan(
            self.index,list(ops),objective=objective,
            zp_budget=zp,ram_budget=ram,
            pins=pins if pins is not None else ({op:ID for op in ops}
                                                 if objective=="size" else None),
            workload_calls={op:100 for op in ops}
              if objective=="speed" and len(ops)>1 else None)

    def test_two_map_full_public_q32_r32_and_one_code_image(self):
        rng=random.Random(0x3232AA6)
        pairs=speed.corpus()
        pairs.extend((rng.getrandbits(32),rng.getrandbits(32))
                     for _ in range(80))
        for base,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            with self.subTest(base=base),tempfile.TemporaryDirectory() as td:
                out=Path(td)
                man=linker.build(self.plan(),out,memory={
                    "code_base":base,"math_io":io,"zp_base":zp})
                use=man["resource_use"]
                self.assertEqual(len(man["link_order"]),1)
                self.assertEqual({x["variant"] for x in man["operations"]},{ID})
                self.assertEqual(use["image_span_bytes"],hybrid.IMAGE_BYTES)
                self.assertEqual(use["main_ram_total_bytes"],RAM)
                self.assertEqual(use["zero_page_bytes"],12)
                self.assertEqual(use["private_ram_scratch_bytes"],0)
                self.assertEqual(len(man["operations"]),2)
                entries={x["api"]:int(x["entry"][1:],16) for x in man["operations"]}
                self.assertEqual(len(set(entries.values())),1)
                self.assertEqual(next(iter(entries.values())),base+hybrid.DISPATCH_OFFSET)
                p=(out/"math_selective.prg").read_bytes()
                self.assertEqual(len(p),hybrid.IMAGE_BYTES+2)
                source,_,_,_=hybrid.assemble(base,io,zp)
                self.assertEqual(p[2:],bytes(source[i] for i in range(base,base+3200)))
                memory=bytearray(65536);memory[base:base+3200]=p[2:]
                cpu=CPU(memory);sp=cpu.sp
                for i,(n,d) in enumerate(pairs):
                    nb=n.to_bytes(4,"little");db=d.to_bytes(4,"little")
                    for api in ("MATH_UDIV32_32","MATH_UMOD32_32"):
                        memory[io+16:io+20]=nb;memory[io+20:io+24]=db
                        memory[io+24:io+32]=b"\x55"*8
                        cpu.c=(i^n^d)&1;cpu.d=0
                        cpu.call(entries[api],150000)
                        q=int.from_bytes(memory[io+24:io+28],"little")
                        rem=int.from_bytes(memory[io+28:io+32],"little")
                        self.assertEqual((q,rem,cpu.c),
                            (n//d if d else 0,n%d if d else 0,int(d==0)),
                            (hex(base),api,hex(n),hex(d)))
                        self.assertEqual(memory[io+16:io+20],nb)
                        self.assertEqual(memory[io+20:io+24],db)
                        self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(memory[base:base+3200]),p[2:])

    def test_speed_model_and_hybrid_budget_guards(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            sp=linker.build(self.plan(objective="speed"),root/"speed")
            model=sp["cycle_model_benchmark"]
            self.assertTrue(model["cpu_model_only"])
            self.assertEqual(set(model["operations"]),
                {"MATH_UDIV32_32","MATH_UMOD32_32"})
            for op in APIS:
                candidate=model["operations"]["MATH_"+op]
                self.assertEqual(candidate["cases"],384)
                self.assertIn(ID,candidate["mean_cycles"])
                self.assertLess(candidate["mean_cycles"][ID],
                                candidate["mean_cycles"]["link:shared-aligned-zerozp"])
            pinned=linker.build(self.plan(),root/"pinned")
            self.assertEqual(pinned["resource_use"]["main_ram_total_bytes"],RAM)
            for ram,zp in ((RAM-1,12),(RAM,11)):
                with self.subTest(ram=ram,zp=zp),self.assertRaises(linker.LinkError):
                    linker.build(self.plan(ram=ram,zp=zp),root/("negative_%d_%d"%(ram,zp)))
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(),root/"reserved",
                    memory={"zp_reserved":[{"start":"$58","end":"$58"}]})

    def test_fail_closed_measured_candidate_set(self):
        api="MATH_UDIV32_32"
        saved=dict(linker.MODULES[api])
        with tempfile.TemporaryDirectory() as td:
            try:
                del linker.MODULES[api][ID]
                with self.assertRaisesRegex(linker.LinkError,
                                            "cycle-model measurement failed"):
                    linker.build(self.plan(ops=("UDIV32_32",),
                                           objective="speed"),Path(td))
            finally:
                linker.MODULES[api]=saved

if __name__=="__main__":
    unittest.main()
