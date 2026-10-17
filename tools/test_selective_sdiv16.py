#!/usr/bin/env python3
"""Signed 16/16 DIV+MOD public ABI, zero-ZP sharing and relocated CPU-model checks."""
from __future__ import annotations
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
import math_builder
import selective_linker as linker

EDGE=(0,1,2,3,7,127,128,255,256,257,32767,32768,32769,65534,65535)
D_EDGE=(0,1,2,3,127,128,255,256,32767,32768,32769,65535)

def signed(value):
    return value-65536 if value&0x8000 else value

def reference(n, d):
    n,d=signed(n),signed(d)
    if not d:
        return 0,0,1
    quot=abs(n)//abs(d)
    if (n<0)!=(d<0):
        quot=-quot
    rem=n-quot*d
    return quot&65535,rem&65535,0

def corpus():
    rng=random.Random(0x5D1616)
    return ([(n,d) for n in EDGE for d in D_EDGE]+
            [(rng.randrange(65536),rng.randrange(65536))
             for _ in range(1500)])

class SDIV16AndSMOD16(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()

    def plan(self,operations=("SDIV16","SMOD16"),ram=241):
        return math_builder.create_plan(
            self.index,list(operations),objective="size",
            zp_budget=0,ram_budget=ram)

    def test_shared_producer_signed_q_r_three_code_and_io_maps(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                m=linker.build(self.plan(),Path(td),memory={
                    "code_base":code,"math_io":io,"scratch_base":scratch})
                u=m["resource_use"]
                self.assertEqual(u["image_span_bytes"],206)
                self.assertEqual(u["main_ram_total_bytes"],241)
                self.assertEqual(u["private_ram_scratch_bytes"],3)
                self.assertEqual(u["zero_page_bytes"],0)
                self.assertEqual(len(m["link_order"]),1)
                entries={v["api"]:int(v["entry"][1:],16) for v in m["operations"]}
                self.assertEqual(entries["MATH_SDIV16"],entries["MATH_SMOD16"])
                image=(Path(td)/"math_selective.prg").read_bytes()
                self.assertEqual(len(image),208)
                self.assertEqual(image[:2],code.to_bytes(2,"little"))
                memory=bytearray(65536)
                memory[code:code+206]=image[2:]
                original=bytes(memory[code:code+206])
                cpu=CPU(memory)
                original_stack=cpu.sp
                for index,(n,d) in enumerate(corpus()):
                    nbytes=n.to_bytes(2,"little")+bytes([0x5a,0xa5])
                    dbytes=d.to_bytes(2,"little")+bytes([0x7c,0x6b])
                    memory[io+16:io+20]=nbytes
                    memory[io+20:io+24]=dbytes
                    memory[io+24:io+28]=bytes([0xcc,0xcc,0x29,0x39])
                    memory[io+28:io+32]=bytes([0xdd,0xdd,0x49,0x59])
                    cpu.d=0
                    cpu.c=(index^n^d)&1
                    cpu.call(entries["MATH_SDIV16" if index&1 else "MATH_SMOD16"],
                             50000)
                    actual=(int.from_bytes(memory[io+24:io+26],"little"),
                            int.from_bytes(memory[io+28:io+30],"little"),cpu.c)
                    self.assertEqual(actual,reference(n,d),(code,n,d))
                    self.assertEqual(bytes(memory[io+26:io+28]),bytes([0x29,0x39]))
                    self.assertEqual(bytes(memory[io+30:io+32]),bytes([0x49,0x59]))
                    self.assertEqual(bytes(memory[io+16:io+20]),nbytes)
                    self.assertEqual(bytes(memory[io+20:io+24]),dbytes)
                    self.assertEqual(cpu.sp,original_stack)
                self.assertEqual(bytes(memory[code:code+206]),original)

    def test_individual_entry_scratch_lifetime_and_ram_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            for operation in ("SDIV16","SMOD16"):
                m=linker.build(self.plan((operation,)),Path(td)/operation)
                self.assertEqual(m["resource_use"]["main_ram_total_bytes"],241)
            joint=linker.build(self.plan(
                ("SDIV16","SMOD16","UMUL16"),ram=349),Path(td)/"mix")
            self.assertEqual(joint["resource_use"]["private_ram_scratch_bytes"],6)
            self.assertEqual(joint["resource_use"]["main_ram_total_bytes"],349)
            self.assertEqual(joint["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(len(joint["link_order"]),2)
            entry={v["api"]:int(v["entry"][1:],16) for v in joint["operations"]}
            image=(Path(td)/"mix"/"math_selective.prg").read_bytes()
            memory=bytearray(65536)
            memory[0x8000:0x8000+len(image)-2]=image[2:]
            cpu=CPU(memory)
            rng=random.Random(0xD1616A)
            for index in range(340):
                n,d=rng.randrange(65536),rng.randrange(65536)
                memory[0xc010:0xc012]=n.to_bytes(2,"little")
                memory[0xc014:0xc016]=d.to_bytes(2,"little")
                cpu.d=0
                cpu.call(entry["MATH_SDIV16" if index&1 else "MATH_SMOD16"],50000)
                q,r,c=reference(n,d)
                self.assertEqual((int.from_bytes(memory[0xc018:0xc01a],"little"),
                                  int.from_bytes(memory[0xc01c:0xc01e],"little"),cpu.c),(q,r,c))
                x,y=rng.randrange(65536),rng.randrange(65536)
                memory[0xc000:0xc002]=x.to_bytes(2,"little")
                memory[0xc004:0xc006]=y.to_bytes(2,"little")
                cpu.call(entry["MATH_UMUL16"],50000)
                self.assertEqual(int.from_bytes(memory[0xc008:0xc00c],"little"),x*y)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=240),Path(td)/"too_small")

if __name__=="__main__":
    unittest.main()
