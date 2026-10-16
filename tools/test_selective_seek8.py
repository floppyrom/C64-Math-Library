#!/usr/bin/env python3
"""SEEK8 operation-first migration: multi-entry, persistent state and moves."""
from __future__ import annotations
import random
from pathlib import Path
import tempfile
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU

FAMILY=["MATH_SEEK8_INIT","MATH_SEEK8_STEP","MATH_SEEK8_STEP_INT","MATH_SEEK8_STEP1"]


class SelectiveSeek8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def plan(self,ops=FAMILY,**kwargs):
        return math_builder.create_plan(self.index,ops,**kwargs)

    def load(self, folder, origin=0x8000, io=0xc000, sb=None):
        memory={"code_base":origin,"math_io":io}
        if sb is not None:
            memory["scratch_base"]=sb
        manifest=selective_linker.build(self.plan(),Path(folder),memory=memory)
        binary=(Path(folder)/"math_selective.prg").read_bytes()
        cpu=CPU(bytearray(65536))
        cpu.mem[origin:origin+len(binary)-2]=binary[2:]
        state=int(manifest["memory_map"]["persistent_state"]["seek8"][1:],16)
        exports={d["api"]:int(d["entry"][1:],16) for d in manifest["operations"]}
        return cpu,manifest,exports,state

    def test_four_distinct_exports_one_physical_kernel(self):
        with tempfile.TemporaryDirectory() as d:
            cpu,man,ex,state=self.load(d)
            self.assertEqual(set(ex),set(FAMILY))
            self.assertEqual(len(set(ex.values())),4)
            self.assertEqual(man["resource_use"]["code_and_tables_bytes"],651)
            self.assertEqual(man["resource_use"]["image_span_bytes"],651)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],19)
            self.assertEqual(man["resource_use"]["persistent_state_bytes"],160)
            self.assertEqual(man["resource_use"]["state_alignment_padding_bytes"],5)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],867)
            inc=(Path(d)/"math_api.inc").read_text()
            self.assertIn("MATH_SEEK8_POS_X = $C038",inc)
            self.assertIn("MATH_SEEK8_POS_Y = $C040",inc)
            self.assertEqual(state,0xc038)
            self.assertEqual(len(man["link_order"]),1)
            self.assertEqual(set(man["link_exports"]),set(FAMILY))

    def test_move_all_slots_and_modes_at_two_relocations(self):
        for code,io,sb in ((0x8000,0xc000,0xc020),(0x7123,0xc100,0xc121)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as d:
                cpu,man,entries,state=self.load(d,code,io,sb)
                original_code=bytes(cpu.mem[code:code+651])
                rng=random.Random(0xC6482026)
                for mode in range(4):
                    for batch in range(15):
                        # Keep eight independent slots alive and interleave
                        # INIT and per-frame STEP calls (real sprite workflow).
                        expected={}
                        for slot in range(8):
                            startx=rng.randrange(256)
                            starty=rng.randrange(256)
                            targetx=rng.randrange(256)
                            targety=rng.randrange(256)
                            if batch==0 and slot==0:
                                targetx,startx=0,0
                                targety,starty=0,0
                            cpu.mem[state+slot]=startx
                            cpu.mem[state+8+slot]=starty
                            cpu.mem[io]=targetx
                            cpu.mem[io+4]=targety
                            if mode==0: speed=(0x80,0x01); step="MATH_SEEK8_STEP"
                            elif mode==1: speed=(0,0x02); step="MATH_SEEK8_STEP_INT"
                            elif mode==2: speed=(0,1); step="MATH_SEEK8_STEP1"
                            else: speed=(0x80,0x81); step="MATH_SEEK8_STEP"
                            cpu.mem[io+16:io+18]=bytes(speed)
                            cpu.x=slot
                            cpu.call(entries["MATH_SEEK8_INIT"],120000)
                            self.assertEqual(cpu.x,slot)
                            # CPU.call reports elapsed cycles; return carry is in cpu.c.
                            self.assertEqual(cpu.c,int((startx,starty)==(targetx,targety)))
                            self.assertEqual((cpu.mem[io],cpu.mem[io+4]),(targetx,targety))
                            self.assertEqual(tuple(cpu.mem[io+16:io+18]),speed)
                            expected[slot]=(targetx,targety,step)
                        for frame in range(530):
                            unfinished=0
                            for slot,(tx,ty,step) in expected.items():
                                cpu.x=slot
                                cpu.call(entries[step],120000)
                                self.assertEqual(cpu.x,slot)
                                if cpu.c==0: unfinished+=1
                                else: self.assertEqual((cpu.mem[state+slot],cpu.mem[state+8+slot]),(tx,ty))
                            if not unfinished:
                                break
                        else:
                            self.fail("SEEK8 slot failed to arrive in bound")
                        for slot,(tx,ty,step) in expected.items():
                            cpu.x=slot
                            cpu.call(entries[step],120000)
                            self.assertEqual(cpu.c,1)
                            self.assertEqual((cpu.mem[state+slot],cpu.mem[state+8+slot]),(tx,ty))
                self.assertEqual(bytes(cpu.mem[code:code+651]),original_code)

    def test_exclusive_scratch_and_state_overlap_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            plan=self.plan()
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(plan,Path(d),memory={
                    "reserved":[{"start":"$C038","end":"$C040"}]})
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(self.plan(ram_budget=866),Path(d))
            self.assertFalse((Path(d)/"math_selective.prg").exists())

    def test_mixed_operation_preserves_durable_seek_state(self):
        with tempfile.TemporaryDirectory() as d:
            plan=self.plan(FAMILY+["MATH_UMUL8"],zp_budget=0,ram_budget=927)
            man=selective_linker.build(plan,Path(d))
            self.assertEqual(man["resource_use"]["persistent_state_bytes"],160)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],927)
            self.assertEqual(set(man["link_exports"]),set(FAMILY+["MATH_UMUL8"]))
            self.assertEqual(len(man["link_order"]),2)
            self.assertEqual(man["resource_use"]["zero_page_bytes"],0)


if __name__=="__main__":
    unittest.main()
