#!/usr/bin/env python3
"""Full signed 24/24 quotient/remainder shared producer, relocations, CPU ABI."""
from __future__ import annotations
import random
import tempfile
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker as linker
from mini6502 import CPU

EDGES=(0,1,2,3,7,127,255,256,65535,65536,0x7fffff,
       0x800000,0x800001,0xfffffe,0xffffff)
DIVS=(0,1,2,3,127,255,0x7fffff,0x800000,0x800001,0xffffff)

def signed24(v):return v-(1<<24) if v&0x800000 else v

def reference(n,d):
    n,d=signed24(n),signed24(d)
    if not d:return 0,0,1
    q=abs(n)//abs(d)
    if (n<0)!=(d<0):q=-q
    rem=n-q*d
    return q&0xffffff,rem&0xffffff,0

def corpus():
    rng=random.Random(0x5D2424)
    return [(n,d) for n in EDGES for d in DIVS]+[
        (rng.getrandbits(24),rng.getrandbits(24)) for _ in range(1250)]

class SDIV24SMOD24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()
    def plan(self,ops=("SDIV24","SMOD24"),ram=364):
        return math_builder.create_plan(
            self.index,list(ops),objective="size",zp_budget=0,ram_budget=ram)

    def test_signed_full_width_three_relocations_and_shared_image(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                m=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                u=m["resource_use"]
                self.assertEqual(u["image_span_bytes"],325)
                self.assertEqual(u["main_ram_total_bytes"],364)
                self.assertEqual(u["private_ram_scratch_bytes"],7)
                self.assertEqual(u["zero_page_bytes"],0)
                self.assertEqual(len(m["link_order"]),1)
                entries={x["api"]:int(x["entry"][1:],16) for x in m["operations"]}
                self.assertEqual(entries["MATH_SDIV24"],entries["MATH_SMOD24"])
                prg=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(prg),327)
                self.assertEqual(prg[:2],code.to_bytes(2,"little"))
                mem=bytearray(65536);mem[code:code+325]=prg[2:]
                original=bytes(mem[code:code+325])
                cpu=CPU(mem);stack=cpu.sp
                for i,(n,d) in enumerate(corpus()):
                    nb=n.to_bytes(3,"little")+bytes([0x5a])
                    db=d.to_bytes(3,"little")+bytes([0xa5])
                    mem[io+16:io+20]=nb
                    mem[io+20:io+24]=db
                    mem[io+24:io+28]=bytes([0xcc,0xcc,0xcc,0x39])
                    mem[io+28:io+32]=bytes([0xdd,0xdd,0xdd,0x59])
                    cpu.d=0;cpu.c=(n^d^i)&1
                    cpu.call(entries["MATH_SDIV24" if i&1 else "MATH_SMOD24"],85000)
                    got=(int.from_bytes(mem[io+24:io+27],"little"),
                         int.from_bytes(mem[io+28:io+31],"little"),cpu.c)
                    self.assertEqual(got,reference(n,d),(code,n,d))
                    self.assertEqual((mem[io+27],mem[io+31]),(0x39,0x59))
                    self.assertEqual(bytes(mem[io+16:io+20]),nb)
                    self.assertEqual(bytes(mem[io+20:io+24]),db)
                    self.assertEqual(cpu.sp,stack)
                self.assertEqual(bytes(mem[code:code+325]),original)

    def test_separate_apis_mixed_calls_and_budget(self):
        with tempfile.TemporaryDirectory() as td:
            for api in ("SDIV24","SMOD24"):
                m=linker.build(self.plan((api,)),Path(td)/api)
                self.assertEqual(m["resource_use"]["main_ram_total_bytes"],364)
            m=linker.build(self.plan(
                ("SDIV24","SMOD24","SDIV16","UMUL16"),ram=678),
                Path(td)/"mixed")
            self.assertEqual(m["resource_use"]["main_ram_total_bytes"],678)
            self.assertEqual(m["resource_use"]["private_ram_scratch_bytes"],7)
            self.assertEqual(len(m["link_order"]),3)
            entry={v["api"]:int(v["entry"][1:],16) for v in m["operations"]}
            prg=(Path(td)/"mixed"/"math_selective.prg").read_bytes()
            mem=bytearray(65536);mem[0x8000:0x8000+len(prg)-2]=prg[2:]
            cpu=CPU(mem);rng=random.Random(0xD24661)
            for i in range(300):
                n,d=rng.getrandbits(24),rng.getrandbits(24)
                mem[0xc010:0xc013]=n.to_bytes(3,"little")
                mem[0xc014:0xc017]=d.to_bytes(3,"little")
                cpu.d=0
                cpu.call(entry["MATH_SDIV24" if i&1 else "MATH_SMOD24"],85000)
                self.assertEqual((int.from_bytes(mem[0xc018:0xc01b],"little"),
                                  int.from_bytes(mem[0xc01c:0xc01f],"little"),cpu.c),
                                 reference(n,d))
                cpu.call(entry["MATH_SDIV16"],50000)
                n16=n&65535;d16=d&65535
                from test_selective_sdiv16 import reference as ref16
                self.assertEqual((int.from_bytes(mem[0xc018:0xc01a],"little"),
                                  int.from_bytes(mem[0xc01c:0xc01e],"little"),cpu.c),
                                 ref16(n16,d16))
                x,y=rng.randrange(65536),rng.randrange(65536)
                mem[0xc000:0xc002]=x.to_bytes(2,"little")
                mem[0xc004:0xc006]=y.to_bytes(2,"little")
                cpu.call(entry["MATH_UMUL16"],50000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00c],"little"),x*y)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=363),Path(td)/"no_ram")
if __name__=="__main__":
    unittest.main()
