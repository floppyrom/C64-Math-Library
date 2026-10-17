#!/usr/bin/env python3
"""Canonical historical V2 fast 24/24 DIV/MOD source-link proof and CPU cycles."""
from __future__ import annotations
import random
import hashlib
import tempfile
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
import selective_udiv24_v2
from mini6502 import CPU

APIS=("MATH_UDIV24","MATH_UMOD24")
FAST="link:v2-repose-fast"
SLOW="link:portable-restoring"


def corpus():
    e=(0,1,2,3,7,15,127,255,256,257,65535,65536,65537,
       0x7fffff,0x800000,0xfffffe,0xffffff)
    data=[(n,d) for n in e for d in e]
    rng=random.Random(0x241017)
    data.extend((rng.getrandbits(24),rng.getrandbits(24)) for _ in range(600))
    data.extend((rng.getrandbits(24),0) for _ in range(50))
    data.extend((rng.getrandbits(24),rng.randrange(1,256)) for _ in range(110))
    return data

class HistoricalV2U24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def build(self,td,variant,code=0x8000,io=0xc000,zp=0x90):
        pins={api:variant for api in APIS}
        p=math_builder.create_plan(self.index,list(APIS),
            pins=pins,zp_budget=3,ram_budget=1550)
        return selective_linker.build(p,Path(td),memory={
            "code_base":code,"math_io":io,"zp_base":zp})

    def test_source_translation_matches_canonical_reassembly(self):
        # Independent original-source transform vs emitted source file, exact byte parity.
        from mini6502 import Assembler
        src=(ROOT/"routines/divide/u24_v2_repose_selective.asm").read_text()
        for code,io,zp in ((0x8000,0xc000,0x90),(0x7123,0xc040,0xb0)):
            source=selective_udiv24_v2.render(code,code+1244,io,zp)
            original,labels,sizes=selective_udiv24_v2.assemble(
                code,code+1244,io,zp)
            self.assertEqual(sizes,(1244,217))
            locations={"KERNEL_CODE":code,"KERNEL_AUX":code+1244,
                "INPUT_NUM":io+16,"INPUT_DIV":io+20,
                "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,"TEMP_ZP":zp}
            adapted=selective_linker.relocate_source({
                "source":"routines/divide/u24_v2_repose_selective.asm",
                "segments":(("KERNEL_CODE",1244),("KERNEL_AUX",217)),
                "zp":3,"scratch":0},locations,ROOT)
            derived,ls,_=Assembler().assemble(adapted)
            self.assertEqual(derived,original)
            self.assertEqual(ls["DU24F_div_u24"],labels["DU24F_div_u24"])
            self.assertIn("sta DU24F_tail_bias+1",adapted)

    def test_same_seed_cpu_math_and_cycle_comparison(self):
        allcases=corpus()
        self.assertGreaterEqual(len(allcases),1000)
        for code,io,zp in ((0x8000,0xc000,0x90),(0x7123,0xc040,0xb0)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as tmp:
                totals={}
                for variant in (SLOW,FAST):
                    m=self.build(tmp,variant,code,io,zp)
                    resources=m["resource_use"]
                    expected=(190,4,0) if variant==SLOW else (1461,0,3)
                    self.assertEqual((resources["code_and_tables_bytes"],
                        resources["private_ram_scratch_bytes"],
                        resources["zero_page_bytes"]),expected)
                    self.assertEqual(len(m["link_order"]),1)
                    self.assertEqual(set(m["link_exports"]),set(APIS))
                    self.assertEqual(len(set(row["entry"] for row in m["operations"])),1)
                    for item in m["operations"]:
                        self.assertEqual(item["variant"],variant)
                        if variant==FAST:
                            self.assertEqual([a["source_path"] for a in item["dependencies"]],
                                ["relocatable_source/v2_pareto_fast/udiv24_direct_repose.inc",
                                 "tools/selective_udiv24_v2.py"])
                    prg=(Path(tmp)/"math_selective.prg").read_bytes()
                    self.assertEqual(hashlib.sha256(prg).hexdigest(),m["prg_sha256"])
                    cpu=CPU(bytearray(65536))
                    cpu.mem[code:code+len(prg)-2]=prg[2:]
                    entry=int(m["operations"][0]["entry"][1:],16)
                    total=0
                    sp=cpu.sp
                    for n,d in allcases:
                        cpu.mem[io+16:io+20]=n.to_bytes(3,"little")+b"\x6a"
                        cpu.mem[io+20:io+24]=d.to_bytes(3,"little")+b"\xa9"
                        cpu.mem[io+24:io+28]=b"\x55"*4
                        cpu.mem[io+28:io+32]=b"\x66"*4
                        cpu.d=0
                        cycles=cpu.call(entry,45000)
                        q=int.from_bytes(cpu.mem[io+24:io+27],"little")
                        r=int.from_bytes(cpu.mem[io+28:io+31],"little")
                        self.assertEqual((q,r,cpu.c),
                            (n//d if d else 0,n%d if d else 0,int(d==0)),
                            (variant,hex(n),hex(d),hex(code)))
                        self.assertEqual(cpu.mem[io+16:io+20],n.to_bytes(3,"little")+b"\x6a")
                        self.assertEqual(cpu.mem[io+20:io+24],d.to_bytes(3,"little")+b"\xa9")
                        self.assertEqual(cpu.mem[io+27],0x55)
                        self.assertEqual(cpu.mem[io+31],0x66)
                        self.assertEqual(cpu.sp,sp)
                        total+=cycles
                    totals[variant]=total
                print("V2 U24 MATCHED CORPUS",hex(code),len(allcases),
                      totals,"mean fast",totals[FAST]/len(allcases),flush=True)
                self.assertLess(totals[FAST],totals[SLOW])
    def test_source_writable_code_and_budget(self):
        with tempfile.TemporaryDirectory() as td:
            result=self.build(td,FAST)
            self.assertEqual(result["resource_use"]["main_ram_total_bytes"],1493)
            source=selective_linker.available_variants()["MATH_UDIV24"]
            fast=next(a for a in source if a["id"]==FAST)
            self.assertTrue(fast["requires_writable_code"])
            self.assertEqual(fast["zp_bytes_reported"],3)
            bad=math_builder.create_plan(self.index,list(APIS),
                pins={api:FAST for api in APIS},zp_budget=2,ram_budget=2000)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(bad,Path(td)/"bad")

if __name__=="__main__":unittest.main()
