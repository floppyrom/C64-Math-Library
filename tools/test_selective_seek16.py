#!/usr/bin/env python3
"""SEEK16 source migration: four independent entries, 248-byte shared state."""
from __future__ import annotations
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU

FAMILY=("MATH_SEEK16_INIT","MATH_SEEK16_STEP","MATH_SEEK16_STEP_INT","MATH_SEEK16_STEP1")
SEEK8=("MATH_SEEK8_INIT","MATH_SEEK8_STEP","MATH_SEEK8_STEP_INT","MATH_SEEK8_STEP1")


class SelectiveSeek16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.index=math_builder.operation_index()

    def plan(self,ops=FAMILY,**kw): return math_builder.create_plan(self.index,list(ops),**kw)

    def load(self,folder,code=0x8000,io=0xc000,scratch=0xc020,ops=FAMILY,limit=None):
        plan=self.plan(ops,zp_budget=0,ram_budget=limit)
        man=selective_linker.build(plan,Path(folder),memory={
            "code_base":code,"math_io":io,"scratch_base":scratch})
        image=(Path(folder)/"math_selective.prg").read_bytes()
        cpu=CPU(bytearray(65536))
        cpu.mem[code:code+len(image)-2]=image[2:]
        exports={row["api"]:int(row["entry"][1:],16) for row in man["operations"]}
        states={name:int(addr[1:],16) for name,addr in
                man["memory_map"]["persistent_state"].items()}
        return cpu,man,exports,states

    def test_four_distinct_exports_single_physical_producer(self):
        with tempfile.TemporaryDirectory() as temp:
            _,man,entries,states=self.load(temp,limit=1202)
            self.assertEqual(set(entries),set(FAMILY))
            self.assertEqual(len(set(entries.values())),4)
            self.assertEqual(len(man["link_order"]),1)
            self.assertEqual(man["resource_use"]["code_and_tables_bytes"],898)
            self.assertEqual(man["resource_use"]["image_span_bytes"],898)
            self.assertEqual(man["resource_use"]["persistent_state_bytes"],248)
            self.assertEqual(man["resource_use"]["state_alignment_padding_bytes"],5)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],19)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],1202)
            self.assertEqual(states["seek16"],0xc038)
            inc=(Path(temp)/"math_api.inc").read_text()
            for field,addr in (("XL","$C038"),("XH","$C040"),("Y","$C048")):
                self.assertIn(f"MATH_SEEK16_POS_{field} = {addr}",inc)

    def test_native_mode_equivalent_fullwidth_moves_two_maps(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),(0x7123,0xc100,0xc121)):
            with self.subTest(origin=code),tempfile.TemporaryDirectory() as td:
                cpu,_,entries,states=self.load(td,code,io,scratch,limit=1202)
                state=states["seek16"]
                original=bytes(cpu.mem[code:code+898])
                rng=random.Random(0xC64162026)
                for mode in range(4):
                    for batch in range(8):
                        goal={}
                        for slot in range(8):
                            start_x=rng.randrange(80,520)
                            start_y=rng.randrange(200)
                            target_x=rng.randrange(640)
                            target_y=rng.randrange(200)
                            if mode==0 and batch==0 and slot==0:
                                target_x,target_y=start_x,start_y
                            cpu.mem[state+slot]=start_x&255
                            cpu.mem[state+8+slot]=start_x>>8
                            cpu.mem[state+16+slot]=start_y
                            cpu.mem[io:io+2]=target_x.to_bytes(2,"little")
                            cpu.mem[io+4]=target_y
                            speed,step=(
                                ((0x80,1),"MATH_SEEK16_STEP"),
                                ((0,2),"MATH_SEEK16_STEP_INT"),
                                ((0,1),"MATH_SEEK16_STEP1"),
                                ((0x80,0x81),"MATH_SEEK16_STEP"),
                            )[mode]
                            cpu.mem[io+16:io+18]=bytes(speed)
                            cpu.x=slot
                            cpu.call(entries["MATH_SEEK16_INIT"],160000)
                            self.assertEqual(cpu.x,slot)
                            self.assertEqual(cpu.c,int((start_x,start_y)==(target_x,target_y)))
                            self.assertEqual(tuple(cpu.mem[io:io+2]),tuple(target_x.to_bytes(2,"little")))
                            self.assertEqual(cpu.mem[io+4],target_y)
                            self.assertEqual(tuple(cpu.mem[io+16:io+18]),speed)
                            goal[slot]=(target_x,target_y,step)
                        for _ in range(700):
                            outstanding=0
                            for slot,(tx,ty,step) in goal.items():
                                cpu.x=slot
                                cpu.call(entries[step],100000)
                                self.assertEqual(cpu.x,slot)
                                if not cpu.c: outstanding+=1
                                else:
                                    actual=(cpu.mem[state+slot]|cpu.mem[state+8+slot]<<8,cpu.mem[state+16+slot])
                                    self.assertEqual(actual,(tx,ty))
                            if not outstanding: break
                        else:
                            self.fail("SEEK16 did not arrive in seven hundred frames")
                        for slot,(tx,ty,step) in goal.items():
                            cpu.x=slot
                            cpu.call(entries[step],100000)
                            self.assertEqual(cpu.c,1)
                            self.assertEqual((cpu.mem[state+slot]|cpu.mem[state+8+slot]<<8,cpu.mem[state+16+slot]),(tx,ty))
                self.assertEqual(bytes(cpu.mem[code:code+898]),original)

    def test_ram_bounds_and_independent_seek8_seek16_state(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertRaises(selective_linker.LinkError,self.load,td,limit=1201)
            self.assertFalse((Path(td)/"math_selective.prg").exists())
            cpu,man,entries,states=self.load(td,ops=FAMILY+SEEK8,limit=2013)
            self.assertEqual(man["resource_use"]["code_and_tables_bytes"],1549)
            self.assertEqual(man["resource_use"]["persistent_state_bytes"],408)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],2013)
            self.assertEqual(len(set(entries.values())),8)
            self.assertEqual(len(man["link_order"]),2)
            self.assertEqual(states["seek16"],0xc038)
            self.assertEqual(states["seek8"],0xc130)
            # Both families are persistent, disjoint, and non-reusable as scratch.
            for base,size in ((states["seek16"],248),(states["seek8"],160)):
                self.assertEqual(base&7,0)
                for addr in range(base,base+size): cpu.mem[addr]=addr&255
            self.assertEqual(cpu.mem[states["seek16"]],0x38)
            self.assertEqual(cpu.mem[states["seek8"]],0x30)
            with tempfile.TemporaryDirectory() as other:
                plan=self.plan(FAMILY+SEEK8)
                with self.assertRaises(selective_linker.LinkError):
                    selective_linker.build(plan,Path(other),memory={
                        "reserved":[{"start":"$C130","end":"$C137"}]})
                self.assertFalse((Path(other)/"math_selective.prg").exists())


if __name__=="__main__": unittest.main()
