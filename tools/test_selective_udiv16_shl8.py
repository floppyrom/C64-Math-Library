#!/usr/bin/env python3
"""CPU-model qualification for portable UDIV16_SHL8 source at arbitrary maps."""
from __future__ import annotations
import random
import sys
import tempfile
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
import math_builder
import selective_linker as linker

EDGE=(0,1,2,3,7,127,128,255,256,257,32767,32768,65534,65535)
DS=(0,1,2,3,7,255,256,257,32767,32768,65535)

def cases():
    rng=random.Random(0x16D108)
    return ([(n,d) for n in EDGE for d in DS] +
            [(rng.randrange(65536),rng.randrange(65536))
             for _ in range(1000)])

class UDIV16SHL8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=("UDIV16_SHL8",),ram=162):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=ram)

    def test_abi_full_domain_reference_and_relocation(self):
        pairs=cases()
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                m=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                use=m["resource_use"]
                self.assertEqual(use["image_span_bytes"],129)
                self.assertEqual(use["main_ram_total_bytes"],162)
                self.assertEqual(use["zero_page_bytes"],0)
                self.assertEqual(use["private_ram_scratch_bytes"],1)
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(prg[:2],code.to_bytes(2,"little"))
                cpu=CPU(bytearray(65536))
                mem=cpu.mem
                mem[code:code+129]=prg[2:]
                orig=bytes(mem[code:code+129])
                sp=cpu.sp
                entry=int(m["operations"][0]["entry"][1:],16)
                for n,d in pairs:
                    inputs=n.to_bytes(2,"little")+bytes([0xa5,0x5a])
                    divisor=d.to_bytes(2,"little")+bytes([0x6b,0x7c])
                    mem[io+16:io+20]=inputs
                    mem[io+20:io+24]=divisor
                    mem[io+24:io+28]=bytes([0x55])*4
                    mem[io+28:io+32]=bytes([0x66,0x66,0x69,0xab])
                    cpu.c=(n^d)&1
                    cpu.d=0
                    cpu.call(entry,50000)
                    q=int.from_bytes(mem[io+24:io+27],"little")
                    r=int.from_bytes(mem[io+28:io+30],"little")
                    expected=((n<<8)//d if d else 0,
                              (n<<8)%d if d else 0,
                              int(d==0))
                    self.assertEqual((q,r,cpu.c),expected,(code,n,d))
                    self.assertEqual(mem[io+27],0)
                    self.assertEqual(bytes(mem[io+30:io+32]),bytes([0x69,0xab]))
                    self.assertEqual(bytes(mem[io+16:io+20]),inputs)
                    self.assertEqual(bytes(mem[io+20:io+24]),divisor)
                    self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+129]),orig)

    def test_global_scratch_sharing_with_multiply_and_full_division(self):
        with tempfile.TemporaryDirectory() as td:
            m=linker.build(self.plan(
                ("UDIV16_SHL8","UDIV32_16","UMUL16"),ram=500),Path(td))
            self.assertEqual(m["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(m["resource_use"]["private_ram_scratch_bytes"],6)
            self.assertEqual(m["resource_use"]["main_ram_total_bytes"],406)
            image=(Path(td)/"math_selective.prg").read_bytes()
            cpu=CPU(bytearray(65536))
            mem=cpu.mem
            mem[0x8000:0x8000+len(image)-2]=image[2:]
            entries={v["api"]:int(v["entry"][1:],16)
                     for v in m["operations"]}
            rng=random.Random(0x3216A8)
            for _ in range(400):
                n=rng.randrange(65536)
                d=rng.randrange(65536)
                mem[0xc010:0xc014]=(n|0xa55a0000).to_bytes(4,"little")
                mem[0xc014:0xc016]=d.to_bytes(2,"little")
                cpu.d=0
                cpu.call(entries["MATH_UDIV16_SHL8"],50000)
                self.assertEqual(int.from_bytes(mem[0xc018:0xc01b],"little"),
                                 (n<<8)//d if d else 0)
                full=n|0xa55a0000
                cpu.call(entries["MATH_UDIV32_16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc018:0xc01c],"little"),
                                 full//d if d else 0)
                x,y=rng.randrange(65536),rng.randrange(65536)
                mem[0xc000:0xc002]=x.to_bytes(2,"little")
                mem[0xc004:0xc006]=y.to_bytes(2,"little")
                cpu.call(entries["MATH_UMUL16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00c],"little"),x*y)

    def test_fail_closed_exact_ram_budget(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=161),Path(td)/"too_small")

if __name__=="__main__":
    unittest.main()
