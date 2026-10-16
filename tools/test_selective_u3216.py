#!/usr/bin/env python3
"""Unsigned 32/16 public DIV/MOD: exhaustive boundary and mixed-call CPU tests.

This is a correctness-only standalone reference migration. The shipped
V1-V5 32/16 speed champions remain unmodified and separate variants must be
transplanted and qualified on comparable input corpora.
"""
from __future__ import annotations
import random
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
import selective_linker as linker
import math_builder

APIS=("MATH_UDIV32_16","MATH_UMOD32_16")


def operands():
    ns=(0,1,2,3,7,15,255,256,257,65535,65536,65537,
        0x7fffffff,0x80000000,0xfffffffe,0xffffffff)
    ds=(0,1,2,3,7,15,127,255,256,257,32767,32768,65534,65535)
    pairs=[(n,d) for n in ns for d in ds]
    rng=random.Random(0xC643216)
    pairs.extend((rng.getrandbits(32),rng.getrandbits(16)) for _ in range(420))
    pairs.extend((rng.getrandbits(32),1 << rng.randrange(16)) for _ in range(100))
    pairs.extend((rng.getrandbits(32),0) for _ in range(24))
    pairs.extend((rng.randrange(65536),rng.randrange(65536)) for _ in range(80))
    return pairs


class U3216ReferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def build(self,path,ops=APIS,code=0x8000,io=0xc000,sb=None,**kw):
        plan=math_builder.create_plan(cls_index(self),list(ops),
                                      zp_budget=kw.pop("zp_budget",0),
                                      ram_budget=kw.pop("ram_budget",197),**kw)
        memory={"code_base":code,"math_io":io}
        if sb is not None:
            memory["scratch_base"]=sb
        return linker.build(plan,Path(path),memory=memory)

    def cpu(self,folder,man):
        prg=(Path(folder)/"math_selective.prg").read_bytes()
        start=prg[0]|prg[1]<<8
        cpu=CPU(bytearray(65536))
        cpu.mem[start:start+len(prg)-2]=prg[2:]
        return cpu,prg

    def test_shared_code_both_and_single_select(self):
        with tempfile.TemporaryDirectory() as td:
            for ops in (APIS,APIS[:1],APIS[1:]):
                man=self.build(td,ops=ops)
                self.assertEqual(man["resource_use"]["code_and_tables_bytes"],162)
                self.assertEqual(man["resource_use"]["image_span_bytes"],162)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],197)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],3)
                self.assertEqual(len(man["link_order"]),1)
                self.assertEqual(set(man["link_exports"]),set(ops))
                self.assertEqual({row["variant"] for row in man["operations"]},
                                 {"link:portable-restoring"})
                for row in man["operations"]:
                    self.assertEqual(row["scratch_bytes"],3)
                    self.assertEqual(row["zp_bytes"],0)
                inc=(Path(td)/"math_api.inc").read_text()
                for api in ops:self.assertIn(api+" = ",inc)
            man=self.build(td)
            entries={row["api"]:row["entry"] for row in man["operations"]}
            self.assertEqual(entries[APIS[0]],entries[APIS[1]])

    def test_public_32_by_16_results_carry_and_io_preserved_at_two_maps(self):
        for code,io,sb in ((0x8000,0xc000,0xc020),
                           (0x7123,0xc140,0xc160)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=self.build(td,code=code,io=io,sb=sb)
                cpu,prg=self.cpu(td,man)
                original=bytes(cpu.mem[code:code+162])
                entries=[int(row["entry"][1:],16) for row in man["operations"]]
                oldsp=cpu.sp
                for i,(n,d) in enumerate(operands()):
                    for entry in entries:
                        cpu.mem[io+16:io+20]=n.to_bytes(4,"little")
                        cpu.mem[io+20:io+22]=d.to_bytes(2,"little")
                        cpu.mem[io+24:io+28]=b"\x55"*4
                        cpu.mem[io+28:io+32]=b"\x66\x66\x69\xab"
                        cpu.c=i&1
                        cpu.call(entry,15000)
                        q=int.from_bytes(cpu.mem[io+24:io+28],"little")
                        rem=int.from_bytes(cpu.mem[io+28:io+30],"little")
                        self.assertEqual((q,rem,cpu.c),
                                         (n//d if d else 0,n%d if d else 0,int(d==0)),
                                         (hex(n),hex(d),hex(code)))
                        self.assertEqual(cpu.mem[io+16:io+20],n.to_bytes(4,"little"))
                        self.assertEqual(cpu.mem[io+20:io+22],d.to_bytes(2,"little"))
                        self.assertEqual(cpu.mem[io+30:io+32],b"\x69\xab")
                        self.assertEqual(cpu.sp,oldsp)
                self.assertEqual(bytes(cpu.mem[code:code+162]),original)
                self.assertEqual(man["resource_use"]["alignment_padding_bytes"],0)

    def test_ram_budget_and_reserved_memory_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(linker.LinkError):
                self.build(td,ram_budget=196)
            self.assertFalse((Path(td)/"math_selective.prg").exists())
            with self.assertRaises(linker.LinkError):
                self.build(td,ram_budget=197,sb=0xc01d)

    def test_mixed_math_uses_only_one_shared_scratch_span(self):
        with tempfile.TemporaryDirectory() as td:
            man=self.build(td,ops=APIS+("MATH_UMUL8",),ram_budget=257)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],3)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"],257)
            self.assertEqual(man["resource_use"]["code_and_tables_bytes"],222)
            self.assertEqual(len(man["link_order"]),2)


def cls_index(obj):
    return obj.index


if __name__=="__main__":
    unittest.main()
