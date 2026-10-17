#!/usr/bin/env python3
"""One V2 32/16 Q/R public producer linked for two APIs, resources and cycles."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_u3216 as speed
import selective_v2_fast_u3216 as v2

FAST="link:v2-sizefast-public"
APIS=("UDIV32_16","UMOD32_16")
SIZE=v2.IMAGE_BYTES
MAIN_RAM=SIZE+32

class V2SizeFast3216BuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=APIS,ram=MAIN_RAM,zp=12,pins=None,calls=None):
        return math_builder.create_plan(
            self.index,list(ops),objective="speed",
            zp_budget=zp,ram_budget=ram,pins=pins,
            workload_calls=calls if calls is not None and len(ops)>1 else
                ({op:100 for op in ops} if len(ops)>1 else None))

    def test_linked_public_two_maps_full_quotient_remainder_and_cpu_contract(self):
        pairs=speed.corpus()
        self.assertEqual(len(pairs),384)
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=linker.build(self.plan(pins={api:FAST for api in APIS}),
                    Path(td),memory={
                        "code_base":code,"math_io":io,"zp_base":zp})
                self.assertEqual(len(man["link_order"]),1)
                self.assertEqual({r["variant"] for r in man["operations"]},{FAST})
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],MAIN_RAM)
                self.assertEqual(man["resource_use"]["code_and_tables_bytes"],SIZE)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],12)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
                entries={r["api"]:int(r["entry"][1:],16) for r in man["operations"]}
                self.assertEqual(len(set(entries.values())),1)
                self.assertEqual(next(iter(entries.values())),code+v2.WRAPPER_OFFSET)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),SIZE+2)
                cpu=CPU(bytearray(65536))
                cpu.mem[code:code+SIZE]=prg[2:]
                sp=cpu.sp
                for i,(n,d) in enumerate(pairs):
                    for api in ("MATH_UDIV32_16","MATH_UMOD32_16"):
                        nb=n.to_bytes(4,"little");db=d.to_bytes(2,"little")
                        cpu.mem[io+16:io+20]=nb;cpu.mem[io+20:io+22]=db
                        cpu.mem[io+24:io+28]=b"\x55"*4
                        cpu.mem[io+28:io+32]=b"\x66\x66\x69\xab"
                        cpu.d=0;cpu.c=(i^d^n)&1
                        cpu.call(entries[api],20000)
                        got=(int.from_bytes(cpu.mem[io+24:io+28],"little"),
                             int.from_bytes(cpu.mem[io+28:io+30],"little"),
                             cpu.c)
                        want=(n//d if d else 0,n%d if d else 0,int(d==0))
                        self.assertEqual(got,want,(api,hex(n),hex(d)))
                        self.assertEqual(cpu.mem[io+16:io+20],nb)
                        self.assertEqual(cpu.mem[io+20:io+22],db)
                        self.assertEqual(cpu.mem[io+30:io+32],b"\x69\xab")
                        self.assertEqual(cpu.sp,sp)
                self.assertEqual(cpu.mem[code:code+SIZE],prg[2:])

    def test_speed_vs_three_zerozp_variants_and_exact_budget(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            high=linker.build(self.plan(ram=MAIN_RAM,zp=12),root/"high")
            means=high["cycle_model_benchmark"]["operations"]["MATH_UDIV32_16"]["mean_cycles"]
            self.assertEqual(set(means),speed.EXPECTED)
            self.assertLess(means[FAST],means["link:accum-unrolled-32"])
            self.assertEqual({r["variant"] for r in high["operations"]},{FAST})
            self.assertEqual(high["resource_use"]["main_ram_total_bytes"],MAIN_RAM)
            self.assertEqual(high["resource_use"]["zero_page_bytes"],12)
            low_zp=linker.build(self.plan(zp=0),root/"low_zp")
            self.assertEqual({r["variant"] for r in low_zp["operations"]},
                             {"link:accum-unrolled-32"})
            low_ram=linker.build(self.plan(ram=164,zp=12),root/"low_ram")
            self.assertEqual({r["variant"] for r in low_ram["operations"]},
                             {"link:accumulator-remainder"})
            for available in (11,):
                pinned={api:FAST for api in APIS}
                with self.assertRaises(linker.LinkError):
                    linker.build(self.plan(zp=available,pins=pinned),
                                 root/"less_zp")
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=MAIN_RAM-1,
                    pins={api:FAST for api in APIS}),root/"less_ram")
            print("V2 FAST U3216 MATCHED",means,flush=True)

if __name__=="__main__":
    unittest.main()
