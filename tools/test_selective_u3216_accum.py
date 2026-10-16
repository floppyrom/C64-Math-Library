#!/usr/bin/env python3
"""Dual-variant 32/16 shared-producer arithmetic and same-corpus CPU speed proof."""
from __future__ import annotations
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
import math_builder
import selective_linker as linker

APIS=("MATH_UDIV32_16","MATH_UMOD32_16")
VARIANTS=("link:portable-restoring","link:accumulator-remainder")
EDGES=(0,1,2,3,127,255,256,257,0xffff,0x10000,0x10001,
       0x7fffffff,0x80000000,0xfffffffe,0xffffffff)
DS=(0,1,2,3,7,127,255,256,257,32767,32768,65535)


def corpus():
    pairs=[(n,d) for n in EDGES for d in DS]
    rng=random.Random(0x32160A11)
    pairs.extend((rng.getrandbits(32),rng.getrandbits(16)) for _ in range(260))
    pairs.extend((rng.getrandbits(32),rng.choice((1,2,3,7,255,256,65535)))
                 for _ in range(100))
    return pairs


class Accumulator3216Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def build(self,out,variant,code,io):
        return linker.build(math_builder.create_plan(
            self.index,list(APIS),
            pins={api:variant for api in APIS},
            zp_budget=0,ram_budget=197),Path(out),
            memory={"code_base":code,"math_io":io})

    def test_same_corpus_cpu_correctness_and_performance_two_relocations(self):
        pairs=corpus()
        self.assertGreaterEqual(len(pairs),500)
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                totals={}
                for variant in VARIANTS:
                    man=self.build(td,variant,code,io)
                    expected_size,expected_scratch=((162,3)
                        if variant=="link:portable-restoring" else (131,1))
                    self.assertEqual(man["resource_use"]["code_and_tables_bytes"],expected_size)
                    self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],expected_scratch)
                    self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                    self.assertEqual(len(man["link_order"]),1)
                    self.assertEqual(set(man["link_exports"]),set(APIS))
                    entries=[int(row["entry"][1:],16) for row in man["operations"]]
                    self.assertEqual(entries[0],entries[1])
                    prg=(Path(td)/"math_selective.prg").read_bytes()
                    cpu=CPU(bytearray(65536))
                    cpu.mem[code:code+len(prg)-2]=prg[2:]
                    orig=bytes(cpu.mem[code:code+expected_size])
                    sp=cpu.sp
                    count=0
                    for n,d in pairs:
                        for entry in entries:
                            cpu.mem[io+16:io+20]=n.to_bytes(4,"little")
                            cpu.mem[io+20:io+22]=d.to_bytes(2,"little")
                            cpu.mem[io+24:io+28]=b"\x55"*4
                            cpu.mem[io+28:io+32]=b"\x66\x66\x69\xab"
                            cpu.c=count&1
                            cycles=cpu.call(entry,15000)
                            q=int.from_bytes(cpu.mem[io+24:io+28],"little")
                            rem=int.from_bytes(cpu.mem[io+28:io+30],"little")
                            self.assertEqual((q,rem,cpu.c),
                                (n//d if d else 0,n%d if d else 0,int(d==0)),
                                (variant,hex(n),hex(d)))
                            self.assertEqual(cpu.mem[io+16:io+20],n.to_bytes(4,"little"))
                            self.assertEqual(cpu.mem[io+20:io+22],d.to_bytes(2,"little"))
                            self.assertEqual(cpu.mem[io+30:io+32],b"\x69\xab")
                            self.assertEqual(cpu.sp,sp)
                            if d:totals[variant]=totals.get(variant,0)+cycles
                            count+=1
                    self.assertEqual(bytes(cpu.mem[code:code+expected_size]),orig)
                    self.assertEqual(count,2*len(pairs))
                # Actual same input pairs at identical addresses for each
                # variant, not comparing unrelated historical benchmark corpora.
                self.assertLess(totals["link:accumulator-remainder"],
                                totals["link:portable-restoring"],totals)
                print("U3216 matched-corpus",hex(code),len(pairs)*2,totals)

    def test_default_global_pareto_and_pin_respect(self):
        with tempfile.TemporaryDirectory() as td:
            plan=math_builder.create_plan(self.index,list(APIS),
                zp_budget=0,ram_budget=197)
            man=linker.build(plan,Path(td))
            self.assertEqual({r["variant"] for r in man["operations"]},
                             {"link:accumulator-remainder"})
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],164)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],1)
            with self.assertRaises(linker.LinkError):
                linker.build(math_builder.create_plan(self.index,list(APIS),
                    zp_budget=0,ram_budget=163),Path(td)/"rejected")


if __name__=="__main__":
    unittest.main()
