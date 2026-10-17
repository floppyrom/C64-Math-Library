#!/usr/bin/env python3
"""Source-linked 16x16->32 / 16 fused unsigned/signed contracts and mixed calls."""
from __future__ import annotations
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU

EDGES=(0,1,2,3,0x007f,0x0080,0x00ff,0x0100,0x7fff,0x8000,0xfffe,0xffff)
OPS=("UMULDIV16","SMULDIV16")
def s16(v):return v-65536 if v&32768 else v
def pairs():
    cases=[(x,y,d) for x in EDGES for y in (0,1,0x7fff,0x8000,0xffff)
           for d in (0,1,2,0x7fff,0x8000,0xffff)]
    rng=random.Random(0x6416d16)
    return cases+[(rng.randrange(65536),rng.randrange(65536),rng.randrange(65536))
                  for _ in range(320)]
def expected(x,y,d,signed):
    if signed:
        p=s16(x)*s16(y);den=s16(d)
        if not den:return 0,0,1
        magnitude=abs(p)//abs(den)
        quotient= -magnitude if (p<0)!=(den<0) else magnitude
        return quotient&0xffffffff,(p-quotient*den)&65535,0
    if not d:return 0,0,1
    return (x*y)//d,(x*y)%d,0

class MulDiv16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ops=OPS,ram=765):
        return math_builder.create_plan(self.index,list(ops),objective="size",
                zp_budget=0,ram_budget=ram)
    def test_full_width_signed_unsigned_three_relocations(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=selective_linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=man["resource_use"]
                self.assertEqual(use["image_span_bytes"],727)
                self.assertEqual(use["private_ram_scratch_bytes"],6)
                self.assertEqual(use["main_ram_total_bytes"],765)
                self.assertEqual(use["zero_page_bytes"],0)
                entry={z["api"]:int(z["entry"][1:],16) for z in man["operations"]}
                img=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(img),729)
                mem=bytearray(65536);mem[code:code+727]=img[2:]
                original=bytes(mem[code:code+727]);cpu=CPU(mem);sp=cpu.sp
                for i,(x,y,d) in enumerate(pairs()):
                    # Test both signed and unsigned entry and alternate
                    # output buffers with one shared call-exclusive scratch map.
                    xb=x.to_bytes(2,"little");yb=y.to_bytes(2,"little")
                    db=d.to_bytes(2,"little")
                    mem[io:io+4]=xb+bytes((0xa5,0x5a))
                    mem[io+4:io+8]=yb+bytes((0x3c,0xc3))
                    mem[io+20:io+24]=db+bytes((0x55,0xaa))
                    before=bytes(mem[io:io+8])+bytes(mem[io+20:io+24])
                    for op in ((OPS if i%2 else OPS[::-1])):
                        cpu.d=0;cpu.c=(x^y^d^i)&1
                        cpu.call(entry["MATH_"+op],180000)
                        q,r,c=expected(x,y,d,op.startswith("S"))
                        gotq=int.from_bytes(mem[io+24:io+28],"little")
                        gotr=int.from_bytes(mem[io+28:io+30],"little")
                        self.assertEqual((gotq,gotr,cpu.c),(q,r,c),
                                         (code,op,x,y,d,i))
                        self.assertEqual(bytes(mem[io:io+8])+bytes(mem[io+20:io+24]),before)
                        self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+727]),original)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(self.plan(ram=764),Path(td)/"low")

if __name__=="__main__":
    unittest.main()
