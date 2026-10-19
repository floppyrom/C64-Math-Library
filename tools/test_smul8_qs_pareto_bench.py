#!/usr/bin/env python3
"""Two-source same-corpus signed8 ABI and measured Pareto comparisons.

The SMC historical source is preserved and timed with writable code. The
read-only source is timed separately under identical public calls; do not
make native-resident or physical PAL timing claims from CPU model cycles.
"""
from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU
import math_builder
import selective_linker as linker

OLD="link:v1-resident-smc"
NEW="link:qs-readonly"
EDGES=(0,1,2,3,15,16,17,63,64,127,128,129,254,255)
COUNT=512


def corpus():
    pairs=[(x,y) for x in EDGES for y in EDGES]
    rng=random.Random(0x5A6438)
    pairs.extend((rng.randrange(256),rng.randrange(256))
                 for _ in range(COUNT-len(pairs)))
    return pairs


def measure(variant,code,io):
    ram=1193 if variant==NEW else 2336
    plan=math_builder.create_plan(
        math_builder.operation_index(),["SMUL8"],objective="size",
        pins={"SMUL8":variant},zp_budget=0,ram_budget=ram)
    with tempfile.TemporaryDirectory() as td:
        folder=Path(td)
        man=linker.build(plan,folder,memory={
            "code_base":code,"math_io":io,
            "scratch_base":io+0x40})
        data=(folder/"math_selective.prg").read_bytes()
        memory=bytearray(65536)
        addr=int.from_bytes(data[:2],"little")
        memory[addr:addr+len(data)-2]=data[2:]
        cpu=CPU(memory)
        entry=int(man["operations"][0]["entry"][1:],16)
        stack=cpu.sp
        cycles=[]
        for k,(x,y) in enumerate(corpus()):
            memory[io]=x
            memory[io+1]=0xa5
            memory[io+4]=y
            memory[io+5]=0x5a
            memory[io+8:io+12]=bytes((0xcc,0xdd,0x42,0x43))
            cpu.a=(x+y+k)&255
            cpu.x=(x^y^k)&255
            cpu.y=(x+k)&255
            cpu.c=(y+k)&1
            cpu.d=0
            count=cpu.call(entry,5000)
            sx=x-(256 if x&128 else 0)
            sy=y-(256 if y&128 else 0)
            actual=int.from_bytes(memory[io+8:io+10],"little")
            if (actual != ((sx*sy)&0xffff) or cpu.c or cpu.sp != stack or
                bytes(memory[io+10:io+12])!=bytes((0x42,0x43)) or
                (memory[io],memory[io+1],memory[io+4],memory[io+5])!=
                    (x,0xa5,y,0x5a)):
                raise AssertionError((variant,x,y,actual,sx*sy))
            cycles.append(count)
        return {"mean":sum(cycles)/len(cycles),
                "max":max(cycles),
                "p95":sorted(cycles)[int(len(cycles)*.95)-1],
                "code_and_tables":man["resource_use"]["code_and_tables_bytes"],
                "main_ram":man["resource_use"]["main_ram_total_bytes"],
                "zero_page":man["resource_use"]["zero_page_bytes"]}


class Signed8ReadOnlyPareto(unittest.TestCase):
    def test_full_public_source_cycles_at_two_origins(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            old=measure(OLD,code,io)
            new=measure(NEW,code,io)
            report={"origin":"$%04X"%code,"pairs":COUNT,
                    "old_smc":old,"new_readonly":new}
            print("SMUL8_SAME_PUBLIC_SOURCE_PARETO",
                  json.dumps(report,sort_keys=True),flush=True)
            self.assertLess(new["main_ram"],old["main_ram"])
            self.assertEqual(new["zero_page"],0)
            self.assertEqual(old["zero_page"],0)
            self.assertGreater(old["mean"],0)
            self.assertGreater(new["mean"],0)


if __name__=="__main__":
    unittest.main()
