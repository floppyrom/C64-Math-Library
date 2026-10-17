#!/usr/bin/env python3
"""Builder-linked zero-ZP unrolled DIV32/16+MOD32/16: speed and safety."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_u3216 as speed

FAST="link:accum-unrolled-32"
APIS=("UDIV32_16","UMOD32_16")
SIZE=1771
RAM=SIZE+32+1

class Unrolled3216BuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=APIS,ram=RAM,pins=None,objective="speed"):
        return math_builder.create_plan(
            self.index,list(ops),objective=objective,zp_budget=0,
            ram_budget=ram,pins=pins,
            workload_calls={op:100 for op in ops} if objective=="speed" and len(ops)>1
                           else None)

    def test_two_maps_384_pairs_both_public_entries_single_binary(self):
        pairs=speed.corpus()
        self.assertEqual(len(pairs),384)
        for base,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(base=base),tempfile.TemporaryDirectory() as td:
                out=Path(td)
                man=linker.build(self.plan(pins={x:FAST for x in APIS}),
                    out,memory={"code_base":base,"math_io":io,"scratch_base":scratch})
                self.assertEqual(len(man["link_order"]),1)
                self.assertEqual(len(man["operations"]),2)
                self.assertEqual({r["variant"] for r in man["operations"]},{FAST})
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],RAM)
                self.assertEqual(man["resource_use"]["code_and_tables_bytes"],SIZE)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],1)
                entry={r["api"]:int(r["entry"][1:],16) for r in man["operations"]}
                self.assertEqual(len(set(entry.values())),1)
                prg=(out/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),SIZE+2)
                mem=bytearray(65536);mem[base:base+SIZE]=prg[2:]
                cpu=CPU(mem);sp=cpu.sp
                for i,(n,d) in enumerate(pairs):
                    for api in ("MATH_UDIV32_16","MATH_UMOD32_16"):
                        nb=n.to_bytes(4,"little");db=d.to_bytes(2,"little")
                        mem[io+16:io+20]=nb;mem[io+20:io+22]=db
                        mem[io+24:io+28]=b"\x55"*4
                        mem[io+28:io+32]=b"\x66\x66\x69\xab"
                        cpu.d=0;cpu.c=(i^n^d)&1
                        cpu.call(entry[api],20000)
                        got=(int.from_bytes(mem[io+24:io+28],"little"),
                             int.from_bytes(mem[io+28:io+30],"little"),cpu.c)
                        want=(n//d if d else 0,n%d if d else 0,int(d==0))
                        self.assertEqual(got,want,(api,n,d))
                        self.assertEqual(mem[io+16:io+20],nb)
                        self.assertEqual(mem[io+20:io+22],db)
                        self.assertEqual(mem[io+30:io+32],b"\x69\xab")
                        self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[base:base+SIZE]),prg[2:])

    def test_automatic_speed_and_zerozp_pareto(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            high=linker.build(self.plan(),root/"high")
            self.assertEqual({r["variant"] for r in high["operations"]},{FAST})
            self.assertEqual(high["resource_use"]["main_ram_total_bytes"],RAM)
            model=high["cycle_model_benchmark"]
            self.assertTrue(model["cpu_model_only"])
            for api in ("MATH_UDIV32_16","MATH_UMOD32_16"):
                means=model["operations"][api]["mean_cycles"]
                self.assertEqual(set(means),speed.EXPECTED)
                self.assertLess(means[FAST],means["link:accumulator-remainder"])
            small=linker.build(self.plan(ram=164),root/"small")
            self.assertEqual({r["variant"] for r in small["operations"]},
                             {"link:accumulator-remainder"})
            self.assertEqual(small["resource_use"]["main_ram_total_bytes"],164)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=163),root/"too_small")

if __name__=="__main__":
    unittest.main()
